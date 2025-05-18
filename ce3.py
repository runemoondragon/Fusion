# ce3.py
# Remove anthropic import if no longer needed directly here
# import anthropic 
from rich.console import Console
from rich.markdown import Markdown
from rich.live import Live
from rich.spinner import Spinner
from rich.panel import Panel
from typing import List, Dict, Any
import importlib
import inspect
import pkgutil
import os
import json
import sys
import logging
import context_sanitizer  # Add this import at the top

from config import Config
from tools.base import BaseTool
# Import the provider base and potentially the factory if needed
from providers.base_provider import BaseProvider 
# Import specific provider classes for type checking
from providers.claude_provider import ClaudeProvider
from providers.openai_provider import OpenAIProvider
from providers.gemini_provider import GeminiProvider
from prompt_toolkit import prompt
from prompt_toolkit.styles import Style
from prompts.system_prompts import SystemPrompts

# Configure logging to only show ERROR level and above
logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)s: %(filename)s:%(lineno)d - %(message)s'
)

# --- ADDED: Mode Prompts Definition ---
MODE_PROMPTS = {
  "deep_research": "You are in Deep Research mode. Research deeply, verify facts, and reference credible sources.",
  "think": "You are in Think mode. Analyze the question using careful, logical step-by-step reasoning.",
  "write_code": "You are in Write/Code mode. Respond with concise, working code and explain it briefly.",
  "image": "You are in Image mode. Describe the visual scene clearly, suitable for generating an illustration."
}

