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
import uuid # For generating unique IDs

app = Flask(__name__, static_folder='static')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
# Add a secret key for session management
# You should set FLASK_SECRET_KEY in your .env file for production
app.secret_key = os.getenv('FLASK_SECRET_KEY', os.urandom(24))

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Assistant is instantiated once, its methods will operate on passed-in history & tokens
assistant = Assistant()

# Define the static list of providers + NeuroSwitch
# Define the constant here, where it's used
NEUROSWITCH_PROVIDER_NAME = "NeuroSwitch"
ALL_PROVIDERS_WITH_NEUROSWITCH = [NEUROSWITCH_PROVIDER_NAME] + list(ProviderFactory._providers.keys())

# --- Provider Aliases and Normalization ---
# Direct provider names (lowercase) that the factory supports
DIRECT_PROVIDER_KEYS = {key.lower() for key in ProviderFactory._providers.keys()}

# Aliases that map to a direct provider (e.g., common model names or shorthand)
# This can be expanded as needed.
DIRECT_PROVIDER_ALIASES = {
    "gpt-4": "openai",
    "gpt-3.5-turbo": "openai",
    "gpt-4-turbo": "openai",
    "gpt-4o": "openai",
    "claude-3-opus": "claude",
    "claude-3-sonnet": "claude",
    "claude-3-haiku": "claude",
    "gemini-1.5-pro": "gemini",
    "gemini-1.0-pro": "gemini",
    # Add other common model name aliases here
}

# Aliases that explicitly mean to use the NeuroSwitch router
NEUROSWITCH_ROUTER_ALIASES = {
    "neuroswitch", # Canonical name
    "auto",
    "router",
    "smart",
    "intelligentrouter"
}
# --- End Provider Aliases ---

# Server-side storage for API client session data
# Key: Client-provided session ID (from X-Session-ID or Authorization header)
# Value: {'conversation_history': [], 'total_tokens_used': 0}
api_client_session_store = {}

def get_request_identifier_and_type() -> tuple[str, str]:
    """
    Determines the session identifier and type ('api' or 'flask_session').
    For API calls, expects 'X-Session-ID' or 'Authorization: Bearer <token>'.
    """
    session_id_header = request.headers.get('X-Session-ID')
    auth_header = request.headers.get('Authorization')

    if session_id_header:
        return session_id_header, "api"
    elif auth_header and auth_header.startswith('Bearer '):
        return auth_header.split(' ')[1], "api" # Use the token as identifier
    else:
        # Fallback to Flask session for direct browser interaction (e.g., testing UI)
        if '_id' not in session: # Flask's session cookie usually manages its own ID
            session['_id'] = str(uuid.uuid4()) # Ensure session is initiated
        # Using session.sid if available and configured for server-side sessions,
        # otherwise, Flask's session object itself is the context.
        # For simplicity here, we'll generate a stable ID if not present.
        if 'neuroswitch_flask_session_id' not in session:
            session['neuroswitch_flask_session_id'] = str(uuid.uuid4())
        return session['neuroswitch_flask_session_id'], "flask_session"

def get_session_data(identifier: str, session_type: str) -> dict:
    """
    Retrieves conversation history and token count for the given identifier and type.
    Initializes if not present.
    """
    if session_type == "api":
        if identifier not in api_client_session_store:
            api_client_session_store[identifier] = {'conversation_history': [], 'total_tokens_used': 0}
            logging.info(f"Initialized new history for API client ID: {identifier}")
        return api_client_session_store[identifier]
    else: # flask_session
        if 'conversation_history' not in session:
            session['conversation_history'] = []
            session['total_tokens_used'] = 0
            logging.info(f"Initialized new history for Flask session ID: {identifier}")
        return {'conversation_history': session['conversation_history'], 'total_tokens_used': session['total_tokens_used']}

def save_session_data(identifier: str, session_type: str, history: list, tokens: int):
    """
    Saves conversation history and token count for the given identifier and type.
    """
    if session_type == "api":
        if identifier in api_client_session_store: # Should always be true if get_session_data was called
             api_client_session_store[identifier]['conversation_history'] = history
             api_client_session_store[identifier]['total_tokens_used'] = tokens
        else: # Should not happen if logic is correct
            logging.error(f"Attempted to save session data for uninitialized API client ID: {identifier}")
            api_client_session_store[identifier] = {'conversation_history': history, 'total_tokens_used': tokens}
    else: # flask_session
        session['conversation_history'] = history
        session['total_tokens_used'] = tokens
        session.modified = True # Important for Flask to save session changes

