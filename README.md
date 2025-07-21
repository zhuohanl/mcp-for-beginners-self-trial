# 1. Quick guide on what's included
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


# 2. How to run
## 2.0 Environment setup
Install `uv` if you have not
See [installation methods](https://docs.astral.sh/uv/getting-started/installation/#installation-methods)

Upon `uv` installed, set up environment by:
```
uv sync
```

## 2.1 Configure `.env` variables
Create `.env` file and fill in the variables. See [.env.example](./.env.example) as an example.

In this repo we use Claude as LLM thus need to set up Anthropic API key.

If you have not got one, follow the steps:
1. Create an Anthropic Account:
If you don't have one, go to the Anthropic website and sign up for an account. 
2. Access the API Keys Section:
Log in to your [Anthropic API Keys page](https://console.anthropic.com/settings/keys). Look for the "API Keys" or similar section, usually in the left-hand menu or profile settings. 
3. Generate a New API Key:
Click the "Create Key" button. You may need to select a workspace or provide a name for the key to help identify it later. 
4. Copy and Use the API Key:
Anthropic will generate a unique API key. Copy this key immediately, then paste it in your `env` file as `ANTHROPIC_API_KEY=<your-api-key>`


## 2.2 Run inspector
```sh
mcp dev servers/server.py
```
OR
```
npx -y @modelcontextprotocol/inspector
```

## 2.3 Run server
`cd` into root of this repo.

```
uv run servers/stdio.py
```
```
uv run servers/httpstreamable.py
```

## 2.4 Run client
`cd` into root of this repo.

```
uv run clients/stdio.py
```
```
uv run clients/httpstreamable.py
```

Note: for `clients/httpstreamable.py`, make sure the server is running before you run the client.

## 2.5 Run Chatbot app
`cd` into root of this repo.

===========================
```
uv run chatbot/1-without-mcp/chatbot.py
```
Sample queries:
- **Search for 2 papers on "LLM interpretability"**

===========================

```
uv run chatbot/2-with-mcp-single-server/mcp_chatbot.py
```
Sample queries:
- **Search for 2 papers on "LLM interpretability"**

===========================
```
uv run chatbot/3-with-mcp-multi-servers/mcp_chatbot.py
```

Sample queries:
- **Fetch the content of this website: https://modelcontextprotocol.io/docs/concepts/architecture and save the content in the file "mcp_summary.md", create a visual diagram that summarizes the content of "mcp_summary.md" and save it in a text file**
- **Fetch deeplearning.ai and find an interesting term. Search for 2 papers around the term and then summarize your findings and write them to a file called results.txt**

===========================
```
uv run chatbot/4-with-mcp-add-reources-prompts/mcp_chatbot.py
```

Sample queries:
- **@folders**
- **@ai_interpretability**
- **/prompts**
- **/prompt generate_search_prompt topic=history num_papers=2**

===========================