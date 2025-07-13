# Environment setup
```
uv sync
```

# Run inspector
```sh
mcp dev servers/server.py
```
OR
```
npx -y @modelcontextprotocol/inspector
```

# Run server
If the python file has a main class with mcp.run():
```
uv run python servers/server.py
```

If the python file does not have a main class with mcp.run():
```
uv run mcp run servers/server.py
```