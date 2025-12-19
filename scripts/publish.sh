#!/bin/bash
# Helper script for publishing to PyPI
# Usage: ./scripts/publish.sh [test|prod]

set -e  # Exit on error

MODE="${1:-test}"  # Default to test mode

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Klydo MCP Server - Publishing Helper${NC}"
echo "========================================"
echo ""

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo -e "${RED}Error: pyproject.toml not found. Please run from project root.${NC}"
    exit 1
fi

# Extract version from pyproject.toml
VERSION=$(grep '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/')
echo -e "Current version: ${GREEN}${VERSION}${NC}"
echo ""

# Ask for confirmation
echo -e "${YELLOW}This will publish version ${VERSION} to ${MODE} PyPI.${NC}"
read -p "Continue? (y/N) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 1
fi

# Step 1: Clean old builds
echo -e "${GREEN}Step 1: Cleaning old builds...${NC}"
rm -rf dist/ build/ *.egg-info
echo "✓ Cleaned"
echo ""

# Step 2: Run tests
echo -e "${GREEN}Step 2: Running tests...${NC}"
if command -v uv &> /dev/null; then
    uv run pytest || {
        echo -e "${RED}Tests failed. Aborting publish.${NC}"
        exit 1
    }
else
    echo -e "${YELLOW}Warning: uv not found. Skipping tests.${NC}"
fi
echo "✓ Tests passed"
echo ""

# Step 3: Build package
echo -e "${GREEN}Step 3: Building package...${NC}"
python -m build
echo "✓ Built successfully"
echo ""

# Step 4: Check package
echo -e "${GREEN}Step 4: Checking package...${NC}"
twine check dist/*
echo "✓ Package checks passed"
echo ""

# Step 5: Upload
if [ "$MODE" = "prod" ]; then
    echo -e "${GREEN}Step 5: Uploading to PyPI (PRODUCTION)...${NC}"
    echo -e "${RED}WARNING: This will publish to production PyPI!${NC}"
    read -p "Are you absolutely sure? (y/N) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Cancelled."
        exit 1
    fi
    twine upload dist/*
    echo ""
    echo -e "${GREEN}✓ Published to PyPI!${NC}"
    echo -e "View at: https://pypi.org/project/klydo-mcp-server/${VERSION}/"
else
    echo -e "${GREEN}Step 5: Uploading to TestPyPI...${NC}"
    twine upload --repository testpypi dist/*
    echo ""
    echo -e "${GREEN}✓ Published to TestPyPI!${NC}"
    echo -e "View at: https://test.pypi.org/project/klydo-mcp-server/${VERSION}/"
    echo ""
    echo -e "${YELLOW}To test installation:${NC}"
    echo "pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple klydo-mcp-server"
fi

echo ""
echo -e "${GREEN}Publishing complete!${NC}"
echo ""

# Suggest next steps
if [ "$MODE" = "test" ]; then
    echo -e "${YELLOW}Next steps:${NC}"
    echo "1. Test the TestPyPI installation"
    echo "2. If everything works, run: ./scripts/publish.sh prod"
    echo "3. Create a git tag: git tag -a v${VERSION} -m 'Release ${VERSION}'"
    echo "4. Push tag: git push origin v${VERSION}"
    echo "5. Create GitHub release"
else
    echo -e "${YELLOW}Next steps:${NC}"
    echo "1. Create git tag: git tag -a v${VERSION} -m 'Release ${VERSION}'"
    echo "2. Push tag: git push origin v${VERSION}"
    echo "3. Create GitHub release at https://github.com/yourusername/klydo-mcp-server/releases/new"
    echo "4. Update version in pyproject.toml for next release"
fi
