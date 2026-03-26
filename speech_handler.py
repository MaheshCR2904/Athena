"""
Speech Handler for Athena Voice Calculator
Handles voice input using speech recognition
"""

import speech_recognition as sr
import threading
import time
from typing import Optional, Callable, Dict


class SpeechHandler:
    """Handles speech recognition and wake word detection"""
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = None
        self.microphone_available = False
        
        # Configuration
        self.energy_threshold = 4000  # Minimum audio energy to consider
        self.phrase_time_limit = 10  # Maximum phrase length in seconds
        self.ambient_noise_duration = 1  # Seconds to calibrate for ambient noise
        
        # State
        self.is_listening = False
        self.is_continuous_mode = False
        self.wake_word_detected = False
        self.wake_words = ['athena', 'hey athena', 'okay athena', 'oi athena']
        
        # Callbacks
        self.on_wake_word: Optional[Callable] = None
        self.on_speech_result: Optional[Callable] = None
        self.on_error: Optional[Callable] = None
        self.on_status_change: Optional[Callable] = None
        
        # Calibration status
        self.is_calibrated = False
        
        # Initialize microphone
        try:
            self.microphone = sr.Microphone()
            self.microphone_available = True
            # Adjust for ambient noise
            try:
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=self.ambient_noise_duration)
                self.is_calibrated = True
            except Exception as e:
                print(f"Warning: Could not calibrate microphone: {e}")
        except Exception as e:
            # Microphone not available - will use text input instead
            self.microphone = None
            self.microphone_available = False
    
    def set_wake_word_callback(self, callback: Callable):
        """Set callback for wake word detection"""
        self.on_wake_word = callback
    
    def set_speech_result_callback(self, callback: Callable):
        """Set callback for speech results"""
        self.on_speech_result = callback
    
    def set_error_callback(self, callback: Callable):
        """Set callback for errors"""
        self.on_error = callback
    
    def set_status_callback(self, callback: Callable):
        """Set callback for status changes"""
        self.on_status_change = callback
    
    def update_status(self, status: str):
        """Update status and notify callback"""
        if self.on_status_change:
            self.on_status_change(status)
    
    def listen_once(self, timeout: float = 5.0) -> Optional[str]:
        """
        Listen for a single speech input
        Returns: The recognized text or None
        """
        if not self.microphone_available:
            self._handle_error("Microphone not available. Please check your audio device.")
            return None
        
        if not self.is_calibrated:
            try:
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                self.is_calibrated = True
            except Exception as e:
                self._handle_error(f"Microphone error: {e}")
                return None
        
        try:
            with self.microphone as source:
                self.update_status("Listening...")
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=self.phrase_time_limit)
            
            self.update_status("Processing...")
            
            # Try Google Speech Recognition first (requires internet)
            try:
                text = self.recognizer.recognize_google(audio)
                self.update_status("Ready")
                return text
            except sr.UnknownValueError:
                # Try with Sphinx as fallback (offline)
                try:
                    text = self.recognizer.recognize_sphinx(audio)
                    self.update_status("Ready")
                    return text
                except:
                    self._handle_error("Could not understand speech. Please try again.")
                    return None
            except sr.RequestError as e:
                # Google service unavailable, try offline
                try:
                    text = self.recognizer.recognize_sphinx(audio)
                    self.update_status("Ready (Offline)")
                    return text
                except:
                    self._handle_error(f"Speech service unavailable: {e}")
                    return None
                    
        except sr.WaitTimeoutError:
            self._handle_error("No speech detected. Please try again.")
            return None
        except Exception as e:
            self._handle_error(f"Error during listening: {e}")
            return None
    
    def listen_continuous(self, stop_event: threading.Event):
        """
        Continuously listen for speech input
        stop_event: Threading event to stop listening
        """
        self.is_listening = True
        self.update_status("Continuous listening mode")
        
        while not stop_event.is_set():
            text = self.listen_once(timeout=3.0)
            
            if text:
                text_lower = text.lower()
                
                # Check for wake word
                if any(wake_word in text_lower for wake_word in self.wake_words):
                    self.wake_word_detected = True
                    if self.on_wake_word:
                        self.on_wake_word(text)
                else:
                    # Process as regular speech
                    if self.on_speech_result:
                        self.on_speech_result(text)
            
            time.sleep(0.1)
        
        self.is_listening = False
        self.update_status("Ready")
    
    def start_continuous_listening(self) -> threading.Thread:
        """Start continuous listening in a separate thread"""
        stop_event = threading.Event()
        thread = threading.Thread(target=self.listen_continuous, args=(stop_event,))
        thread.daemon = True
        thread.start()
        return stop_event
    
    def stop_listening(self):
        """Stop continuous listening"""
        self.is_listening = False
        self.update_status("Ready")
    
    def check_wake_word(self, audio) -> bool:
        """Check if audio contains wake word"""
        try:
            text = self.recognizer.recognize_google(audio).lower()
            return any(wake_word in text for wake_word in self.wake_words)
        except:
            return False
    
    def _handle_error(self, message: str):
        """Handle and report errors"""
        if self.on_error:
            self.on_error(message)
        else:
            print(f"Error: {message}")
        self.update_status("Ready")
    
    def get_available_microphones(self) -> Dict:
        """Get list of available microphones"""
        try:
            mics = sr.Microphone.list_microphone_names()
            return {i: name for i, name in enumerate(mics)}
        except:
            return {0: "Default Microphone"}
    
    def test_microphone(self) -> bool:
        """Test if microphone is working"""
        if not self.microphone_available:
            return False
        try:
            with self.microphone as source:
                audio = self.recognizer.listen(source, timeout=1)
            return True
        except:
            return False


# Demo usage
if __name__ == "__main__":
    handler = SpeechHandler()
    
    print("Available microphones:", handler.get_available_microphones())
    print("\nTesting microphone...")
    
    if handler.test_microphone():
        print("Microphone is working!")
        print("\nSay something (press Ctrl+C to stop)...")
        
        while True:
            text = handler.listen_once()
            if text:
                print(f"You said: {text}")
    else:
        print("Microphone test failed. Please check your microphone.")
