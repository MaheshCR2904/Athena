# Athena Voice Calculator
An AI-powered voice-controlled calculator using Python with natural language understanding, context-aware computation, and real-time speech interaction.

## Features

- 🎤 **Voice Input** - Continuous listening mode with wake word detection ("Hey Athena")
- 🗣️ **Natural Language** - Understands queries like "What is 25 percent of 480?"
- 🧠 **Context Awareness** - "Add 10 to previous result" using last calculated value
- 🔄 **Multi-step Commands** - "5 + 3 then multiply by 2" (processes sequentially)
- 📊 **Smart NLP** - Synonym understanding (plus = add = increase)
- 🎯 **GUI Interface** - Real-time display with dark mode
- 📝 **History Panel** - Tracks all calculations with export capability
- 🔊 **Voice Feedback** - Human-like responses using text-to-speech

## Installation

1. Install required dependencies:
```bash
pip install speechrecognition pyttsx3
```

2. Run the application:
```bash
python main.py
```

## Usage

- **Click the microphone** or say "Hey Athena" to start
- **Speak your calculation** naturally
- Examples:
  - "What is 25 percent of 480?"
  - "Add 50 to the previous result"
  - "Calculate the square root of 144 and multiply it by 3"
  - "5 plus 3 then multiply by 2"

## Requirements

- Python 3.8+
- Windows 10/11
- Internet connection (for online mode) - falls back to offline

## Project Structure

```
athena/
├── main.py              # Entry point
├── nlp_engine.py        # Natural language processing
├── speech_handler.py    # Speech recognition
├── tts_engine.py        # Text-to-speech
├── context_manager.py   # Context memory
├── calculator.py        # Math evaluation
├── gui.py              # GUI interface
└── requirements.txt     # Dependencies
```