@app.route('/')
def home():
    req_id, req_type = get_request_identifier_and_type() # Ensure session is created if flask_session
    # Pass the combined list of providers to the template
    # available_providers = list(ProviderFactory._providers.keys()) # Old way
    available_providers = ALL_PROVIDERS_WITH_NEUROSWITCH # New list including NeuroSwitch
    # Default to NeuroSwitch if nothing is selected? Or keep claude? Let's keep claude for now.
    selected_provider = session.get('provider', 'claude') 
    logging.info(f"Home route accessed by ID: {req_id} (Type: {req_type})")
    return render_template('index.html', 
                           providers=available_providers, 
                           selected_provider=selected_provider)

@app.route('/set_provider', methods=['POST'])
def set_provider():
    req_id, req_type = get_request_identifier_and_type()
    data = request.json
    provider_name = data.get('provider')
    # available_providers = list(ProviderFactory._providers.keys()) # Old check
    available_providers = ALL_PROVIDERS_WITH_NEUROSWITCH # Check against the full list
    if provider_name and provider_name in available_providers:
        session['provider'] = provider_name
        logging.info(f"Set provider selection to: {provider_name} for Flask session context (ID: {req_id})")
        return jsonify({'status': 'success', 'provider': provider_name})
    else:
        logging.warning(f"Invalid provider requested: {provider_name} by ID: {req_id}")
        return jsonify({'status': 'error', 'message': 'Invalid provider'}), 400

