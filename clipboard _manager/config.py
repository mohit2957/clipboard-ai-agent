"""
═══════════════════════════════════════
  Configuration Constants
═══════════════════════════════════════
"""

# Ollama model name
MODEL_NAME = "llama3:8b"

# SQLite database file path
DB_PATH = "clipboard_manager.db"

# Directory to store copied images
IMAGE_DIR = "clipboard_images"

# How often to check clipboard (seconds)
POLL_INTERVAL = 1.5

# Maximum content length sent to LLM
MAX_CONTENT_LENGTH = 500

# GUI window settings
WINDOW_TITLE = "🧠 AI Smart Clipboard Manager"
WINDOW_WIDTH = 960
WINDOW_HEIGHT = 720
MIN_WIDTH = 800
MIN_HEIGHT = 600

# Color theme (Dark Catppuccin)
COLORS = {
    'bg':       '#1e1e2e',
    'bg2':      '#313244',
    'fg':       '#cdd6f4',
    'accent':   '#89b4fa',
    'green':    '#a6e3a1',
    'red':      '#f38ba8',
    'heading':  '#45475a',
}

# Content type icons
TYPE_ICONS = {
    'text':  '📝',
    'link':  '🔗',
    'image': '🖼️',
}