class Assistant:
    """
    The Assistant class manages:
    - Loading of tools from a specified directory.
    - Orchestrating conversation flow with a given AI provider.
    - Handling user commands such as 'refresh' and 'reset'.
    - Token usage tracking and display.
    - Tool execution based on provider responses.

    This class is STATELESS regarding conversation history and total tokens.
    These are passed in and returned by the chat method.
    """

    def __init__(self):
        # API key check might be deferred to providers or kept general
        # if not getattr(Config, 'ANTHROPIC_API_KEY', None): # Remove or adapt check
        #     raise ValueError("No ANTHROPIC_API_KEY found in environment variables") 

        # Remove Anthropic client initialization
        # self.client = anthropic.Anthropic(api_key=Config.ANTHROPIC_API_KEY) 

        # STATELESS: conversation_history and total_tokens_used are removed from instance variables
        # self.conversation_history: List[Dict[str, Any]] = [] 
        # self.total_tokens_used = 0

        self.console = Console() # For server-side logging/tool display
        self.thinking_enabled = getattr(Config, 'ENABLE_THINKING', False)
        self.tools = self._load_tools()

    def _execute_uv_install(self, package_name: str) -> bool:
        """
        Execute the uvpackagemanager tool directly to install the missing package.
        Returns True if installation seems successful (no errors in output), otherwise False.
        """
        class ToolUseMock:
            name = "uvpackagemanager"
            input = {
                "command": "install",
                "packages": [package_name]
            }

        result = self._execute_tool(ToolUseMock())
        if "Error" not in result and "failed" not in result.lower():
            self.console.print("[green]The package was installed successfully.[/green]")
            return True
        else:
            self.console.print(f"[red]Failed to install {package_name}. Output:[/red] {result}")
            return False

    def _load_tools(self) -> List[Dict[str, Any]]:
        """
        Dynamically load all tool classes from the tools directory.
        If a dependency is missing, prompt the user to install it via uvpackagemanager.
        
        Returns:
            A list of tools (dicts) containing their 'name', 'description', and 'input_schema'.
        """
        tools = []
        tools_path = getattr(Config, 'TOOLS_DIR', None)

        if tools_path is None:
            self.console.print("[red]TOOLS_DIR not set in Config[/red]")
            return tools

        # Clear cached tool modules for fresh import
        for module_name in list(sys.modules.keys()):
            if module_name.startswith('tools.') and module_name != 'tools.base':
                del sys.modules[module_name]

        try:
            for module_info in pkgutil.iter_modules([str(tools_path)]):
                if module_info.name == 'base':
                    continue

                # Attempt loading the tool module
                try:
                    module = importlib.import_module(f'tools.{module_info.name}')
                    self._extract_tools_from_module(module, tools)
                except ImportError as e:
                    # Handle missing dependencies
                    missing_module = self._parse_missing_dependency(str(e))
                    self.console.print(f"\n[yellow]Missing dependency:[/yellow] {missing_module} for tool {module_info.name}")
                    user_response = input(f"Would you like to install {missing_module}? (y/n): ").lower()

                    if user_response == 'y':
                        success = self._execute_uv_install(missing_module)
                        if success:
                            # Retry loading the module after installation
                            try:
                                module = importlib.import_module(f'tools.{module_info.name}')
                                self._extract_tools_from_module(module, tools)
                            except Exception as retry_err:
                                self.console.print(f"[red]Failed to load tool after installation: {str(retry_err)}[/red]")
                        else:
                            self.console.print(f"[red]Installation of {missing_module} failed. Skipping this tool.[/red]")
                    else:
                        self.console.print(f"[yellow]Skipping tool {module_info.name} due to missing dependency[/yellow]")
                except Exception as mod_err:
                    self.console.print(f"[red]Error loading module {module_info.name}:[/red] {str(mod_err)}")
        except Exception as overall_err:
            self.console.print(f"[red]Error in tool loading process:[/red] {str(overall_err)}")

        return tools

    def _parse_missing_dependency(self, error_str: str) -> str:
        """
        Parse the missing dependency name from an ImportError string.
        """
        if "No module named" in error_str:
            parts = error_str.split("No module named")
            missing_module = parts[-1].strip(" '\"")
        else:
            missing_module = error_str
        return missing_module

    def _extract_tools_from_module(self, module, tools: List[Dict[str, Any]]) -> None:
        """
        Given a tool module, find and instantiate all tool classes (subclasses of BaseTool).
        Append them to the 'tools' list.
        """
        for name, obj in inspect.getmembers(module):
            if (inspect.isclass(obj) and issubclass(obj, BaseTool) and obj != BaseTool):
                try:
                    tool_instance = obj()
                    tools.append({
                        "name": tool_instance.name,
                        "description": tool_instance.description,
                        "input_schema": tool_instance.input_schema
                    })
                    self.console.print(f"[green]Loaded tool:[/green] {tool_instance.name}")
                except Exception as tool_init_err:
                    self.console.print(f"[red]Error initializing tool {name}:[/red] {str(tool_init_err)}")

    def refresh_tools(self):
        """
        Refresh the list of tools and show newly discovered tools.
        """
        current_tool_names = {tool['name'] for tool in self.tools}
        self.tools = self._load_tools()
        new_tool_names = {tool['name'] for tool in self.tools}
        new_tools = new_tool_names - current_tool_names

        if new_tools:
            self.console.print("\n")
            for tool_name in new_tools:
                tool_info = next((t for t in self.tools if t['name'] == tool_name), None)
                if tool_info:
                    description_lines = tool_info['description'].strip().split('\n')
                    formatted_description = '\n    '.join(line.strip() for line in description_lines)
                    self.console.print(f"[bold green]NEW[/bold green] 🔧 [cyan]{tool_name}[/cyan]:\n    {formatted_description}")
        else:
            self.console.print("\n[yellow]No new tools found[/yellow]")

    def display_available_tools(self):
        """
        Print a list of currently loaded tools.
        """
        self.console.print("\n[bold cyan]Available tools:[/bold cyan]")
        tool_names = [tool['name'] for tool in self.tools]
        if tool_names:
            formatted_tools = ", ".join([f"🔧 [cyan]{name}[/cyan]" for name in tool_names])
        else:
            formatted_tools = "No tools available."
        self.console.print(formatted_tools)
        self.console.print("\n---")

    def _display_tool_usage(self, tool_name: str, input_data: Dict, result: str):
        """
        If SHOW_TOOL_USAGE is enabled, display the input and result of a tool execution.
        Handles special cases like image data and large outputs for cleaner display.
        This method uses self.console for output and does not depend on instance history.
        """
        if not getattr(Config, 'SHOW_TOOL_USAGE', False):
            return

        # Clean up input data by removing any large binary/base64 content
        cleaned_input = self._clean_data_for_display(input_data)
        
        # Clean up result data
        cleaned_result = self._clean_data_for_display(result)

        tool_info = f"""[cyan]📥 Input:[/cyan] {json.dumps(cleaned_input, indent=2)}
[cyan]📤 Result:[/cyan] {cleaned_result}"""
        
        panel = Panel(
            tool_info,
            title=f"Tool used: {tool_name}",
            title_align="left",
            border_style="cyan",
            padding=(1, 2)
        )
        self.console.print(panel)

    def _clean_data_for_display(self, data):
        """
        Helper method to clean data for display by handling various data types
        and removing/replacing large content like base64 strings.
        This method is pure and does not depend on instance history.
        """
        if isinstance(data, str):
            try:
                # Try to parse as JSON first
                parsed_data = json.loads(data)
                return self._clean_parsed_data(parsed_data)
            except json.JSONDecodeError:
                # If it's a long string, check for base64 patterns
                if len(data) > 1000 and ';base64,' in data:
                    return "[base64 data omitted]"
                return data
        elif isinstance(data, dict):
            return self._clean_parsed_data(data)
        else:
            return data

    def _clean_parsed_data(self, data):
        """
        Recursively clean parsed data, replacing large strings with placeholders.
        This method is pure and does not depend on instance history.
        """
        if isinstance(data, dict):
            cleaned = {}
            for key, value in data.items():
                # Handle image data in various formats
                if key in ['data', 'image', 'source'] and isinstance(value, str):
                    if len(value) > 1000 and (';base64,' in value or value.startswith('data:')):
                        cleaned[key] = "[base64 data omitted]"
                    else:
                        cleaned[key] = value
                else:
                    cleaned[key] = self._clean_parsed_data(value)
            return cleaned
        elif isinstance(data, list):
            return [self._clean_parsed_data(item) for item in data]
        elif isinstance(data, str) and len(data) > 1000 and ';base64,' in data:
            return "[base64 data omitted]"
        return data

    def _execute_tool(self, tool_use_block: Any, current_conversation_for_tool_context: List[Dict[str, Any]]) -> str:
        """
        Execute a tool based on the tool_use_block from the LLM.
        Args:
            tool_use_block: The tool use block object from the LLM (e.g., Anthropic's ToolUseBlock or similar dict).
                            Expected to have 'name' and 'input' attributes/keys.
            current_conversation_for_tool_context: The current conversation history, passed for potential
                                                   context if a tool ever needs it (though tools should aim to be stateless).
        Returns:
            A string result from the tool execution.
        """
        tool_name = getattr(tool_use_block, 'name', tool_use_block.get('name'))
        tool_input = getattr(tool_use_block, 'input', tool_use_block.get('input'))

        if not tool_name or tool_input is None: # tool_input can be an empty dict {} for no-arg tools
            logging.error(f"Tool execution error: Missing name or input in tool_use_block: {tool_use_block}")
            return "Error: Tool name or input missing in tool request."

        # Find the tool definition (schema) from self.tools loaded at init
        tool_definition = next((t for t in self.tools if t['name'] == tool_name), None)
        if not tool_definition:
            logging.error(f"Tool execution error: Tool '{tool_name}' not found in loaded tools.")
            return f"Error: Tool '{tool_name}' is not available or not loaded."

        try:
            # Dynamically find and instantiate the tool class for execution.
            # This assumes tool names map to modules/classes in a predictable way or are registered.
            # For simplicity, this example attempts to find the tool instance using _find_tool_instance_in_module.
            # In a more robust system, self.tools might store actual callable instances or factories.
            
            # Attempt to find the module based on common naming conventions if not directly stored.
            # This part is heuristic and might need refinement based on actual tool module structure.
            module_name_candidate = f"tools.{tool_name.replace('Tool', '').lower()}tool" 
            if "duckduckgo" in tool_name: module_name_candidate = "tools.duckduckgotool" # Example for specific known tools
            # Add more specific mappings if general convention doesn't cover all tools

            tool_instance = None
            try:
                module = importlib.import_module(module_name_candidate)
                tool_instance = self._find_tool_instance_in_module(module, tool_name)
            except ImportError:
                logging.warning(f"Could not import module {module_name_candidate} for tool {tool_name}. Trying other tools modules.")
                # Fallback: iterate through all loaded tool modules if direct import fails (less efficient)
                tools_path = getattr(Config, 'TOOLS_DIR', 'tools')
                for mod_info in pkgutil.iter_modules([str(tools_path)]):
                    if mod_info.name == 'base': continue
                    try:
                        module = importlib.import_module(f'tools.{mod_info.name}')
                        tool_instance = self._find_tool_instance_in_module(module, tool_name)
                        if tool_instance: break
                    except ImportError:
                        continue # Skip modules that can't be imported
            
            if not tool_instance:
                logging.error(f"Tool execution error: Could not load/find executable for tool '{tool_name}'.")
                return f"Error: Tool '{tool_name}' could not be loaded for execution."

            logging.info(f"Executing tool: {tool_name} with input: {tool_input}")
            result = tool_instance.execute(**tool_input) # Execute the tool's method
            
            if Config.SHOW_TOOL_USAGE:
                self._display_tool_usage(tool_name, tool_input, result) # Uses self.console
            
            return str(result) # Ensure result is a string

        except Exception as e:
            logging.exception(f"Exception during execution of tool '{tool_name}'")
            return f"Error executing tool '{tool_name}': {str(e)}"

    def _find_tool_instance_in_module(self, module, tool_name_to_find: str) -> BaseTool | None:
        """
        Given a tool module, find and instantiate a tool class that matches tool_name_to_find.
        """
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and issubclass(obj, BaseTool) and obj != BaseTool:
                try:
                    # Instantiate the tool to check its actual 'name' property/attribute
                    tool_candidate_instance = obj()
                    if hasattr(tool_candidate_instance, 'name') and tool_candidate_instance.name == tool_name_to_find:
                        return tool_candidate_instance # Return the instance if names match
                except Exception as e:
                    # Log error if a specific tool class in the module fails to instantiate
                    logging.error(f"Error instantiating tool class {name} from module {module.__name__} while searching for {tool_name_to_find}: {e}")
        return None # Tool not found in this module

    def _display_token_usage(self, usage_this_call: Dict[str, int], cumulative_total_tokens: int):
        """
        Displays token usage for the current API call and the cumulative total for the session.
        Args:
            usage_this_call: Dict with 'input_tokens', 'output_tokens' for the current call.
            cumulative_total_tokens: The total tokens used so far in this session.
        """
        if not getattr(Config, 'SHOW_TOKEN_USAGE', True): # Default to True if not set
            return

        input_str = f"Input: {usage_this_call.get('input_tokens', 'N/A')}"
        output_str = f"Output: {usage_this_call.get('output_tokens', 'N/A')}"
        total_str = f"Total Used (Session): {cumulative_total_tokens}"
        max_tokens_str = f"Max Allowed (Session): {Config.MAX_CONVERSATION_TOKENS}"
        runtime_str = f"Runtime: {usage_this_call.get('runtime', 'N/A'):.2f}s" if usage_this_call.get('runtime') else ""

        usage_info = f"[bold yellow]Token Usage:[/bold yellow] {input_str}, {output_str}. {total_str} / {max_tokens_str}. {runtime_str}"
        self.console.print(Markdown(usage_info))

    def chat(self, user_input: Any, provider: BaseProvider,
             conversation_history: List[Dict[str, Any]],
             total_tokens_used: int, # Current total for this session, passed in
             mode: str | None = None,
             request_id: str | None = None) -> Dict[str, Any]: # Optional request_id for logging
        """
        Processes a chat message, interacts with the provider, and handles tool use.
        This method is STATELESS regarding history and tokens.
        It operates on the provided conversation_history and total_tokens_used.
        Returns a dictionary including the updated history, tokens, and response.
        """
        # Work on copies to avoid modifying the lists/values passed from app.py directly in this scope
        current_conversation_history = [dict(msg) for msg in conversation_history] # Deep copy for safety
        current_total_tokens_used = total_tokens_used

        log_prefix = f"[ID: {request_id}] " if request_id else ""

        # 1. Add user message to history
        if isinstance(user_input, str):
            current_conversation_history.append({"role": "user", "content": user_input})
        elif isinstance(user_input, list): # For multi-part messages (e.g., image and text)
            current_conversation_history.append({"role": "user", "content": user_input})
        else:
            # Handle other potential structured inputs if necessary, or log a warning
            logging.warning(f"{log_prefix}Unexpected user_input type: {type(user_input)}. Converting to string.")
            current_conversation_history.append({"role": "user", "content": str(user_input)})

        # 2. Token limit check for the session (early exit or truncation strategy)
        if current_total_tokens_used >= Config.MAX_CONVERSATION_TOKENS:
            logging.warning(f"{log_prefix}Session token limit ({Config.MAX_CONVERSATION_TOKENS}) already reached or exceeded: {current_total_tokens_used}. Not processing new message.")
            # Optionally, implement history truncation here via context_sanitizer
            # For now, just return an error or a message indicating limit reached.
            return {
                'response': "Token limit for this conversation session has been reached. Please reset the conversation or start a new one.",
                'tool_name': None,
                'usage': {'input_tokens': 0, 'output_tokens': 0, 'runtime': 0},
                'updated_conversation_history': current_conversation_history, # Return current history as is
                'updated_total_tokens_used': current_total_tokens_used
            }

        # 3. Sanitize history for the specific provider
        provider_name_simple = provider.name.lower().replace("provider", "")
        # context_sanitizer.sanitize_history will be called before each API call within the loop

        # 4. System prompt (mode handling) - often handled by provider or by prepending to messages
        # System prompts might be added by the provider internally or by pre-pending to message list if necessary.
        # For instance, if MODE_PROMPTS are used, they might be injected as the first system message if provider supports it,
        # or handled by the provider's specific `chat` implementation. This part is provider-dependent.
        # Example: Provider's chat method might take a `system_message` argument from `MODE_PROMPTS.get(mode)`

        # 5. Main interaction loop (for potential tool use)
        MAX_TOOL_LOOPS = Config.MAX_TOOL_CALLS if hasattr(Config, 'MAX_TOOL_CALLS') else 5 # Default to 5 loops
        loop_count = 0
        last_api_response_data = {'usage': {'input_tokens': 0, 'output_tokens': 0, 'runtime': 0}} # For token/usage tracking
        final_response_text_parts = []
        tool_name_invoked_in_turn = None

        while loop_count < MAX_TOOL_LOOPS:
            loop_count += 1
            logging.info(f"{log_prefix}Chat loop iteration: {loop_count}")

            # Sanitize the *current full history* for the provider before this API call
            messages_for_api_call = context_sanitizer.sanitize_history(
                current_conversation_history,
                provider_name_simple
            )
            
            # Check token count *after* sanitization and before API call if possible (though input tokens are an estimate)
            # This is more complex as exact input token count is usually from provider response.
            # Primary check is at the start of `chat` and after each provider response.

            try:
                api_response = provider.chat(
                    messages=messages_for_api_call,
                    tools=self.tools, # List of tool schemas
                    config=Config
                )
                # api_response is dict: {'content': ..., 'usage': ..., 'stop_reason': ..., etc.}
                last_api_response_data = api_response # Store for usage and other details

                # Accumulate tokens from this call
                call_input_tokens = api_response.get('usage', {}).get('input_tokens', 0)
                call_output_tokens = api_response.get('usage', {}).get('output_tokens', 0)
                current_total_tokens_used += call_input_tokens + call_output_tokens
                
                if Config.SHOW_TOKEN_USAGE:
                    self._display_token_usage(api_response.get('usage', {}), current_total_tokens_used)

                # Check token limit again after receiving response and updating session total
                if current_total_tokens_used >= Config.MAX_CONVERSATION_TOKENS:
                    logging.warning(f"{log_prefix}Session token limit ({Config.MAX_CONVERSATION_TOKENS}) reached after API call: {current_total_tokens_used}.")
                    # Potentially truncate response or just note that limit is hit.
                    # For now, we'll allow the current response to be processed.

                response_content_list = api_response.get('content', [])
                # Ensure content is a list, even if provider returns a single block or string
                if not isinstance(response_content_list, list):
                    response_content_list = [response_content_list] if response_content_list else []
                
                assistant_message_parts_for_history = []
                tool_calls_requested_by_llm = []
                text_received_this_iteration = False

                for block_item in response_content_list:
                    # Sanitize/convert provider-specific blocks (e.g., Anthropic TextBlock) to dicts
                    block = context_sanitizer._to_dict_if_possible(block_item)
                    
                    if isinstance(block, dict) and block.get('type') == 'text':
                        final_response_text_parts.append(block.get('text', ''))
                        assistant_message_parts_for_history.append(block)
                        text_received_this_iteration = True
                    elif isinstance(block, dict) and block.get('type') == 'tool_use':
                        tool_calls_requested_by_llm.append(block)
                        assistant_message_parts_for_history.append(block) # Add tool_use to assistant message
                        tool_name_invoked_in_turn = block.get('name', tool_name_invoked_in_turn)
                    elif isinstance(block, str): # Handle plain string content
                        final_response_text_parts.append(block)
                        assistant_message_parts_for_history.append({"type": "text", "text": block})
                        text_received_this_iteration = True
                    else:
                        logging.warning(f"{log_prefix}Unsupported content block type or format: {block}")
                
                # Add assistant's full response (text and/or tool_use blocks) to history
                if assistant_message_parts_for_history:
                    current_conversation_history.append({
                        "role": "assistant",
                        "content": assistant_message_parts_for_history
                    })
                elif not tool_calls_requested_by_llm: # No content and no tools, potentially an issue
                    logging.warning(f"{log_prefix}Provider returned no text and no tool calls.")
                    # We might break here or add a default "No response" message
                    # If this is the first iteration and no text, it means the very first response was empty
                    if loop_count == 1 and not final_response_text_parts:
                        final_response_text_parts.append("[Provider returned no actionable response]")
                    break # Exit loop if no tools and no new text parts from assistant this turn

                if not tool_calls_requested_by_llm:
                    logging.info(f"{log_prefix}No tool calls requested by LLM. Ending chat loop.")
                    break # No tools to call, this turn is complete.

                # --- Execute requested tools --- 
                logging.info(f"{log_prefix}LLM requested {len(tool_calls_requested_by_llm)} tool(s). Executing...")
                tool_results_content_for_history = [] # Renamed from tool_results_for_llm for clarity
                
                for tool_call_request_block in tool_calls_requested_by_llm:
                    tool_use_id = tool_call_request_block.get('id')
                    tool_name = tool_call_request_block.get('name') # Get name for each call
                    
                    tool_execution_result_content_str = self._execute_tool(tool_call_request_block, current_conversation_history)
                    
                    # Check for successful filecreatortool execution to modify LLM feedback
                    if tool_name == "filecreatortool":
                        try:
                            tool_output_data = json.loads(tool_execution_result_content_str)
                            if tool_output_data.get("created_files", 0) > 0 and tool_output_data.get("failed_files", 0) == 0:
                                logging.info(f"{log_prefix}FileCreatorTool succeeded. Modifying feedback to LLM.")
                                # Replace the raw JSON output with a more instructive message for the LLM
                                # This message becomes the content of the tool_result block for this specific tool call.
                                tool_execution_result_content_str = (
                                    f"The file creation via '{tool_name}' was successful. "
                                    f"Details: {json.dumps(tool_output_data)}. "
                                    f"Please inform the user that the file has been created and do not call any more tools for this request."
                                )
                                # This modified string will be used in the tool_result block below.
                        except json.JSONDecodeError:
                            logging.warning(f"{log_prefix}Could not parse FileCreatorTool output as JSON: {tool_execution_result_content_str}")
                        except Exception as e_fct_parse:
                            logging.error(f"{log_prefix}Error processing FileCreatorTool output for feedback modification: {e_fct_parse}")

                    tool_result_block = {
                        "type": "tool_result",
                        "tool_use_id": tool_use_id,
                        "content": tool_execution_result_content_str # Use the (potentially modified) string content
                    }
                    tool_results_content_for_history.append(tool_result_block)
                
                # Add tool results to history for the next call to the LLM
                if tool_results_content_for_history: # Only add if there are results
                    current_conversation_history.append({
                        "role": "user", 
                        "content": tool_results_content_for_history
                    })
                    final_response_text_parts = [] 
                    logging.info(f"{log_prefix}Added {len(tool_results_content_for_history)} tool result(s) to history. Continuing loop.")
                else: # Should not happen if tool_calls_requested_by_llm was not empty
                    logging.warning(f"{log_prefix}No tool results to add to history despite tool calls being requested. This might be an issue.")
                    break # Avoid potential infinite loop if something went wrong with tool execution reporting

            except Exception as e:
                logging.exception(f"{log_prefix}Exception during provider.chat() or tool processing in loop iteration {loop_count}")
                # Use the text gathered so far (if any) or an error message
                text_to_return = " ".join(final_response_text_parts).strip() if final_response_text_parts else f"An error occurred during processing: {str(e)}"
                return {
                    'response': text_to_return,
                    'tool_name': tool_name_invoked_in_turn,
                    'usage': last_api_response_data.get('usage', {}),
                    'updated_conversation_history': current_conversation_history,
                    'updated_total_tokens_used': current_total_tokens_used
                }

            if loop_count >= MAX_TOOL_LOOPS:
                logging.warning(f"{log_prefix}Max tool loops ({MAX_TOOL_LOOPS}) reached.")
                if not final_response_text_parts: # If last iteration was tool call and no text yet
                    final_response_text_parts.append("[Max tool iterations reached. No final text response from assistant.]")
                break
        
        # Consolidate final text response
        final_response_str = " ".join(final_response_text_parts).strip()
        if not final_response_str and not tool_name_invoked_in_turn: # Check if there was truly no output
            final_response_str = "[No response content]"
        elif not final_response_str and tool_name_invoked_in_turn and loop_count >= MAX_TOOL_LOOPS:
             final_response_str = "[Assistant used a tool but reached max iterations without further text response.]"
        elif not final_response_str and tool_name_invoked_in_turn:
             final_response_str = "[Assistant used a tool. No additional text was generated.]"

        logging.info(f"{log_prefix}Chat processing complete. Final response length: {len(final_response_str)}, Total tokens for session: {current_total_tokens_used}")

        return {
            'response': final_response_str,
            'tool_name': tool_name_invoked_in_turn, # Name of the last tool invoked in the turn
            'usage': last_api_response_data.get('usage', {}), # Usage from the *last* successful LLM call
            'updated_conversation_history': current_conversation_history,
            'updated_total_tokens_used': current_total_tokens_used
        }

    def reset(self):
        """
        This method is now a no-op as history is managed per-session in app.py.
        The Assistant instance itself is stateless regarding conversation history.
        """
        # self.console.print("[yellow]Assistant.reset() called, but history is session-managed by the calling application.[/yellow]")
        pass

