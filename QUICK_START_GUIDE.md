# Quick Start Guide for Users

This guide is for **users** who want to install and use the Klydo MCP server with Claude Desktop.

## Installation (3 Easy Ways)

### Method 1: Using uvx (Easiest - Recommended)

No installation needed! Just configure Claude Desktop:

1. Open Claude Desktop configuration:
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
   - **Linux**: `~/.config/Claude/claude_desktop_config.json`

2. Add this configuration:
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

3. Restart Claude Desktop

That's it! `uvx` will automatically download and run the latest version.

### Method 2: Using pipx (Isolated Installation)

1. Install pipx if you don't have it:
   ```bash
   pip install pipx
   pipx ensurepath
   ```

2. Install Klydo MCP Server:
   ```bash
   pipx install klydo-mcp-server
   ```

3. Configure Claude Desktop:
   ```json
   {
     "mcpServers": {
       "klydo": {
         "command": "klydo"
       }
     }
   }
   ```

4. Restart Claude Desktop

### Method 3: Using pip (Global Installation)

1. Install:
   ```bash
   pip install klydo-mcp-server
   ```

2. Configure Claude Desktop (same as Method 2):
   ```json
   {
     "mcpServers": {
       "klydo": {
         "command": "klydo"
       }
     }
   }
   ```

3. Restart Claude Desktop

## Verify Installation

After restarting Claude Desktop, you should see the Klydo MCP server connected. You can verify by asking Claude:

```
"Can you search for trending tshirts for men?"
```

Claude should be able to use the Klydo tools to search for products.

## Configuration (Optional)

By default, the server uses Myntra as the data source. To change settings:

1. Create a `.env` file in your home directory or project directory
2. Add configuration:
   ```bash
   # Switch to Klydo brand scraper
   KLYDO_DEFAULT_SCRAPER=klydo

   # Adjust cache duration (in seconds)
   KLYDO_CACHE_TTL=3600

   # Adjust request timeout (in seconds)
   KLYDO_REQUEST_TIMEOUT=30
   ```

3. Restart Claude Desktop for changes to take effect

## Available Features

Once installed, Claude can help you:

1. **Search for products**
   - "Find black cotton dresses under ₹2000"
   - "Show me nike running shoes for men"

2. **Get product details**
   - "Get more details about product STL_XXXXX"
   - "Show me all images for this product"

3. **Discover trending items**
   - "What are the trending tshirts?"
   - "Show trending shoes for women"

## Updating

### If using uvx
Just restart Claude Desktop - uvx checks for updates automatically

### If using pipx
```bash
pipx upgrade klydo-mcp-server
```

### If using pip
```bash
pip install --upgrade klydo-mcp-server
```

Then restart Claude Desktop.

## Uninstalling

### If using uvx
Remove the configuration from Claude Desktop config file

### If using pipx
```bash
pipx uninstall klydo-mcp-server
```

### If using pip
```bash
pip uninstall klydo-mcp-server
```

Then remove the configuration from Claude Desktop and restart.

## Troubleshooting

### Issue: Claude can't see the Klydo tools

**Solution:**
1. Verify the MCP server configuration in `claude_desktop_config.json`
2. Check that the JSON syntax is valid (no trailing commas, proper quotes)
3. Restart Claude Desktop completely (quit and reopen)
4. Check Claude Desktop logs:
   - **macOS**: `~/Library/Logs/Claude/mcp*.log`
   - **Windows**: `%APPDATA%\Claude\logs\mcp*.log`

### Issue: Command not found when using pip/pipx

**Solution:**
1. Ensure the installation completed successfully
2. For pipx: Run `pipx ensurepath` and restart your terminal
3. For pip: Check that your Python Scripts directory is in PATH
4. Try using the full path to the command in the config

### Issue: Rate limiting or timeout errors

**Solution:**
1. Create a `.env` file and increase timeout:
   ```bash
   KLYDO_REQUEST_TIMEOUT=60
   ```
2. Add rate limiting:
   ```bash
   KLYDO_REQUESTS_PER_MINUTE=20
   ```
3. Restart Claude Desktop

### Issue: No products found

**Solution:**
1. Try different search terms (be more specific)
2. Try switching scrapers in `.env`:
   ```bash
   KLYDO_DEFAULT_SCRAPER=myntra  # or klydo
   ```
3. Check your internet connection

## Getting Help

- **GitHub Issues**: Report bugs at [github.com/yourusername/klydo-mcp-server/issues](https://github.com/yourusername/klydo-mcp-server/issues)
- **Documentation**: See [README.md](README.md) for more details
- **PyPI Page**: [pypi.org/project/klydo-mcp-server/](https://pypi.org/project/klydo-mcp-server/)

## Privacy & Data

- The Klydo MCP server does not collect or store any personal data
- It only makes requests to e-commerce websites (Myntra, Klydo) on your behalf
- All data is cached locally and temporarily
- No tracking or analytics

## License

MIT License - See [LICENSE](LICENSE) for details
