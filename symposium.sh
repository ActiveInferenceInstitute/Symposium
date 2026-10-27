#!/usr/bin/env bash
#
# Symposium Runner - UV-based execution
#
# This script ensures the symposium package runs in a uv-managed virtual environment
# with all dependencies properly installed.
#

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║         🎯 SYMPOSIUM      - ACTIVE INFERENCE 🎯                ║${NC}"
echo -e "${BLUE}║             UV-Managed Environment Setup                       ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo -e "${RED}❌ uv is not installed${NC}"
    echo ""
    echo "Install uv with:"
    echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo ""
    echo "Or visit: https://github.com/astral-sh/uv"
    exit 1
fi

echo -e "${GREEN}✅ uv is installed: $(uv --version)${NC}"

# Bind uv to this project's environment, including when launched by another uv app.
export UV_PROJECT_ENVIRONMENT="$SCRIPT_DIR/.venv"
unset VIRTUAL_ENV

echo -e "${YELLOW}📦 Installing locked dependencies...${NC}"
uv sync --locked

# Check for .env file
if [ ! -f ".env" ]; then
    echo ""
    echo -e "${YELLOW}⚠️  No .env file found${NC}"
    if [ -f ".env.example" ]; then
        echo "   Create one from .env.example:"
        echo "   cp .env.example .env"
    fi
    echo ""
    echo "   Required API keys:"
    echo "   - PERPLEXITY_API_KEY (for background research)"
    echo "   - OPENROUTER_API_KEY (for curricula generation)"
    echo ""
fi

# Run the application
echo ""
echo -e "${BLUE}🚀 Starting Symposium...${NC}"
echo ""

# Use uv to run Python with the virtual environment
uv run --locked python run.py "$@"



