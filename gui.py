"""
GUI for Athena Voice Calculator
Tkinter-based graphical interface with enhanced modern design
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
from typing import Callable, Optional
import threading
import time
import math


class RoundedFrame(tk.Canvas):
    """Rounded frame with customizable corner radius"""
    
    def __init__(self, parent, width, height, bg_color, corner_radius=12, **kwargs):
        super().__init__(parent, width=width, height=height, bg=bg_color, 
                        highlightthickness=0, **kwargs)
        self.bg_color = bg_color
        self.corner_radius = corner_radius
        self.width = width
        self.height = height
        self._draw_rounded_rectangle()
    
    def _draw_rounded_rectangle(self):
        """Draw rounded rectangle"""
        self.delete("all")
        x1, y1 = self.corner_radius, 0
        x2, y2 = self.width - self.corner_radius, self.height
        x3, y3 = self.width, self.height
        x4, y4 = self.width, self.corner_radius
        
        # Draw the rounded shape
        self.create_polygon([
            x1, 0, x2, 0, x3, y4, x3, y3,
            x2, y3, x1, y3, 0, y2, 0, y1
        ], fill=self.bg_color, outline=self.bg_color)
        
        # Add subtle shadow effect with gradient lines
        for i in range(3):
            alpha = 30 - (i * 10)
            self.create_arc([0, 0, self.corner_radius*2, self.corner_radius*2],
                          start=90, extent=90, fill=self.bg_color, outline=self.bg_color)
            self.create_arc([self.width - self.corner_radius*2, 0, self.width, self.corner_radius*2],
                          start=0, extent=90, fill=self.bg_color, outline=self.bg_color)


class AnimatedMicButton(tk.Canvas):
    """Animated microphone button with pulse effect"""
    
    def __init__(self, parent, size=80, **kwargs):
        super().__init__(parent, width=size, height=size, bg='transparent', 
                        highlightthickness=0, **kwargs)
        self.size = size
        self.is_listening = False
        self.pulse_phase = 0
        self.pulse_after_id = None
        self._draw_button()
    
    def _draw_button(self, pulse_intensity=0):
        """Draw microphone button with optional pulse"""
        center = self.size // 2
        base_radius = (self.size // 2) - 10
        
        # Clear previous drawings
        self.delete("all")
        
        # Draw pulse rings (when listening)
        if self.is_listening:
            for i in range(3):
                ring_radius = base_radius + 15 + (i * 10) + (pulse_intensity * 20)
                if ring_radius < base_radius + 35:
                    alpha = int(100 - (i * 30) - (pulse_intensity * 50))
                    color = f"#{0:02x}{217:02x}{255:02x}"  # accent_primary with alpha
                    self.create_oval(center - ring_radius, center - ring_radius,
                                   center + ring_radius, center + ring_radius,
                                   outline=color, width=2)
        
        # Draw outer circle with gradient effect
        self.create_oval(5, 5, self.size-5, self.size-5,
                        fill='#21262D', outline='#00D9FF', width=3)
        
        # Draw microphone icon
        mic_x = center
        mic_y = center - 5
        
        # Mic body
        self.create_oval(mic_x - 10, mic_y - 15, mic_x + 10, mic_y + 10,
                        fill='#00D9FF', outline='')
        
        # Mic stand
        self.create_line(mic_x - 15, mic_y + 5, mic_x - 15, mic_y + 20,
                        fill='#00D9FF', width=3)
        self.create_line(mic_x + 15, mic_y + 5, mic_x + 15, mic_y + 20,
                        fill='#00D9FF', width=3)
        self.create_arc(mic_x - 18, mic_y + 15, mic_x + 18, mic_y + 30,
                       start=0, extent=180, style=tk.ARC, outline='#00D9FF', width=3)
    
    def set_listening(self, is_listening: bool):
        """Set listening state"""
        self.is_listening = is_listening
        if is_listening:
            self._start_pulse()
        else:
            self._stop_pulse()
    
    def _start_pulse(self):
        """Start pulse animation"""
        if not self.is_listening:
            return
        self.pulse_phase = (self.pulse_phase + 0.15) % (2 * math.pi)
        pulse_intensity = (math.sin(self.pulse_phase) + 1) / 2
        self._draw_button(pulse_intensity)
        self.pulse_after_id = self.after(50, self._start_pulse)
    
    def _stop_pulse(self):
        """Stop pulse animation"""
        if self.pulse_after_id:
            self.after_cancel(self.pulse_after_id)
            self.pulse_after_id = None
        self._draw_button(0)


class WaveformVisualizer(tk.Canvas):
    """Audio waveform visualization"""
    
    def __init__(self, parent, width=120, height=60, **kwargs):
        super().__init__(parent, width=width, height=height, bg='#21262D',
                        highlightthickness=0, **kwargs)
        self.width = width
        self.height = height
        self.is_active = False
        self.bars = []
        self.animation_id = None
        self._create_bars()
    
    def _create_bars(self):
        """Create initial bars"""
        bar_count = 15
        bar_width = 4
        gap = (self.width - (bar_count * bar_width)) / (bar_count + 1)
        
        for i in range(bar_count):
            x = gap + i * (bar_width + gap)
            bar = self.create_rectangle(x, self.height/2, x + bar_width, self.height/2,
                                       fill='#00D9FF', outline='')
            self.bars.append({'id': bar, 'x': x, 'base_y': self.height/2})
    
    def start(self):
        """Start animation"""
        self.is_active = True
        self._animate()
    
    def stop(self):
        """Stop animation"""
        self.is_active = False
        if self.animation_id:
            self.after_cancel(self.animation_id)
            self.animation_id = None
        self._reset_bars()
    
    def _animate(self):
        """Animate waveform"""
        if not self.is_active:
            return
        
        import random
        for bar in self.bars:
            # Random height between 10 and height-10
            bar_height = random.randint(10, self.height - 20)
            y1 = (self.height - bar_height) / 2
            y2 = y1 + bar_height
            self.coords(bar['id'], bar['x'], y1, bar['x'] + 4, y2)
        
        self.animation_id = self.after(100, self._animate)
    
    def _reset_bars(self):
        """Reset bars to default state"""
        for bar in self.bars:
            y1 = self.height / 2 - 2
            y2 = self.height / 2 + 2
            self.coords(bar['id'], bar['x'], y1, bar['x'] + 4, y2)


class AthenaGUI:
    """Main GUI for Athena Voice Calculator with enhanced design"""
    
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
        self.root.geometry("950x720")
        self.root.configure(bg=self.COLORS['bg_primary'])
        
        # Enable transparency support
        self.root.attributes('-alpha', 1.0)
        
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
        self._create_main_container()
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
    
    def _create_header(self):
        """Create header bar with gradient effect"""
        header = tk.Frame(self.root, bg=self.COLORS['bg_secondary'], height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        # Add subtle gradient bar at top
        gradient_bar = tk.Frame(header, bg=self.COLORS['accent_primary'], height=3)
        gradient_bar.pack(fill=tk.X)
        
        # Left side - Title with icon
        title_frame = tk.Frame(header, bg=self.COLORS['bg_secondary'])
        title_frame.pack(side=tk.LEFT, padx=20, pady=10)
        
        # AI Icon (brain with spark)
        icon_label = tk.Label(title_frame, text="🧠",
                            bg=self.COLORS['bg_secondary'],
                            fg=self.COLORS['accent_primary'],
                            font=('Segoe UI', 22))
        icon_label.pack(side=tk.LEFT)
        
        # Title text
        title_text = tk.Frame(title_frame, bg=self.COLORS['bg_secondary'])
        title_text.pack(side=tk.LEFT, padx=(10, 0))
        
        title = tk.Label(title_text, text="Athena",
                        bg=self.COLORS['bg_secondary'],
                        fg=self.COLORS['text_primary'],
                        font=('Segoe UI', 18, 'bold'))
        title.pack(anchor=tk.W)
        
        subtitle = tk.Label(title_text, text="Voice Calculator",
                           bg=self.COLORS['bg_secondary'],
                           fg=self.COLORS['text_muted'],
                           font=('Segoe UI', 9))
        subtitle.pack(anchor=tk.W)
        
        # Right side - Controls
        right_frame = tk.Frame(header, bg=self.COLORS['bg_secondary'])
        right_frame.pack(side=tk.RIGHT, padx=20, pady=10)
        
        # Status indicator with glow effect
        self.status_frame = tk.Frame(right_frame, bg=self.COLORS['bg_secondary'])
        self.status_frame.pack(side=tk.RIGHT)
        
        self.status_indicator = tk.Label(self.status_frame, text="●",
                                         bg=self.COLORS['bg_secondary'],
                                         fg=self.COLORS['accent_success'],
                                         font=('Segoe UI', 12))
        self.status_indicator.pack(side=tk.LEFT)
        
        self.status_text = tk.Label(self.status_frame, text=" Online",
                                    bg=self.COLORS['bg_secondary'],
                                    fg=self.COLORS['text_secondary'],
                                    font=('Segoe UI', 10))
        self.status_text.pack(side=tk.LEFT)
        
        # Settings button
        settings_btn = tk.Button(right_frame, text="⚙️",
                                bg=self.COLORS['bg_tertiary'],
                                fg=self.COLORS['text_secondary'],
                                font=('Segoe UI', 14),
                                bd=0,
                                padx=10,
                                cursor='hand2',
                                command=self._settings_click)
        settings_btn.pack(side=tk.RIGHT, padx=(15, 0))
        
        # Minimize button
        min_btn = tk.Button(right_frame, text="─",
                           bg=self.COLORS['bg_tertiary'],
                           fg=self.COLORS['text_secondary'],
                           font=('Segoe UI', 14),
                           bd=0,
                           width=3,
                           cursor='hand2',
                           command=lambda: self.root.iconify())
        min_btn.pack(side=tk.RIGHT)
    
    def _create_main_container(self):
        """Create main container with padding"""
        container = tk.Frame(self.root, bg=self.COLORS['bg_primary'])
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Create three columns with rounded panels
        # Left: Voice panel
        self.voice_container = tk.Frame(container, bg=self.COLORS['bg_primary'])
        self.voice_container.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # Center: Display panel
        self.display_container = tk.Frame(container, bg=self.COLORS['bg_primary'])
        self.display_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Right: History panel
        self.history_container = tk.Frame(container, bg=self.COLORS['bg_primary'])
        self.history_container.pack(side=tk.RIGHT, fill=tk.Y)
    
    def _create_voice_panel(self):
        """Create voice input panel with modern design"""
        # Panel background with rounded corners
        voice_bg = tk.Frame(self.voice_container, bg=self.COLORS['bg_secondary'],
                           padx=15, pady=15)
        voice_bg.pack(fill=tk.Y)
        
        # Section title with icon
        title_frame = tk.Frame(voice_bg, bg=self.COLORS['bg_secondary'])
        title_frame.pack(pady=(10, 20))
        
        title_icon = tk.Label(title_frame, text="🎤",
                             bg=self.COLORS['bg_secondary'],
                             font=('Segoe UI', 14))
        title_icon.pack(side=tk.LEFT)
        
        title = tk.Label(title_frame, text=" Voice Input",
                        bg=self.COLORS['bg_secondary'],
                        fg=self.COLORS['text_primary'],
                        font=('Segoe UI', 13, 'bold'))
        title.pack(side=tk.LEFT, padx=(5, 0))
        
        # Waveform visualizer
        self.waveform = WaveformVisualizer(self.voice_container, width=130, height=60)
        self.waveform.pack(pady=(0, 15))
        
        # Microphone button
        self.mic_button = AnimatedMicButton(self.voice_container, size=80)
        self.mic_button.pack(pady=15)
        
        # Bind click event
        self.mic_button.bind('<Button-1>', lambda e: self._mic_click())
        
        # Status label with animation
        self.voice_status = tk.Label(voice_bg, text="Click to speak",
                                    bg=self.COLORS['bg_secondary'],
                                    fg=self.COLORS['text_muted'],
                                    font=('Segoe UI', 11))
        self.voice_status.pack(pady=10)
        
        # Mode toggle frame
        mode_frame = tk.LabelFrame(voice_bg, text=" Mode",
                                   bg=self.COLORS['bg_secondary'],
                                   fg=self.COLORS['text_secondary'],
                                   font=('Segoe UI', 10),
                                   padx=10, pady=10)
        mode_frame.pack(pady=20, fill=tk.X)
        
        self.mode_var = tk.StringVar(value="single")
        
        single_btn = tk.Radiobutton(mode_frame, text="🎯 Single Command",
                                    variable=self.mode_var, value="single",
                                    bg=self.COLORS['bg_secondary'],
                                    fg=self.COLORS['text_secondary'],
                                    selectcolor=self.COLORS['bg_tertiary'],
                                    activebackground=self.COLORS['bg_secondary'],
                                    font=('Segoe UI', 10),
                                    command=self._mode_changed)
        single_btn.pack(anchor=tk.W, pady=5)
        
        continuous_btn = tk.Radiobutton(mode_frame, text="🔄 Continuous",
                                       variable=self.mode_var, value="continuous",
                                       bg=self.COLORS['bg_secondary'],
                                       fg=self.COLORS['text_secondary'],
                                       selectcolor=self.COLORS['bg_tertiary'],
                                       activebackground=self.COLORS['bg_secondary'],
                                       font=('Segoe UI', 10),
                                       command=self._mode_changed)
        continuous_btn.pack(anchor=tk.W, pady=5)
        
        # Wake word label
        wake_frame = tk.Frame(voice_bg, bg=self.COLORS['bg_tertiary'], padx=10, pady=8)
        wake_frame.pack(pady=15, fill=tk.X)
        
        wake_label = tk.Label(wake_frame,
                             text="💡 Say 'Hey Athena'\nto activate",
                             bg=self.COLORS['bg_tertiary'],
                             fg=self.COLORS['text_muted'],
                             font=('Segoe UI', 9),
                             justify=tk.CENTER)
        wake_label.pack()
        
        # Action buttons
        btn_frame = tk.Frame(voice_bg, bg=self.COLORS['bg_secondary'])
        btn_frame.pack(pady=15, fill=tk.X)
        
        clear_btn = tk.Button(btn_frame, text="🗑️ Clear",
                             bg=self.COLORS['bg_tertiary'],
                             fg=self.COLORS['text_secondary'],
                             font=('Segoe UI', 10),
                             bd=0,
                             padx=15, pady=8,
                             cursor='hand2',
                             command=self._clear_click)
        clear_btn.pack(fill=tk.X)
    
    def _create_display_panel(self):
        """Create main display panel with modern design"""
        # Panel background
        display_bg = tk.Frame(self.display_container, bg=self.COLORS['bg_secondary'],
                            padx=20, pady=15)
        display_bg.pack(fill=tk.BOTH, expand=True)
        
        # Section title
        title_frame = tk.Frame(display_bg, bg=self.COLORS['bg_secondary'])
        title_frame.pack(pady=(5, 20), fill=tk.X)
        
        title_icon = tk.Label(title_frame, text="📊",
                             bg=self.COLORS['bg_secondary'],
                             font=('Segoe UI', 14))
        title_icon.pack(side=tk.LEFT)
        
        title = tk.Label(title_frame, text=" Calculator",
                        bg=self.COLORS['bg_secondary'],
                        fg=self.COLORS['text_primary'],
                        font=('Segoe UI', 13, 'bold'))
        title.pack(side=tk.LEFT, padx=(5, 0))
        
        # Input display card
        input_card = tk.Frame(display_bg, bg=self.COLORS['bg_tertiary'], padx=15, pady=12)
        input_card.pack(fill=tk.X, pady=(0, 12))
        
        input_label = tk.Label(input_card, text="🎙️ Your voice input:",
                              bg=self.COLORS['bg_tertiary'],
                              fg=self.COLORS['text_muted'],
                              font=('Segoe UI', 10, 'bold'))
        input_label.pack(anchor=tk.W)
        
        self.input_display = tk.Label(input_card, text="...",
                                      bg=self.COLORS['bg_tertiary'],
                                      fg=self.COLORS['text_primary'],
                                      font=('Segoe UI', 14),
                                      wraplength=380,
                                      justify=tk.LEFT,
                                      anchor=tk.W)
        self.input_display.pack(fill=tk.X, pady=(8, 0))
        
        # Expression display card
        expr_card = tk.Frame(display_bg, bg=self.COLORS['bg_tertiary'], padx=15, pady=12)
        expr_card.pack(fill=tk.X, pady=(0, 12))
        
        expr_label = tk.Label(expr_card, text="🔢 Parsed expression:",
                             bg=self.COLORS['bg_tertiary'],
                             fg=self.COLORS['text_muted'],
                             font=('Segoe UI', 10, 'bold'))
        expr_label.pack(anchor=tk.W)
        
        self.expr_display = tk.Label(expr_card, text="...",
                                     bg=self.COLORS['bg_tertiary'],
                                     fg=self.COLORS['accent_secondary'],
                                     font=('Cascadia Code', 15, 'bold'),
                                     wraplength=380,
                                     justify=tk.LEFT,
                                     anchor=tk.W)
        self.expr_display.pack(fill=tk.X, pady=(8, 0))
        
        # Result display card with accent border
        result_card = tk.Frame(display_bg, bg=self.COLORS['bg_primary'],
                              padx=20, pady=15, highlightbackground=self.COLORS['accent_primary'],
                              highlightthickness=2)
        result_card.pack(fill=tk.X, pady=(0, 15))
        
        result_label = tk.Label(result_card, text="✨ Result:",
                               bg=self.COLORS['bg_primary'],
                               fg=self.COLORS['text_muted'],
                               font=('Segoe UI', 10, 'bold'))
        result_label.pack(anchor=tk.W)
        
        # Result value with large font
        self.result_display = tk.Label(result_card, text="0",
                                       bg=self.COLORS['bg_primary'],
                                       fg=self.COLORS['accent_primary'],
                                       font=('Segoe UI', 42, 'bold'))
        self.result_display.pack(fill=tk.X, pady=(10, 5))
        
        # Explanation section
        explain_frame = tk.Frame(display_bg, bg=self.COLORS['bg_tertiary'], padx=15, pady=10)
        explain_frame.pack(fill=tk.X)
        
        self.explain_btn = tk.Button(explain_frame,
                                    text="💡 Explain how I got this",
                                    bg=self.COLORS['bg_tertiary'],
                                    fg=self.COLORS['text_secondary'],
                                    font=('Segoe UI', 11),
                                    bd=0,
                                    padx=10, pady=5,
                                    cursor='hand2',
                                    command=self._explain_click)
        self.explain_btn.pack()
        
        # Explanation text (hidden by default)
        self.explanation_text = tk.Label(display_bg, text="",
                                         bg=self.COLORS['bg_tertiary'],
                                         fg=self.COLORS['text_secondary'],
                                         font=('Segoe UI', 10),
                                         wraplength=380,
                                         justify=tk.LEFT,
                                         padx=15, pady=10)
        self.explanation_text.pack(fill=tk.X, pady=(10, 0))
        self.explanation_text.pack_forget()
    
    def _create_history_panel(self):
        """Create history panel with modern design"""
        # Panel background
        history_bg = tk.Frame(self.history_container, bg=self.COLORS['bg_secondary'],
                             padx=15, pady=15)
        history_bg.pack(fill=tk.BOTH, expand=True)
        
        # Section title
        title_frame = tk.Frame(history_bg, bg=self.COLORS['bg_secondary'])
        title_frame.pack(pady=(5, 15), fill=tk.X)
        
        title_icon = tk.Label(title_frame, text="📜",
                             bg=self.COLORS['bg_secondary'],
                             font=('Segoe UI', 14))
        title_icon.pack(side=tk.LEFT)
        
        title = tk.Label(title_frame, text=" History",
                        bg=self.COLORS['bg_secondary'],
                        fg=self.COLORS['text_primary'],
                        font=('Segoe UI', 13, 'bold'))
        title.pack(side=tk.LEFT, padx=(5, 0))
        
        # History list with custom styling
        list_frame = tk.Frame(history_bg, bg=self.COLORS['bg_tertiary'])
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        self.history_list = tk.Listbox(list_frame,
                                       bg=self.COLORS['bg_tertiary'],
                                       fg=self.COLORS['text_primary'],
                                       font=('Segoe UI', 10),
                                       bd=0,
                                       highlightthickness=0,
                                       selectbackground=self.COLORS['accent_primary'],
                                       selectforeground=self.COLORS['bg_primary'],
                                       activestyle='none',
                                       padding=5)
        self.history_list.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = tk.Scrollbar(list_frame, width=8,
                                 troughcolor=self.COLORS['bg_tertiary'],
                                 bg=self.COLORS['text_muted'])
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.history_list.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.history_list.yview)
        
        # Bind selection
        self.history_list.bind('<<ListboxSelect>>', self._history_selected)
        
        # Buttons frame
        buttons_frame = tk.Frame(history_bg, bg=self.COLORS['bg_secondary'])
        buttons_frame.pack(fill=tk.X)
        
        # Export button
        export_btn = tk.Button(buttons_frame, text="📤 Export",
                              bg=self.COLORS['bg_tertiary'],
                              fg=self.COLORS['text_secondary'],
                              font=('Segoe UI', 10),
                              bd=0,
                              padx=12, pady=6,
                              cursor='hand2',
                              command=self._export_click)
        export_btn.pack(side=tk.LEFT)
        
        # Clear history button
        clear_hist_btn = tk.Button(buttons_frame, text="🗑️ Clear",
                                  bg=self.COLORS['bg_tertiary'],
                                  fg=self.COLORS['text_secondary'],
                                  font=('Segoe UI', 10),
                                  bd=0,
                                  padx=12, pady=6,
                                  cursor='hand2',
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
            self.explanation_text.pack(fill=tk.X, pady=(10, 10))
    
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
            self.mic_button.set_listening(True)
            self.waveform.start()
            self.voice_status.configure(text="Listening...",
                                       fg=self.COLORS['accent_primary'])
            # Add status to header
            self.status_text.configure(text=" Listening")
            self.status_indicator.configure(fg=self.COLORS['accent_primary'])
        else:
            self.mic_button.set_listening(False)
            self.waveform.stop()
            self.voice_status.configure(text="Click to speak",
                                       fg=self.COLORS['text_muted'])
            # Update header status
            self.status_text.configure(text=" Online")
            self.status_indicator.configure(fg=self.COLORS['accent_success'])
    
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
        self.status_text.configure(text=f" {status}")
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
