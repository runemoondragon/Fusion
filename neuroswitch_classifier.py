import requests
import logging
import os

print("--- neuroswitch_classifier.py: Module Execution START ---")

# Configure basic logging for this module specifically
# This will help ensure its INFO messages are seen during import, even if app.py configures logging later.
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler() # Ensure output to console
    ]
)

print("--- neuroswitch_classifier.py: Basic logging configured ---")

# import requests # Removed as it\'s no longer needed for local inference
# from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer # Moved
# from transformers.pipelines import ZeroShotClassificationPipeline # Moved

# --- Constants for NeuroSwitch ---
CANDIDATE_LABELS = [
    "image generation",
    "data analysis",
    "programming help",
    "text summarization",
    "translation",
    "sentiment analysis",
    "code generation",
    "content creation",
    "math problem solving",
    "SEO analysis",
    "product recommendation",
    "grammar checking",
    "financial forecasting",
    "legal document review",
    "personal assistant task",
    "weather forecast",
    "health advice",
    "recipe suggestion",
    "historical fact",
    "travel planning",
    "general question"
]

# Mapping from classified labels to provider names (ensure these match your actual provider identifiers)
LABEL_PROVIDER_MAP = {
    # Gemini's domain
    "weather forecast": "gemini",
    "recipe suggestion": "gemini",
    "travel planning": "gemini",
    "personal assistant task": "gemini",
    "translation": "gemini",
    "general question": "gemini",

    # Claude's domain
    "text summarization": "claude",
    "legal document review": "claude",
    "sentiment analysis": "claude",
    "health advice": "claude",
    "historical fact": "claude",

    # OpenAI's domain
    "image generation": "openai",
    "data analysis": "openai",
    "programming help": "openai",
    "code generation": "openai",
    "content creation": "openai",
    "math problem solving": "openai",
    "SEO analysis": "openai",
    "product recommendation": "openai",
    "grammar checking": "openai",
    "financial forecasting": "openai",

    # fallback
    "unknown": "claude"
}

DEFAULT_PROVIDER = "claude"  # Fallback provider if NeuroSwitch fails or input is empty

# --- Pipeline Initialization ---
classifier_pipeline = None # Explicitly None initially
MODEL_NAME = "facebook/bart-large-mnli"

print(f"--- neuroswitch_classifier.py: Attempting to initialize pipeline for {MODEL_NAME} ---")
try:
    print("--- neuroswitch_classifier.py: Importing transformers... ---")
    from transformers import pipeline
    from transformers.pipelines import ZeroShotClassificationPipeline # Import here
    print("--- neuroswitch_classifier.py: Transformers imported. Creating pipeline... ---")
    
    # Ensure pipeline type hint matches the imported class
    classifier_pipeline: ZeroShotClassificationPipeline | None = None 

    logging.info(f"(Log) Initializing local zero-shot pipeline with model: {MODEL_NAME}...")
    classifier_pipeline = pipeline("zero-shot-classification", model=MODEL_NAME, use_auth_token=False, token=None)
    print("--- neuroswitch_classifier.py: Pipeline CREATED successfully! ---")
    logging.info(f"(Log) Local zero-shot pipeline initialized successfully.")

except ImportError as e:
    print(f"--- neuroswitch_classifier.py: ERROR during import: {e} ---") # Print error
    logging.error(f"Failed to initialize pipeline: Missing libraries (transformers/torch/tensorflow?). Error: {e}")
    classifier_pipeline = None
except Exception as e:
    print(f"--- neuroswitch_classifier.py: ERROR during pipeline creation: {e} ---") # Print error
    logging.exception(f"Failed to initialize local zero-shot pipeline: {e}")
    classifier_pipeline = None

print("--- neuroswitch_classifier.py: End of initialization block ---")

def get_neuroswitch_provider(text_input: str) -> dict:
    """
    Classifies the input text using a local zero-shot model and returns the
    selected provider name and the NeuroSwitch status.

    Args:
        text_input: The user\'s query.

    Returns:
        A dictionary containing:
            "provider": The name of the selected AI provider.
            "neuroswitch_active": Boolean indicating if classification was successful.
            "fallback_reason": String explaining why fallback occurred, if any.
    """
    status = {
        "provider": DEFAULT_PROVIDER,
        "neuroswitch_active": False,  # Assume inactive unless classification succeeds
        "fallback_reason": None
    }

    # Check if pipeline failed to load
    if classifier_pipeline is None:
        reason = f"Local classifier pipeline ({MODEL_NAME}) failed to initialize."
        # Keep warning for actual issues
        logging.warning(f"NeuroSwitch disabled: {reason}. Request routed to default: {DEFAULT_PROVIDER}") 
        status["fallback_reason"] = reason
        return status

    if not text_input:
        # Use print for this info level message
        print(f"--- NeuroSwitch: Received empty input, using default provider: {DEFAULT_PROVIDER} ---") 
        # logging.info("NeuroSwitch received empty input, using default provider.") # Replaced
        status["neuroswitch_active"] = False
        return status
    
    # Use print for this info level message
    print(f"--- NeuroSwitch: Classifying locally: '{text_input[:100]}...' ---") 
    # logging.info(f"NeuroSwitch classifying locally: '{text_input[:100]}...'") # Replaced
    classified_label = "unknown"

    try:
        result = classifier_pipeline(text_input, CANDIDATE_LABELS, multi_label=False)
        
        # Use print for the detailed raw output
        print(f"--- NeuroSwitch: RAW classification result object: {result} ---") 
        # logging.info(f"NeuroSwitch RAW classification result object: {result}") # Replaced

        if result and 'labels' in result and result['labels'] and 'scores' in result and result['scores']:
            classified_label = result['labels'][0]
            top_score = result['scores'][0]
            status["neuroswitch_active"] = True
            # Use print for the top pick info
            print(f"--- NeuroSwitch: Local classification TOP PICK: Label='{classified_label}', Score={top_score:.4f} ---") 
            # logging.info(f"Local classification TOP PICK: Label='{classified_label}', Score={top_score:.4f}") # Replaced
        else:
            # Keep warning for actual issues
            logging.warning(f"Local classification pipeline returned unexpected or incomplete result: {result}") 
            status["fallback_reason"] = "Classification returned no labels or scores."

        selected_provider = LABEL_PROVIDER_MAP.get(classified_label, DEFAULT_PROVIDER)
        status["provider"] = selected_provider
        # Use print for routing info
        print(f"--- NeuroSwitch: Routing to provider: '{selected_provider}' based on label '{classified_label}' ---") 
        # logging.info(f"NeuroSwitch routing to provider: '{selected_provider}' based on label '{classified_label}'") # Replaced

    except Exception as e:
        # Keep exception logging
        logging.exception("NeuroSwitch local classification failed.") 
        reason = f"Local classification failed: {str(e)}"
        status["fallback_reason"] = reason
        status["provider"] = DEFAULT_PROVIDER

    return status 