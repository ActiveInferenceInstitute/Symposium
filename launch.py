#!/usr/bin/env python3
"""
Symposium Launcher

Quick launcher for the Symposium interactive interface.
"""

import logging
import os
import sys
from pathlib import Path

# Setup logging first
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


def activate_virtual_environment():
    """Activate the virtual environment if not already active."""
    logger.info("Checking virtual environment")
    venv_path = Path(".venv")
    if venv_path.exists() and not (
        hasattr(sys, "real_prefix")
        or (hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix)
    ):
        venv_python = venv_path / "bin" / "python"
        if venv_python.exists():
            logger.info(f"Activating virtual environment: {venv_python}")
            # Re-execute with virtual environment
            os.execv(str(venv_python), [str(venv_python)] + sys.argv)
        else:
            logger.error("Virtual environment found but no Python executable")
            print("⚠️  Virtual environment found but no Python executable")
    elif not venv_path.exists():
        logger.error("No virtual environment found")
        print("❌ No virtual environment found.")
        print('   Run: uv venv && uv pip install -e ".[dev]"')
        sys.exit(1)


def main():
    """Launch the Symposium interactive interface."""
    logger.info("Starting Symposium launcher")
    print("🚀 Launching Symposium Interactive Interface...")
    print()

    # Check if we're in the right directory
    if not Path("pyproject.toml").exists():
        logger.error("Not in Symposium project directory")
        print("❌ Not in Symposium project directory.")
        print("   Please run from the symposium project root.")
        sys.exit(1)

    # Activate virtual environment if needed
    activate_virtual_environment()

    # Validate the installed package in-process. The legacy `setup.py` runner is
    # deprecated (install/validation is driven by uv + pyproject.toml), so do not
    # shell out to it.
    logger.info("Running setup validation")
    print("🔧 Running setup validation...")
    try:
        import symposium  # noqa: F401

        logger.info("Setup validation passed")
        print("✅ Setup validation passed")
    except ImportError as e:
        logger.warning(f"Setup validation could not import the package: {e}")
        print(
            '⚠️  symposium package not importable — run `uv pip install -e ".[dev]"` first. Continuing...'
        )

    print()
    print("🎯 Starting Symposium Interactive Interface...")
    print("   Choose from numbered options to:")
    print("   • Explore available research data")
    print("   • Research individuals using Perplexity AI")
    print("   • Process participants using OpenRouter")
    print("   • Generate research profiles and proposals")
    print("   • Create network visualizations")
    print("   • Manage configuration and settings")
    print()

    # Launch the interactive interface
    try:
        logger.info("Importing and starting interactive interface")
        import run

        run.main()
    except KeyboardInterrupt:
        logger.info("User interrupted launcher")
        print("\n\n👋 Thank you for using Symposium!")
    except ImportError as e:
        logger.error(f"Import error: {e}")
        print(f"\n❌ Import error: {e}")
        print("   Make sure the symposium package is installed.")
        print('   Run: uv pip install -e ".[dev]"')
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error launching interface: {e}")
        print(f"\n❌ Error launching interface: {e}")
        print("   Try running: python run.py")
        sys.exit(1)


if __name__ == "__main__":
    main()
