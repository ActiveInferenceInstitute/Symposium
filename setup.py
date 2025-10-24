#!/usr/bin/env python3
"""
Symposium Setup Script

Initializes the Symposium environment, checks dependencies, and validates configuration.
"""

import os
import sys
import logging
from pathlib import Path
from typing import List, Tuple

# Setup logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('setup.log', mode='a')
    ]
)
logger = logging.getLogger(__name__)

# Add current directory to Python path
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))
    logger.info(f"Added {current_dir} to Python path")

# Ensure we're in the right directory
os.chdir(current_dir)

def run_command(command: str, description: str = "") -> bool:
    """Run a shell command and return success status."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description}")
            return True
        else:
            print(f"❌ {description} - Error: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ {description} - Exception: {e}")
        return False

def check_python_version() -> bool:
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major == 3 and version.minor >= 10:
        print(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"❌ Python version: {version.major}.{version.minor}.{version.micro} (requires 3.10+)")
        return False

def check_virtual_environment() -> bool:
    """Check if running in virtual environment."""
    in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    if in_venv:
        print("✅ Virtual environment active")
        return True
    else:
        print("⚠️  Warning: Not in virtual environment (recommended)")
        return True  # Don't fail, just warn

def check_dependencies() -> bool:
    """Check if required dependencies are installed."""
    logger.info("Checking dependencies")
    # Map of package names to their import names
    package_imports = {
        'openai': 'openai',
        'pandas': 'pandas',
        'numpy': 'numpy',
        'matplotlib': 'matplotlib',
        'seaborn': 'seaborn',
        'networkx': 'networkx',
        'scikit-learn': 'sklearn',
        'python-dotenv': 'dotenv',
        'pytest': 'pytest',
        'wordcloud': 'wordcloud',
        'adjusttext': 'adjustText',
        'backoff': 'backoff'
    }

    all_installed = True
    for package_name, import_name in package_imports.items():
        try:
            __import__(import_name)
            logger.info(f"Dependency check passed: {package_name}")
            print(f"✅ {package_name}")
        except ImportError as e:
            logger.error(f"Dependency missing: {package_name} - {e}")
            print(f"❌ {package_name} - Missing")
            all_installed = False

    return all_installed

def check_environment_file() -> bool:
    """Check and setup environment file."""
    env_file = Path('.env')
    env_example = Path('.env.example')

    if not env_example.exists():
        print("❌ .env.example not found")
        return False

    if not env_file.exists():
        print("⚠️  .env file not found - copying from .env.example")
        try:
            import shutil
            shutil.copy(env_example, env_file)
            print("✅ Created .env file from template")
            return True
        except Exception as e:
            print(f"❌ Failed to create .env file: {e}")
            return False

    print("✅ .env file exists")
    return True

def check_api_keys() -> Tuple[bool, bool]:
    """Check API key configuration."""
    from dotenv import load_dotenv
    load_dotenv()

    perplexity_key = os.getenv('PERPLEXITY_API_KEY')
    openrouter_key = os.getenv('OPENROUTER_API_KEY')

    perplexity_ok = bool(perplexity_key)
    openrouter_ok = bool(openrouter_key)

    if perplexity_ok:
        print("✅ Perplexity API key configured")
    else:
        print("❌ Perplexity API key missing (set PERPLEXITY_API_KEY)")

    if openrouter_ok:
        print("✅ OpenRouter API key configured")
    else:
        print("❌ OpenRouter API key missing (set OPENROUTER_API_KEY)")

    return perplexity_ok, openrouter_ok

def check_data_structure() -> bool:
    """Check data directory structure."""
    required_dirs = [
        'data/inputs/aif_2024',
        'data/inputs/aif_2025',
        'data/catechisms',
        'data/domains',
        'data/prompts',
        'outputs'
    ]

    all_dirs_ok = True
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print(f"✅ {dir_path}")
        else:
            print(f"⚠️  {dir_path} - Directory missing")
            all_dirs_ok = False

    return all_dirs_ok

def check_package_installation() -> bool:
    """Check if symposium package is installed."""
    try:
        import symposium
        print(f"✅ Symposium package installed (v{symposium.__version__})")
        return True
    except ImportError:
        print("❌ Symposium package not installed")
        print("   Run: uv pip install -e .")
        return False

def test_api_connectivity() -> Tuple[bool, bool]:
    """Test API connectivity."""
    logger.info("Testing API connectivity")
    perplexity_ok = False
    openrouter_ok = False

    try:
        # Import modules with error handling
        logger.info("Importing symposium modules for API testing")
        from symposium.core.config import Config
        from symposium.core.api import APIClient
        logger.info("API modules imported successfully")

        config = Config()
        logger.info("Configuration loaded")

        # Test Perplexity
        try:
            logger.info("Testing Perplexity API")
            client = APIClient.create('perplexity')
            response = client.get_response(
                "Respond with 'API test successful' if you receive this message.",
                "You are a helpful assistant."
            )
            if 'API test successful' in response:
                perplexity_ok = True
                logger.info("Perplexity API test successful")
                print("✅ Perplexity API connectivity verified")
            else:
                logger.warning("Perplexity API response unexpected")
                print("❌ Perplexity API response unexpected")
        except ImportError as e:
            logger.error(f"Perplexity API import failed: {e}")
            print(f"❌ Perplexity API test failed: Module import error")
        except Exception as e:
            logger.error(f"Perplexity API test failed: {e}")
            print(f"❌ Perplexity API test failed: {e}")

        # Test OpenRouter
        try:
            logger.info("Testing OpenRouter API")
            client = APIClient.create('openrouter')
            response = client.get_response(
                "Respond with 'API test successful' if you receive this message.",
                "You are a helpful assistant."
            )
            if 'API test successful' in response:
                openrouter_ok = True
                logger.info("OpenRouter API test successful")
                print("✅ OpenRouter API connectivity verified")
            else:
                logger.warning("OpenRouter API response unexpected")
                print("❌ OpenRouter API response unexpected")
        except ImportError as e:
            logger.error(f"OpenRouter API import failed: {e}")
            print(f"❌ OpenRouter API test failed: Module import error")
        except Exception as e:
            logger.error(f"OpenRouter API test failed: {e}")
            print(f"❌ OpenRouter API test failed: {e}")

    except ImportError as e:
        logger.error(f"Symposium modules not available: {e}")
        print(f"❌ API connectivity test failed: Symposium package not installed")
        print("   Run: uv pip install -e \".[dev]\"")

    return perplexity_ok, openrouter_ok

def main():
    """Run complete setup validation."""
    logger.info("Starting Symposium setup validation")
    print("🚀 SYMPOSIUM SETUP VALIDATION")
    print("=" * 50)

    # Check if running as script or module
    if __name__ != "__main__":
        logger.info("Running as module")
        print("Running as module...")
        # Adjust paths if needed
        if not Path('pyproject.toml').exists():
            # Try to find project root
            for parent in Path(__file__).parents:
                if (parent / 'pyproject.toml').exists():
                    os.chdir(parent)
                    logger.info(f"Changed to project root: {parent}")
                    break

    # Basic checks
    checks = [
        ("Python Version", check_python_version),
        ("Virtual Environment", check_virtual_environment),
        ("Package Installation", check_package_installation),
        ("Environment File", check_environment_file),
        ("Data Structure", check_data_structure),
        ("Dependencies", check_dependencies),
    ]

    all_passed = True
    for check_name, check_func in checks:
        print(f"\n📋 {check_name}:")
        result = check_func()
        if not result:
            all_passed = False

    # API configuration
    print("\n🔑 API Configuration:")
    perplexity_ok, openrouter_ok = check_api_keys()
    if not (perplexity_ok or openrouter_ok):
        all_passed = False

    # API connectivity (optional)
    print("\n🌐 API Connectivity Test:")
    api_perplexity_ok, api_openrouter_ok = test_api_connectivity()

    print("\n📊 SETUP SUMMARY:")
    print("-" * 30)

    if all_passed:
        print("🎉 Setup complete! Ready to run Symposium.")
        print()
        print("Next steps:")
        print("1. Run: python run.py")
        print("2. Choose from the interactive menu options")
        print("3. Start analyzing research data and generating content")

        # Show available data
        data_dir = Path('data/inputs/aif_2024')
        if data_dir.exists():
            researchers = [d.name for d in data_dir.iterdir() if d.is_dir()]
            if researchers:
                print(f"\n📁 Available researcher data: {len(researchers)} profiles")
                print(f"   Sample: {', '.join(researchers[:3])}")

        return True
    else:
        print("❌ Setup incomplete. Please resolve the issues above.")
        print("\nTroubleshooting:")
        print("1. Install dependencies: uv pip install -e \".[dev]\"")
        print("2. Set API keys in .env file")
        print("3. Create required directories")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
