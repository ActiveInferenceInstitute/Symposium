"""Source-grounded dossiers and native-template abstract books from public bundles."""

from __future__ import annotations

import hashlib
import json
import os
import signal
import subprocess
import zipfile
from pathlib import Path
from urllib.parse import quote
from xml.etree import ElementTree as ET

from .models import PublicBundle, PublicPresentation, validate_bundle


class ArtifactError(RuntimeError):
    """Artifact prerequisites or native rendering failed; logs remain in the workspace."""


def _literal(value: str) -> str:
    """Encode punctuation so submitted prose cannot become Markdown, HTML, or TeX."""
    return "\n".join(
        "".join(
            char if char.isalnum() or char == " " else f"&#{ord(char)};" for char in line
        ).replace("    ", "&#32;&#32;&#32;&#32;")
        for line in value.split("\n")
    )


def _talks(bundle: PublicBundle) -> list[PublicPresentation]:
    return sorted(
        bundle["presentations"],
        key=lambda t: (
            t["contribution_type"].casefold(),
            t["presenter"].casefold(),
            t["title"].casefold(),
            t["id"],
        ),
    )


def _source(talk: PublicPresentation, *, provenance: bool = True) -> str:
    abstract = (
        _literal(talk["abstract"])
        if talk["abstract"].strip()
        else "No program abstract has been published for this presentation yet."
    )
    return (
        f"# {_literal(talk['title'])}\n\n"
        f"Presenter: {_literal(talk['presenter'])}\n\n"
        f"Contribution: {_literal(talk['contribution_type'])}\n\n"
        + (f"Public ID: {_literal(talk['id'])}\n\n" if provenance else "")
        + f"## Submitted abstract\n\n{abstract}\n\n"
        f"Source: [submitted source](<{quote(talk['source_url'], safe=':/?=&%#')}>)\n\n"
        + (f"Abstract SHA256: {talk['abstract_sha256']}\n" if provenance else "")
    )


def _write(path: Path, text: str) -> None:
    with path.open("x", encoding="utf-8") as handle:
        handle.write(text)


def write_dossiers(bundle: PublicBundle, output_dir: Path) -> list[Path]:
    """Write one organizer dossier per approved contribution into a new directory."""
    public = validate_bundle(bundle)
    output_dir.mkdir(parents=True, exist_ok=False)
    paths = []
    for talk in _talks(public):
        text = _source(talk) + (
            "\n## Organizer review checklist\n\n"
            "- [ ] Confirm the submitted title, presenter, and abstract with the presenter.\n"
            "- [ ] Confirm contribution format and scheduling needs.\n"
            "- [ ] Confirm public permissions for any additional material before publication.\n"
            "- [ ] Prepare discussion questions grounded in the submitted abstract.\n"
            "\n## Public learning resources\n\n"
            "These approved event resources are starting points; topic relevance and author "
            "identity have not been inferred.\n\n"
        )
        for resource in sorted(public["resources"], key=lambda r: r["id"]):
            text += f"- {_literal(resource['title'])}: {_literal(resource['url'])}\n"
        discovery = "https://openalex.org/works?search=" + quote(talk["title"], safe="")
        text += (
            "\nOpenAlex discovery-only search (not a verified identity or literature match): "
            f"{_literal(discovery)}\n"
        )
        path = output_dir / f"{talk['id']}.md"
        _write(path, text)
        paths.append(path)
    return paths


