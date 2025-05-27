from flask import Flask, render_template, request, jsonify, url_for, session, send_from_directory
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
import json # Added for json.dumps in reset route

app = Flask(__name__, static_folder='static')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
# Add a secret key for session management
# You should set FLASK_SECRET_KEY in your .env file for production
app.secret_key = os.getenv('FLASK_SECRET_KEY', os.urandom(24))

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
# Ensure base generated files directory exists
if hasattr(Config, 'GENERATED_FILES_DIR') and Config.GENERATED_FILES_DIR:
    os.makedirs(Config.GENERATED_FILES_DIR, exist_ok=True)
    logging.info(f"Ensured base directory for generated files exists: {Config.GENERATED_FILES_DIR}")
else:
    logging.warning("Config.GENERATED_FILES_DIR is not set. File generation by tools might fail or use a default relative path.")

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
    
    # NEW: Extract provider-specific API keys from headers
    openai_user_key = request.headers.get("X-OpenAI-API-Key")
    claude_user_key = request.headers.get("X-Claude-API-Key")
    gemini_user_key = request.headers.get("X-Gemini-API-Key")
    # END NEW

    # !!!!! ----- ADDED CRITICAL LOGGING ----- !!!!!
    logging.critical(f"----- NEW /chat REQUEST -----")
    logging.critical(f"Incoming req_id: {req_id}, req_type: {req_type}")
    # Log all headers for API requests to see exactly what's coming in
    if req_type == "api":
        headers_str = json.dumps(dict(request.headers), indent=2)
        logging.critical(f"Incoming API Request Headers: {headers_str}")
    
    # Log the state of api_client_session_store BEFORE getting session data
    if req_type == "api":
        # Make a copy of keys to avoid issues if dict changes during iteration (though unlikely here)
        current_keys = list(api_client_session_store.keys())
        logging.critical(f"Current api_client_session_store keys: {current_keys}")
        if req_id in api_client_session_store:
            # Log only a summary of history to avoid huge log lines
            history_summary = []
            if api_client_session_store[req_id]['conversation_history']:
                first_msg_role = api_client_session_store[req_id]['conversation_history'][0].get('role', 'unknown')
                first_msg_content_preview = str(api_client_session_store[req_id]['conversation_history'][0].get('content', ''))[:50]
                history_summary.append(f"First msg: role={first_msg_role}, content='{first_msg_content_preview}...'")
                if len(api_client_session_store[req_id]['conversation_history']) > 1:
                    history_summary.append(f"...and {len(api_client_session_store[req_id]['conversation_history']) - 1} more message(s).")
            else:
                history_summary.append("History is empty.")
            logging.critical(f"Data for req_id '{req_id}' IN api_client_session_store BEFORE get_session_data: History summary: {', '.join(history_summary)}. Tokens: {api_client_session_store[req_id]['total_tokens_used']}")
        else:
            logging.critical(f"req_id '{req_id}' NOT YET IN api_client_session_store.")
    # !!!!! ----- END OF ADDED CRITICAL LOGGING ----- !!!!!

    session_data = get_session_data(req_id, req_type)
    current_conversation_history = session_data['conversation_history']
    current_total_tokens_used = session_data['total_tokens_used']
    
    # !!!!! ----- ADDED CRITICAL LOGGING ----- !!!!!
    # Log summary of history AFTER get_session_data
    history_summary_after = []
    if current_conversation_history:
        first_msg_role_after = current_conversation_history[0].get('role', 'unknown')
        first_msg_content_preview_after = str(current_conversation_history[0].get('content', ''))[:50]
        history_summary_after.append(f"First msg: role={first_msg_role_after}, content='{first_msg_content_preview_after}...'")
        if len(current_conversation_history) > 1:
            history_summary_after.append(f"...and {len(current_conversation_history) - 1} more message(s).")
    else:
        history_summary_after.append("History is empty.")
    logging.critical(f"Data for req_id '{req_id}' LOADED BY get_session_data: History summary: {', '.join(history_summary_after)}. Tokens: {current_total_tokens_used}")
    # !!!!! ----- END OF ADDED CRITICAL LOGGING ----- !!!!!

    # A. Extract external API key from X-Provider-API-Key header
    # No longer needed as we use specific keys above.

    data = request.json
    logging.debug(f"API Chat ID: {req_id}. Full request JSON data: {data}")

    message = data.get('message')
    image_data = data.get('image_data') 
    mode = data.get('mode')
    client_specified_model = data.get('model') # ITEM 1: Extract client-specified model

    # --- Refined Provider Selection Logic for API and Flask UI ---
    is_direct_provider_request = False 
    provider_to_use_for_routing_or_direct_call = None # Will hold the name for direct instantiation or NEUROSWITCH_PROVIDER_NAME

    if req_type == "api":
        # --- ADDED: Log raw request body ---
        try:
            raw_request_body = request.data.decode('utf-8')
            logging.debug(f"API Chat ID: {req_id}. Raw request body: {raw_request_body}")
        except Exception as e:
            logging.error(f"API Chat ID: {req_id}. Error decoding raw request body: {e}")
        # --- END ADDED ---

        # --- ADDED: Log parsed JSON payload (data) ---
        logging.debug(f"API Chat ID: {req_id}. Parsed JSON payload (data): {data}")
        # --- END ADDED ---
        
        model_from_payload = data.get('requested_provider')
        normalized_model_payload = str(model_from_payload).lower() if model_from_payload else None

        logging.info(f"API Chat ID: {req_id}. Provider determination based on JSON payload 'requested_provider': '{model_from_payload}'")

        if normalized_model_payload:
            if normalized_model_payload in DIRECT_PROVIDER_KEYS: # e.g., model: "openai"
                provider_to_use_for_routing_or_direct_call = normalized_model_payload
                is_direct_provider_request = True 
            elif DIRECT_PROVIDER_ALIASES.get(normalized_model_payload) in DIRECT_PROVIDER_KEYS: # e.g. model: "gpt-4o"
                provider_to_use_for_routing_or_direct_call = DIRECT_PROVIDER_ALIASES[normalized_model_payload]
                is_direct_provider_request = True
                logging.info(f"API Chat ID: {req_id}. 'requested_provider' field '{model_from_payload}' mapped to direct provider '{provider_to_use_for_routing_or_direct_call}' via alias.")
            elif normalized_model_payload in NEUROSWITCH_ROUTER_ALIASES: # e.g., model: "neuroswitch"
                provider_to_use_for_routing_or_direct_call = NEUROSWITCH_PROVIDER_NAME
                # is_direct_provider_request remains False, so NeuroSwitch will run if this is the final decision
            else: # Unrecognized 'model' value
                logging.warning(f"API Chat ID: {req_id}. 'requested_provider' field '{model_from_payload}' not recognized. Defaulting to NeuroSwitch router.")
                provider_to_use_for_routing_or_direct_call = NEUROSWITCH_PROVIDER_NAME
                # is_direct_provider_request remains False
        else: # 'model' field is missing
            logging.warning(f"API Chat ID: {req_id}. 'requested_provider' field missing in JSON payload. Defaulting to NeuroSwitch router.")
            provider_to_use_for_routing_or_direct_call = NEUROSWITCH_PROVIDER_NAME
            # is_direct_provider_request remains False

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
            # is_direct_provider_request remains False
        else: 
            logging.warning(f"Flask Session Chat ID: {req_id}. Provider '{provider_from_session}' from session not recognized. Defaulting to NeuroSwitch router.")
            provider_to_use_for_routing_or_direct_call = NEUROSWITCH_PROVIDER_NAME
            # is_direct_provider_request remains False
    
    logging.info(f"Chat ID: {req_id}. Initial Provider Decision: '{provider_to_use_for_routing_or_direct_call}', Is Direct Request Flag: {is_direct_provider_request}")

    # --- NeuroSwitch Logic ---
    actual_provider_name_to_instantiate = provider_to_use_for_routing_or_direct_call 
    neuroswitch_active = False # Default, only set True if classifier actually runs
    fallback_reason = None # Initialize fallback_reason

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

    # Classifier runs if it was NOT a direct request AND the chosen path was NeuroSwitch
    if not is_direct_provider_request and provider_to_use_for_routing_or_direct_call == NEUROSWITCH_PROVIDER_NAME:
        logging.info(f"NeuroSwitch classifier activated for ID: {req_id}. Classifying input: '{text_input_for_classification[:100]}...' ")
        neuroswitch_status = get_neuroswitch_provider(text_input_for_classification)
        actual_provider_name_to_instantiate = neuroswitch_status["provider"] 
        neuroswitch_active = neuroswitch_status["neuroswitch_active"] 
        fallback_reason = neuroswitch_status["fallback_reason"]
        logging.info(f"NeuroSwitch classifier for ID: {req_id} result: Provider='{actual_provider_name_to_instantiate}', Classifier Active Flag={neuroswitch_active}, Reason='{fallback_reason}'")
    elif is_direct_provider_request:
        # Direct provider was chosen, classifier is bypassed.
        # actual_provider_name_to_instantiate is already correctly set from provider_to_use_for_routing_or_direct_call
        logging.info(f"Chat ID: {req_id}. Using DIRECTLY specified provider: {actual_provider_name_to_instantiate}. NeuroSwitch classifier bypassed.")
        # neuroswitch_active remains False
    else:
        # This case means is_direct_provider_request is False,
        # AND provider_to_use_for_routing_or_direct_call was NOT NEUROSWITCH_PROVIDER_NAME.
        # This implies an invalid provider name was given that wasn't a direct key, alias, or NeuroSwitch alias.
        # We'll attempt to use what was decided directly, but log an error as this path is unexpected.
        logging.error(f"Chat ID: {req_id}. Unexpected provider routing state. Provider for routing was '{provider_to_use_for_routing_or_direct_call}' but not NeuroSwitch, and not flagged as a direct request. Attempting to use it directly. NeuroSwitch classifier bypassed.")
        actual_provider_name_to_instantiate = provider_to_use_for_routing_or_direct_call 
        # neuroswitch_active remains False

    # --- End NeuroSwitch Logic ---

    # NEW: API Key Selection Logic
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
        # Consider returning an error response here
        return jsonify({
            'response': f"Error: Unknown provider '{actual_provider_name_to_instantiate}' specified.",
            'provider_used': actual_provider_name_to_instantiate,
            'neuroswitch_active': neuroswitch_active,
            'fallback_reason': fallback_reason, # Already initialized
            'token_usage': {'total_tokens': current_total_tokens_used, 'max_tokens': Config.MAX_CONVERSATION_TOKENS}
        }), 500

    if selected_key_to_pass_to_factory:
        logging.info(f"[Chat ID: {req_id}] Attempting to initialize provider '{actual_provider_name_to_instantiate}' using API key from: {key_source_for_logging}.")
    else:
        # This log indicates that neither a user-provided header key NOR a .env key was found for the selected provider.
        logging.warning(f"[Chat ID: {req_id}] No API key found for provider '{actual_provider_name_to_instantiate}' from header or .env. Provider initialization will likely fail or use a non-functional default.")
    # END NEW

    # Instantiate the provider (either direct or chosen by NeuroSwitch)
    logging.info(f"API Chat ID: {req_id}. Attempting to instantiate provider: '{actual_provider_name_to_instantiate}' with key from '{key_source_for_logging}'. Client-specified model: '{client_specified_model}'.") # ITEM 2: Update log message
    try:
        provider = ProviderFactory.create_provider(
            actual_provider_name_to_instantiate, 
            api_key=selected_key_to_pass_to_factory,
            client_model=client_specified_model # ITEM 3: Pass client_specified_model to factory
        )
    except ValueError as e:
         logging.error(f"[Chat ID: {req_id}] Failed to create provider instance '{actual_provider_name_to_instantiate}': {e}")
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
        # Call assistant.chat, REMOVE x_provider_api_key
        result_data = assistant.chat(
            user_input=message_content,
            provider=provider, 
            conversation_history=current_conversation_history, 
            total_tokens_used=current_total_tokens_used,       
            mode=mode,
            request_id=req_id
            # REMOVED: x_provider_api_key=x_provider_api_key 
        )

        logging.debug(f"App.py: Data received from assistant.chat: {json.dumps(result_data)}")

        # Save the updated history and tokens back to the correct session store
        save_session_data(req_id, req_type, result_data['updated_conversation_history'], result_data['updated_total_tokens_used'])
        logging.info(f"Chat successful for ID: {req_id}. New history length: {len(result_data['updated_conversation_history'])}. New Tokens: {result_data['updated_total_tokens_used']}")

        response_text = result_data.get('response', "[No response text received]")
        tool_name = result_data.get('tool_name')
        usage_from_assistant = result_data.get('usage', {}) # This is per-call usage
        model_actually_used = result_data.get('model_used') # ITEM 1: Extract model_used
        file_downloads_from_assistant = result_data.get('file_downloads') # Extract file_downloads
        
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
            'provider_used': actual_provider_name_to_instantiate, 
            'model_used': model_actually_used, # ITEM 2: Include model_used in the response
            'neuroswitch_active': neuroswitch_active, 
            'fallback_reason': fallback_reason,
            'token_usage': token_usage_response,
            'file_downloads': file_downloads_from_assistant # Add file_downloads to the response
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
    
    # !!!!! ----- ADDED CRITICAL LOGGING ----- !!!!!
    logging.critical(f"----- NEW /reset REQUEST -----")
    logging.critical(f"Incoming req_id for reset: {req_id}, req_type: {req_type}")
    if req_type == "api":
        # Make a copy of keys to avoid issues if dict changes during iteration
        current_keys_before_reset = list(api_client_session_store.keys())
        logging.critical(f"Resetting API client session. BEFORE reset, keys in api_client_session_store: {current_keys_before_reset}")
        if req_id in api_client_session_store:
            logging.critical(f"Data for req_id '{req_id}' being reset. Old history length: {len(api_client_session_store[req_id]['conversation_history'])}, Old tokens: {api_client_session_store[req_id]['total_tokens_used']}")
    # !!!!! ----- END OF ADDED CRITICAL LOGGING ----- !!!!!
    
    if req_type == "api":
        if req_id in api_client_session_store:
            api_client_session_store[req_id]['conversation_history'] = []
            api_client_session_store[req_id]['total_tokens_used'] = 0
            logging.critical(f"Conversation RESET for API client ID: {req_id}. Store now contains history length: {len(api_client_session_store[req_id]['conversation_history'])}, tokens: {api_client_session_store[req_id]['total_tokens_used']}")
            status_message = f"Conversation reset for API client ID: {req_id}"
        else:
            # This case means the ID wasn't in the store, so initialize it as empty.
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

