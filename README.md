# 🧠 AI-Powered Smart Clipboard Manager

An intelligent clipboard manager built with Python that uses a local LLM
(Ollama with llama3:8b) to automatically classify, summarize, and tag
clipboard content. Stores text, images, and links.

![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Ollama](https://img.shields.io/badge/LLM-llama3:8b-green)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📝 **Text Capture** | Automatically stores copied text |
| 🔗 **Link Detection** | Identifies and categorizes URLs |
| 🖼️ **Image Capture** | Saves copied screenshots and images |
| 🧠 **AI Classification** | Auto-categorizes content using llama3:8b |
| 🏷️ **Auto Tagging** | AI generates relevant tags for each item |
| 📄 **Auto Summary** | AI creates short summaries |
| 🔍 **Smart Search** | AI-powered semantic search |
| ⭐ **Favorites** | Mark important clipboard items |
| 🎨 **Dark Theme** | Clean dark-themed Tkinter GUI |
| 🗑️ **Delete / Clear** | Remove single or all items |

---

## 📸 How It Works

```
Copy something (text/link/image)
        │
        ▼
Clipboard Monitor detects new content
        │
        ▼
Content type detected (text / link / image)
        │
        ▼
Stored in SQLite database
        │
        ▼
AI Agent analyzes content (llama3:8b)
        │
        ▼
Category, Summary, Tags auto-generated
        │
        ▼
GUI updates with new item
```

---

## 🗂️ Project Structure

```
ai-smart-clipboard-manager/
├── config.py                # Configuration constants
├── database.py              # SQLite database manager
├── ai_agent.py              # AI agent (Ollama llama3:8b)
├── content_detector.py      # Content type detection
├── clipboard_monitor.py     # Background clipboard watcher
├── gui.py                   # Tkinter GUI
├── main.py                  # Entry point
├── build.py                 # Build .exe script
├── create_icon.py           # Icon generator
├── create_release.py        # Release packager
├── icon.ico                 # App icon
├── requirements.txt         # Dependencies
├── .gitignore               # Git ignore rules
└── README.md                # This file
```

---

## 📋 Requirements

- **Windows 10/11**
- **Python 3.8+**
- **Ollama** installed and running
- **llama3:8b** model pulled
- **NVIDIA GPU** recommended (works on CPU too)

---

## 🚀 Installation

### Option 1: Download Release (Easy)

1. Go to [Releases](https://github.com/mohit2957/ai-smart-clipboard-manager/releases)
2. Download `AI-Clipboard-Manager-v1.0.0.zip`
3. Extract the ZIP
4. Install [Ollama](https://ollama.com/download)
5. Open terminal and run:
   ```bash
   ollama pull llama3:8b
   ollama serve
   ```
6. Double-click `AI-Clipboard-Manager.exe`

### Option 2: Run from Source (Developer)

```bash
# Clone the repo
git clone https://github.com/mohit2957/ai-smart-clipboard-manager.git
cd ai-smart-clipboard-manager

# Install dependencies
pip install -r requirements.txt

# Pull the LLM model
ollama pull llama3:8b

# Start Ollama
ollama serve

# Run the app (in a new terminal)
python main.py
```

---

## 📦 Dependencies

```
ollama
pyperclip
Pillow
pywin32
```

Install all:
```bash
pip install -r requirements.txt
```

---

## 🎮 Usage

1. **Start the app** → `python main.py`
2. **Click ▶ Start Monitoring** in the GUI
3. **Copy anything** — text, links, or screenshots
4. Items appear automatically with AI-generated tags
5. **Search** by keyword or click **🧠 AI Search** for smart matching
6. Click any item to see **full details and image preview**
7. **Copy back** to clipboard with one click

---

## 🧠 AI Classification Examples

| You Copy | Category | Tags |
|----------|----------|------|
| `def hello(): print("hi")` | Code | python, function, programming |
| `https://github.com/repo` | URL | github, repository, development |
| `Meeting at 3pm tomorrow` | Note | meeting, schedule, reminder |
| `john@email.com` | Email | contact, email, communication |
| Screenshot of a website | Image | screenshot, web, visual |

---

## 🔨 Build .exe (For Developers)

```bash
# Create app icon
python create_icon.py

# Build Windows executable
python build.py

# Create release package
python create_release.py
```

Output: `dist/AI-Clipboard-Manager.exe`

---

## 🛠️ Configuration

Edit `config.py` to customize:

```python
MODEL_NAME = "llama3:8b"        # Change LLM model
POLL_INTERVAL = 1.5             # Clipboard check interval (seconds)
WINDOW_WIDTH = 960              # GUI window width
WINDOW_HEIGHT = 720             # GUI window height
```

---

## 📁 Data Storage

| What | Where | Auto-Created |
|------|-------|-------------|
| Clipboard items | `clipboard_manager.db` (SQLite) | ✅ Yes |
| Copied images | `clipboard_images/` folder | ✅ Yes |
| Settings | `config.py` | ❌ Part of code |

---

## ❓ Troubleshooting

| Problem | Solution |
|---------|----------|
| `ollama` not found | Install from [ollama.com](https://ollama.com/download) |
| Model not found | Run `ollama pull llama3:8b` |
| App won't start | Make sure `ollama serve` is running |
| Slow classification | Use GPU — check with `nvidia-smi` |
| Images not captured | Install `pywin32`: `pip install pywin32` |
| No GPU detected | Update NVIDIA drivers |

---

## 🤝 Contributing

1. Fork the repo
2. Create a branch: `git checkout -b feature-name`
3. Commit changes: `git commit -m "Add feature"`
4. Push: `git push origin feature-name`
5. Open a Pull Request

---

## 📜 License

This project is licensed under the MIT License.

---

## 🙏 Built With

- [Python](https://python.org)
- [Ollama](https://ollama.com) — Local LLM
- [llama3:8b](https://ollama.com/library/llama3) — Meta's LLM
- [Tkinter](https://docs.python.org/3/library/tkinter.html) — GUI
- [SQLite](https://sqlite.org) — Database
- [Pillow](https://pillow.readthedocs.io) — Image processing