def stage_abstract_book(bundle: PublicBundle, workspace: Path) -> Path:
    """Stage a deterministic full-abstract book; refuse an existing project."""
    public = validate_bundle(bundle)
    event = public["event"]
    project = workspace / "projects" / f"symposium_{event['year']}"
    project.mkdir(parents=True, exist_ok=False)
    manuscript = project / "manuscript"
    manuscript.mkdir()
    config = {
        "paper": {
            "title": f"{_literal(event['title'])} — Book of Abstracts (Working Program)",
            "year": event["year"],
        },
        "authors": [],
        "publication": {"transmission_bookends": {"enabled": False}},
        "render": {
            "formats": {"pdf": True, "docx": True, "html": False, "slides": False, "epub": False}
        },
        "rendering": {"include_date": False},
        "metadata": {"language": "en", "geometry": "a4paper,margin=25mm"},
    }
    # JSON is a YAML subset and safely quotes user-supplied configuration strings.
    _write(manuscript / "config.yaml", json.dumps(config, ensure_ascii=False, indent=2) + "\n")
    text = (
        "# About this program {.unnumbered}\n\n"
        f"Event dates: {_literal(event['start_date'])} to {_literal(event['end_date'])}.\n\n"
        "This working program collection contains approved public abstracts and explicitly marks entries awaiting an abstract. Inclusion does not assert "
        "that a presentation has occurred or that a recording has been received.\n\n"
    )
    talks = _talks(public)
    page_break = "\n\n\\newpage\n\n"
    text += page_break + page_break.join(
        _source(talk, provenance=False).replace("## Submitted abstract", "**Submitted abstract**")
        for talk in talks
    )
    _write(manuscript / "01_abstract_book.md", text)
    manifest = {
        "schema_version": 1,
        "event_id": event["id"],
        "talk_count": len(talks),
        "talks": [{"id": talk["id"], "abstract_sha256": talk["abstract_sha256"]} for talk in talks],
    }
    _write(project / "abstract_manifest.json", json.dumps(manifest, indent=2) + "\n")
    return project


def _set_docx_page_geometry(path: Path) -> None:
    """Give the native Word artifact the same metric A4 page geometry as its PDF."""
    namespace = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
    ET.register_namespace("w", namespace)
    ET.register_namespace(
        "r", "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
    )
    with zipfile.ZipFile(path) as source:
        document = ET.fromstring(source.read("word/document.xml"))
        for section in document.iter(f"{{{namespace}}}sectPr"):
            for tag, values in (
                ("pgSz", {"w": "11906", "h": "16838"}),
                (
                    "pgMar",
                    {
                        "top": "1417",
                        "bottom": "1417",
                        "left": "1417",
                        "right": "1417",
                        "header": "708",
                        "footer": "708",
                        "gutter": "0",
                    },
                ),
            ):
                element = section.find(f"{{{namespace}}}{tag}")
                if element is None:
                    element = ET.SubElement(section, f"{{{namespace}}}{tag}")
                element.attrib = {f"{{{namespace}}}{key}": value for key, value in values.items()}
        target = path.with_suffix(".a4.docx")
        with target.open("xb") as handle, zipfile.ZipFile(handle, "w") as output:
            for member in source.infolist():
                output.writestr(
                    member,
                    ET.tostring(document, encoding="utf-8", xml_declaration=True)
                    if member.filename == "word/document.xml"
                    else source.read(member),
                )
    target.replace(path)