@app.route('/download_file/<request_id_from_url>/<path:filename>', methods=['GET'])
def download_generated_file(request_id_from_url: str, filename: str):
    current_req_id, req_type = get_request_identifier_and_type()
    logging.debug(f"Download attempt for file '{filename}' under request_id_from_url '{request_id_from_url}'. Current session req_id: '{current_req_id}', type: '{req_type}'.")

    # Security Check: Ensure the request_id in the URL matches the current session's ID
    # This is crucial to prevent users from accessing other users' files.
    if request_id_from_url != current_req_id:
        logging.warning(f"Forbidden download attempt: URL request_id '{request_id_from_url}' does not match session req_id '{current_req_id}'.")
        return jsonify({'error': 'Forbidden. You do not have permission to access this file.'}), 403

    # Sanitize the filename from the URL path
    safe_filename = secure_filename(filename)
    if not safe_filename or safe_filename != filename: # Check if secure_filename altered it (e.g., removed path components) or emptied it
        logging.warning(f"Download attempt with potentially unsafe filename rejected. Original: '{filename}', Secured: '{safe_filename}'.")
        return jsonify({'error': 'Invalid filename.'}), 400

    try:
        # Construct the directory path for this specific request_id
        # Config.GENERATED_FILES_DIR should be an absolute path or resolvable relative to app root.
        # It's safer if Config.GENERATED_FILES_DIR is an absolute path.
        # For send_from_directory, the first argument is the directory, and the second is the path (filename) relative to that directory.
        session_specific_dir = os.path.join(Config.GENERATED_FILES_DIR, request_id_from_url)
        
        logging.info(f"Attempting to send file '{safe_filename}' from directory '{session_specific_dir}' for req_id '{current_req_id}'.")

        # Ensure the base generated files directory exists (though subdirs are made by the tool)
        if not os.path.isdir(Config.GENERATED_FILES_DIR):
            logging.error(f"Configuration error: Config.GENERATED_FILES_DIR ('{Config.GENERATED_FILES_DIR}') does not exist.")
            return jsonify({'error': 'Server configuration error preventing file download.'}), 500
        
        # Check if the session-specific directory exists
        if not os.path.isdir(session_specific_dir):
            logging.warning(f"File download failed: Session directory '{session_specific_dir}' not found for file '{safe_filename}'.")
            return jsonify({'error': 'File not found (session directory missing).'}), 404
            
        # Check if the file itself exists within that directory
        file_path_to_check = os.path.join(session_specific_dir, safe_filename)
        if not os.path.isfile(file_path_to_check):
            logging.warning(f"File download failed: File '{safe_filename}' not found in '{session_specific_dir}'.")
            return jsonify({'error': 'File not found.'}), 404

        return send_from_directory(
            directory=session_specific_dir, 
            path=safe_filename, # path is relative to 'directory'
            as_attachment=True
        )

    except FileNotFoundError: # Should be caught by checks above, but as a fallback
        logging.warning(f"File not found for download: '{safe_filename}' in session dir for '{request_id_from_url}'.")
        return jsonify({'error': 'File not found.'}), 404
    except Exception as e:
        logging.exception(f"Error during file download for req_id '{current_req_id}', file '{safe_filename}': {e}")
        return jsonify({'error': 'An unexpected error occurred while trying to download the file.'}), 500

if __name__ == '__main__':
    # Use debug=True for development, False for production
    # Consider using a proper WSGI server like gunicorn or waitress for production
    app.run(debug=True, host='0.0.0.0', port=5000) # Run on 0.0.0.0 to be accessible on network 