import requests
import os
import logging

# Candidate Labels for NeuroSwitch Classification
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

# Label-to-Provider Mapping
LABEL_PROVIDER_MAP = {
     # Gemini’s domain
    "image generation": "gemini",
    "recipe suggestion": "gemini",
    "travel planning": "gemini",
    "personal assistant task": "gemini",

    # Claude’s domain
    "legal document review": "claude",
    "health advice": "claude",
    "historical fact": "claude",
    "general question": "claude",
    "text summarization": "claude",
    "grammar checking": "claude",

    # OpenAI’s domain
    "data analysis": "openai",
    "programming help": "openai",
    "code generation": "openai",
    "content creation": "openai",
    "math problem solving": "openai",
    "SEO analysis": "openai",
    "product recommendation": "openai",
    "translation": "openai",
    "sentiment analysis": "openai",
    "financial forecasting": "openai",

    # fallback
    "unknown": "claude"
}

DEFAULT_PROVIDER = "claude" # Fallback if anything goes wrong

class HuggingFaceClassifier:
    """
    Uses Hugging Face Inference API for zero-shot text classification.
    Requires HF_API_KEY environment variable.
    """
    def __init__(self):
        # Using facebook/bart-large-mnli as specified
        self.api_url = "https://api-inference.huggingface.co/models/facebook/bart-large-mnli"
        api_key = os.getenv('HF_API_KEY')
        if not api_key:
            logging.error("HF_API_KEY environment variable not set!")
            # Raise an error or handle this case appropriately
            raise ValueError("Hugging Face API Key (HF_API_KEY) not found in environment.")
            
        self.headers = {"Authorization": f"Bearer {api_key}"}
        logging.info("HuggingFaceClassifier initialized.")

    def classify(self, user_input: str, labels: list[str]) -> str:
        """
        Classifies the user input against the provided candidate labels.

        Args:
            user_input: The text to classify.
            labels: A list of candidate labels.

        Returns:
            The label with the highest score, or "unknown" if classification fails.
        """
        if not user_input or not labels:
            logging.warning("Classifier called with empty input or labels.")
            print("[NeuroSwitch Console] Classifier called with empty input or labels.") 
            return "unknown"
            
        payload = {
            "inputs": user_input,
            "parameters": {
                "candidate_labels": labels,
                "multi_label": False # Assume single best label for routing
            }
        }
        logging.debug(f"Sending payload to HF API: {payload}")
        print(f"[NeuroSwitch Console] Sending payload to HF API: {payload}") 
        try:
            response = requests.post(self.api_url, headers=self.headers, json=payload, timeout=30)
            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
            result = response.json()
            logging.debug(f"Received result from HF API: {result}")
            print(f"[NeuroSwitch Console] Received result from HF API: {result}") 

            # Check the expected structure
            if isinstance(result, dict) and 'labels' in result and 'scores' in result:
                 if result['labels'] and result['scores']:
                     # The API returns labels sorted by score, highest first
                     top_label = result['labels'][0]
                     top_score = result['scores'][0]
                     logging.info(f"Classification result: Label='{top_label}', Score={top_score:.4f}")
                     print(f"[NeuroSwitch Console] Classification result: Label='{top_label}', Score={top_score:.4f}") 
                     return top_label
                 else:
                     logging.warning("HF API returned empty labels or scores list.")
                     print("[NeuroSwitch Console] HF API returned empty labels or scores list.") 
                     return "unknown"
            elif isinstance(result, dict) and 'error' in result:
                logging.error(f"HF API Error: {result['error']}")
                print(f"[NeuroSwitch Console] HF API Error: {result['error']}") 
                return "unknown"
            else:
                 logging.error(f"Unexpected response format from HF API: {result}")
                 print(f"[NeuroSwitch Console] Unexpected response format from HF API: {result}") 
                 return "unknown"

        except requests.exceptions.Timeout:
            logging.error(f"HF API request timed out after 30 seconds.")
            print("[NeuroSwitch Console] HF API request timed out after 30 seconds.") 
            return "unknown"
        except requests.exceptions.RequestException as e:
            logging.error(f"HTTP Request failed: {e}")
            print(f"[NeuroSwitch Console] HTTP Request failed: {e}") 
            return "unknown"
        except Exception as e:
            logging.exception(f"Error during classification request: {e}")
            print(f"[NeuroSwitch Console] Error during classification request: {e}") 
            return "unknown"

# --- Main Function for NeuroSwitch ---

# Initialize the classifier once when the module is loaded
try:
    classifier_instance = HuggingFaceClassifier()
except ValueError as e:
    logging.error(f"Failed to initialize classifier: {e}. NeuroSwitch will be disabled.")
    classifier_instance = None # Set to None if initialization fails

def get_neuroswitch_provider(text_input: str) -> dict:
    """
    Classifies the input text and returns a dictionary containing the 
    selected provider name and the NeuroSwitch status.

    Args:
        text_input: The user's message text.

    Returns:
        A dictionary like:
        {
            "provider": "claude", 
            "neuroswitch_active": True, 
            "fallback_reason": None
        }
        or
        {
            "provider": "claude", 
            "neuroswitch_active": False, 
            "fallback_reason": "API key not configured"
        }
    """
    # Initialize status dictionary
    status = {
        "provider": DEFAULT_PROVIDER,
        "neuroswitch_active": False,
        "fallback_reason": None
    }
    
    if not classifier_instance:
        reason = "HF_API_KEY not configured or classifier failed to initialize"
        logging.warning(f"NeuroSwitch disabled: {reason}. Request routed to default: {DEFAULT_PROVIDER}")
        status["fallback_reason"] = reason
        return status # Return immediately with default provider and inactive status
        
    if not text_input:
        logging.info("NeuroSwitch received empty input, using default provider.")
        # Treat as inactive as no classification happened, but no error reason
        status["neuroswitch_active"] = False 
        return status

    logging.info(f"NeuroSwitch classifying input: '{text_input[:100]}...'")
    
    try:
        # Perform classification
        classified_label = classifier_instance.classify(text_input, CANDIDATE_LABELS)
        
        # Map the label to a provider
        selected_provider = LABEL_PROVIDER_MAP.get(classified_label, DEFAULT_PROVIDER)
        
        status["provider"] = selected_provider
        status["neuroswitch_active"] = True # Classification was successful
        logging.info(f"NeuroSwitch classified as '{classified_label}', routing to provider: '{selected_provider}'")
        
    except Exception as e:
        # Log the exception from the classification attempt
        logging.exception("NeuroSwitch classification failed.") 
        reason = f"Classification failed: {str(e)}"
        status["fallback_reason"] = reason
        # Keep provider as DEFAULT_PROVIDER and neuroswitch_active as False
        logging.warning(f"NeuroSwitch fallback: {reason}. Using default: {DEFAULT_PROVIDER}")
        
    return status 