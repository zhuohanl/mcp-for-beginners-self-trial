from dotenv import load_dotenv
from anthropic import Anthropic
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client
from typing import List, Dict, TypedDict
from contextlib import AsyncExitStack
from pathlib import Path

import os
import json
import asyncio

load_dotenv()

class ToolDefinition(TypedDict):
    name: str
    description: str
    input_schema: dict

class MCP_ChatBot:

    def __init__(self):
        # Initialize session and client objects
        self.sessions: List[ClientSession] = [] # new
        self.exit_stack = AsyncExitStack() # new
        self.anthropic = Anthropic()
        self.available_tools: List[ToolDefinition] = [] # new
        self.tool_to_session: Dict[str, ClientSession] = {} # new


    async def connect_to_server(self, server_name: str, server_config: dict) -> None:
        """Connect to a single MCP server."""
        try:
            server_params = StdioServerParameters(**server_config)
            stdio_transport = await self.exit_stack.enter_async_context(
                stdio_client(server_params)
            ) # new
            read, write = stdio_transport
            session = await self.exit_stack.enter_async_context(
                ClientSession(read, write)
            ) # new
            await session.initialize()
            self.sessions.append(session)
            
            # List available tools for this session
            response = await session.list_tools()
            tools = response.tools
            print(f"\nConnected to {server_name} with tools:", [t.name for t in tools])
            
            for tool in tools: # new
                tool_def = {
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.inputSchema
                }
                self.tool_to_session[tool.name] = session
                self.available_tools.append(tool_def)
        except Exception as e:
            print(f"\nFailed to connect to {server_name}: {e}")

    async def connect_to_servers(self): # new
        """Connect to all configured MCP servers."""
        try:
            # Load server configuration from JSON file
            config_path = Path(__file__).parent / "server_config.json"
            with open(config_path, "r") as file:
                data = json.load(file)
            
            servers = data.get("mcpServers", {})
            
            for server_name, server_config in servers.items():
                # Create a copy to avoid modifying the original config
                modified_config = server_config.copy()
                modified_config["args"] = server_config["args"].copy()
                
                # Check if any argument is a Python file path
                for i, arg in enumerate(modified_config["args"]):
                    if isinstance(arg, str) and arg.endswith(".py"):
                        # Convert relative path to absolute path based on this script's location
                        script_dir = Path(__file__).parent
                        if not Path(arg).is_absolute():
                            modified_config["args"][i] = str(script_dir / arg)
                        print(f"\nModified argument {i} for server {server_name}: {modified_config['args'][i]}")
                
                print(f"\nConnecting to server: {server_name}")
                await self.connect_to_server(server_name, modified_config)
        except Exception as e:
            print(f"\nError loading server configuration: {e}")
            raise
    
    async def process_query(self, query):
        messages = [{'role':'user', 'content':query}]
        response = self.anthropic.messages.create(max_tokens = 2024,
                                      model = os.getenv("ANTHROPIC_MODEL"), 
                                      tools = self.available_tools,
                                      messages = messages)
        process_query = True
        while process_query:
            assistant_content = []
            for content in response.content:
                if content.type =='text':
                    print(f"\nAssistant: {content.text}")
                    assistant_content.append(content)
                    if(len(response.content) == 1):
                        process_query= False
                elif content.type == 'tool_use':
                    assistant_content.append(content)
                    messages.append({'role':'assistant', 'content':assistant_content})
                    tool_id = content.id
                    tool_args = content.input
                    tool_name = content.name
                    
    
                    print(f"\nApplication: Calling tool {tool_name} with args {tool_args}")
                    
                    # Call a tool
                    session = self.tool_to_session[tool_name] # new
                    result = await session.call_tool(tool_name, arguments=tool_args)
                    messages.append({"role": "user", 
                                      "content": [
                                          {
                                              "type": "tool_result",
                                              "tool_use_id":tool_id,
                                              "content": result.content
                                          }
                                      ]
                                    })
                    response = self.anthropic.messages.create(max_tokens = 2024,
                                      model = os.getenv("ANTHROPIC_MODEL"), 
                                      tools = self.available_tools,
                                      messages = messages) 
                    
                    if(len(response.content) == 1 and response.content[0].type == "text"):
                        print(f"\nAssistant: {response.content[0].text}")
                        process_query= False

    
    
    async def chat_loop(self):
        """Run an interactive chat loop"""
        print("\nMCP Chatbot Started!")
        print("Type your queries or 'quit' to exit.")
        
        while True:
            try:
                query = input("\nUser: ").strip()
        
                if query.lower() == 'quit':
                    break
                    
                await self.process_query(query)
                print("\n")
                    
            except Exception as e:
                print(f"\nError: {str(e)}")
    
    async def cleanup(self): # new
        """Cleanly close all resources using AsyncExitStack."""
        await self.exit_stack.aclose()


async def main():
    chatbot = MCP_ChatBot()
    try:
        # the mcp clients and sessions are not initialized using "with"
        # like in the previous lesson
        # so the cleanup should be manually handled
        await chatbot.connect_to_servers() # new! 
        await chatbot.chat_loop()
    finally:
        await chatbot.cleanup() #new! 


if __name__ == "__main__":
    asyncio.run(main())