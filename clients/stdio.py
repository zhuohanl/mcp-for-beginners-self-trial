from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client

import asyncio
import json
from dataclasses import asdict

# Create server parameters for stdio connection
server_params = StdioServerParameters(
    command="python",  # Executable
    args=["servers/server.py"],  # Optional command line arguments
    env=None,  # Optional environment variables
)

def to_json(payload):
    try:
        if hasattr(payload, "dict"):
            return json.dumps(payload.model_dump(), ensure_ascii=False)
        elif hasattr(payload, "to_dict"):
            return json.dumps(payload.to_dict(), ensure_ascii=False)
        elif hasattr(payload, "__dataclass_fields__"):
            return json.dumps(asdict(payload), ensure_ascii=False)
        else:
            return json.dumps(payload, ensure_ascii=False)
    except Exception:
        return str(payload)

class LoggingRead:
    def __init__(self, read_stream):
        self._read_stream = read_stream

    async def receive(self):
        data = await self._read_stream.receive()
        payload = getattr(data, "message", data)
        print(f"[RESPONSE PAYLOAD] {to_json(payload)}")
        return data

    def __getattr__(self, name):
        return getattr(self._read_stream, name)

    async def __aenter__(self):
        await self._read_stream.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return await self._read_stream.__aexit__(exc_type, exc_val, exc_tb)

    def __aiter__(self):
        self._aiter = self._read_stream.__aiter__()
        return self

    async def __anext__(self):
        data = await self._aiter.__anext__()
        payload = getattr(data, "message", data)
        print(f"[RESPONSE PAYLOAD] {to_json(payload)}")
        return data

class LoggingWrite:
    def __init__(self, write_stream):
        self._write_stream = write_stream

    async def send(self, data):
        payload = getattr(data, "message", data)
        print(f"[REQUEST PAYLOAD] {to_json(payload)}")
        return await self._write_stream.send(data)

    def __getattr__(self, name):
        return getattr(self._write_stream, name)

    async def __aenter__(self):
        await self._write_stream.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return await self._write_stream.__aexit__(exc_type, exc_val, exc_tb)

async def run():
    async with stdio_client(server_params) as (read, write):
        # Wrap read and write with logging
        logging_read = LoggingRead(read)
        logging_write = LoggingWrite(write)
        async with ClientSession(
            logging_read, logging_write
        ) as session:
            # Initialize the connection
            await session.initialize()

            # # List available prompts
            # prompts = await session.list_prompts()

            # # Get a prompt
            # prompt = await session.get_prompt(
            #     "example-prompt", arguments={"arg1": "value"}
            # )

            # # List available resources
            # resources = await session.list_resources()

            # List available tools
            tools = await session.list_tools()

            # Read a resource
            # content, mime_type = await session.read_resource("file://some/path")

            # Call a tool
            result = await session.call_tool("add", arguments={"a": 5, "b": 3})
            print(result)


if __name__ == "__main__":
    import asyncio

    asyncio.run(run())