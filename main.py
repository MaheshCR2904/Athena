"""
Athena Voice Calculator - Main Entry Point
AI-powered voice-controlled calculator with natural language understanding
"""

import threading
import time
import tkinter as tk
from gui import AthenaGUI
from nlp_engine import NLPEngine
from speech_handler import SpeechHandler
from tts_engine import TTSEngine
from context_manager import ContextManager
from calculator import Calculator


class AthenaApp:
    """Main application class for Athena Voice Calculator"""
    
    def __init__(self):
        # Initialize components
        self.gui = AthenaGUI()
        self.nlp = NLPEngine()
        self.speech = SpeechHandler()
        self.tts = TTSEngine()
        self.context = ContextManager()
        self.calc = Calculator()
        
        # State
        self.is_continuous = False
        self.stop_event = threading.Event()
        self.current_expression = ""
        self.current_result = 0
        self.current_explanation = ""
        
        # Setup callbacks
        self._setup_callbacks()
        
        # Load history into GUI
        self._load_history()
        
        # Start with text input mode if no microphone
        if not self.speech.microphone_available:
            self.gui.update_voice_status("No microphone - click for text input")
    
    def _setup_callbacks(self):
        """Setup GUI callbacks"""
        self.gui.on_listen_click = self.start_listening
        self.gui.on_clear_click = self.clear_display
        self.gui.on_history_select = self.on_history_selected
        self.gui.on_export_click = self.export_history
        self.gui.on_settings_click = self.show_settings
    
    def _load_history(self):
        """Load history into GUI"""
        history = self.context.get_history()
        for record in history:
            self.gui.add_history_item(
                record['expression'],
                record['formatted_result']
            )
    
    def start_listening(self):
        """Start voice recognition"""
        if self.gui.is_listening:
            self.stop_listening()
            return
        
        # Check if microphone is available
        if not self.speech.microphone_available:
            self.gui.update_voice_status("No microphone - using text input")
            self._show_text_input_dialog()
            return
        
        self.gui.set_listening(True)
        self.gui.update_status("Listening...")
        
        # Start listening in a separate thread
        thread = threading.Thread(target=self._listen_loop)
        thread.daemon = True
        thread.start()
    
    def _listen_loop(self):
        """Main listening loop"""
        while self.gui.is_listening and not self.stop_event.is_set():
            try:
                # Listen for speech
                text = self.speech.listen_once(timeout=3.0)
                
                if text:
                    # Check for wake word
                    if any(wake in text.lower() for wake in ['hey athena', 'athena', 'okay athena']):
                        self.tts.speak("I'm listening")
                        self.gui.update_voice_status("Say your calculation...")
                        
                        # Listen for the actual command
                        text = self.speech.listen_once(timeout=5.0)
                        if text:
                            self.process_input(text)
                    else:
                        # Process as regular input
                        self.process_input(text)
                        
            except Exception as e:
                print(f"Listen error: {e}")
                time.sleep(0.5)
        
        self.gui.set_listening(False)
    
    def stop_listening(self):
        """Stop voice recognition"""
        self.gui.set_listening(False)
        self.stop_event.set()
        self.stop_event.clear()
    
    def process_input(self, text: str):
        """Process voice input"""
        if not text:
            return
        
        # Update GUI with input
        self.gui.update_input(text)
        self.gui.update_status("Processing...")
        
        # Check if context is needed
        if self.context.get_last_result() is not None:
            self.nlp.set_context(
                self.context.get_last_result(),
                self.context.get_last_expression()
            )
        
        # Parse the input
        parsed = self.nlp.parse(text)
        
        if parsed['needs_clarification']:
            # Ask for clarification
            self.gui.update_expression("Needs clarification")
            self.tts.speak(parsed['clarification'])
            self.gui.update_status("Ready")
            return
        
        if not parsed['is_valid']:
            self.gui.update_expression("Could not understand")
            self.tts.speak_error('not_understood')
            self.gui.update_status("Ready")
            return
        
        # Update expression display
        self.gui.update_expression(parsed['expression'])
        self.current_expression = parsed['expression']
        
        # Evaluate the expression
        result, error = self.calc.evaluate(parsed['expression'])
        
        if error:
            self.gui.update_result("Error")
            self.tts.speak_error('no_result')
            self.gui.update_status("Ready")
            return
        
        # Format result
        formatted_result = self.calc.format_result(result)
        self.gui.update_result(formatted_result)
        self.current_result = result
        
        # Generate explanation
        self.current_explanation = self.calc.explain_calculation(
            parsed['expression'], result
        )
        self.gui.update_explanation(self.current_explanation)
        
        # Store in context
        self.context.store_result(
            parsed['expression'],
            result,
            text
        )
        
        # Add to history
        self.gui.add_history_item(parsed['expression'], formatted_result)
        
        # Speak the result
        self.tts.speak_response(result, parsed['expression'])
        
        self.gui.update_status("Ready")
    
    def clear_display(self):
        """Clear the display"""
        self.gui.update_input("")
        self.gui.update_expression("")
        self.gui.update_result("0")
        self.gui.update_explanation("")
        self.current_expression = ""
        self.current_result = 0
        self.current_explanation = ""
    
    def on_history_selected(self, index: int):
        """Handle history item selection"""
        record = self.context.get_previous(index)
        if record:
            self.gui.update_input(record['raw_input'] or record['expression'])
            self.gui.update_expression(record['expression'])
            self.gui.update_result(record['formatted_result'])
            
            # Set context
            self.nlp.set_context(record['result'], record['expression'])
    
    def export_history(self):
        """Export history to file"""
        success = self.context.export_to_file()
        if success:
            self.tts.speak("History exported successfully")
        else:
            self.tts.speak("Could not export history")
    
    def show_settings(self):
        """Show settings dialog"""
        # Simple settings message
        self.tts.speak("Settings coming soon")
    
    def _show_text_input_dialog(self):
        """Show text input dialog when microphone is not available"""
        # Create a simple dialog
        dialog = tk.Toplevel(self.gui.root)
        dialog.title("Text Input")
        dialog.geometry("400x150")
        dialog.configure(bg=self.gui.COLORS['bg_secondary'])
        
        # Label
        label = tk.Label(dialog, text="Enter your calculation:",
                        bg=self.gui.COLORS['bg_secondary'],
                        fg=self.gui.COLORS['text_primary'],
                        font=('Segoe UI', 12))
        label.pack(pady=10)
        
        # Entry
        entry = tk.Entry(dialog, font=('Segoe UI', 14),
                        bg=self.gui.COLORS['bg_tertiary'],
                        fg=self.gui.COLORS['text_primary'],
                        insertbackground=self.gui.COLORS['text_primary'])
        entry.pack(pady=10, padx=20, fill=tk.X)
        entry.focus()
        
        def submit():
            text = entry.get()
            dialog.destroy()
            if text:
                self.process_input(text)
        
        # Submit button
        btn = tk.Button(dialog, text="Calculate", command=submit,
                       bg=self.gui.COLORS['accent_primary'],
                       fg=self.gui.COLORS['bg_primary'],
                       font=('Segoe UI', 12, 'bold'),
                       bd=0)
        btn.pack(pady=10)
        
        # Bind Enter key
        entry.bind('<Return>', lambda e: submit())
    
    def run(self):
        """Run the application"""
        # Welcome message
        self.tts.speak("Athena is ready. Click the microphone or say hey Athena to start.")
        self.gui.update_status("Ready")
        
        # Start GUI
        self.gui.start()


def main():
    """Main entry point"""
    app = AthenaApp()
    app.run()


if __name__ == "__main__":
    main()
