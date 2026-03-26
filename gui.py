"""
GUI for Athena Voice Calculator
Tkinter-based graphical interface
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
from typing import Callable, Optional
import threading
import time


class AthenaGUI:
    """Main GUI for Athena Voice Calculator"""
    
    # Color scheme (Dark Mode)
    COLORS = {
        'bg_primary': '#0D1117',
        'bg_secondary': '#161B22',
        'bg_tertiary': '#21262D',
        'accent_primary': '#00D9FF',
        'accent_secondary': '#A855F7',
        'accent_success': '#10B981',
        'accent_warning': '#F59E0B',
        'accent_error': '#EF4444',
        'text_primary': '#FFFFFF',
        'text_secondary': '#8B949E',
        'text_muted': '#484F58',
        'border': '#30363D'
    }
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Athena - Voice Calculator")
        self.root.geometry("900x700")
        self.root.configure(bg=self.COLORS['bg_primary'])
        
        # Callbacks
        self.on_listen_click: Optional[Callable] = None
        self.on_clear_click: Optional[Callable] = None
        self.on_history_select: Optional[Callable] = None
        self.on_export_click: Optional[Callable] = None
        self.on_settings_click: Optional[Callable] = None
        
        # State
        self.is_listening = False
        self.listen_thread: Optional[threading.Thread] = None
        self.stop_listen_event = threading.Event()
        
        # Build UI
        self._create_styles()
        self._create_header()
        self._create_main_content()
        self._create_voice_panel()
        self._create_display_panel()
        self._create_history_panel()
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
    
    def _create_styles(self):
        """Create custom styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure styles
        style.configure('Title.TLabel',
                       background=self.COLORS['bg_primary'],
                       foreground=self.COLORS['text_primary'],
                       font=('Segoe UI', 20, 'bold'))
        
        style.configure('Heading.TLabel',
                       background=self.COLORS['bg_secondary'],
                       foreground=self.COLORS['text_primary'],
                       font=('Segoe UI', 14, 'semibold'))
        
        style.configure('Body.TLabel',
                       background=self.COLORS['bg_secondary'],
                       foreground=self.COLORS['text_secondary'],
                       font=('Segoe UI', 12))
        
        style.configure('Status.TLabel',
                       background=self.COLORS['bg_primary'],
                       foreground=self.COLORS['text_muted'],
                       font=('Segoe UI', 10))
        
        style.configure('Accent.TButton',
                       background=self.COLORS['accent_primary'],
                       foreground=self.COLORS['bg_primary'],
                       font=('Segoe UI', 12, 'bold'),
                       borderwidth=0)
        
        style.configure('Secondary.TButton',
                       background=self.COLORS['bg_tertiary'],
                       foreground=self.COLORS['text_primary'],
                       font=('Segoe UI', 11),
                       borderwidth=0)
    
    def _create_header(self):
        """Create header bar"""
        header = tk.Frame(self.root, bg=self.COLORS['bg_secondary'], height=50)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        # Title
        title = tk.Label(header, text="🧠 Athena", 
                        bg=self.COLORS['bg_secondary'],
                        fg=self.COLORS['accent_primary'],
                        font=('Segoe UI', 18, 'bold'))
        title.pack(side=tk.LEFT, padx=20)
        
        # Subtitle
        subtitle = tk.Label(header, text="Voice Calculator",
                           bg=self.COLORS['bg_secondary'],
                           fg=self.COLORS['text_muted'],
                           font=('Segoe UI', 10))
        subtitle.pack(side=tk.LEFT, padx=5)
        
        # Status indicator
        self.status_indicator = tk.Label(header, text="● Ready",
                                         bg=self.COLORS['bg_secondary'],
                                         fg=self.COLORS['accent_success'],
                                         font=('Segoe UI', 10))
        self.status_indicator.pack(side=tk.RIGHT, padx=20)
        
        # Settings button
        settings_btn = tk.Button(header, text="⚙️",
                                bg=self.COLORS['bg_secondary'],
                                fg=self.COLORS['text_secondary'],
                                font=('Segoe UI', 14),
                                bd=0,
                                command=self._settings_click)
        settings_btn.pack(side=tk.RIGHT, padx=10)
    
    def _create_main_content(self):
        """Create main content area"""
        # Main container
        main = tk.Frame(self.root, bg=self.COLORS['bg_primary'])
        main.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Create three columns
        # Left: Voice panel (150px)
        # Center: Display panel (flexible)
        # Right: History panel (250px)
        
        self.voice_frame = tk.Frame(main, bg=self.COLORS['bg_secondary'],
                                    width=150, height=500)
        self.voice_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        self.voice_frame.pack_propagate(False)
        
        self.display_frame = tk.Frame(main, bg=self.COLORS['bg_secondary'],
                                      width=400)
        self.display_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.history_frame = tk.Frame(main, bg=self.COLORS['bg_secondary'],
                                      width=250)
        self.history_frame.pack(side=tk.RIGHT, fill=tk.Y)
    
    def _create_voice_panel(self):
        """Create voice input panel"""
        # Title
        title = tk.Label(self.voice_frame, text="🎤 Voice",
                        bg=self.COLORS['bg_secondary'],
                        fg=self.COLORS['text_primary'],
                        font=('Segoe UI', 12, 'bold'))
        title.pack(pady=(20, 10))
        
        # Microphone button
        self.mic_button = tk.Button(self.voice_frame,
                                   text="🎙️",
                                   font=('Segoe UI', 40),
                                   bg=self.COLORS['bg_tertiary'],
                                   fg=self.COLORS['accent_primary'],
                                   bd=0,
                                   width=5, height=2,
                                   command=self._mic_click)
        self.mic_button.pack(pady=20)
        
        # Status label
        self.voice_status = tk.Label(self.voice_frame, text="Click to speak",
                                    bg=self.COLORS['bg_secondary'],
                                    fg=self.COLORS['text_muted'],
                                    font=('Segoe UI', 10))
        self.voice_status.pack(pady=10)
        
        # Mode toggle
        self.mode_var = tk.StringVar(value="single")
        mode_frame = tk.Frame(self.voice_frame, bg=self.COLORS['bg_secondary'])
        mode_frame.pack(pady=20, padx=10)
        
        single_btn = tk.Radiobutton(mode_frame, text="Single",
                                    variable=self.mode_var, value="single",
                                    bg=self.COLORS['bg_secondary'],
                                    fg=self.COLORS['text_secondary'],
                                    selectcolor=self.COLORS['bg_tertiary'],
                                    command=self._mode_changed)
        single_btn.pack()
        
        continuous_btn = tk.Radiobutton(mode_frame, text="Continuous",
                                       variable=self.mode_var, value="continuous",
                                       bg=self.COLORS['bg_secondary'],
                                       fg=self.COLORS['text_secondary'],
                                       selectcolor=self.COLORS['bg_tertiary'],
                                       command=self._mode_changed)
        continuous_btn.pack()
        
        # Wake word label
        wake_label = tk.Label(self.voice_frame,
                             text="Say 'Hey Athena' to activate",
                             bg=self.COLORS['bg_secondary'],
                             fg=self.COLORS['text_muted'],
                             font=('Segoe UI', 9),
                             wraplength=120)
        wake_label.pack(pady=20, padx=10)
        
        # Clear button
        clear_btn = tk.Button(self.voice_frame, text="🗑️ Clear",
                             bg=self.COLORS['bg_tertiary'],
                             fg=self.COLORS['text_secondary'],
                             font=('Segoe UI', 10),
                             bd=0,
                             command=self._clear_click)
        clear_btn.pack(pady=10)
    
    def _create_display_panel(self):
        """Create main display panel"""
        # Title
        title = tk.Label(self.display_frame, text="📊 Calculator",
                        bg=self.COLORS['bg_secondary'],
                        fg=self.COLORS['text_primary'],
                        font=('Segoe UI', 12, 'bold'))
        title.pack(pady=(20, 10))
        
        # Input display
        input_label = tk.Label(self.display_frame, text="Your voice input:",
                              bg=self.COLORS['bg_secondary'],
                              fg=self.COLORS['text_muted'],
                              font=('Segoe UI', 10))
        input_label.pack(pady=(10, 5), anchor=tk.W, padx=20)
        
        self.input_display = tk.Label(self.display_frame, text="...",
                                      bg=self.COLORS['bg_tertiary'],
                                      fg=self.COLORS['text_primary'],
                                      font=('Segoe UI', 14),
                                      wraplength=350,
                                      justify=tk.LEFT,
                                      padx=15, pady=10)
        self.input_display.pack(fill=tk.X, padx=20, pady=(0, 15))
        
        # Expression display
        expr_label = tk.Label(self.display_frame, text="Parsed expression:",
                             bg=self.COLORS['bg_secondary'],
                             fg=self.COLORS['text_muted'],
                             font=('Segoe UI', 10))
        expr_label.pack(pady=(10, 5), anchor=tk.W, padx=20)
        
        self.expr_display = tk.Label(self.display_frame, text="...",
                                     bg=self.COLORS['bg_tertiary'],
                                     fg=self.COLORS['accent_secondary'],
                                     font=('Cascadia Code', 14),
                                     wraplength=350,
                                     justify=tk.LEFT,
                                     padx=15, pady=10)
        self.expr_display.pack(fill=tk.X, padx=20, pady=(0, 15))
        
        # Result display
        result_label = tk.Label(self.display_frame, text="Result:",
                               bg=self.COLORS['bg_secondary'],
                               fg=self.COLORS['text_muted'],
                               font=('Segoe UI', 10))
        result_label.pack(pady=(10, 5), anchor=tk.W, padx=20)
        
        self.result_display = tk.Label(self.display_frame, text="0",
                                       bg=self.COLORS['bg_primary'],
                                       fg=self.COLORS['accent_primary'],
                                       font=('Segoe UI', 36, 'bold'),
                                       padx=20, pady=20)
        self.result_display.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        # Explanation button
        self.explain_btn = tk.Button(self.display_frame,
                                    text="💡 Explain how I got this",
                                    bg=self.COLORS['bg_tertiary'],
                                    fg=self.COLORS['text_secondary'],
                                    font=('Segoe UI', 11),
                                    bd=0,
                                    command=self._explain_click)
        self.explain_btn.pack(pady=10)
        
        # Explanation text (hidden by default)
        self.explanation_text = tk.Label(self.display_frame, text="",
                                         bg=self.COLORS['bg_tertiary'],
                                         fg=self.COLORS['text_secondary'],
                                         font=('Segoe UI', 10),
                                         wraplength=350,
                                         justify=tk.LEFT,
                                         padx=15, pady=10)
        self.explanation_text.pack(fill=tk.X, padx=20, pady=(10, 20))
        self.explanation_text.pack_forget()
    
    def _create_history_panel(self):
        """Create history panel"""
        # Title
        title = tk.Label(self.history_frame, text="📜 History",
                        bg=self.COLORS['bg_secondary'],
                        fg=self.COLORS['text_primary'],
                        font=('Segoe UI', 12, 'bold'))
        title.pack(pady=(20, 10))
        
        # History list
        self.history_list = tk.Listbox(self.history_frame,
                                       bg=self.COLORS['bg_tertiary'],
                                       fg=self.COLORS['text_primary'],
                                       font=('Segoe UI', 10),
                                       bd=0,
                                       highlightthickness=0,
                                       selectbackground=self.COLORS['accent_primary'])
        self.history_list.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        # Scrollbar
        scrollbar = tk.Scrollbar(self.history_list)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.history_list.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.history_list.yview)
        
        # Bind selection
        self.history_list.bind('<<ListboxSelect>>', self._history_selected)
        
        # Buttons frame
        buttons_frame = tk.Frame(self.history_frame, bg=self.COLORS['bg_secondary'])
        buttons_frame.pack(pady=10, padx=15, fill=tk.X)
        
        # Export button
        export_btn = tk.Button(buttons_frame, text="📤 Export",
                              bg=self.COLORS['bg_tertiary'],
                              fg=self.COLORS['text_secondary'],
                              font=('Segoe UI', 10),
                              bd=0,
                              command=self._export_click)
        export_btn.pack(side=tk.LEFT)
        
        # Clear history button
        clear_hist_btn = tk.Button(buttons_frame, text="🗑️",
                                  bg=self.COLORS['bg_tertiary'],
                                  fg=self.COLORS['text_secondary'],
                                  font=('Segoe UI', 10),
                                  bd=0,
                                  command=self._clear_history_click)
        clear_hist_btn.pack(side=tk.RIGHT)
    
    # Event handlers
    def _mic_click(self):
        """Handle microphone button click"""
        if self.on_listen_click:
            self.on_listen_click()
    
    def _clear_click(self):
        """Handle clear button click"""
        if self.on_clear_click:
            self.on_clear_click()
    
    def _settings_click(self):
        """Handle settings button click"""
        if self.on_settings_click:
            self.on_settings_click()
    
    def _history_selected(self, event):
        """Handle history item selection"""
        selection = self.history_list.curselection()
        if selection and self.on_history_select:
            self.on_history_select(selection[0])
    
    def _export_click(self):
        """Handle export button click"""
        if self.on_export_click:
            self.on_export_click()
    
    def _clear_history_click(self):
        """Handle clear history button click"""
        self.history_list.delete(0, tk.END)
    
    def _mode_changed(self):
        """Handle mode change"""
        pass
    
    def _explain_click(self):
        """Handle explain button click"""
        if self.explanation_text.winfo_viewable():
            self.explanation_text.pack_forget()
        else:
            self.explanation_text.pack(fill=tk.X, padx=20, pady=(10, 20))
    
    def _on_close(self):
        """Handle window close"""
        self.stop_listening()
        self.root.destroy()
    
    # Public methods
    def start(self):
        """Start the GUI main loop"""
        self.root.mainloop()
    
    def set_listening(self, is_listening: bool):
        """Update listening state"""
        self.is_listening = is_listening
        
        if is_listening:
            self.mic_button.configure(bg=self.COLORS['accent_primary'],
                                     fg=self.COLORS['bg_primary'])
            self.voice_status.configure(text="Listening...",
                                       fg=self.COLORS['accent_primary'])
            self._animate_mic()
        else:
            self.mic_button.configure(bg=self.COLORS['bg_tertiary'],
                                     fg=self.COLORS['accent_primary'])
            self.voice_status.configure(text="Click to speak",
                                       fg=self.COLORS['text_muted'])
    
    def _animate_mic(self):
        """Animate microphone button"""
        if self.is_listening:
            # Pulse animation
            self.mic_button.configure(bg=self.COLORS['accent_primary'])
            self.root.after(500, lambda: self.mic_button.configure(
                bg=self.COLORS['bg_tertiary'] if not self.is_listening else self.COLORS['accent_primary']
            ))
            if self.is_listening:
                self.root.after(1000, self._animate_mic)
    
    def update_input(self, text: str):
        """Update input display"""
        self.input_display.configure(text=text if text else "...")
    
    def update_expression(self, text: str):
        """Update expression display"""
        self.expr_display.configure(text=text if text else "...")
    
    def update_result(self, text: str):
        """Update result display"""
        self.result_display.configure(text=text if text else "0")
    
    def update_explanation(self, text: str):
        """Update explanation display"""
        self.explanation_text.configure(text=text)
    
    def update_status(self, status: str, is_online: bool = True):
        """Update status indicator"""
        self.status_indicator.configure(text=f"● {status}")
        if is_online:
            self.status_indicator.configure(fg=self.COLORS['accent_success'])
        else:
            self.status_indicator.configure(fg=self.COLORS['accent_warning'])
    
    def update_voice_status(self, text: str):
        """Update voice status text"""
        self.voice_status.configure(text=text)
    
    def add_history_item(self, expression: str, result: str):
        """Add item to history"""
        self.history_list.insert(tk.END, f"{expression} = {result}")
        # Auto-scroll to bottom
        self.history_list.see(tk.END)
    
    def clear_history(self):
        """Clear history list"""
        self.history_list.delete(0, tk.END)
    
    def get_history_item(self, index: int) -> str:
        """Get history item at index"""
        try:
            return self.history_list.get(index)
        except:
            return ""
    
    def stop_listening(self):
        """Stop listening"""
        self.stop_listen_event.set()
        self.set_listening(False)


# Demo
if __name__ == "__main__":
    gui = AthenaGUI()
    gui.start()
