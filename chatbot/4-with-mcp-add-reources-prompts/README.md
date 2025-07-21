# Difference compared with `chatbot\3-with-mcp-multi-servers\mcp_chatbot.py`

1. Enhanced Session Management
- Changed from simple list-based session tracking to a unified dictionary-based approach
- `self.sessions` now maps tool names, prompt names, and resource URIs to their respective sessions
- Removed separate `self.tool_to_session` mapping

2. Resource Support Added
- Added capability to list and read resources from MCP servers
- New `get_resource()` method to retrieve resource content
- Support for `@<topic>` syntax to access paper resources
- Special handling for papers:// URIs with fallback logic

3. Prompts Support Added
- Added `self.available_prompts` list to track available prompts
- New `list_prompts()` method to display available prompts
- New `execute_prompt()` method to run prompts with arguments
- Support for `/prompts` and `/prompt <name>` commands

4. Improved Query Processing Loop
- Restructured the main processing loop to be more robust
- Better handling of multiple tool calls in sequence
- Cleaner separation between tool use detection and execution

5. Enhanced User Interface
- Added command system with `/` prefix for special commands
- Added `@` prefix for resource access
- More comprehensive help text and usage instructions
- Better error handling and user feedback