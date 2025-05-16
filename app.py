from flask import Flask, render_template, request, jsonify, url_for, session
from ce3 import Assistant
import os
from werkzeug.utils import secure_filename
import base64
from config import Config
# Import the factory
from providers.provider_factory import ProviderFactory
import logging # Add logging
# Import the NeuroSwitch classifier function and default provider
from neuroswitch_classifier import get_neuroswitch_provider, DEFAULT_PROVIDER

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

# Define the static list of providers + NeuroSwitch
# Define the constant here, where it's used
NEUROSWITCH_PROVIDER_NAME = "NeuroSwitch"
ALL_PROVIDERS_WITH_NEUROSWITCH = [NEUROSWITCH_PROVIDER_NAME] + list(ProviderFactory._providers.keys())

@app.route('/')
def home():
    # Pass the combined list of providers to the template
    # available_providers = list(ProviderFactory._providers.keys()) # Old way
    available_providers = ALL_PROVIDERS_WITH_NEUROSWITCH # New list including NeuroSwitch
    # Default to NeuroSwitch if nothing is selected? Or keep claude? Let's keep claude for now.
    selected_provider = session.get('provider', 'claude') 
    return render_template('index.html', 
                           providers=available_providers, 
                           selected_provider=selected_provider)

@app.route('/set_provider', methods=['POST'])
def set_provider():
    data = request.json
    provider_name = data.get('provider')
    # available_providers = list(ProviderFactory._providers.keys()) # Old check
    available_providers = ALL_PROVIDERS_WITH_NEUROSWITCH # Check against the full list
    if provider_name and provider_name in available_providers:
        session['provider'] = provider_name
        logging.info(f"Set provider selection to: {provider_name}")
        return jsonify({'status': 'success', 'provider': provider_name})
    else:
        logging.warning(f"Invalid provider requested: {provider_name}")
        return jsonify({'status': 'error', 'message': 'Invalid provider'}), 400

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    message = data.get('message', '')
    image_data = data.get('image')
    mode = data.get('mode')
    # --- Get model preference from request body first, then session ---
    requested_model = data.get('model')  # Get model directly from request
    session_provider = session.get('provider')
    
    # Check if this is an API call by looking at headers
    is_api_call = request.headers.get('Content-Type') == 'application/json' and \
                 request.headers.get('Accept') == 'application/json'
    
    # Determine provider selection logic
    if is_api_call:
        # For API calls:
        # - If model is null, use NeuroSwitch
        # - If model is set, use that provider
        provider_selection = NEUROSWITCH_PROVIDER_NAME if requested_model is None else requested_model
    else:
        # For internal chat, maintain existing behavior
        provider_selection = requested_model or session_provider or DEFAULT_PROVIDER

    logging.info(f"Request type: {'API' if is_api_call else 'Browser'}, Model/Provider requested: {requested_model} (from request), {session_provider} (from session) -> Using: {provider_selection}, Mode: {mode}")

    actual_provider_name = DEFAULT_PROVIDER
    neuroswitch_active = False # Default to inactive
    fallback_reason = None     # Default to no reason
    text_input_for_classification = ""

    # Prepare message content and extract text ...
    if image_data:
        message_content = [
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/jpeg", # TODO: Detect media_type
                    "data": image_data.split(',')[1] if ',' in image_data else image_data
                }
            }
        ]
        if message.strip():
            text_part = {"type": "text", "text": message}
            message_content.append(text_part)
            text_input_for_classification = message # Use text part for classification
        else:
             # If only image, maybe classify based on a standard prompt or default?
             # For now, if only image, let's default or maybe force Gemini?
             # Let's stick to default if NeuroSwitch is chosen with only image for now.
             text_input_for_classification = "Image uploaded" # Placeholder text?
    else:
        message_content = message
        text_input_for_classification = message # Use the whole message if no image

    # --- NeuroSwitch Logic ---    
    # Add debugging logs here
    logging.info(f"DEBUG: Value retrieved from session['provider']: '{provider_selection}'")
    logging.info(f"DEBUG: Value of NEUROSWITCH_PROVIDER_NAME constant: '{NEUROSWITCH_PROVIDER_NAME}'")
    logging.info(f"DEBUG: Result of comparison (provider_selection == NEUROSWITCH_PROVIDER_NAME): {provider_selection == NEUROSWITCH_PROVIDER_NAME}")
    
    if provider_selection == NEUROSWITCH_PROVIDER_NAME:
        logging.info(f"NeuroSwitch activated. Classifying input...")
        # Call the classifier function - now returns a dict
        neuroswitch_status = get_neuroswitch_provider(text_input_for_classification)
        actual_provider_name = neuroswitch_status["provider"]
        neuroswitch_active = neuroswitch_status["neuroswitch_active"]
        fallback_reason = neuroswitch_status["fallback_reason"]
        logging.info(f"NeuroSwitch result: Provider='{actual_provider_name}', Active={neuroswitch_active}, Reason='{fallback_reason}'")
    else:
        # Use the provider selected manually by the user
        actual_provider_name = provider_selection
        neuroswitch_active = False # Not active if manually selected
        logging.info(f"Using manually selected provider: {actual_provider_name}")
    # --- End NeuroSwitch Logic ---

    try:
        # Create provider instance using the determined name
        provider = ProviderFactory.create_provider(actual_provider_name)
    except ValueError as e:
         logging.error(f"Failed to create provider '{actual_provider_name}': {e}")
         return jsonify({
             'response': f"Error: Could not initialize AI provider '{actual_provider_name}'. Please select a valid provider.",
             'thinking': False,
             'tool_name': None,
             'provider_used': actual_provider_name,
             'neuroswitch_active': neuroswitch_active,
             'fallback_reason': fallback_reason,
             'token_usage': {'total_tokens': assistant.total_tokens_used, 'max_tokens': Config.MAX_CONVERSATION_TOKENS}
         }), 200
    except Exception as e:
         logging.exception(f"Unexpected error creating provider '{actual_provider_name}'")
         return jsonify({
             'response': f"Error: An unexpected error occurred while setting up the AI provider.",
             'thinking': False,
             'tool_name': None,
             'provider_used': actual_provider_name,
             'neuroswitch_active': neuroswitch_active,
             'fallback_reason': fallback_reason,
             'token_usage': {'total_tokens': assistant.total_tokens_used, 'max_tokens': Config.MAX_CONVERSATION_TOKENS}
         }), 200
    
    try:
        # Call assistant.chat, PASSING the mode
        result = assistant.chat(message_content, provider, mode=mode)
        response_text = result.get('response', "[No response text received]")
        tool_name = result.get('tool_name')
        usage = result.get('usage', {})
        token_usage = {
            'input_tokens': usage.get('input_tokens'),
            'output_tokens': usage.get('output_tokens'),
            'total_tokens': assistant.total_tokens_used,
            'max_tokens': Config.MAX_CONVERSATION_TOKENS,
            'runtime': usage.get('runtime')
        }
        
        # Return success response with status fields
        return jsonify({
            'response': response_text,
            'thinking': False,
            'tool_name': tool_name,
            'provider_used': actual_provider_name,
            'neuroswitch_active': neuroswitch_active,
            'fallback_reason': fallback_reason,
            'token_usage': token_usage
        })
        
    except Exception as e:
        logging.exception("Error during assistant.chat call") # Log the full traceback
        return jsonify({
            'response': f"Error processing chat: {str(e)}",
            'thinking': False,
            'tool_name': None,
            'provider_used': actual_provider_name,
            'neuroswitch_active': neuroswitch_active,
            'fallback_reason': fallback_reason,
            'token_usage': {'total_tokens': assistant.total_tokens_used, 'max_tokens': Config.MAX_CONVERSATION_TOKENS}
        }), 200

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