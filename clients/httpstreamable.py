from mcp.client.streamable_http import streamablehttp_client
from mcp import ClientSession

import json
from dataclasses import asdict

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

async def main():
    # Connect to a streamable HTTP server
    async with streamablehttp_client("http://localhost:8000/mcp") as (
        read_stream,
        write_stream,
        _,
    ):
        # Wrap read and write with logging
        logging_read = LoggingRead(read_stream)
        logging_write = LoggingWrite(write_stream)
        # Create a session using the client streams
        async with ClientSession(logging_read, logging_write) as session:
            # Initialize the connection
            await session.initialize()
            # Call a tool
            tool_result = await session.call_tool("add", {"a": 5, "b": 3})
            print(f"Tool result: {tool_result}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())