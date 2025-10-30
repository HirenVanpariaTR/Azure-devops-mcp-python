# Azure DevOps MCP Server - Python Conversion

This document describes the conversion of the Azure DevOps MCP server from TypeScript to Python.

## Project Structure

The Python version maintains a similar structure to the TypeScript original:

```
azure_devops_mcp/
├── __init__.py              # Package initialization
├── main.py                  # Main entry point (converted from src/index.ts)
├── auth.py                  # Authentication (converted from src/auth.ts)  
├── useragent.py            # User agent composition (converted from src/useragent.ts)
├── org_tenants.py          # Organization tenant management (converted from src/org-tenants.ts)
├── shared/
│   ├── __init__.py
│   └── domains.py          # Domain management (converted from src/shared/domains.ts)
└── tools/
    ├── __init__.py         # Tools configuration (converted from src/tools.ts)
    ├── core.py            # Core tools (converted from src/tools/core.ts)
    ├── work.py            # Work tools (placeholder)
    ├── pipelines.py       # Pipeline tools (placeholder)
    ├── repositories.py    # Repository tools (placeholder)
    ├── work_items.py      # Work item tools (placeholder)
    ├── wiki.py           # Wiki tools (placeholder)
    ├── test_plans.py     # Test plan tools (placeholder)
    ├── search.py         # Search tools (placeholder)
    └── advanced_security.py # Advanced security tools (placeholder)
```

## Key Changes

### 1. Dependencies

**TypeScript dependencies → Python equivalents:**
- `@modelcontextprotocol/sdk` → `mcp`
- `azure-devops-node-api` → `azure-devops`
- `@azure/identity` → `azure-identity`
- `yargs` → `click`
- `zod` → `pydantic`

### 2. Authentication

The authentication module converts:
- MSAL Node (`@azure/msal-node`) → Azure Identity (`azure-identity`)
- Interactive browser authentication using `InteractiveBrowserCredential`
- Azure CLI authentication using `AzureCliCredential`
- Default credential chain using `DefaultAzureCredential`

### 3. Main Entry Point

**TypeScript → Python changes:**
- `yargs` argument parsing → `click` command-line interface
- `McpServer` → `mcp.server.Server`
- `StdioServerTransport` → `mcp.server.stdio.stdio_server`

### 4. Tools Implementation

The core tools module demonstrates the conversion pattern:
- TypeScript `server.tool()` → Python `@server.call_tool()` decorator
- `zod` schema validation → Type hints and manual validation
- Azure DevOps Node API → Python Azure DevOps SDK

## Implementation Status

### ✅ Completed
- [x] Project structure and packaging (`pyproject.toml`, `requirements.txt`)
- [x] Main entry point with CLI interface
- [x] Authentication module with all three auth types
- [x] Domain management system
- [x] Tools configuration framework
- [x] Core tools (basic implementation)
- [x] User agent composition
- [x] Organization tenant caching
- [x] Basic test setup

### 🚧 Partially Implemented
- [ ] Core tools (missing identity search functionality)

### ❌ Todo
- [ ] Work tools (`src/tools/work.ts`)
- [ ] Pipeline tools (`src/tools/pipelines.ts`)
- [ ] Repository tools (`src/tools/repositories.ts`)  
- [ ] Work item tools (`src/tools/work-items.ts`)
- [ ] Wiki tools (`src/tools/wiki.ts`)
- [ ] Test plan tools (`src/tools/test-plans.ts`)
- [ ] Search tools (`src/tools/search.ts`)
- [ ] Advanced security tools (`src/tools/advanced-security.ts`)
- [ ] Complete test coverage (convert from Jest to pytest)
- [ ] Error handling and logging improvements
- [ ] Type hints completion
- [ ] Documentation updates

## Usage

### Installation

```bash
cd python-version
pip install -e ".[dev]"
```

### Running the Server

```bash
# Basic usage
mcp-server-azuredevops myorg

# Specific domains
mcp-server-azuredevops myorg --domains core repositories

# Azure CLI authentication
mcp-server-azuredevops myorg --authentication azcli

# Environment variable authentication
mcp-server-azuredevops myorg --authentication env
```

### Testing

```bash
pytest
```

## Next Steps

1. **Complete Tool Implementation**: Implement the remaining tool modules by converting each TypeScript tool file to Python equivalent

2. **Improve Error Handling**: Add comprehensive error handling and logging using Python's `logging` module

3. **Type Safety**: Add complete type hints throughout the codebase using `typing` module

4. **Testing**: Convert all Jest tests to pytest and ensure good test coverage

5. **Performance**: Optimize for Python-specific patterns and async operations

6. **Documentation**: Update all documentation to reflect Python usage patterns

## Development Notes

- The Python version uses `async/await` extensively to match the TypeScript async patterns
- All Azure DevOps API calls are wrapped in try/catch for error handling
- The MCP server integration follows the Python MCP SDK patterns
- Authentication tokens are properly managed using Azure Identity library
- Domain-based tool configuration maintains the same flexibility as the TypeScript version