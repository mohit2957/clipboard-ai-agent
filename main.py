"""
═══════════════════════════════════════════════════════════════
  AI-Powered Smart Clipboard Manager
  
  Entry point — run this file to start the application.
  
  Prerequisites:
    1. Install Ollama:  https://ollama.com/download
    2. Pull model:      ollama pull llama3:8b
    3. Install deps:    pip install ollama pyperclip Pillow pywin32
    4. Start Ollama:    ollama serve
    5. Run this:        python main.py
═══════════════════════════════════════════════════════════════
"""

from config import MODEL_NAME
from gui import ClipboardManagerGUI


def main():
    print("=" * 55)
    print("  🧠 AI-Powered Smart Clipboard Manager")
    print(f"  Model : {MODEL_NAME}")
    print("  Press ▶ Start in the GUI to begin monitoring")
    print("=" * 55)
    print()

    app = ClipboardManagerGUI()
    app.run()


if __name__ == "__main__":
    main()