def render_abstract_book(
    bundle: PublicBundle,
    workspace: Path,
    template_root: Path,
    *,
    timeout: int = 600,
) -> dict[str, Path]:
    """Render a fresh project with the real template pipeline and retain run evidence."""
    public = validate_bundle(bundle)
    if timeout <= 0:
        raise ArtifactError("Render timeout must be positive")
    template_root = template_root.resolve()
    workspace = workspace.resolve()
    vault = next((p for p in Path(__file__).resolve().parents if p.is_mount()), None)
    if vault is None or vault == Path(vault.anchor):
        raise ArtifactError("Repository must be on the mounted GitVault volume")
    if not template_root.is_relative_to(vault) or not workspace.is_relative_to(vault):
        raise ArtifactError("Template and render workspace must be on the repository volume")
    if workspace.is_relative_to(template_root):
        raise ArtifactError("Render workspace must be outside the template repository")
    python = template_root / ".venv" / "bin" / "python"
    pipeline = template_root / "infrastructure" / "rendering" / "pipeline.py"
    if not python.is_file() or not pipeline.is_file():
        raise ArtifactError("Missing template interpreter or native pipeline")
    project = stage_abstract_book(public, workspace)
    launcher = project / "render_native.py"
    _write(
        launcher,
        r"""from pathlib import Path
import sys
vault = Path(sys.argv[3]).resolve()
if sys.version_info[:2] != (3, 14):
    raise RuntimeError("Template interpreter must be Python 3.14")
if not all(Path(p).resolve().is_relative_to(vault) for p in (sys.prefix, sys.base_prefix)):
    raise RuntimeError("Template interpreter prefixes must be on GitVault")
# The template's general prose remapper verbalizes a literal tilde as "about"
# and changes the middle-dot glyph. Submitted abstracts must retain their text.
# Apply this narrow process-local compatibility policy; never modify Template.
from infrastructure.rendering import _pdf_unicode_remap as remap
expected = {r"\textasciitilde{}": "about ", r"\textasciitilde": "about "}
if any(remap._LATEX_TEXT_MACRO_REPLACEMENTS.get(key) != value for key, value in expected.items()):
    raise RuntimeError("Template literal-preservation contract changed; review adapter")
remap._LATEX_TEXT_MACRO_REPLACEMENTS = {key: value for key, value in remap._LATEX_TEXT_MACRO_REPLACEMENTS.items() if key not in expected}
remap._PROSE_GLYPH_REPLACEMENTS = {key: value for key, value in remap._PROSE_GLYPH_REPLACEMENTS.items() if key != "·"}
from infrastructure.rendering.pipeline import execute_render_pipeline
raise SystemExit(execute_render_pipeline(sys.argv[1], repo_root=Path(sys.argv[2]), skip_manuscript_hydration=True))
""",
    )
    env = os.environ.copy()
    env.pop("VIRTUAL_ENV", None)
    env["PYTHONPATH"] = str(template_root)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    for key, directory in (
        ("TMPDIR", "tmp"),
        ("XDG_CACHE_HOME", "cache"),
        ("MPLCONFIGDIR", "matplotlib"),
        ("UV_CACHE_DIR", "uv-cache"),
    ):
        path = project / directory
        path.mkdir()
        env[key] = str(path)
    env["UV_LINK_MODE"] = "copy"
    command = [str(python), str(launcher), project.name, str(workspace), str(vault)]
    _write(project / "render_command.json", json.dumps(command, indent=2) + "\n")
    with (
        (project / "render.stdout.log").open("xb") as stdout,
        (project / "render.stderr.log").open("xb") as stderr,
    ):
        with subprocess.Popen(
            command,
            cwd=workspace,
            env=env,
            stdin=subprocess.DEVNULL,
            stdout=stdout,
            stderr=stderr,
            start_new_session=True,
        ) as process:
            try:
                status = process.wait(timeout=timeout)
            except subprocess.TimeoutExpired as exc:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()
                _write(
                    project / "render_status.json",
                    json.dumps({"timed_out": True, "timeout": timeout}),
                )
                raise ArtifactError(f"Native render timed out; logs: {project}") from exc
    _write(project / "render_status.json", json.dumps({"returncode": status, "timed_out": False}))
    if status:
        raise ArtifactError(f"Native render exited {status}; logs: {project}")
    outputs = {
        kind: project / "output" / kind / f"{project.name}_combined.{kind}"
        for kind in ("pdf", "docx")
    }
    for kind, path in outputs.items():
        if not path.is_file() or path.stat().st_size == 0:
            raise ArtifactError(f"Native render missing nonempty {kind}: {path}")
    native_docx_sha256 = hashlib.sha256(outputs["docx"].read_bytes()).hexdigest()
    _set_docx_page_geometry(outputs["docx"])
    manifest = json.loads((project / "abstract_manifest.json").read_text(encoding="utf-8"))
    manifest["literal_preservation"] = {"tilde": True, "middle_dot": True}
    manifest["docx_layout"] = {"paper": "A4", "margins_mm": 25, "native_sha256": native_docx_sha256}
    manifest["outputs"] = {
        kind: {"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
        for kind, path in outputs.items()
    }
    manifest["manuscript_sha256"] = hashlib.sha256(
        (project / "manuscript" / "01_abstract_book.md").read_bytes()
    ).hexdigest()
    outputs["manifest"] = project / "render_manifest.json"
    _write(outputs["manifest"], json.dumps(manifest, indent=2) + "\n")
    return outputs
