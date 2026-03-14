"""
═══════════════════════════════════════
  Database Manager
  Handles all SQLite operations
═══════════════════════════════════════
"""

import os
import sqlite3
import hashlib
import threading
from datetime import datetime
from config import DB_PATH, IMAGE_DIR


class DatabaseManager:
    def __init__(self):
        """Initialize database connection and create tables."""
        os.makedirs(IMAGE_DIR, exist_ok=True)
        self.lock = threading.Lock()
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self.conn.execute("PRAGMA journal_mode=WAL")
        self._create_tables()

    def _create_tables(self):
        """Create the clipboard_items table if it doesn't exist."""
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS clipboard_items (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                content_type TEXT    NOT NULL,
                content      TEXT    NOT NULL,
                category     TEXT    DEFAULT '',
                summary      TEXT    DEFAULT '',
                tags         TEXT    DEFAULT '',
                timestamp    TEXT    NOT NULL,
                is_favorite  INTEGER DEFAULT 0,
                content_hash TEXT    UNIQUE
            )
        ''')
        self.conn.commit()
        print("[Database] Tables ready.")

    # ═══════════════════════════════════════
    #  INSERT
    # ═══════════════════════════════════════

    def add_item(self, content_type, content, category='', summary='', tags=''):
        """
        Add a new clipboard item to the database.
        Returns the item ID if successful, None if duplicate.
        """
        # Generate hash to prevent duplicates
        if isinstance(content, str):
            content_hash = hashlib.md5(content.encode()).hexdigest()
        else:
            content_hash = hashlib.md5(content).hexdigest()

        with self.lock:
            try:
                self.conn.execute('''
                    INSERT INTO clipboard_items
                        (content_type, content, category, summary,
                         tags, timestamp, content_hash)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    content_type,
                    content,
                    category,
                    summary,
                    tags,
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    content_hash
                ))
                self.conn.commit()
                item_id = self.conn.execute(
                    "SELECT last_insert_rowid()"
                ).fetchone()[0]
                print(f"[Database] Added item #{item_id} ({content_type})")
                return item_id

            except sqlite3.IntegrityError:
                print("[Database] Duplicate content skipped.")
                return None

    # ═══════════════════════════════════════
    #  READ
    # ═══════════════════════════════════════

    def get_all_items(self, filter_type=None):
        """Get all items, optionally filtered by content type."""
        with self.lock:
            if filter_type and filter_type != 'All':
                rows = self.conn.execute(
                    'SELECT * FROM clipboard_items WHERE content_type=? ORDER BY id DESC',
                    (filter_type.lower(),)
                ).fetchall()
            else:
                rows = self.conn.execute(
                    'SELECT * FROM clipboard_items ORDER BY id DESC'
                ).fetchall()
        return rows

    def search_items(self, query):
        """Search items by content, category, tags, or summary."""
        like = f'%{query}%'
        with self.lock:
            rows = self.conn.execute('''
                SELECT * FROM clipboard_items
                WHERE content  LIKE ?
                   OR category LIKE ?
                   OR tags     LIKE ?
                   OR summary  LIKE ?
                ORDER BY id DESC
            ''', (like, like, like, like)).fetchall()
        return rows

    def get_item_by_id(self, item_id):
        """Get a single item by its ID."""
        with self.lock:
            row = self.conn.execute(
                'SELECT * FROM clipboard_items WHERE id=?',
                (item_id,)
            ).fetchone()
        return row

    # ═══════════════════════════════════════
    #  UPDATE
    # ═══════════════════════════════════════

    def update_ai_data(self, item_id, category, summary, tags):
        """Update AI-generated category, summary, and tags."""
        with self.lock:
            self.conn.execute('''
                UPDATE clipboard_items
                SET category=?, summary=?, tags=?
                WHERE id=?
            ''', (category, summary, tags, item_id))
            self.conn.commit()
            print(f"[Database] Updated AI data for item #{item_id}")

    def toggle_favorite(self, item_id):
        """Toggle the favorite status of an item."""
        with self.lock:
            self.conn.execute(
                'UPDATE clipboard_items SET is_favorite = NOT is_favorite WHERE id=?',
                (item_id,)
            )
            self.conn.commit()

    # ═══════════════════════════════════════
    #  DELETE
    # ═══════════════════════════════════════

    def delete_item(self, item_id):
        """Delete a single item and its image file if applicable."""
        with self.lock:
            row = self.conn.execute(
                'SELECT content_type, content FROM clipboard_items WHERE id=?',
                (item_id,)
            ).fetchone()

            # Delete image file from disk
            if row and row[0] == 'image' and os.path.exists(row[1]):
                os.remove(row[1])
                print(f"[Database] Deleted image file: {row[1]}")

            self.conn.execute(
                'DELETE FROM clipboard_items WHERE id=?',
                (item_id,)
            )
            self.conn.commit()
            print(f"[Database] Deleted item #{item_id}")

    def clear_all(self):
        """Delete ALL items and their image files."""
        with self.lock:
            # Delete all image files
            rows = self.conn.execute(
                'SELECT content FROM clipboard_items WHERE content_type="image"'
            ).fetchall()
            for row in rows:
                if os.path.exists(row[0]):
                    os.remove(row[0])

            self.conn.execute('DELETE FROM clipboard_items')
            self.conn.commit()
            print("[Database] Cleared all items.")

    # ═══════════════════════════════════════
    #  LIFECYCLE
    # ═══════════════════════════════════════

    def close(self):
        """Close the database connection."""
        self.conn.close()
        print("[Database] Connection closed.")