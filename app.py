from flask import Flask, render_template, request, jsonify, url_for, session, send_from_directory, Response
from ce3 import Assistant
import os
from werkzeug.utils import secure_filename
import base64
from config import Config
from dotenv import load_dotenv
load_dotenv()
# Import the factory
from providers.provider_factory import ProviderFactory
import logging # Add logging
# Import the NeuroSwitch classifier function and default provider
from neuroswitch_classifier import get_neuroswitch_provider, DEFAULT_PROVIDER
import uuid # For generating unique IDs
import json # Added for json.dumps in reset route
from functools import wraps # Added wraps

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

# --- Basic Auth Definition ---
EXPECTED_USERNAME = os.getenv("FLASK_BASIC_AUTH_USERNAME")
EXPECTED_PASSWORD = os.getenv("FLASK_BASIC_AUTH_PASSWORD")

def check_auth(username, password):
    """This function is called to check if a username / password combination is valid."""
    # Ensure that expected values are set, otherwise auth will always fail silently or pass if both are None and provided are None.
    if not EXPECTED_USERNAME or not EXPECTED_PASSWORD:
        logging.warning("Basic Auth username or password not set in environment. Auth will fail.")
        return False
    return username == EXPECTED_USERNAME and password == EXPECTED_PASSWORD

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_basic_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated
# --- End Basic Auth Definition ---

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
        # Use the token itself as the identifier for API calls
        return auth_header.split('Bearer ')[1].strip(), "api"
    else:
        # Fallback to Flask session for direct browser interaction
        if '_id' not in session: # Flask's session cookie usually manages its own ID
            session['_id'] = str(uuid.uuid4()) # Ensure Flask session is initiated
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
@requires_basic_auth # Apply the decorator
def home():
    req_id, req_type = get_request_identifier_and_type()
    available_providers = ALL_PROVIDERS_WITH_NEUROSWITCH
    selected_provider = session.get('provider', DEFAULT_PROVIDER) # Use DEFAULT_PROVIDER
    logging.info(f"Home route accessed by ID: {req_id} (Type: {req_type})") # Keep this as INFO
    return render_template('index.html', 
                           providers=available_providers, 
                           selected_provider=selected_provider)

