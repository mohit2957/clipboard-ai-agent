"""
═══════════════════════════════════════
  Clipboard Monitor
  Background thread that watches the
  clipboard for new content
═══════════════════════════════════════
"""

import os
import time
import hashlib
import threading
from io import BytesIO
from datetime import datetime

import pyperclip
from PIL import Image, ImageGrab

from config import IMAGE_DIR, POLL_INTERVAL
from content_detector import ContentDetector


class ClipboardMonitor:
    def __init__(self, db, ai_agent, on_new_item_callback):
        """
        Initialize the clipboard monitor.

        Args:
            db:                   DatabaseManager instance
            ai_agent:             AIAgent instance
            on_new_item_callback: Function to call when new item is added
        """
        self.db = db
        self.ai = ai_agent
        self.callback = on_new_item_callback

        self.running = False
        self.last_text = ""
        self.last_image_hash = ""
        self.thread = None

    # ═══════════════════════════════════════
    #  START / STOP
    # ═══════════════════════════════════════

    def start(self):
        """Start monitoring the clipboard in a background thread."""
        if self.running:
            print("[Monitor] Already running.")
            return

        self.running = True

        # Store current clipboard content to avoid re-capturing
        try:
            self.last_text = pyperclip.paste()
        except Exception:
            self.last_text = ""

        self.thread = threading.Thread(
            target=self._monitor_loop,
            daemon=True
        )
        self.thread.start()
        print("[Monitor] ▶ Started watching clipboard...")

    def stop(self):
        """Stop monitoring the clipboard."""
        self.running = False
        print("[Monitor] ⏹ Stopped.")

    # ═══════════════════════════════════════
    #  MAIN LOOP
    # ═══════════════════════════════════════

    def _monitor_loop(self):
        """Main monitoring loop — runs in background thread."""
        while self.running:
            try:
                self._check_clipboard()
            except Exception as e:
                print(f"[Monitor Error] {e}")

            time.sleep(POLL_INTERVAL)

    def _check_clipboard(self):
        """Check clipboard for new content (images first, then text)."""
        # Priority 1: Check for images
        if self._check_for_image():
            return  # Image found, skip text check

        # Priority 2: Check for text / links
        self._check_for_text()

    # ═══════════════════════════════════════
    #  IMAGE DETECTION
    # ═══════════════════════════════════════

    def _check_for_image(self):
        """
        Check if clipboard contains an image.
        Returns True if image was found and processed.
        """
        try:
            image = ImageGrab.grabclipboard()

            if image and isinstance(image, Image.Image):
                # Calculate hash to detect duplicates
                buf = BytesIO()
                image.save(buf, format='PNG')
                img_hash = hashlib.md5(buf.getvalue()).hexdigest()

                if img_hash != self.last_image_hash:
                    self.last_image_hash = img_hash
                    self._save_and_store_image(image)
                    return True

        except Exception as e:
            print(f"[Monitor] Image check error: {e}")

        return False

    def _save_and_store_image(self, image):
        """Save image to disk and store in database."""
        # Generate unique filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"clip_{timestamp}.png"
        filepath = os.path.join(IMAGE_DIR, filename)

        # Save to disk
        image.save(filepath, 'PNG')
        print(f"[Monitor] 🖼️ Image saved: {filepath}")

        # Store in database
        item_id = self.db.add_item('image', filepath)

        if item_id:
            # Run AI analysis in background
            threading.Thread(
                target=self._analyze_and_update,
                args=(item_id, f"Image file: {filename}", 'image'),
                daemon=True
            ).start()

            # Notify GUI
            self.callback()

    # ═══════════════════════════════════════
    #  TEXT / LINK DETECTION
    # ═══════════════════════════════════════

    def _check_for_text(self):
        """Check if clipboard contains new text or link."""
        try:
            current_text = pyperclip.paste()

            # Skip if empty or same as before
            if not current_text or not current_text.strip():
                return
            if current_text == self.last_text:
                return

            self.last_text = current_text

            # Detect content type
            content_type = ContentDetector.detect_type(current_text)
            icon = '🔗' if content_type == 'link' else '📝'
            print(f"[Monitor] {icon} New {content_type} detected")

            # Store in database
            item_id = self.db.add_item(content_type, current_text)

            if item_id:
                # Run AI analysis in background
                threading.Thread(
                    target=self._analyze_and_update,
                    args=(item_id, current_text, content_type),
                    daemon=True
                ).start()

                # Notify GUI
                self.callback()

        except Exception as e:
            print(f"[Monitor] Text check error: {e}")

    # ═══════════════════════════════════════
    #  AI ANALYSIS (runs in background)
    # ═══════════════════════════════════════

    def _analyze_and_update(self, item_id, content, content_type):
        """
        Run AI analysis on new content and update the database.
        This runs in a separate thread to avoid blocking.
        """
        print(f"[Monitor] 🧠 Analyzing item #{item_id}...")

        category, summary, tags = self.ai.analyze_content(
            content, content_type
        )

        self.db.update_ai_data(item_id, category, summary, tags)

        # Refresh GUI after analysis completes
        self.callback()

        print(f"[Monitor] ✅ Item #{item_id} analyzed: {category}")