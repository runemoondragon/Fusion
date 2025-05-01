# Fusion AI ⚡️🤖

A smart, multi-AI assistant framework that dynamically switches between AI providers — Claude, Gemini, and GPT — via a unified web interface. Fusion allows users to leverage the strengths of different models for various tasks directly from their browser.

Built with flexibility and user experience in mind.

---

## 🚀 Why Fusion AI?

Most AI tools lock users into a single provider. Fusion AI provides a single interface to interact with multiple leading AI models, allowing users to choose the best one for their current need.

### Key Concepts:
- **Provider Switching:** Easily select Claude, Gemini, or GPT from a dropdown menu.
- **Unified Interface:** Consistent chat experience regardless of the selected provider.
- **Bring Your Own Keys:** Connects to your personal API keys for each service.

---

## ✨ Key Features

- 🌐 **Web-Based UI:** Modern chat interface built with Flask, Tailwind CSS, and vanilla JavaScript.
- 🔄 **Provider Selection:** Dropdown menu to instantly switch between Claude, Gemini, and GPT.
- 💾 **Provider Persistence:** Remembers your selected provider across interactions within a session.
- 📊 **Token Usage Tracking:** Displays accumulated token usage (input + output) across all providers in a visual progress bar (relative to a configurable max).
- 🖼️ **Image Upload:** Supports uploading images for analysis by multimodal models (provider capability permitting).
- 🎨 **Dynamic Avatars:** Messages are tagged with the avatar of the AI provider that generated the response.
- 🛠️ **Dynamic Tool Loading:** Automatically discovers and loads available tools from the `tools/` directory.
- 📦 **Dependency Handling:** Prompts to install missing Python packages required by tools (uses `uv`).
- ⌨️ **Command Input:** Supports `/refresh`, `/reset`, `/quit` via suggestion cards or direct typing.
- ✨ **Clean UI:** Minimalist sidebar (non-functional placeholders currently), main chat area with centered welcome message, and a floating input bar with feature buttons and suggestion cards.

---

## 💻 Local Setup

### Prerequisites
- Python 3.10+
- Your own API keys stored in a `.env` file:
  - `ANTHROPIC_API_KEY` (for Claude)
  - `OPENAI_API_KEY` (for OpenAI GPT)
  - `GEMINI_API_KEY` (for Google Gemini)

### Installation & Running

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/runemoondragon/Fusion.git # Or your repo URL
    cd Fusion
    ```

2.  **Install dependencies:**
    It's recommended to use a virtual environment.
    ```bash
    python -m venv .venv
    # Activate the environment (Windows)
    # .\.venv\Scripts\activate
    # Activate the environment (macOS/Linux)
    # source .venv/bin/activate

    # Install packages (using pip or uv)
    pip install -r requirements.txt
    # or if you have uv installed:
    # uv pip install -r requirements.txt
    ```

3.  **Create `.env` file:**
    Create a file named `.env` in the project root directory and add your API keys:
    ```dotenv
    ANTHROPIC_API_KEY=your_anthropic_key
    OPENAI_API_KEY=your_openai_key
    GEMINI_API_KEY=your_gemini_key
    # Optional: Set a Flask secret key for sessions
    # FLASK_SECRET_KEY=a_very_secret_random_string
    ```

4.  **Run the Flask application:**
    ```bash
    python app.py
    ```
    Alternatively, use a production server like Gunicorn or Waitress:
    ```bash
    # Example using Waitress (install via pip install waitress)
    # waitress-serve --host 0.0.0.0 --port 5000 app:app
    ```

5.  **Open your browser:**
    Navigate to `http://127.0.0.1:5000` (or the address provided by the server).

---

## 🔧 Project Structure

```
Fusion/
├── .venv/                  # Virtual environment (optional)
├── providers/              # AI provider integration logic (Claude, Gemini, OpenAI)
│   ├── base_provider.py
│   ├── claude_provider.py
│   ├── gemini_provider.py
│   ├── openai_provider.py
│   └── provider_factory.py
├── static/                 # Frontend assets
│   ├── css/style.css
│   ├── js/chat.js
│   └── *.png               # Logos and icons
├── templates/
│   └── index.html          # Main HTML file for the UI
├── tools/                  # Directory for dynamically loaded tools
│   ├── base.py
│   └── ... (individual tool files)
├── uploads/                # Temporary folder for image uploads
├── .env                    # API keys and environment variables (create this)
├── .gitignore
├── app.py                  # Flask application entry point and routes
├── ce3.py                  # Core assistant logic (tool handling, chat flow)
├── config.py               # Application configuration
├── prompts/                # System prompts for the AI
│   └── system_prompts.py
├── requirements.txt        # Python dependencies
├── readme.md               # This file
└── ...                     # Other project files (like pyproject.toml, uv.lock)
```

---

## 🛠️ Available Tools (Loaded Dynamically)

The application automatically loads tools placed in the `tools/` directory that inherit from `BaseTool`. Based on the current files, these include:

- `browsertool`: Opens URLs.
- `createfolderstool`: Creates folders.
- `diffeditortool`: Performs text replacements.
- `duckduckgotool`: Web searches.
- `e2bcodetool`: (Purpose depends on implementation - likely code execution via e2b)
- `filecontentreadertool`: Reads file contents.
- `filecreatortool`: Creates files.
- `fileedittool`: Edits files.
- `lintingtool`: Lints Python code.
- `screenshottool`: Takes screenshots.
- `toolcreator`: Creates new tools (meta-tool).
- `uvpackagemanager`: Installs Python packages using UV.
- `webscrapertool`: Extracts web page content.

*Note: The effectiveness and safety of tools like code execution or file modification depend heavily on their implementation.* 

---

## 📅 Potential Future Directions (Ideas)

- Admin dashboard for usage stats & cost tracking.
- Configurable routing rules (e.g., use Model X for coding, Model Y for research).
- Fallback strategies if a provider fails.
- Persistent chat history.
- Integration with vector databases for RAG.
- Support for more models (Mistral, local LLMs via Ollama, etc.).

---

## 🧩 License

MIT License (Please confirm/update if different)

---

Fusion AI — Chat with Claude, Gemini, and GPT in one place.