## **Neuroswitch System Architecture**

### **1\. Frontend (Web UI)**

* Modern, Responsive UI: Built with HTML, CSS (Tailwind), and JavaScript.  
* Features:  
* Two-column layout: sidebar (provider selection, features), main chat area.  
* Dynamic chat with avatars for each provider.  
* Floating input, suggestion cards, and feature buttons.  
* Token usage bar and real-time updates.  
* Handles file/image uploads and tool usage display.  
* Provider selection (Claude, OpenAI, Gemini, NeuroSwitch).

### **2\. Backend (Flask API)**

* Flask App (app.py):  
* Serves the frontend and provides API endpoints (/chat, /set\_provider, /reset, /upload).  
* Manages session state (provider selection, etc.).  
* Handles both browser and API clients.  
* Orchestrates provider selection, including NeuroSwitch routing.  
* Assistant Orchestration (ce3.py):  
* Manages conversation history, tool execution, and provider interaction.  
* Handles context sanitization for cross-provider compatibility.  
* Tracks and accumulates token usage.  
* Returns detailed response objects (including token usage and runtime).  
* Provider Abstraction Layer (providers/):  
* Provider Factory: Dynamically instantiates the correct provider class.  
* Provider Classes: Each provider (Claude, OpenAI, Gemini) implements a chat() method, returning content and usage stats.  
* NeuroSwitch: A smart router that classifies the user’s intent and selects the best provider for each message.  
* Tool System (tools/):  
* BaseTool: Abstract class for all tools.  
* Dynamic Tool Loading: Tools are Python classes auto-discovered and loaded at runtime.  
* Tool Execution: Tools can be invoked by any provider that supports tool use/function calling.  
* Context Sanitizer (context\_sanitizer.py):  
* Translates and adapts conversation history for each provider’s unique requirements.  
* Ensures seamless context continuity when switching providers.

### **3\. Token & Usage Tracking**

* Backend: Tracks input, output, and total tokens, as well as runtime for each request.  
* Frontend: Displays token usage bar and stats to the user.

### **4\. API & Integration**

* REST API: /chat endpoint accepts JSON payloads and returns detailed responses (including tokens, runtime, provider used, etc.).  
* Supports both browser and programmatic/API clients.

### **5\. Session & State Management**

* Flask session: Tracks selected provider and other user/session-specific state.  
* Conversation history: Maintained in memory for each session.

---

## **Diagram (Textual)**

text

Apply to ce3.py

\[User (Web UI/API)\] 

      |

      v

\[Flask App (app.py)\]

      |

      v

\[Assistant (ce3.py)\]

      |

      \+-------------------+

      |                   |

\[Provider Factory\]   \[Tool System\]

      |                   |

      v                   v

\[Claude/OpenAI/Gemini/NeuroSwitch\]   \[Loaded Tools\]

      |

      v

\[External AI APIs\]

---

## **Key Innovations**

* Provider-agnostic chat with context continuity.  
* Dynamic, pluggable tool system.  
* NeuroSwitch: smart provider routing.  
* Unified, modern UI with real-time token usage.  
* Extensible and developer-friendly architecture.

