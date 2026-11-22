"""Discovery regressions using real public rendering and synthetic hostile inputs."""

import json
import re
import xml.etree.ElementTree as ET

import pytest

from symposium.organizing.discovery import canonical_base
from symposium.organizing.site import build_site
from tests.test_organizing_site import Tags
from tests.test_organizing_site import bundle as public_bundle


@pytest.fixture
def bundle():
    return public_bundle.__wrapped__()


@pytest.mark.parametrize(
    "url",
    [
        "http://example.org/Symposium/",
        "https://user:secret@example.org/",
        "https://example.org/a/../b/",
        "https://example.org/%2e%2e/",
        "https://example.org/%252e%252e/",
        "https://example.org/a\\b/",
        "https://example.org/?token=x",
        "https://example.org/#part",
        "https://example.org/index.html",
        "https://example.org:bad/",
        "https://example.org/\n",
        "https://example.org/%00/",
        "//example.org/",
        "https:///missing",
        "https://example.org//path/",
    ],
)
def test_invalid_site_url_rejected_before_output(bundle, tmp_path, url):
    output = tmp_path / "site"
    with pytest.raises(ValueError):
        build_site(bundle, output, site_url=url)
    assert not output.exists()


def test_project_prefix_and_real_html_sitemap(bundle, tmp_path):
    base = "https://example.org/nested/Symposium/"
    index = build_site(bundle, tmp_path / "site", site_url=base.rstrip("/"))
    assert canonical_base(base.rstrip("/")) == base
    for page in ("index.html", "methods.html"):
        tags = Tags((index.parent / page).read_text()).tags
        assert any(
            a.get("rel") == "canonical"
            and a.get("href") == (base if page == "index.html" else base + page)
            for _, a in tags
        )
        assert not any(a.get("href", "").startswith("/") for _, a in tags)
        assert any(
            a.get("property") == "og:url"
            and a.get("content") == (base if page == "index.html" else base + page)
            for _, a in tags
        )
    sitemap = ET.parse(index.parent / "sitemap.xml")
    assert [n.text for n in sitemap.findall(".//{*}loc")] == [
        base,
        base + "methods.html",
    ]
    assert sitemap.findall(".//{*}lastmod") == []


def test_event_jsonld_safe_and_truthful(bundle, tmp_path):
    attack = '</script><script>alert("injected")</script>'
    bundle["event"]["title"] = attack
    index = build_site(bundle, tmp_path / "site")
    source = index.read_text()
    tags = Tags(source).tags
    assert len([t for t, _ in tags if t == "script"]) == 2
    data = json.loads(
        re.search(r'<script type="application/ld\+json">(.*?)</script>', source, re.S)[1]
    )
    assert data == {
        "@context": "https://schema.org",
        "@type": "Event",
        "name": attack,
        "url": "https://activeinferenceinstitute.github.io/Symposium/",
        "startDate": bundle["event"]["start_date"],
        "endDate": bundle["event"]["end_date"],
    }
    assert attack not in source


def test_discovery_excludes_participant_profiles_and_has_no_person_schema(bundle, tmp_path):
    bundle["participants"][0]["learning_needs"] = "PRIVATE-SEO-SENTINEL"
    index = build_site(bundle, tmp_path / "site")
    search = json.loads((index.parent / "search-index.json").read_text())
    assert {e["kind"] for e in search["entries"]} == {
        "methods",
        "workflow",
        "repository",
        "presentation",
    }
    for name in ("search-index.json", "ecosystem.json", "methods.html", "llms.txt"):
        text = (index.parent / name).read_text()
        assert "PRIVATE-SEO-SENTINEL" not in text
        assert "Synthetic Learner" not in text
        assert '"@type": "Person"' not in text
    assert "PRIVATE-SEO-SENTINEL" in index.read_text()
    assert json.loads((index.parent / "program.json").read_text()) == bundle
    assert not (index.parent / "proceedings.json").exists()


def test_methods_navigation_and_sources_work_without_javascript(bundle, tmp_path):
    index = build_site(bundle, tmp_path / "site")
    methods = (index.parent / "methods.html").read_text()
    tags = Tags(methods).tags
    ids = {a["id"] for _, a in tags if "id" in a}
    catalog = json.loads((index.parent / "ecosystem.json").read_text())
    assert [a["src"] for t, a in tags if t == "script" and a.get("src")] == ["static/site.js"]
    assert not any("hidden" in a for _, a in tags if "data-record" in a)
    for _, attrs in tags:
        target = attrs.get("href", "")
        if target.startswith("#"):
            assert target[1:] in ids
        elif target and not target.startswith("https://"):
            assert (index.parent / target.split("#")[0]).is_file()
    for workflow in catalog["workflows"]:
        assert "workflow-" + workflow["id"] in ids
    for repository in catalog["repositories"]:
        assert "repository-" + repository["id"] in ids
        assert repository["evidence_url"] in methods
    assert 'href="methods.html"' in index.read_text()
    data = json.loads(
        re.search(r'<script type="application/ld\+json">(.*?)</script>', methods, re.S)[1]
    )
    assert data["@type"] == "CollectionPage"


def test_final_2026_proceedings_are_discoverable_without_changing_program(bundle, tmp_path):
    published = bundle["event"]
    published.update(id="symposium-2026", start_date="2026-11-12", end_date="2026-11-13")
    index = build_site(bundle, tmp_path / "site")
    root = index.parent
    source = index.read_text()
    methods = (root / "methods.html").read_text()
    book = json.loads((root / "proceedings.json").read_text())
    assert book["doi"] == "10.5281/zenodo.24409077"
    assert book["concept_doi"] == "10.5281/zenodo.23986504"
    assert book["published_on"] == "2026-11-21"
    links = {attrs.get("href") for _, attrs in Tags(source).tags}
    assert {
        "#working-book",
        "https://doi.org/" + book["doi"],
        "https://doi.org/" + book["concept_doi"],
        book["pdf_url"],
        book["docx_url"],
        book["release_url"],
        "proceedings.json",
    } <= links
    assert published["participant_registration_url"] not in links
    assert published["presenter_registration_url"] not in links
    assert 'href="index.html#working-book"' in methods
    assert "https://doi.org/" + book["doi"] in (root / "llms.txt").read_text()
    entries = json.loads((root / "search-index.json").read_text())["entries"]
    assert [e["url"] for e in entries if e["kind"] == "publication"] == ["index.html#working-book"]
    event_metadata = json.loads(
        re.search(r'<script type="application/ld\+json">(.*?)</script>', source, re.S)[1]
    )
    assert event_metadata["subjectOf"]["identifier"] == book["doi"]
    assert event_metadata["subjectOf"]["@type"] == "Book"
    assert json.loads((root / "program.json").read_text()) == bundle


def test_sitemap_escapes_canonical_path(bundle, tmp_path):
    base = "https://example.org/a&b/"
    index = build_site(bundle, tmp_path / "site", site_url=base)
    assert ET.parse(index.parent / "sitemap.xml").find(".//{*}loc").text == base
