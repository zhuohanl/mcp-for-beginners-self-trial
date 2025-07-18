# Quick guide on what's included
## Concepts
- [stdio.py](concepts/stdio.py): an example implementation of STDIO with a loop of user input and LLM output
- [jsonrpc.py](concepts/jsonrpc.py): an example implementation of JSON-RPC 2.0 using HTTP

## MCP Servers
- [stdio](servers/stdio.py): an example implementation of MCP server using STDIO transport
- [httpstreamable](servers/httpstreamable.py): an example implementation of MCP server using HTTP Streamable transport

## MCP Clients
- [stdio](clients/stdio.py): an example implementation of MCP client using STDIO transport. Included wrappers of read and write streams to log the payloads before passing along.
- [httpstreamable](clients/httpstreamable.py): an example implementation of MCP client using HTTP Streamable transport. Included wrappers of read and write streams to log the payloads before passing along.

## Example Chatbot Application
- [chatbot](chatbot/without-mcp/chatbot.py): an example chatbot application using function calling rather than MCP
- [mcp_chatbot](chatbot/with-mcp/mcp_chatbot.py): an example chatbot application using MCP

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
`cd` into root of this repo.

If the python file has a main class with mcp.run():
```
uv run servers/stdio.py
```

If the python file does not have a main class with mcp.run():
```
uv run mcp run servers/stdio.py
```

# Run client
`cd` into root of this repo.

```
uv run clients/stdio.py
```
```
uv run clients/httpstreamable.py
```

# Run Chatbot app
`cd` into root of this repo.

```
uv run chatbot/without-mcp/chatbot.py
```

```
uv run chatbot/with-mcp/mcp_chatbot.py
```