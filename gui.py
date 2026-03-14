"""
═══════════════════════════════════════
  GUI — Tkinter Interface
  Main window for the clipboard manager
═══════════════════════════════════════
"""

import tkinter as tk
from tkinter import ttk, messagebox
from io import BytesIO

import pyperclip
from PIL import Image, ImageTk

from config import (
    WINDOW_TITLE, WINDOW_WIDTH, WINDOW_HEIGHT,
    MIN_WIDTH, MIN_HEIGHT, COLORS, TYPE_ICONS
)
from database import DatabaseManager
from ai_agent import AIAgent
from clipboard_monitor import ClipboardMonitor


class ClipboardManagerGUI:
    """Main GUI application for the Smart Clipboard Manager."""

    # ── Database column indices ──
    COL_ID       = 0
    COL_TYPE     = 1
    COL_CONTENT  = 2
    COL_CATEGORY = 3
    COL_SUMMARY  = 4
    COL_TAGS     = 5
    COL_TIME     = 6
    COL_FAV      = 7

    def __init__(self):
        """Initialize all components and build the GUI."""

        # ── Core components ──
        self.db = DatabaseManager()
        self.ai = AIAgent()

        # ── Main window ──
        self.root = tk.Tk()
        self.root.title(WINDOW_TITLE)
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.minsize(MIN_WIDTH, MIN_HEIGHT)
        self.root.configure(bg=COLORS['bg'])

        # ── Image reference (prevent garbage collection) ──
        self._detail_image_ref = None

        # ── Build all UI sections ──
        self._setup_styles()
        self._build_toolbar()
        self._build_search_bar()
        self._build_treeview()
        self._build_detail_panel()
        self._build_statusbar()

        # ── Clipboard monitor ──
        self.monitor = ClipboardMonitor(
            self.db, self.ai, self._schedule_refresh
        )

        # ── Load existing data ──
        self._refresh_list()

        # ── Window close handler ──
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    # ═══════════════════════════════════════
    #  STYLES
    # ═══════════════════════════════════════

    def _setup_styles(self):
        """Configure dark theme styles for all widgets."""
        style = ttk.Style()
        style.theme_use('clam')

        bg      = COLORS['bg']
        fg      = COLORS['fg']
        bg2     = COLORS['bg2']
        accent  = COLORS['accent']
        green   = COLORS['green']
        red     = COLORS['red']
        heading = COLORS['heading']

        style.configure('TFrame',  background=bg)
        style.configure('TLabel',  background=bg, foreground=fg,
                        font=('Segoe UI', 10))
        style.configure('TButton', background=bg2, foreground=fg,
                        font=('Segoe UI', 10), padding=6)
        style.map('TButton', background=[('active', accent)])

        style.configure('Green.TButton', background=green,
                        foreground='#1e1e2e')
        style.map('Green.TButton', background=[('active', '#74c7a4')])

        style.configure('Red.TButton', background=red,
                        foreground='#1e1e2e')
        style.map('Red.TButton', background=[('active', '#e06c8a')])

        style.configure('Header.TLabel',
                        font=('Segoe UI', 14, 'bold'),
                        foreground=accent)

        style.configure('Treeview',
                        background=bg2, foreground=fg,
                        fieldbackground=bg2,
                        font=('Consolas', 10), rowheight=28)
        style.configure('Treeview.Heading',
                        background=heading, foreground=fg,
                        font=('Segoe UI', 10, 'bold'))
        style.map('Treeview',
                  background=[('selected', accent)],
                  foreground=[('selected', '#1e1e2e')])

    # ═══════════════════════════════════════
    #  TOOLBAR
    # ═══════════════════════════════════════

    def _build_toolbar(self):
        """Build the top toolbar with title and control buttons."""
        toolbar = ttk.Frame(self.root)
        toolbar.pack(fill='x', padx=10, pady=(10, 5))

        # Title
        ttk.Label(
            toolbar,
            text="🧠 AI Smart Clipboard Manager",
            style='Header.TLabel'
        ).pack(side='left')

        # Control buttons (right side)
        controls = ttk.Frame(toolbar)
        controls.pack(side='right')

        self.btn_start = ttk.Button(
            controls, text="▶ Start Monitoring",
            style='Green.TButton', command=self._start_monitor
        )
        self.btn_start.pack(side='left', padx=2)

        self.btn_stop = ttk.Button(
            controls, text="⏹ Stop",
            command=self._stop_monitor
        )
        self.btn_stop.pack(side='left', padx=2)

        ttk.Button(
            controls, text="🗑 Clear All",
            style='Red.TButton', command=self._clear_all
        ).pack(side='left', padx=2)

    # ═══════════════════════════════════════
    #  SEARCH BAR
    # ═══════════════════════════════════════

    def _build_search_bar(self):
        """Build the search and filter row."""
        search_frame = ttk.Frame(self.root)
        search_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(search_frame, text="🔍").pack(side='left')

        # Search input
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(
            search_frame, textvariable=self.search_var,
            width=40, font=('Segoe UI', 10)
        )
        search_entry.pack(side='left', padx=5)
        search_entry.bind('<Return>', lambda e: self._do_search())

        # Search buttons
        ttk.Button(
            search_frame, text="Search",
            command=self._do_search
        ).pack(side='left', padx=2)

        ttk.Button(
            search_frame, text="🧠 AI Search",
            command=self._do_ai_search
        ).pack(side='left', padx=2)

        ttk.Button(
            search_frame, text="Reset",
            command=self._refresh_list
        ).pack(side='left', padx=2)

        # Filter dropdown
        ttk.Label(search_frame, text="  Filter:").pack(side='left')

        self.filter_var = tk.StringVar(value='All')
        filter_combo = ttk.Combobox(
            search_frame, textvariable=self.filter_var,
            values=['All', 'Text', 'Link', 'Image'],
            state='readonly', width=8
        )
        filter_combo.pack(side='left', padx=5)
        filter_combo.bind(
            '<<ComboboxSelected>>',
            lambda e: self._refresh_list()
        )

    # ═══════════════════════════════════════
    #  TREEVIEW — Items List
    # ═══════════════════════════════════════

    def _build_treeview(self):
        """Build the main item list with scrollbar."""
        tree_frame = ttk.Frame(self.root)
        tree_frame.pack(fill='both', expand=True, padx=10, pady=5)

        columns = ('id', 'type', 'preview', 'category', 'tags', 'time', 'fav')

        self.tree = ttk.Treeview(
            tree_frame, columns=columns,
            show='headings', selectmode='browse'
        )

        # Column headings
        self.tree.heading('id',       text='ID',       anchor='center')
        self.tree.heading('type',     text='Type',     anchor='center')
        self.tree.heading('preview',  text='Preview',  anchor='w')
        self.tree.heading('category', text='Category', anchor='center')
        self.tree.heading('tags',     text='Tags',     anchor='w')
        self.tree.heading('time',     text='Time',     anchor='center')
        self.tree.heading('fav',      text='⭐',       anchor='center')

        # Column widths
        self.tree.column('id',       width=40,  stretch=False, anchor='center')
        self.tree.column('type',     width=60,  stretch=False, anchor='center')
        self.tree.column('preview',  width=300, stretch=True,  anchor='w')
        self.tree.column('category', width=100, stretch=False, anchor='center')
        self.tree.column('tags',     width=150, stretch=True,  anchor='w')
        self.tree.column('time',     width=140, stretch=False, anchor='center')
        self.tree.column('fav',      width=40,  stretch=False, anchor='center')

        # Scrollbar
        scrollbar = ttk.Scrollbar(
            tree_frame, orient='vertical',
            command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # Selection event
        self.tree.bind('<<TreeviewSelect>>', self._on_item_select)

    # ═══════════════════════════════════════
    #  DETAIL PANEL
    # ═══════════════════════════════════════

    def _build_detail_panel(self):
        """Build the bottom detail panel."""
        detail_frame = ttk.Frame(self.root)
        detail_frame.pack(fill='x', padx=10, pady=5)

        # ── Info labels ──
        info_row = ttk.Frame(detail_frame)
        info_row.pack(fill='x')

        self.lbl_type = ttk.Label(info_row, text="Type: —")
        self.lbl_type.pack(side='left', padx=(0, 20))

        self.lbl_category = ttk.Label(info_row, text="Category: —")
        self.lbl_category.pack(side='left', padx=(0, 20))

        self.lbl_summary = ttk.Label(info_row, text="Summary: —")
        self.lbl_summary.pack(side='left', fill='x', expand=True)

        # ── Content text box ──
        self.detail_text = tk.Text(
            detail_frame, height=6, wrap='word',
            bg=COLORS['bg2'], fg=COLORS['fg'],
            insertbackground=COLORS['fg'],
            font=('Consolas', 10), relief='flat',
            padx=8, pady=8
        )
        self.detail_text.pack(fill='x', pady=(5, 5))

        # ── Image preview ──
        self.img_label = ttk.Label(detail_frame)
        self.img_label.pack(fill='x', pady=5)
        self.img_label.pack_forget()  # hidden by default

        # ── Action buttons ──
        btn_row = ttk.Frame(detail_frame)
        btn_row.pack(fill='x')

        ttk.Button(
            btn_row, text="📋 Copy to Clipboard",
            command=self._copy_selected
        ).pack(side='left', padx=2)

        ttk.Button(
            btn_row, text="⭐ Toggle Favorite",
            command=self._toggle_fav
        ).pack(side='left', padx=2)

        ttk.Button(
            btn_row, text="🗑 Delete",
            style='Red.TButton',
            command=self._delete_selected
        ).pack(side='left', padx=2)

    # ═══════════════════════════════════════
    #  STATUS BAR
    # ═══════════════════════════════════════

    def _build_statusbar(self):
        """Build the bottom status bar."""
        self.status_var = tk.StringVar(
            value="⏸ Monitor stopped  |  Items: 0"
        )
        ttk.Label(
            self.root, textvariable=self.status_var,
            font=('Segoe UI', 9)
        ).pack(fill='x', padx=10, pady=(0, 5))

    # ═══════════════════════════════════════
    #  MONITOR CONTROLS
    # ═══════════════════════════════════════

    def _start_monitor(self):
        """Start the clipboard monitor."""
        self.monitor.start()
        self._update_status()

    def _stop_monitor(self):
        """Stop the clipboard monitor."""
        self.monitor.stop()
        self._update_status()

    def _update_status(self):
        """Update the status bar text."""
        count = len(self.tree.get_children())
        if self.monitor.running:
            self.status_var.set(f"🟢 Monitoring clipboard...  |  Items: {count}")
        else:
            self.status_var.set(f"⏸ Monitor stopped  |  Items: {count}")

    # ═══════════════════════════════════════
    #  REFRESH / SEARCH
    # ═══════════════════════════════════════

    def _schedule_refresh(self):
        """Thread-safe GUI refresh (called from background threads)."""
        self.root.after(0, self._refresh_list)

    def _refresh_list(self):
        """Reload items from database and update the treeview."""
        filter_type = self.filter_var.get()
        items = self.db.get_all_items(filter_type)
        self._populate_tree(items)

    def _do_search(self):
        """Perform keyword search."""
        query = self.search_var.get().strip()
        if not query:
            self._refresh_list()
            return
        items = self.db.search_items(query)
        self._populate_tree(items)

    def _do_ai_search(self):
        """Perform AI-powered semantic search."""
        query = self.search_var.get().strip()
        if not query:
            return

        all_items = self.db.get_all_items()
        matching_ids = self.ai.smart_search(query, all_items)

        if matching_ids:
            items = [
                item for item in all_items
                if item[self.COL_ID] in matching_ids
            ]
        else:
            # Fallback to keyword search
            items = self.db.search_items(query)

        self._populate_tree(items)

    def _populate_tree(self, items):
        """Clear and repopulate the treeview with items."""
        self.tree.delete(*self.tree.get_children())

        for item in items:
            icon = TYPE_ICONS.get(item[self.COL_TYPE], '📄')
            preview = item[self.COL_CONTENT][:60].replace('\n', ' ')
            fav = '⭐' if item[self.COL_FAV] else ''

            self.tree.insert('', 'end',
                iid=str(item[self.COL_ID]),
                values=(
                    item[self.COL_ID],
                    f"{icon} {item[self.COL_TYPE]}",
                    preview,
                    item[self.COL_CATEGORY],
                    item[self.COL_TAGS],
                    item[self.COL_TIME],
                    fav
                )
            )

        self._update_status()

    # ═══════════════════════════════════════
    #  ITEM SELECTION
    # ═══════════════════════════════════════

    def _on_item_select(self, event):
        """Handle treeview item selection — show details."""
        selected = self.tree.selection()
        if not selected:
            return

        item_id = int(selected[0])
        item = self.db.get_item_by_id(item_id)
        if not item:
            return

        # Update info labels
        self.lbl_type.config(
            text=f"Type: {item[self.COL_TYPE]}"
        )
        self.lbl_category.config(
            text=f"Category: {item[self.COL_CATEGORY]}"
        )
        self.lbl_summary.config(
            text=f"Summary: {item[self.COL_SUMMARY]}"
        )

        # Update content display
        self.detail_text.delete('1.0', 'end')

        if item[self.COL_TYPE] == 'image':
            self._show_image_preview(item[self.COL_CONTENT])
            self.detail_text.insert('1.0', f"📁 {item[self.COL_CONTENT]}")
        else:
            self._hide_image_preview()
            self.detail_text.insert('1.0', item[self.COL_CONTENT])

    def _show_image_preview(self, filepath):
        """Show image thumbnail in the detail panel."""
        try:
            img = Image.open(filepath)
            img.thumbnail((400, 200))
            photo = ImageTk.PhotoImage(img)
            self.img_label.config(image=photo)
            self._detail_image_ref = photo  # prevent garbage collection
            self.img_label.pack(fill='x', pady=5)
        except Exception as e:
            self._hide_image_preview()
            print(f"[GUI] Image preview error: {e}")

    def _hide_image_preview(self):
        """Hide the image preview label."""
        self.img_label.pack_forget()
        self._detail_image_ref = None

    # ═══════════════════════════════════════
    #  ACTIONS
    # ═══════════════════════════════════════

    def _copy_selected(self):
        """Copy selected item back to clipboard."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Select an item first.")
            return

        item = self.db.get_item_by_id(int(selected[0]))
        if not item:
            return

        if item[self.COL_TYPE] == 'image':
            self._copy_image_to_clipboard(item[self.COL_CONTENT])
        else:
            pyperclip.copy(item[self.COL_CONTENT])

        self.status_var.set("✅ Copied to clipboard!")

    def _copy_image_to_clipboard(self, filepath):
        """Copy image file back to Windows clipboard."""
        try:
            import win32clipboard

            img = Image.open(filepath)
            output = BytesIO()
            img.convert('RGB').save(output, 'BMP')
            data = output.getvalue()[14:]  # strip BMP header

            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardData(
                win32clipboard.CF_DIB, data
            )
            win32clipboard.CloseClipboard()

        except ImportError:
            messagebox.showinfo(
                "Info",
                f"Install pywin32 to copy images.\n"
                f"Image saved at:\n{filepath}"
            )

    def _toggle_fav(self):
        """Toggle favorite status of selected item."""
        selected = self.tree.selection()
        if not selected:
            return
        self.db.toggle_favorite(int(selected[0]))
        self._refresh_list()

    def _delete_selected(self):
        """Delete the selected item."""
        selected = self.tree.selection()
        if not selected:
            return

        if messagebox.askyesno("Delete", "Delete this clipboard item?"):
            self.db.delete_item(int(selected[0]))
            self._hide_image_preview()
            self.detail_text.delete('1.0', 'end')
            self._refresh_list()

    def _clear_all(self):
        """Delete ALL clipboard history."""
        if messagebox.askyesno(
            "Clear All", "Delete ALL clipboard history?"
        ):
            self.db.clear_all()
            self._hide_image_preview()
            self.detail_text.delete('1.0', 'end')
            self._refresh_list()

    # ═══════════════════════════════════════
    #  LIFECYCLE
    # ═══════════════════════════════════════

    def _on_close(self):
        """Handle window close — cleanup resources."""
        self.monitor.stop()
        self.db.close()
        self.root.destroy()

    def run(self):
        """Start the GUI event loop."""
        self.root.mainloop()