@app.route('/chat', methods=['POST'])
def chat():
    req_id, req_type = get_request_identifier_and_type()
    session_data = get_session_data(req_id, req_type)
    current_conversation_history = session_data['conversation_history']
    current_total_tokens_used = session_data['total_tokens_used']

    data = request.json
    message = data.get('message', '')
    image_data = data.get('image')
    mode = data.get('mode')
    
    # --- Refined Provider Selection Logic for API and Flask UI ---
    provider_to_use_for_routing_or_direct_call = None # This will be determined first
    is_direct_provider_request = False # Flag to bypass NeuroSwitch classifier

    if req_type == "api":
        # For API calls, check 'provider' then 'model' fields from payload
        provider_from_payload = data.get('provider')
        model_from_payload = data.get('model') # 'model' is often used for specific LLM names
        
        # Normalize inputs
        normalized_provider_payload = str(provider_from_payload).lower() if provider_from_payload else None
        normalized_model_payload = str(model_from_payload).lower() if model_from_payload else None

        logging.info(f"API Chat ID: {req_id}. Payload provider: '{provider_from_payload}', model: '{model_from_payload}'")

        # Priority 1: 'provider' field in payload
        if normalized_provider_payload:
            if normalized_provider_payload in DIRECT_PROVIDER_KEYS:
                provider_to_use_for_routing_or_direct_call = normalized_provider_payload
                is_direct_provider_request = True
            elif DIRECT_PROVIDER_ALIASES.get(normalized_provider_payload) in DIRECT_PROVIDER_KEYS:
                provider_to_use_for_routing_or_direct_call = DIRECT_PROVIDER_ALIASES[normalized_provider_payload]
                is_direct_provider_request = True
            elif normalized_provider_payload in NEUROSWITCH_ROUTER_ALIASES:
                provider_to_use_for_routing_or_direct_call = NEUROSWITCH_PROVIDER_NAME
                is_direct_provider_request = False # Explicitly use router
            # else: unrecognized provider string, will fall through to model or default

        # Priority 2: 'model' field in payload (if provider field didn't specify a direct provider)
        if not is_direct_provider_request and normalized_model_payload:
            if normalized_model_payload in DIRECT_PROVIDER_KEYS: # e.g. model: "openai"
                provider_to_use_for_routing_or_direct_call = normalized_model_payload
                is_direct_provider_request = True
            elif DIRECT_PROVIDER_ALIASES.get(normalized_model_payload) in DIRECT_PROVIDER_KEYS: # e.g. model: "gpt-4o"
                provider_to_use_for_routing_or_direct_call = DIRECT_PROVIDER_ALIASES[normalized_model_payload]
                is_direct_provider_request = True
            elif normalized_model_payload in NEUROSWITCH_ROUTER_ALIASES: # e.g. model: "neuroswitch"
                provider_to_use_for_routing_or_direct_call = NEUROSWITCH_PROVIDER_NAME
                is_direct_provider_request = False # Explicitly use router
            # else: unrecognized model string

        # Default for API if nothing specific was matched to a direct provider or router
        if provider_to_use_for_routing_or_direct_call is None:
            provider_to_use_for_routing_or_direct_call = NEUROSWITCH_PROVIDER_NAME # Default to NeuroSwitch routing
            is_direct_provider_request = False
            logging.info(f"API Chat ID: {req_id}. No direct provider match from payload, defaulting to NeuroSwitch router.")

    else: # req_type == "flask_session" (Internal UI / Direct Browser)
        # For Flask sessions, use the provider set in the session (e.g., by the UI dropdown)
        provider_from_session = session.get('provider', DEFAULT_PROVIDER) # DEFAULT_PROVIDER could be "NeuroSwitch" or a direct one
        normalized_session_provider = provider_from_session.lower()
        
        logging.info(f"Flask Session Chat ID: {req_id}. Provider from session: '{provider_from_session}'")

        if normalized_session_provider in DIRECT_PROVIDER_KEYS:
            provider_to_use_for_routing_or_direct_call = normalized_session_provider
            is_direct_provider_request = True
        elif DIRECT_PROVIDER_ALIASES.get(normalized_session_provider) in DIRECT_PROVIDER_KEYS:
            provider_to_use_for_routing_or_direct_call = DIRECT_PROVIDER_ALIASES[normalized_session_provider]
            is_direct_provider_request = True
        elif normalized_session_provider in NEUROSWITCH_ROUTER_ALIASES:
            provider_to_use_for_routing_or_direct_call = NEUROSWITCH_PROVIDER_NAME
            is_direct_provider_request = False
        else: # Unrecognized or default from session might imply NeuroSwitch routing
            provider_to_use_for_routing_or_direct_call = NEUROSWITCH_PROVIDER_NAME
            is_direct_provider_request = False
            logging.warning(f"Flask Session Chat ID: {req_id}. Provider '{provider_from_session}' from session not recognized as direct, defaulting to NeuroSwitch router.")

    logging.info(f"Chat ID: {req_id}. Determined Provider for Routing/Direct Call: '{provider_to_use_for_routing_or_direct_call}', Is Direct Request: {is_direct_provider_request}")
    # --- End Refined Provider Selection Logic ---

    actual_provider_name_to_instantiate = provider_to_use_for_routing_or_direct_call # Initial value before NeuroSwitch classifier potentially changes it
    neuroswitch_active = False
    fallback_reason = None
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
    # This block now only runs if is_direct_provider_request is False AND provider_to_use_for_routing_or_direct_call is NEUROSWITCH_PROVIDER_NAME
    
    if not is_direct_provider_request and provider_to_use_for_routing_or_direct_call == NEUROSWITCH_PROVIDER_NAME:
        logging.info(f"NeuroSwitch classifier activated for ID: {req_id}. Classifying input: '{text_input_for_classification[:100]}...' ")
        neuroswitch_status = get_neuroswitch_provider(text_input_for_classification)
        actual_provider_name_to_instantiate = neuroswitch_status["provider"] # Classifier determines the final provider
        neuroswitch_active = neuroswitch_status["neuroswitch_active"] # Mark that NeuroSwitch *logic* was active
        fallback_reason = neuroswitch_status["fallback_reason"]
        logging.info(f"NeuroSwitch classifier for ID: {req_id} result: Provider='{actual_provider_name_to_instantiate}', Active(Logic)={neuroswitch_active}, Reason='{fallback_reason}'")
    elif is_direct_provider_request:
        # neuroswitch_active remains False as we are bypassing the classifier
        actual_provider_name_to_instantiate = provider_to_use_for_routing_or_direct_call # Already set
        logging.info(f"Using DDIRECTLY specified provider for ID: {req_id}: {actual_provider_name_to_instantiate}. NeuroSwitch classifier bypassed.")
    else:
        # This case implies provider_to_use_for_routing_or_direct_call was a direct provider name but somehow is_direct_provider_request was false.
        # Should ideally not be reached if logic above is correct. Defaulting to safety.
        logging.warning(f"Chat ID: {req_id}. Inconsistent state in provider selection. Defaulting to use determined provider '{provider_to_use_for_routing_or_direct_call}' directly. NeuroSwitch classifier bypassed.")
        actual_provider_name_to_instantiate = provider_to_use_for_routing_or_direct_call
        neuroswitch_active = False

    # --- End NeuroSwitch Logic ---

    try:
        # Create provider instance using the determined name
        provider = ProviderFactory.create_provider(actual_provider_name_to_instantiate)
    except ValueError as e:
         logging.error(f"Failed to create provider instance '{actual_provider_name_to_instantiate}' for ID: {req_id}: {e}")
         return jsonify({
             'response': f"Error: Could not initialize AI provider '{actual_provider_name_to_instantiate}'. Please select a valid provider or check configuration.",
             'provider_used': actual_provider_name_to_instantiate,
             'neuroswitch_active': neuroswitch_active,
             'fallback_reason': fallback_reason,
             'token_usage': {'total_tokens': current_total_tokens_used, 'max_tokens': Config.MAX_CONVERSATION_TOKENS}
         }), 400 # Client error for invalid provider
    except Exception as e:
         logging.exception(f"Unexpected error creating provider '{actual_provider_name_to_instantiate}' for ID: {req_id}")
         return jsonify({
             'response': f"Error: An unexpected error occurred while setting up the AI provider.",
             'provider_used': actual_provider_name_to_instantiate,
             'neuroswitch_active': neuroswitch_active,
             'fallback_reason': fallback_reason,
             'token_usage': {'total_tokens': current_total_tokens_used, 'max_tokens': Config.MAX_CONVERSATION_TOKENS}
         }), 500 # Server error
    
    try:
        # Call assistant.chat, PASSING the mode
        result_data = assistant.chat(
            user_input=message_content,
            provider=provider,
            conversation_history=current_conversation_history, # Pass current history for this session
            total_tokens_used=current_total_tokens_used,       # Pass current tokens for this session
            mode=mode,
            # Pass request_id for logging within assistant if needed, though assistant should be mostly agnostic
            # request_id=req_id 
        )

        # Save the updated history and tokens back to the correct session store
        save_session_data(req_id, req_type, result_data['updated_conversation_history'], result_data['updated_total_tokens_used'])
        logging.info(f"Chat successful for ID: {req_id}. New history length: {len(result_data['updated_conversation_history'])}. New Tokens: {result_data['updated_total_tokens_used']}")

        response_text = result_data.get('response', "[No response text received]")
        tool_name = result_data.get('tool_name')
        usage_from_assistant = result_data.get('usage', {}) # This is per-call usage
        
        token_usage_response = {
            'input_tokens': usage_from_assistant.get('input_tokens'),
            'output_tokens': usage_from_assistant.get('output_tokens'),
            'total_tokens': result_data['updated_total_tokens_used'], # This is the cumulative for the session
            'max_tokens': Config.MAX_CONVERSATION_TOKENS,
            'runtime': usage_from_assistant.get('runtime')
        }
        
        return jsonify({
            'response': response_text,
            'tool_name': tool_name,
            'provider_used': actual_provider_name_to_instantiate, # Reflect the actual provider instance used
            'neuroswitch_active': neuroswitch_active, # This now reflects if NeuroSwitch *classifier logic* ran
            'fallback_reason': fallback_reason,
            'token_usage': token_usage_response
        })
        
    except Exception as e:
        logging.exception(f"Error during assistant.chat call for ID: {req_id}")
        return jsonify({
            'response': f"Error processing chat: {str(e)}",
            'provider_used': actual_provider_name_to_instantiate,
            'neuroswitch_active': neuroswitch_active,
            'fallback_reason': fallback_reason,
            'token_usage': {'total_tokens': current_total_tokens_used, 'max_tokens': Config.MAX_CONVERSATION_TOKENS}
        }), 500 # Server error during chat processing

