# ce3.py
from rich.console import Console
from rich.markdown import Markdown
from rich.live import Live
from rich.spinner import Spinner
from rich.panel import Panel
from typing import List, Dict, Any
import json
import sys
import logging
import context_sanitizer  # Add this import at the top

from config import Config
# Remove tool-related imports
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
    - Orchestrating conversation flow with a given AI provider.
    - Handling user commands such as 'refresh' and 'reset'.
    - Token usage tracking and display.
    - Conversation management without tool execution.

    This class is STATELESS regarding conversation history and total tokens.
    These are passed in and returned by the chat method.
    """

    def __init__(self):
        self.console = Console() # For server-side logging
        self.thinking_enabled = getattr(Config, 'ENABLE_THINKING', False)
        self.system_prompts = SystemPrompts()

    def _display_token_usage(self, usage_this_call: Dict[str, int], cumulative_total_tokens: int):
        """
        Display token usage statistics.
        """
        if not getattr(Config, 'SHOW_TOKEN_USAGE', False):
            return

        input_tokens = usage_this_call.get('input_tokens', 0)
        output_tokens = usage_this_call.get('output_tokens', 0)
        total_tokens_this_call = input_tokens + output_tokens

        # Display current call token usage
        self.console.print(f"[cyan]Tokens this call:[/cyan] {total_tokens_this_call} (in: {input_tokens}, out: {output_tokens})")
        
        # Display cumulative usage
        self.console.print(f"[cyan]Total tokens:[/cyan] {cumulative_total_tokens}")
        
        # Calculate and display percentage of max usage
        max_tokens = getattr(Config, 'MAX_CONVERSATION_TOKENS', 200000)
        percentage = (cumulative_total_tokens / max_tokens) * 100
        self.console.print(f"[cyan]Usage:[/cyan] {percentage:.1f}% of {max_tokens:,}")

    def chat(self, 
             user_input: any, 
             provider: BaseProvider, 
             conversation_history: list, 
             total_tokens_used: int, 
             mode: str, 
             request_id: str # Added for consistent logging
            ) -> Dict[str, Any]:
        """
        Process a chat interaction with the given provider.
        
        Args:
            user_input: The user's input (string or dict with text/image)
            provider: The AI provider instance to use
            conversation_history: List of previous messages
            total_tokens_used: Running total of tokens used
            mode: The conversation mode
            request_id: Unique identifier for this request
            
        Returns:
            Dict containing:
                - assistant_response: The AI's response text
                - updated_history: Updated conversation history
                - total_tokens: Updated token count
                - provider_used: Name of the provider used
                - model_used: Name of the specific model used
                - usage: Detailed usage information
        """
        try:
            # Handle special commands
            if isinstance(user_input, str):
                if user_input.lower() == '/reset':
                    return {
                        'assistant_response': 'Conversation history cleared.',
                        'updated_history': [],
                        'total_tokens': 0,
                        'provider_used': provider.name,
                        'model_used': 'unknown',
                        'usage': {'input_tokens': 0, 'output_tokens': 0, 'runtime': 0}
                    }
                elif user_input.lower() == '/quit':
                    return {
                        'assistant_response': 'Goodbye!',
                        'updated_history': conversation_history,
                        'total_tokens': total_tokens_used,
                        'provider_used': provider.name,
                        'model_used': 'unknown',
                        'usage': {'input_tokens': 0, 'output_tokens': 0, 'runtime': 0}
                    }

            # Process user input
            if isinstance(user_input, dict):
                # Handle structured input (e.g., with images)
                processed_input = user_input
            else:
                # Simple text input
                processed_input = {"type": "text", "text": str(user_input)}

            # Add mode prompt if specified
            mode_prompt = MODE_PROMPTS.get(mode, "")
            if mode_prompt and mode != "normal":
                if isinstance(processed_input, dict) and processed_input.get("type") == "text":
                    processed_input["text"] = f"{mode_prompt}\n\n{processed_input['text']}"

            # Create user message
            user_message = {
                "role": "user", 
                "content": [processed_input] if isinstance(processed_input, dict) else processed_input
            }

            # Add to conversation history
            updated_history = conversation_history + [user_message]

            # Sanitize history for the target provider
            sanitized_history = context_sanitizer.sanitize_history(updated_history, provider.name)

            # Get system prompt
            system_prompt = self.system_prompts.get_system_prompt(mode)
            
            # Prepare messages with system prompt
            messages = [{"role": "system", "content": system_prompt}] + sanitized_history

            # Make API call to provider (no tools passed)
            response = provider.chat(messages, [], Config)

            # Extract response content
            if isinstance(response.get('content'), list):
                # Handle structured response
                text_parts = []
                for part in response['content']:
                    if isinstance(part, dict):
                        if part.get('type') == 'text':
                            text_parts.append(part.get('text', ''))
                        else:
                            text_parts.append(str(part))
                    else:
                        text_parts.append(str(part))
                assistant_response = '\n'.join(text_parts)
            else:
                assistant_response = str(response.get('content', ''))

            # Add assistant response to history
            assistant_message = {
                "role": "assistant",
                "content": assistant_response
            }
            final_history = updated_history + [assistant_message]

            # Update token usage
            usage_this_call = response.get('usage', {})
            input_tokens = usage_this_call.get('input_tokens', 0)
            output_tokens = usage_this_call.get('output_tokens', 0)
            tokens_this_call = input_tokens + output_tokens
            updated_total_tokens = total_tokens_used + tokens_this_call

            # Display token usage if enabled
            self._display_token_usage(usage_this_call, updated_total_tokens)

            return {
                'assistant_response': assistant_response,
                'updated_history': final_history,
                'total_tokens': updated_total_tokens,
                'provider_used': provider.name,
                'model_used': response.get('model_used', 'unknown'),
                'usage': usage_this_call
            }

        except Exception as e:
            logging.exception(f"Error in chat method for request {request_id}")
            return {
                'assistant_response': f'Error: {str(e)}',
                'updated_history': conversation_history,
                'total_tokens': total_tokens_used,
                'provider_used': provider.name if provider else 'unknown',
                'model_used': 'unknown',
                'usage': {'input_tokens': 0, 'output_tokens': 0, 'runtime': 0}
            }

    def reset(self):
        """
        Reset method - now simplified since no tools to reload.
        """
        self.console.print("[green]Assistant reset complete.[/green]")

def main():
    """
    Main CLI interface - simplified without tool functionality.
    """
    assistant = Assistant()
    
    # Style for prompt
    style = Style.from_dict({
        'prompt': '#00aa00 bold',
    })
    
    print("Fusion AI Assistant (Tool-free mode)")
    print("Commands: /reset, /quit")
    print("---")
    
    conversation_history = []
    total_tokens = 0
    
    while True:
        try:
            user_input = prompt('You: ', style=style)
            
            if user_input.lower() in ['/quit', 'quit', 'exit']:
                print("Goodbye!")
                break
                
            # For CLI mode, we'd need to specify a provider
            # This is mainly for the web interface now
            print("CLI mode requires provider selection - use web interface")
            
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break

if __name__ == "__main__":
    main()