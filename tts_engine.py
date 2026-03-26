"""
Text-to-Speech Engine for Athena Voice Calculator
Handles voice output using pyttsx3
"""

import pyttsx3
import threading
from typing import Optional, Callable


class TTSEngine:
    """Text-to-Speech engine for Athena"""
    
    # Voice personality configurations
    PERSONALITIES = {
        'friendly': {
            'rate': 180,
            'volume': 1.0,
            'pitch': 1.0
        },
        'professional': {
            'rate': 160,
            'volume': 0.9,
            'pitch': 1.0
        },
        'casual': {
            'rate': 200,
            'volume': 1.0,
            'pitch': 1.1
        },
        'robot': {
            'rate': 140,
            'volume': 0.8,
            'pitch': 0.8
        }
    }
    
    def __init__(self):
        self.engine = None
        self.is_initialized = False
        self.current_personality = 'friendly'
        
        # Queue for speech
        self.speech_queue = []
        self.is_speaking = False
        self.speech_lock = threading.Lock()
        
        # Callbacks
        self.on_speech_start: Optional[Callable] = None
        self.on_speech_end: Optional[Callable] = None
        
        # Initialize the engine
        self._initialize()
    
    def _initialize(self):
        """Initialize the TTS engine"""
        try:
            self.engine = pyttsx3.init()
            
            # Apply default settings
            self.set_personality(self.current_personality)
            
            # Get available voices
            voices = self.engine.getProperty('voices')
            if voices:
                # Try to find a good voice
                for voice in voices:
                    if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                        self.engine.setProperty('voice', voice.id)
                        break
            
            self.is_initialized = True
            
        except Exception as e:
            print(f"Warning: Could not initialize TTS engine: {e}")
            self.is_initialized = False
    
    def set_personality(self, personality: str):
        """Set the voice personality"""
        if personality in self.PERSONALITIES:
            self.current_personality = personality
            settings = self.PERSONALITIES[personality]
            
            if self.engine:
                self.engine.setProperty('rate', settings['rate'])
                self.engine.setProperty('volume', settings['volume'])
    
    def get_available_personalities(self) -> list:
        """Get list of available personalities"""
        return list(self.PERSONALITIES.keys())
    
    def set_rate(self, rate: int):
        """Set speech rate (words per minute)"""
        if self.engine:
            self.engine.setProperty('rate', rate)
    
    def set_volume(self, volume: float):
        """Set volume (0.0 to 1.0)"""
        if self.engine:
            self.engine.setProperty('volume', max(0.0, min(1.0, volume)))
    
    def set_voice(self, voice_id: str):
        """Set voice by ID"""
        if self.engine:
            try:
                self.engine.setProperty('voice', voice_id)
            except:
                pass
    
    def get_available_voices(self) -> list:
        """Get list of available voices"""
        if self.engine:
            return self.engine.getProperty('voices')
        return []
    
    def speak(self, text: str, blocking: bool = False):
        """
        Speak the given text
        blocking: If True, wait for speech to complete. If False, speak asynchronously.
        """
        if not self.is_initialized or not self.engine:
            return
            
        if blocking:
            self._speak_blocking(text)
        else:
            thread = threading.Thread(target=self._speak_blocking, args=(text,))
            thread.daemon = True
            thread.start()
    
    def _speak_blocking(self, text: str):
        """Speak text synchronously"""
        with self.speech_lock:
            self.is_speaking = True
            
            if self.on_speech_start:
                self.on_speech_start(text)
            
            try:
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception as e:
                print(f"TTS Error: {e}")
            
            self.is_speaking = False
            
            if self.on_speech_end:
                self.on_speech_end(text)
    
    def speak_response(self, result: float, expression: str = None):
        """Generate and speak a natural language response"""
        # Format the result
        if result == int(result):
            result_text = str(int(result))
        else:
            result_text = f"{result:.2f}"
        
        # Generate response based on expression type
        response = self._generate_response(result_text, expression)
        
        self.speak(response)
    
    def _generate_response(self, result: str, expression: str = None) -> str:
        """Generate a natural language response"""
        import random
        
        # Response templates
        templates = [
            f"The result is {result}",
            f"That equals {result}",
            f"Here's your answer: {result}",
            f"The calculation gives us {result}",
            f"Result: {result}",
        ]
        
        # Add expression context if available
        if expression:
            templates.extend([
                f"{expression} equals {result}",
                f"Based on your calculation, the answer is {result}",
            ])
        
        return random.choice(templates)
    
    def speak_error(self, error_type: str):
        """Speak an error message"""
        import random
        
        error_messages = {
            'not_understood': [
                "I didn't catch that. Please try again.",
                "Sorry, I didn't understand. Could you repeat that?",
                "I couldn't understand that. Please speak more clearly."
            ],
            'ambiguous': [
                "I need a bit more clarity. Could you repeat that?",
                "I wasn't sure about that. Could you clarify?",
            ],
            'no_result': [
                "I couldn't calculate that. Please check your expression.",
                "I'm having trouble with that calculation.",
            ],
            'network': [
                "I can't connect to the speech service right now. Please check your internet.",
                "Working in offline mode now.",
            ]
        }
        
        messages = error_messages.get(error_type, error_messages['not_understood'])
        self.speak(random.choice(messages))
    
    def speak_wake(self):
        """Speak confirmation when wake word is detected"""
        self.speak("I'm listening")
    
    def speak_help(self):
        """Speak available commands"""
        help_text = """
        You can ask me calculations like:
        What is 25 percent of 480?
        Add 50 to the previous result
        Calculate the square root of 144
        
        Or say hey Athena to activate me.
        """
        self.speak(help_text)
    
    def stop(self):
        """Stop current speech"""
        if self.engine:
            try:
                self.engine.stop()
            except:
                pass
        self.is_speaking = False
    
    def is_currently_speaking(self) -> bool:
        """Check if currently speaking"""
        return self.is_speaking
    
    def queue_speech(self, text: str):
        """Add text to speech queue"""
        self.speech_queue.append(text)
        
        if not self.is_speaking:
            self._process_queue()
    
    def _process_queue(self):
        """Process speech queue"""
        while self.speech_queue and not self.is_speaking:
            text = self.speech_queue.pop(0)
            self.speak(text, blocking=True)


# Demo usage
if __name__ == "__main__":
    tts = TTSEngine()
    
    if tts.is_initialized:
        print("TTS Engine initialized!")
        print(f"Available personalities: {tts.get_available_personalities()}")
        print(f"Available voices: {len(tts.get_available_voices())}")
        
        # Test speech
        print("\nTesting speech...")
        tts.speak("Hello! I am Athena, your voice calculator.")
        tts.speak("Try saying: What is 25 percent of 480?")
    else:
        print("TTS Engine not available")
