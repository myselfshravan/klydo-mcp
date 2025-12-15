# Project Overview

Klydo is a fashion app designed for India's 18-32 year-olds that uses AI to help users discover and shop fashion trends quickly. An MCP (Model Context Protocol) server will enable AI assistants like Claude to interact with Klydo's fashion catalog, recommendations, and shopping features programmatically.[2]

## Technical Stack & Setup

Since you've already initialized with `uv` and want to use FastAPI with Pydantic, you can leverage FastMCP, which seamlessly integrates with FastAPI applications. FastMCP automatically converts your FastAPI routes into MCP tools while preserving typing, schema definitions, and Pydantic validations.[3]

## Initial Project Structure

```bash
klydo-mcp-server/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI application
│   ├── models.py        # Pydantic models
│   ├── routes/
│   │   ├── products.py  # Product search/browse
│   │   ├── trends.py    # Fashion trends
│   │   └── recommendations.py
│   └── services/
│       └── klydo_api.py # Klydo API integration
├── mcp_server.py        # MCP server entry point
├── pyproject.toml
└── README.md
```

## Core MCP Tools to Implement

Your MCP server should expose these key capabilities:

- **Product Discovery**: Search fashion items by category, trend, or style
- **Trend Analysis**: Get current fashion trends for Gen Z audience
- **Personalized Recommendations**: AI-powered outfit suggestions
- **Product Details**: Retrieve detailed information about specific items
- **Availability Check**: Check product availability and pricing

## Implementation Approach

Create your FastAPI app with standard endpoints, then wrap it with FastMCP. The FastMCP framework will inspect your app and automatically convert each route into an MCP tool. Use Python type hints and docstrings extensively, as FastMCP uses them to generate tool definitions automatically.[4][3]

For running the server, you'll use the stdio transport for local development with Claude Desktop, or HTTP/SSE transport for production deployment. The server initialization follows the pattern: `mcp = FastMCP.from_fastapi(app=server)` followed by `mcp.run()`.[5][3]

[1](https://www.klydo.in)
[2](https://in.linkedin.com/company/klydo-app)
[3](https://www.speakeasy.com/mcp/framework-guides/building-fastapi-server)
[4](https://modelcontextprotocol.io/docs/develop/build-server)
[5](https://northflank.com/blog/how-to-build-and-deploy-a-model-context-protocol-mcp-server)
[6](https://find-and-update.company-information.service.gov.uk/company/09689396)
[7](https://startup-seeker.com/company/klydo~io)
[8](https://www.instagram.com/klydo.official/)
[9](https://ai.pydantic.dev/mcp/fastmcp-client/)
[10](https://www.linkedin.com/company/klydo-clock)
