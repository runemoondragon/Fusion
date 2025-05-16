## **Neuroswich Component Diagram (Textual)**

text

Apply to ce3.py

\+-------------------+         \+-------------------+         \+-------------------+

|    Frontend UI    | \<-----\> |    Flask App      | \<-----\> |   Assistant Core  |

| (HTML/JS/CSS)     |  HTTP   |   (app.py)        |  Calls  |    (ce3.py)       |

\+-------------------+         \+-------------------+         \+-------------------+

        |                            |                               |

        |                            |                               |

        |                            v                               v

        |                  \+-------------------+         \+-------------------+

        |                  |  Provider Factory |         |   Tool System     |

        |                  | (provider\_factory)|         |   (tools/\*.py)    |

        |                  \+-------------------+         \+-------------------+

        |                            |                               |

        |                            v                               |

        |                  \+-------------------+                     |

        |                  |  Providers        |                     |

        |                  | (Claude, OpenAI,  |                     |

        |                  |  Gemini, Neuro...)|                     |

        |                  \+-------------------+                     |

        |                            |                               |

        |                            v                               |

        |                  \+-------------------+                     |

        |                  | External AI APIs  |                     |

        |                  \+-------------------+                     |

        |                                                        \+---v---+

        |                                                        | Tools |

        |                                                        \+-------+

        |                            |                               |

        |                            v                               |

        |                  \+-------------------+                     |

        |                  | Context Sanitizer | \<-------------------+

        |                  \+-------------------+

Key Components:

* Frontend UI: User interface, provider selection, chat, token bar, etc.  
* Flask App: HTTP endpoints, session management, API routing.  
* Assistant Core: Orchestrates chat, tool use, context, and provider logic.  
* Provider Factory: Instantiates the correct provider.  
* Providers: Claude, OpenAI, Gemini, NeuroSwitch (router).  
* Tool System: Dynamically loaded Python tools.  
* Context Sanitizer: Adapts conversation history for each provider.

---

## **2\. Sequence Diagram (API Call with Tool Use and Provider Switch)**

text

Apply to ce3.py

User (UI/API)

    |

    | 1\. Sends message (with/without image/tool) via /chat

    v

Flask App (app.py)

    |

    | 2\. Determines provider (Claude/OpenAI/Gemini/NeuroSwitch)

    | 3\. Passes message to Assistant

    v

Assistant (ce3.py)

    |

    | 4\. Sanitizes context for selected provider

    | 5\. Calls Provider.chat()

    v

Provider (e.g., OpenAIProvider)

    |

    | 6\. Formats message, sends to external API

    | 7\. Receives response (may include tool call)

    | 8\. Returns content \+ usage (input/output tokens, runtime)

    ^

    | 9\. If tool call: Assistant executes tool via Tool System

    |10. Tool result is added to conversation history

    |11. Assistant may re-call Provider with tool result

    |

    |12. Final response, token usage, runtime returned to Flask App

    v

Flask App

    |

    |13. Returns JSON response to User (includes tokens, runtime, provider used, etc.)

    v

User (UI/API)

---

### **Provider Switch Sequence**

1. User switches provider in UI (e.g., from OpenAI to Claude).  
1. Flask updates session, but keeps conversation history.  
1. Assistant uses Context Sanitizer to adapt history for new provider.  
1. New provider receives compatible history and continues the chat seamlessly.

---

## **Summary Table**

| Component | Role/Responsibility ||---------------------|---------------------------------------------------------|| Frontend UI | User interaction, chat, provider selection, token bar || Flask App | API endpoints, session, routing, error handling || Assistant (ce3.py) | Orchestration, context, tool execution, token tracking || Provider Factory | Instantiates correct provider class || Providers | API integration (Claude, OpenAI, Gemini, NeuroSwitch) || Tool System | Dynamic Python tools, tool execution || Context Sanitizer | Adapts history for each provider’s requirements