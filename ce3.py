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
    level=logging.ERROR,
    format='%(levelname)s: %(message)s'
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
    """

    def __init__(self):
        # API key check might be deferred to providers or kept general
        # if not getattr(Config, 'ANTHROPIC_API_KEY', None): # Remove or adapt check
        #     raise ValueError("No ANTHROPIC_API_KEY found in environment variables") 

        # Remove Anthropic client initialization
        # self.client = anthropic.Anthropic(api_key=Config.ANTHROPIC_API_KEY) 

        self.conversation_history: List[Dict[str, Any]] = []
        self.console = Console()

        self.thinking_enabled = getattr(Config, 'ENABLE_THINKING', False)
        # Temperature might move to provider call if it varies
        # self.temperature = getattr(Config, 'DEFAULT_TEMPERATURE', 0.7) 
        self.total_tokens_used = 0

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
        Recursively clean parsed JSON/dict data, handling nested structures
        and replacing large data with placeholders.
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

    def _execute_tool(self, tool_use):
        """
        Given a tool usage request (with tool name and inputs),
        dynamically load and execute the corresponding tool.
        """
        tool_name = tool_use.name
        tool_input = tool_use.input or {}
        tool_result = None

        try:
            module = importlib.import_module(f'tools.{tool_name}')
            tool_instance = self._find_tool_instance_in_module(module, tool_name)

            if not tool_instance:
                tool_result = f"Tool not found: {tool_name}"
            else:
                # Execute the tool with the provided input
                try:
                    result = tool_instance.execute(**tool_input)
                    # Keep structured data intact
                    tool_result = result
                except Exception as exec_err:
                    tool_result = f"Error executing tool '{tool_name}': {str(exec_err)}"
        except ImportError:
            tool_result = f"Failed to import tool: {tool_name}"
        except Exception as e:
            tool_result = f"Error executing tool: {str(e)}"

        # Display tool usage with proper handling of structured data
        self._display_tool_usage(tool_name, tool_input, 
            json.dumps(tool_result) if not isinstance(tool_result, str) else tool_result)
        return tool_result

    def _find_tool_instance_in_module(self, module, tool_name: str):
        """
        Search a given module for a tool class matching tool_name and return an instance of it.
        """
        for name, obj in inspect.getmembers(module):
            if (inspect.isclass(obj) and issubclass(obj, BaseTool) and obj != BaseTool):
                candidate_tool = obj()
                if candidate_tool.name == tool_name:
                    return candidate_tool
        return None

    def _display_token_usage(self, usage: Dict[str, int]):
        """
        Display token usage. 
        Now receives usage dict directly from the provider response processing.
        Updates total token count.
        """
        input_tokens = usage.get('input_tokens', 0)
        output_tokens = usage.get('output_tokens', 0)
        
        # Update total token usage
        self.total_tokens_used += input_tokens + output_tokens

        used_percentage = (self.total_tokens_used / Config.MAX_CONVERSATION_TOKENS) * 100
        remaining_tokens = max(0, Config.MAX_CONVERSATION_TOKENS - self.total_tokens_used)

        self.console.print(f"\nTokens: In={input_tokens:,}, Out={output_tokens:,} | Total: {self.total_tokens_used:,} / {Config.MAX_CONVERSATION_TOKENS:,}")

        bar_width = 40
        filled = int(used_percentage / 100 * bar_width)
        bar = "█" * filled + "░" * (bar_width - filled)

        color = "green"
        if used_percentage > 75:
            color = "yellow"
        if used_percentage > 90:
            color = "red"

        self.console.print(f"[{color}][{bar}] {used_percentage:.1f}%[/{color}]")

        if remaining_tokens < 20000: # Keep warning threshold
            self.console.print(f"[bold red]Warning: Only {remaining_tokens:,} tokens remaining![/bold red]")

        self.console.print("---")

        # Return True if token limit is reached
        return self.total_tokens_used >= Config.MAX_CONVERSATION_TOKENS

    def chat(self, user_input, provider: BaseProvider, mode: str | None = None) -> Dict[str, Any]:
        """
        Process a chat message using the specified provider.
        Orchestrates the conversation loop including tool calls and mode injection.
        user_input can be either a string (text-only) or a list (multimodal message).
        mode: Optional string indicating the selected operational mode.
        Returns:
            A dictionary containing the final response text and the name of the last tool used (if any).
            e.g., {'response': '...', 'tool_name': '...'}
        """
        final_response_text = ""
        last_tool_name = None
        
        # Handle special CLI commands first (only for string input)
        if isinstance(user_input, str):
            if user_input.lower() == 'refresh':
                self.refresh_tools()
                return {'response': "Tools refreshed successfully!", 'tool_name': None}
            elif user_input.lower() == 'reset':
                self.reset()
                return {'response': "Conversation reset!", 'tool_name': None}
            elif user_input.lower() == 'quit':
                 return {'response': "Goodbye!", 'tool_name': None} # Or handle exit differently

        try:
            # Add user message to conversation history
            # Use a copy of the history for this turn's processing to avoid persistent mode injection
            current_turn_history = list(self.conversation_history) # Create a shallow copy
            current_turn_history.append({
                "role": "user",
                "content": user_input 
            })

            max_turns = 5 # Safety break for tool loops
            turn_count = 0

            # Start conversation loop (handles potential tool calls)
            while turn_count < max_turns:
                turn_count += 1
                
                # Check token limit before calling provider
                if self.total_tokens_used >= Config.MAX_CONVERSATION_TOKENS:
                    self.console.print("\n[bold red]Token limit reached! Please reset the conversation.[/bold red]")
                    return {'response': "Token limit reached! Please type 'reset' to start a new conversation.", 'tool_name': None}

                # --- Determine if the last message was a tool result --- 
                was_last_message_tool_result = False
                if turn_count > 1 and current_turn_history: # Check if not the first turn
                    last_msg = current_turn_history[-1]
                    if last_msg.get('role') == 'user' and isinstance(last_msg.get('content'), list):
                        # Check if any item in the content list is a tool_result
                        if any(isinstance(item, dict) and item.get('type') == 'tool_result' for item in last_msg['content']):
                            was_last_message_tool_result = True
                            logging.info("Detected that the previous turn ended with tool results.")
                
                # --- Modified Mode Injection Logic --- 
                messages_to_send = list(current_turn_history) # Work with turn-specific history copy
                provider_name = provider.name # Get the actual provider's name
                logging.info(f"Processing turn {turn_count} with provider: {provider_name}, Mode: {mode}")

                # Inject mode prompt ONLY if:
                # 1. Provider is NOT NeuroSwitch (handled by provider_name check)
                # 2. A valid mode is selected
                # 3. The PREVIOUS message was NOT a tool result (to avoid breaking sequence for providers like Claude)
                if provider_name in ["ClaudeProvider", "OpenAIProvider", "GeminiProvider"] and mode and mode in MODE_PROMPTS and not was_last_message_tool_result:
                    system_message = {"role": "system", "content": MODE_PROMPTS[mode]}
                    messages_to_send.insert(0, system_message) 
                    logging.info(f"Injected system prompt for mode: '{mode}'")
                elif was_last_message_tool_result:
                     logging.info("Skipping mode prompt injection because previous message was a tool result.")
                # --- END Mode Injection Logic ---

                # Show thinking indicator
                live_spinner = None
                if self.thinking_enabled and self.console: # Check console exists for CLI use
                    live_spinner = Live(Spinner('dots', text='Thinking...', style="cyan"), 
                                        refresh_per_second=10, transient=True, console=self.console)
                    live_spinner.start()

                try:
                     # Call the provider's chat method
                     api_response = provider.chat(
                         messages=messages_to_send, 
                         tools=self.tools,
                         config=Config
                     )
                finally:
                    if live_spinner:
                        live_spinner.stop()

                # Process usage info and check token limit
                usage = api_response.get('usage', {})
                if self._display_token_usage(usage): # display also updates total_tokens_used and returns True if limit reached
                    return {'response': "Token limit reached during processing! Please type 'reset' to start a new conversation.", 'tool_name': last_tool_name}

                # Extract content (might be list or other structure depending on provider)
                response_content = api_response.get('content')
                stop_reason = api_response.get('stop_reason') # Get stop reason if available

                # --- Tool Handling Logic ---
                tool_calls_detected = False
                tool_results = []
                assistant_message_content = [] # Build assistant message content list
                potential_final_text = "" # Store text part in case it's the final response
                
                # Check if the response content is a list (common format now)
                if isinstance(response_content, list):
                     for block in response_content:
                         # --- Provider-Specific Block Processing --- 
                         is_tool_use = False
                         block_type = None
                         tool_use_id = None
                         tool_name = None
                         tool_input = None
                         text_content = None

                         if isinstance(provider, ClaudeProvider) and hasattr(block, 'type'):
                             # Claude uses Pydantic objects with dot notation
                             block_type = block.type
                             if block_type == 'tool_use':
                                 is_tool_use = True
                                 tool_use_id = block.id
                                 tool_name = block.name
                                 tool_input = block.input or {}
                             elif block_type == 'text':
                                 text_content = block.text
                                 potential_final_text = text_content # Store text

                         elif isinstance(provider, (OpenAIProvider, GeminiProvider)) and isinstance(block, dict):
                             # OpenAI/Gemini providers were implemented to return dicts
                             block_type = block.get('type')
                             if block_type == 'tool_use':
                                 is_tool_use = True
                                 tool_use_id = block.get('id')
                                 tool_name = block.get('name')
                                 tool_input = block.get('input', {})
                             elif block_type == 'text':
                                  text_content = block.get('text', '')
                                  potential_final_text = text_content # Store text
                         # --- End Provider-Specific Block Processing ---

                         # Add the original block to the assistant message history
                         # (assuming providers return compatible dict/object structures for history)
                         assistant_message_content.append(block)

                         # If it was a tool use, execute it
                         if is_tool_use:
                             tool_calls_detected = True
                             last_tool_name = tool_name # Track last tool used
                             self.console.print(f"\n[bold yellow]  Executing Tool: {tool_name}[/bold yellow]\n")
                             
                             # Need to pass the correct object/dict to _execute_tool
                             # _execute_tool expects an object with .name and .input attributes
                             # Let's create a simple mock object for consistency if needed
                             class ToolUseMock:
                                 def __init__(self, name, input_data, id_val=None): # Add id if needed
                                     self.name = name
                                     self.input = input_data
                                     self.id = id_val # Store id if available
                             
                             tool_use_obj = ToolUseMock(tool_name, tool_input, tool_use_id)
                             result = self._execute_tool(tool_use_obj)

                             # Format tool result for history
                             tool_results.append({
                                 "type": "tool_result",
                                 "tool_use_id": tool_use_id,
                                  "tool_name": tool_name, # Removed: Causes error for Claude API
                                 "content": result 
                             })
                         # else: pass # If it's just text, we stored it in potential_final_text
                
                # Handle cases where the entire response might be a single string (less common now)
                elif isinstance(response_content, str):
                    potential_final_text = response_content
                    # Add the simple string response to history
                    assistant_message_content.append({"type": "text", "text": response_content}) 
                
                # --- End Tool Handling ---

                if tool_calls_detected:
                    # Add assistant's message (containing tool_use blocks) to history
                    self.conversation_history.append({
                         "role": "assistant",
                         "content": assistant_message_content 
                     })
                    # Add the tool results as a user message and continue loop
                    self.conversation_history.append({
                        "role": "user", # Role for tool results
                        "content": tool_results
                    })
                    # Update current_turn_history for the next iteration of the while loop
                    current_turn_history.append({"role": "assistant", "content": assistant_message_content })
                    current_turn_history.append({"role": "user", "content": tool_results})
                    continue # Continue loop to get model response after tool execution
                else:
                    # No tool use detected, this is the final response.
                    # Use the text content we captured earlier.
                    final_response_text = potential_final_text
                    
                    # Add the final assistant message to history
                    self.conversation_history.append({
                        "role": "assistant",
                        # Store the structured content if available, otherwise the text
                        "content": assistant_message_content if assistant_message_content else final_response_text
                    })

                    # Validate final response text
                    if not final_response_text and assistant_message_content:
                        final_response_text = "[Assistant responded with non-text content]"
                    elif not final_response_text and not assistant_message_content:
                         final_response_text = "[No suitable content found in response]"
                    
                    # Break the loop as we have the final answer
                    break

            if turn_count >= max_turns:
                 final_response_text = "[Reached maximum tool execution turns]"
                 self.console.print(f"[bold red]{final_response_text}[/bold red]")

            # --- IMPORTANT: Add the initial user message to persistent history --- 
            # This was only added to current_turn_history before the loop
            # We need to add it *now* to ensure it's saved even if errors occurred within the loop
            # Find the user message added at the start of the try block
            initial_user_message_index = -1
            for i, msg in enumerate(reversed(current_turn_history)):
                 if msg['role'] == 'user' and msg['content'] == user_input:
                      # This assumes the user_input is unique enough for this turn
                      # A more robust way might involve passing the message index or ID
                      initial_user_message_index = len(current_turn_history) - 1 - i
                      break 
            
            if initial_user_message_index != -1 and not any(msg['role'] == 'user' and msg['content'] == user_input for msg in self.conversation_history):
                self.conversation_history.insert(len(self.conversation_history) - (len(current_turn_history) - 1 - initial_user_message_index), current_turn_history[initial_user_message_index])
            elif initial_user_message_index == -1:
                 logging.warning("Could not reliably find initial user message to add to persistent history.")
                 # As a fallback, add it now if it seems missing
                 if not any(msg['role'] == 'user' and msg['content'] == user_input for msg in self.conversation_history):
                     self.conversation_history.insert(max(0, len(self.conversation_history)-1), {"role": "user", "content": user_input}) 

            return {'response': final_response_text, 'tool_name': last_tool_name}

        except ConnectionError as e:
             logging.error(f"Connection Error in chat: {e}")
             return {'response': f"Error communicating with AI provider: {e}", 'tool_name': None}
        except Exception as e:
            logging.exception("Error during chat processing")
            return {'response': f"An unexpected error occurred: {str(e)}", 'tool_name': None}

    def reset(self):
        """
        Reset the assistant's memory and token usage.
        """
        self.conversation_history = []
        self.total_tokens_used = 0
        # Only print if console is available (for CLI)
        if hasattr(self, 'console') and self.console:
            self.console.print("\n[bold green]🔄 Assistant memory has been reset![/bold green]")

            # Optional: Display welcome and tools for CLI (Also needs indent if uncommented)
            # welcome_text = ...
            # self.console.print(Markdown(welcome_text))
            # self.display_available_tools()


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