@app.route('/upload', methods=['POST'])
def upload_file():
    req_id, _ = get_request_identifier_and_type()
    logging.info(f"Upload attempt by ID: {req_id}")
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
        filename = secure_filename(file.filename)
        # Note: Storing uploads should be carefully considered for production (e.g., object storage)
        # For NeuroSwitch, this seems like a helper for image modality, not persistent storage.
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
    req_id, req_type = get_request_identifier_and_type()
    
    if req_type == "api":
        if req_id in api_client_session_store:
            api_client_session_store[req_id]['conversation_history'] = []
            api_client_session_store[req_id]['total_tokens_used'] = 0
            logging.info(f"Conversation reset for API client ID: {req_id}")
            status_message = f"Conversation reset for API client ID: {req_id}"
        else:
            logging.info(f"No active session to reset for API client ID: {req_id}")
            status_message = f"No active session to reset for API client ID: {req_id}"
    else: # flask_session
        session['conversation_history'] = []
        session['total_tokens_used'] = 0
        session.modified = True
        logging.info(f"Conversation reset for Flask session ID: {req_id}")
        status_message = f"Conversation reset for Flask session ID: {req_id}"
        
    return jsonify({'status': 'success', 'message': status_message})

if __name__ == '__main__':
    # Use debug=True for development, False for production
    # Consider using a proper WSGI server like gunicorn or waitress for production
    app.run(debug=True, host='0.0.0.0', port=5000) # Run on 0.0.0.0 to be accessible on network 