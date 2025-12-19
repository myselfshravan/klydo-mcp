# Publishing Guide: Klydo MCP Server to PyPI

This comprehensive guide covers how to publish the Klydo MCP server to PyPI so users can install it globally without cloning the repository.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [One-Time Setup](#one-time-setup)
3. [Pre-Publishing Checklist](#pre-publishing-checklist)
4. [Publishing to PyPI](#publishing-to-pypi)
5. [Post-Publishing](#post-publishing)
6. [User Installation](#user-installation)
7. [Versioning Strategy](#versioning-strategy)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before publishing, ensure you have:

- **Python 3.11+** installed
- **uv** package manager installed (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- **PyPI account** - Create one at [https://pypi.org/account/register/](https://pypi.org/account/register/)
- **TestPyPI account** (optional but recommended) - [https://test.pypi.org/account/register/](https://test.pypi.org/account/register/)
- **PyPI API token** - Generate at [https://pypi.org/manage/account/token/](https://pypi.org/manage/account/token/)

---

## One-Time Setup

### 1. Create PyPI API Token

1. Go to [https://pypi.org/manage/account/token/](https://pypi.org/manage/account/token/)
2. Click "Add API token"
3. Give it a name like "klydo-mcp-server"
4. Scope: Choose "Entire account" for first-time, or specific project after first upload
5. Click "Add token"
6. **IMPORTANT**: Copy the token immediately (it starts with `pypi-`)
7. Store it securely (you won't see it again)

### 2. Configure PyPI Credentials

**Option A: Using environment variables (Recommended)**

Add to your `~/.zshrc` or `~/.bashrc`:

```bash
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-YOUR_API_TOKEN_HERE
```

Then reload: `source ~/.zshrc`

**Option B: Using .pypirc file**

Create `~/.pypirc`:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-YOUR_API_TOKEN_HERE

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-YOUR_TESTPYPI_TOKEN_HERE
```

Set proper permissions:
```bash
chmod 600 ~/.pypirc
```

### 3. Install Build Tools

```bash
# Install build and publishing tools
uv pip install --system build twine
```

---

## Pre-Publishing Checklist

Before each release, verify:

### 1. Update Version Number

Edit `pyproject.toml`:

```toml
[project]
name = "klydo-mcp-server"
version = "0.1.1"  # ← Update this
```

Follow [Semantic Versioning](https://semver.org/):
- **0.1.0 → 0.1.1**: Bug fixes (PATCH)
- **0.1.0 → 0.2.0**: New features, backward compatible (MINOR)
- **0.1.0 → 1.0.0**: Breaking changes (MAJOR)

### 2. Update GitHub URLs

In `pyproject.toml`, replace `yourusername` with your actual GitHub username:

```toml
[project.urls]
Homepage = "https://github.com/YOUR_USERNAME/klydo-mcp-server"
Repository = "https://github.com/YOUR_USERNAME/klydo-mcp-server"
Issues = "https://github.com/YOUR_USERNAME/klydo-mcp-server/issues"
```

### 3. Update README.md

Ensure README.md has:
- Clear installation instructions
- Usage examples
- Configuration guide
- Up-to-date feature list

### 4. Test Locally

```bash
# Run tests
uv run pytest

# Test the CLI command
uv run klydo

# Test installation from local build
uv pip install .
```

### 5. Clean Previous Builds

```bash
# Remove old build artifacts
rm -rf dist/ build/ *.egg-info
```

---

## Publishing to PyPI

### Step 1: Build the Distribution

```bash
# Navigate to project root
cd /path/to/klydo-mcp-server

# Build the package
python -m build
```

This creates:
- `dist/klydo_mcp_server-0.1.0-py3-none-any.whl` (wheel)
- `dist/klydo-mcp-server-0.1.0.tar.gz` (source distribution)

### Step 2: Test Upload to TestPyPI (Optional but Recommended)

```bash
# Upload to TestPyPI first
twine upload --repository testpypi dist/*

# Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ \
    --extra-index-url https://pypi.org/simple \
    klydo-mcp-server
```

The `--extra-index-url` ensures dependencies come from the real PyPI.

### Step 3: Upload to Production PyPI

```bash
# Upload to production PyPI
twine upload dist/*
```

You'll see output like:
```
Uploading distributions to https://upload.pypi.org/legacy/
Uploading klydo_mcp_server-0.1.0-py3-none-any.whl
100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 50.0/50.0 kB • 00:01
Uploading klydo-mcp-server-0.1.0.tar.gz
100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 35.0/35.0 kB • 00:01

View at:
https://pypi.org/project/klydo-mcp-server/0.1.0/
```

### Step 4: Verify on PyPI

1. Visit [https://pypi.org/project/klydo-mcp-server/](https://pypi.org/project/klydo-mcp-server/)
2. Check that:
   - Version number is correct
   - README renders properly
   - All links work
   - Metadata is accurate

---

## Post-Publishing

### 1. Create Git Tag

```bash
# Tag the release
git tag -a v0.1.0 -m "Release version 0.1.0"

# Push tag to GitHub
git push origin v0.1.0
```

### 2. Create GitHub Release

1. Go to your GitHub repository
2. Click "Releases" → "Create a new release"
3. Select the tag you just created (`v0.1.0`)
4. Title: `v0.1.0 - Initial Public Release`
5. Description: Add release notes (features, bug fixes, breaking changes)
6. Attach the built distribution files from `dist/`
7. Click "Publish release"

### 3. Test Installation

```bash
# Test installation from PyPI
pip install klydo-mcp-server

# Verify it works
klydo --version  # Should show version
```

### 4. Update Documentation

Update README.md and any other docs to reference the PyPI installation method as the primary installation approach.

---

## User Installation

Once published to PyPI, users can install in three ways:

### Method 1: Using pip (Global Install)

```bash
pip install klydo-mcp-server
```

**Claude Desktop Configuration:**

```json
{
  "mcpServers": {
    "klydo": {
      "command": "klydo"
    }
  }
}
```

### Method 2: Using pipx (Isolated Install - Recommended)

```bash
# Install pipx if not already installed
pip install pipx
pipx ensurepath

# Install klydo-mcp-server in isolated environment
pipx install klydo-mcp-server
```

**Claude Desktop Configuration:**

```json
{
  "mcpServers": {
    "klydo": {
      "command": "klydo"
    }
  }
}
```

### Method 3: Using uvx (Modern Approach)

```bash
# No installation needed - uvx runs it on-demand
uvx klydo-mcp-server
```

**Claude Desktop Configuration:**

```json
{
  "mcpServers": {
    "klydo": {
      "command": "uvx",
      "args": ["klydo-mcp-server"]
    }
  }
}
```

---

## Versioning Strategy

Follow [Semantic Versioning](https://semver.org/) (MAJOR.MINOR.PATCH):

| Change Type | Version Update | Example |
|-------------|----------------|---------|
| Bug fixes, minor tweaks | Patch | 0.1.0 → 0.1.1 |
| New features (backward compatible) | Minor | 0.1.0 → 0.2.0 |
| Breaking changes | Major | 0.9.0 → 1.0.0 |

### Version Lifecycle

- **0.x.x**: Pre-1.0, API may change
- **1.0.0**: First stable release with API stability guarantee
- **1.x.x**: Backward compatible features and fixes
- **2.0.0**: Breaking changes to API

---

## Troubleshooting

### Error: "File already exists"

**Problem**: Trying to upload a version that already exists on PyPI.

**Solution**:
1. Increment version in `pyproject.toml`
2. Rebuild: `python -m build`
3. Upload again: `twine upload dist/*`

Note: You cannot replace or delete versions on PyPI once uploaded.

### Error: "Invalid or non-existent authentication"

**Problem**: PyPI credentials not configured correctly.

**Solution**:
1. Verify token starts with `pypi-`
2. Check `~/.pypirc` or environment variables
3. Regenerate token if needed
4. Ensure username is `__token__` (not your PyPI username)

### Error: "HTTPError: 403 Forbidden"

**Problem**: Token doesn't have permission for this project.

**Solution**:
1. For first upload, use "Entire account" scope token
2. After first upload, create project-specific token
3. Update credentials with new token

### README not rendering properly on PyPI

**Problem**: PyPI uses strict CommonMark, not all GitHub Markdown features.

**Solution**:
1. Test locally: `python -m readme_renderer README.md`
2. Install: `pip install readme-renderer`
3. Avoid: HTML, GitHub-specific extensions
4. Use: Standard Markdown syntax

### Package not found after upload

**Problem**: PyPI CDN caching delay.

**Solution**:
- Wait 1-2 minutes for CDN propagation
- Refresh the PyPI page
- Try installation again

### Import errors after installation

**Problem**: Package structure mismatch.

**Solution**:
1. Check `pyproject.toml` → `[tool.hatch.build.targets.wheel]` → `packages = ["src/klydo"]`
2. Verify directory structure: `src/klydo/__init__.py` exists
3. Rebuild and test locally first

---

## Complete Publishing Workflow

Here's the complete checklist for each release:

```bash
# 1. Update version in pyproject.toml
# 2. Update CHANGELOG if you have one
# 3. Commit changes
git add .
git commit -m "Bump version to 0.1.1"

# 4. Clean old builds
rm -rf dist/ build/ *.egg-info

# 5. Run tests
uv run pytest

# 6. Build package
python -m build

# 7. Test with TestPyPI (optional)
twine upload --repository testpypi dist/*

# 8. Upload to PyPI
twine upload dist/*

# 9. Create git tag
git tag -a v0.1.1 -m "Release version 0.1.1"
git push origin main
git push origin v0.1.1

# 10. Create GitHub release (via web interface)

# 11. Test installation
pip install --upgrade klydo-mcp-server
```

---

## Automated Publishing with GitHub Actions

For future automation, create `.github/workflows/publish.yml`:

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install build twine

      - name: Build package
        run: python -m build

      - name: Publish to PyPI
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
        run: twine upload dist/*
```

Store your PyPI token in GitHub repository secrets as `PYPI_API_TOKEN`.

---

## Additional Resources

- **PyPI Help**: [https://pypi.org/help/](https://pypi.org/help/)
- **Python Packaging Guide**: [https://packaging.python.org/](https://packaging.python.org/)
- **Twine Documentation**: [https://twine.readthedocs.io/](https://twine.readthedocs.io/)
- **Semantic Versioning**: [https://semver.org/](https://semver.org/)
- **MCP Documentation**: [https://modelcontextprotocol.io/](https://modelcontextprotocol.io/)

---

## Support

If you encounter issues:

1. Check the [Troubleshooting](#troubleshooting) section
2. Review PyPI's [publishing guide](https://packaging.python.org/tutorials/packaging-projects/)
3. Open an issue on GitHub
4. Contact PyPI support for account-specific issues
