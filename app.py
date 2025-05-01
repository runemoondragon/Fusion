from flask import Flask, render_template, request, jsonify, url_for, session
from ce3 import Assistant
import os
from werkzeug.utils import secure_filename
import base64
from config import Config
# Import the factory
from providers.provider_factory import ProviderFactory
import logging # Add logging

app = Flask(__name__, static_folder='static')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
# Add a secret key for session management
# You should set FLASK_SECRET_KEY in your .env file for production
app.secret_key = os.getenv('FLASK_SECRET_KEY', os.urandom(24))

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize the assistant (now stateless regarding provider client)
assistant = Assistant()

@app.route('/')
def home():
    # Pass the list of available providers to the template
    available_providers = list(ProviderFactory._providers.keys())
    selected_provider = session.get('provider', 'claude') # Default to claude
    return render_template('index.html', 
                           providers=available_providers, 
                           selected_provider=selected_provider)

@app.route('/set_provider', methods=['POST'])
def set_provider():
    data = request.json
    provider_name = data.get('provider')
    available_providers = list(ProviderFactory._providers.keys())
    if provider_name and provider_name in available_providers:
        session['provider'] = provider_name
        logging.info(f"Set provider to: {provider_name}")
        return jsonify({'status': 'success', 'provider': provider_name})
    else:
        logging.warning(f"Invalid provider requested: {provider_name}")
        return jsonify({'status': 'error', 'message': 'Invalid provider'}), 400

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    message = data.get('message', '')
    image_data = data.get('image')  # Get the base64 image data
    
    # Determine the provider to use
    provider_name = session.get('provider', 'claude') # Default to claude
    logging.info(f"Using provider: {provider_name}")

    try:
        # Create the provider instance using the factory
        provider = ProviderFactory.create_provider(provider_name)
    except ValueError as e:
         logging.error(f"Failed to create provider '{provider_name}': {e}")
         return jsonify({
             'response': f"Error: Could not initialize AI provider '{provider_name}'. Please select a valid provider.",
             'thinking': False,
             'tool_name': None,
             'token_usage': {'total_tokens': assistant.total_tokens_used, 'max_tokens': Config.MAX_CONVERSATION_TOKENS}
         }), 200 # Return 200 for frontend handling
    except Exception as e:
         logging.exception(f"Unexpected error creating provider '{provider_name}'")
         return jsonify({
             'response': f"Error: An unexpected error occurred while setting up the AI provider.",
             'thinking': False,
             'tool_name': None,
             'token_usage': {'total_tokens': assistant.total_tokens_used, 'max_tokens': Config.MAX_CONVERSATION_TOKENS}
         }), 200

    # Prepare the message content
    if image_data:
        message_content = [
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/jpeg", # TODO: Detect media_type from image_data if possible
                    "data": image_data.split(',')[1] if ',' in image_data else image_data
                }
            }
        ]
        if message.strip():
            message_content.append({"type": "text", "text": message})
    else:
        message_content = message
    
    try:
        # Call the refactored assistant.chat with the selected provider
        result = assistant.chat(message_content, provider)
        
        response_text = result.get('response', "[No response text received]")
        tool_name = result.get('tool_name') # Get tool name from the result dict

        # Get current token usage from assistant
        token_usage = {
            'total_tokens': assistant.total_tokens_used,
            'max_tokens': Config.MAX_CONVERSATION_TOKENS
        }
        
        return jsonify({
            'response': response_text,
            'thinking': False, # Thinking state is handled within assistant now
            'tool_name': tool_name,
            'token_usage': token_usage
        })
        
    except Exception as e:
        logging.exception("Error during assistant.chat call") # Log the full traceback
        return jsonify({
            'response': f"Error processing chat: {str(e)}",
            'thinking': False,
            'tool_name': None,
            'token_usage': {'total_tokens': assistant.total_tokens_used, 'max_tokens': Config.MAX_CONVERSATION_TOKENS}
        }), 200 # Return 200 for frontend handling

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Get the actual media type
        media_type = file.content_type or 'image/jpeg'  # Default to jpeg if not detected
        
        # Convert image to base64
        with open(filepath, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        
        # Clean up the file
        os.remove(filepath)
        
        return jsonify({
            'success': True,
            'image_data': encoded_string,
            'media_type': media_type
        })
    
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/reset', methods=['POST'])
def reset():
    # Reset the assistant's conversation history
    assistant.reset()
    # Optional: Reset the provider selection in session? 
    # session['provider'] = 'claude' # Uncomment to reset provider on reset
    logging.info("Conversation reset.")
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    # Use debug=True for development, False for production
    # Consider using a proper WSGI server like gunicorn or waitress for production
    app.run(debug=True, host='0.0.0.0', port=5000) # Run on 0.0.0.0 to be accessible on network 