def main():
    """
    Entry point for the assistant CLI loop.
    Provides a prompt for user input and handles 'quit' and 'reset' commands.
    """
    console = Console()
    style = Style.from_dict({'prompt': 'orange'})

    try:
        assistant = Assistant()
        # How to select provider here? Default to Claude? Add argument?
        # provider = ProviderFactory.create_provider("claude") # Example: Default
    except ValueError as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        console.print("Please ensure ANTHROPIC_API_KEY is set correctly.")
        return

    welcome_text = """
# Claude Engineer v3. A self-improving assistant framework with tool creation

Type 'refresh' to reload available tools
Type 'reset' to clear conversation history
Type 'quit' to exit

Available tools:
"""
    console.print(Markdown(welcome_text))
    assistant.display_available_tools()

    while True:
        try:
            # ... Prompt user ...
            user_input_text = prompt("You: ", style=style).strip()

            if user_input_text.lower() == 'quit':
                break
            
            # Need to select provider here for CLI use
            # For now, let's assume Claude for testing CLI
            from providers.provider_factory import ProviderFactory # Local import for CLI
            provider_name = "claude" # Hardcode for CLI example
            provider = ProviderFactory.create_provider(provider_name)

            # Call the refactored chat method
            result = assistant.chat(user_input_text, provider)
            response_text = result.get('response', '[No response]')

            # Display response using Rich Markdown
            console.print("\n")
            console.print(Markdown(response_text))
            console.print("\n---\n")

            # Check if response indicates exit (e.g., from 'quit' command)
            if response_text == "Goodbye!":
                break
            if "Token limit reached" in response_text:
                # Maybe prompt user to reset or exit
                pass
        
        # Ensure except blocks are correctly aligned with the try block inside the loop
        except KeyboardInterrupt:
            # This break exits the while True loop
            break 
        except Exception as e:
            console.print(f"\n[bold red]An error occurred:[/bold red] {str(e)}")

    # This print is outside the loop
    console.print("Exiting.")

if __name__ == "__main__":
    main()