@app.route('/set_provider', methods=['POST'])
def set_provider():
    req_id, req_type = get_request_identifier_and_type()
    data = request.json
    provider_name = data.get('provider')
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
    
    # Extract provider-specific API keys from headers
    openai_user_key = request.headers.get("X-OpenAI-API-Key")
    claude_user_key = request.headers.get("X-Claude-API-Key")
    gemini_user_key = request.headers.get("X-Gemini-API-Key")

    logging.critical(f"----- NEW /chat REQUEST -----")
    logging.critical(f"Incoming req_id: {req_id}, req_type: {req_type}")

    session_data = get_session_data(req_id, req_type)
    server_stored_history = session_data['conversation_history']
    current_total_tokens_used = session_data['total_tokens_used']

    data = request.json
    logging.debug(f"API Chat ID: {req_id}. Full request JSON data: {data}")

    # --- Get client-provided history if available ---
    client_provided_history = data.get('history')
    history_to_use = server_stored_history # Default to server-side history
    history_source_for_logging = "server_store"

    if client_provided_history is not None and isinstance(client_provided_history, list):
        logging.info(f"Chat ID: {req_id}. Client provided a history with {len(client_provided_history)} messages. PRIORITIZING client history.")
        history_to_use = client_provided_history
        history_source_for_logging = "client_payload"
    else:
        logging.info(f"Chat ID: {req_id}. No valid client-provided history found, or not provided. Using history from {history_source_for_logging} with {len(history_to_use)} messages.")

    message = data.get('message')
    image_data = data.get('image_data') 
    mode = data.get('mode')
    client_specified_model = data.get('model')

    # --- Refined Provider Selection Logic for API and Flask UI ---
    is_direct_provider_request = False 
    provider_to_use_for_routing_or_direct_call = None

    if req_type == "api":
        model_from_payload = data.get('requested_provider')
        normalized_model_payload = str(model_from_payload).lower() if model_from_payload else None

        logging.info(f"API Chat ID: {req_id}. Provider determination based on JSON payload 'requested_provider': '{model_from_payload}'")

        if normalized_model_payload:
            if normalized_model_payload in DIRECT_PROVIDER_KEYS:
                provider_to_use_for_routing_or_direct_call = normalized_model_payload
                is_direct_provider_request = True 
            elif DIRECT_PROVIDER_ALIASES.get(normalized_model_payload) in DIRECT_PROVIDER_KEYS:
                provider_to_use_for_routing_or_direct_call = DIRECT_PROVIDER_ALIASES[normalized_model_payload]
                is_direct_provider_request = True
                logging.info(f"API Chat ID: {req_id}. 'requested_provider' field '{model_from_payload}' mapped to direct provider '{provider_to_use_for_routing_or_direct_call}' via alias.")
            elif normalized_model_payload in NEUROSWITCH_ROUTER_ALIASES:
                provider_to_use_for_routing_or_direct_call = NEUROSWITCH_PROVIDER_NAME
            else:
                logging.warning(f"API Chat ID: {req_id}. 'requested_provider' field '{model_from_payload}' not recognized. Defaulting to NeuroSwitch router.")
                provider_to_use_for_routing_or_direct_call = NEUROSWITCH_PROVIDER_NAME
        else:
            logging.warning(f"API Chat ID: {req_id}. 'requested_provider' field missing in JSON payload. Defaulting to NeuroSwitch router.")
            provider_to_use_for_routing_or_direct_call = NEUROSWITCH_PROVIDER_NAME

    else: # req_type == "flask_session"
        provider_from_session = session.get('provider', DEFAULT_PROVIDER)
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
        else: 
            logging.warning(f"Flask Session Chat ID: {req_id}. Provider '{provider_from_session}' from session not recognized. Defaulting to NeuroSwitch router.")
            provider_to_use_for_routing_or_direct_call = NEUROSWITCH_PROVIDER_NAME
    
    logging.info(f"Chat ID: {req_id}. Initial Provider Decision: '{provider_to_use_for_routing_or_direct_call}', Is Direct Request Flag: {is_direct_provider_request}")

    # --- NeuroSwitch Logic ---
    actual_provider_name_to_instantiate = provider_to_use_for_routing_or_direct_call 
    neuroswitch_active = False
    fallback_reason = None

    # Prepare message content and extract text for classification
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
            text_input_for_classification = message
        else:
             text_input_for_classification = "Image uploaded"
    else:
        message_content = message
        text_input_for_classification = message

    # Classifier runs if it was NOT a direct request AND the chosen path was NeuroSwitch
    if not is_direct_provider_request and provider_to_use_for_routing_or_direct_call == NEUROSWITCH_PROVIDER_NAME:
        logging.info(f"NeuroSwitch classifier activated for ID: {req_id}. Classifying input: '{text_input_for_classification[:100]}...' ")
        neuroswitch_status = get_neuroswitch_provider(text_input_for_classification)
        actual_provider_name_to_instantiate = neuroswitch_status["provider"] 
        neuroswitch_active = neuroswitch_status["neuroswitch_active"] 
        fallback_reason = neuroswitch_status["fallback_reason"]
        logging.info(f"NeuroSwitch classifier for ID: {req_id} result: Provider='{actual_provider_name_to_instantiate}', Classifier Active Flag={neuroswitch_active}, Reason='{fallback_reason}'")
    elif is_direct_provider_request:
        logging.info(f"Chat ID: {req_id}. Using DIRECTLY specified provider: {actual_provider_name_to_instantiate}. NeuroSwitch classifier bypassed.")
    else:
        logging.error(f"Chat ID: {req_id}. Unexpected provider routing state. Provider for routing was '{provider_to_use_for_routing_or_direct_call}' but not NeuroSwitch, and not flagged as a direct request. Attempting to use it directly. NeuroSwitch classifier bypassed.")
        actual_provider_name_to_instantiate = provider_to_use_for_routing_or_direct_call 

    # API Key Selection Logic
    selected_key_to_pass_to_factory = None
    key_source_for_logging = "Unknown" 

    if actual_provider_name_to_instantiate == "openai":
        if openai_user_key:
            selected_key_to_pass_to_factory = openai_user_key
            key_source_for_logging = "X-OpenAI-API-Key header"
        else:
            selected_key_to_pass_to_factory = Config.OPENAI_API_KEY
            key_source_for_logging = ".env (OPENAI_API_KEY)"
    elif actual_provider_name_to_instantiate == "claude":
        if claude_user_key:
            selected_key_to_pass_to_factory = claude_user_key
            key_source_for_logging = "X-Claude-API-Key header"
        else:
            selected_key_to_pass_to_factory = Config.ANTHROPIC_API_KEY
            key_source_for_logging = ".env (ANTHROPIC_API_KEY)"
    elif actual_provider_name_to_instantiate == "gemini":
        if gemini_user_key:
            selected_key_to_pass_to_factory = gemini_user_key
            key_source_for_logging = "X-Gemini-API-Key header"
        else:
            selected_key_to_pass_to_factory = Config.GEMINI_API_KEY
            key_source_for_logging = ".env (GEMINI_API_KEY)"
    else:
        logging.error(f"[Chat ID: {req_id}] Unknown provider '{actual_provider_name_to_instantiate}' determined. Cannot select API key.")
        return jsonify({
            'response': f"Error: Unknown provider '{actual_provider_name_to_instantiate}' specified.",
            'provider_used': actual_provider_name_to_instantiate,
            'model_used': 'unknown',
            'neuroswitch_active': neuroswitch_active,
            'fallback_reason': fallback_reason,
            'token_usage': {'total_tokens': current_total_tokens_used, 'max_tokens': Config.MAX_CONVERSATION_TOKENS}
        }), 500

    if selected_key_to_pass_to_factory:
        logging.info(f"[Chat ID: {req_id}] Attempting to initialize provider '{actual_provider_name_to_instantiate}' using API key from: {key_source_for_logging}.")
    else:
        logging.warning(f"[Chat ID: {req_id}] No API key found for provider '{actual_provider_name_to_instantiate}' from header or .env. Provider initialization will likely fail or use a non-functional default.")

    # Instantiate the provider
    logging.info(f"API Chat ID: {req_id}. Attempting to instantiate provider: '{actual_provider_name_to_instantiate}' with key from '{key_source_for_logging}'. Client-specified model: '{client_specified_model}'.")
    try:
        provider = ProviderFactory.create_provider(
            actual_provider_name_to_instantiate, 
            api_key=selected_key_to_pass_to_factory,
            client_model=client_specified_model
        )
    except ValueError as e:
         logging.error(f"[Chat ID: {req_id}] Failed to create provider instance '{actual_provider_name_to_instantiate}': {e}")
         return jsonify({
             'response': f"Error: Could not initialize AI provider '{actual_provider_name_to_instantiate}'. Please select a valid provider or check configuration.",
             'provider_used': actual_provider_name_to_instantiate,
             'model_used': 'unknown',
             'neuroswitch_active': neuroswitch_active,
             'fallback_reason': fallback_reason,
             'token_usage': {'total_tokens': current_total_tokens_used, 'max_tokens': Config.MAX_CONVERSATION_TOKENS}
         }), 400
    except Exception as e:
         logging.exception(f"Unexpected error creating provider '{actual_provider_name_to_instantiate}' for ID: {req_id}")
         return jsonify({
             'response': f"Error: An unexpected error occurred while setting up the AI provider.",
             'provider_used': actual_provider_name_to_instantiate,
             'model_used': 'unknown',
             'neuroswitch_active': neuroswitch_active,
             'fallback_reason': fallback_reason,
             'token_usage': {'total_tokens': current_total_tokens_used, 'max_tokens': Config.MAX_CONVERSATION_TOKENS}
         }), 500
    
    try:
        # Call assistant.chat (simplified without tool support)
        result_data = assistant.chat(
            user_input=message_content,
            provider=provider, 
            conversation_history=history_to_use,
            total_tokens_used=current_total_tokens_used,       
            mode=mode,
            request_id=req_id
        )

        logging.debug(f"App.py: Data received from assistant.chat: {json.dumps(result_data, default=str)}")

        # Save the updated history and tokens back to the correct session store
        save_session_data(req_id, req_type, result_data['updated_history'], result_data['total_tokens'])
        logging.info(f"Chat successful for ID: {req_id}. New history length: {len(result_data['updated_history'])}. New Tokens: {result_data['total_tokens']}")

        response_text = result_data.get('assistant_response', "[No response text received]")
        provider_used = result_data.get('provider_used', actual_provider_name_to_instantiate)
        model_used = result_data.get('model_used', 'unknown')
        usage_from_assistant = result_data.get('usage', {})
        
        token_usage_response = {
            'input_tokens': usage_from_assistant.get('input_tokens', 0),
            'output_tokens': usage_from_assistant.get('output_tokens', 0),
            'runtime': usage_from_assistant.get('runtime', 0.0),
            'total_tokens': result_data['total_tokens'],
            'max_tokens': Config.MAX_CONVERSATION_TOKENS,
        }
        
        return jsonify({
            'response': response_text,
            'provider_used': provider_used,
            'model_used': model_used,
            'neuroswitch_active': neuroswitch_active, 
            'fallback_reason': fallback_reason,
            'token_usage': token_usage_response
        })
        
    except Exception as e:
        logging.exception(f"Error during assistant.chat call for ID: {req_id}")
        return jsonify({
            'response': f"Error processing chat: {str(e)}",
            'provider_used': actual_provider_name_to_instantiate,
            'model_used': 'unknown',
            'neuroswitch_active': neuroswitch_active,
            'fallback_reason': fallback_reason,
            'token_usage': {'total_tokens': current_total_tokens_used, 'max_tokens': Config.MAX_CONVERSATION_TOKENS}
        }), 500

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
    
    logging.critical(f"----- NEW /reset REQUEST -----")
    logging.critical(f"Incoming req_id for reset: {req_id}, req_type: {req_type}")
    
    if req_type == "api":
        if req_id in api_client_session_store:
            api_client_session_store[req_id]['conversation_history'] = []
            api_client_session_store[req_id]['total_tokens_used'] = 0
            logging.critical(f"Conversation RESET for API client ID: {req_id}")
            status_message = f"Conversation reset for API client ID: {req_id}"
        else:
            api_client_session_store[req_id] = {'conversation_history': [], 'total_tokens_used': 0}
            logging.critical(f"No active session found for API client ID '{req_id}' to reset, but INITIALIZED it as empty.")
            status_message = f"No active session found for API client ID '{req_id}' to reset; initialized as new empty session."
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