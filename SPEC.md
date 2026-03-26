# Athena - AI Voice Calculator Specification

## 1. Project Overview

**Project Name:** Athena Voice Calculator  
**Type:** Desktop Application (Python)  
**Core Functionality:** An AI-powered voice-controlled calculator that understands natural language, maintains context, and provides conversational interaction with both voice and visual feedback.  
**Target Users:** Users who prefer hands-free mathematical operations, accessibility-focused users, and anyone wanting a more natural calculator experience.

---

## 2. UI/UX Specification

### 2.1 Window Structure

- **Main Window:** Single-window application (900x700 pixels minimum)
- **Layout:** Three-column design
  - Left panel: Voice input visualization & status
  - Center panel: Main calculator display & results
  - Right panel: Calculation history

### 2.2 Visual Design

#### Color Palette (Dark Mode - Primary)
| Element | Color | Hex Code |
|---------|-------|----------|
| Background Primary | Deep Space | #0D1117 |
| Background Secondary | Dark Slate | #161B22 |
| Background Tertiary | Charcoal | #21262D |
| Accent Primary | Electric Cyan | #00D9FF |
| Accent Secondary | Soft Purple | #A855F7 |
| Accent Success | Emerald | #10B981 |
| Accent Warning | Amber | #F59E0B |
| Accent Error | Coral Red | #EF4444 |
| Text Primary | Pure White | #FFFFFF |
| Text Secondary | Silver | #8B949E |
| Text Muted | Gray | #484F58 |
| Border | Dark Border | #30363D |

#### Typography
- **Font Family:** "Segoe UI", "Inter", system-ui
- **Heading Large:** 28px, Bold
- **Heading Medium:** 20px, SemiBold
- **Body:** 14px, Regular
- **Monospace (expressions):** "Cascadia Code", "Consolas", monospace, 16px

#### Spacing System
- Base unit: 8px
- Small: 8px
- Medium: 16px
- Large: 24px
- XLarge: 32px

#### Visual Effects
- Border radius: 12px (cards), 8px (buttons), 24px (pills)
- Box shadows: 0 4px 24px rgba(0, 0, 0, 0.4)
- Subtle gradient on accent elements
- Animated pulse for listening state
- Smooth transitions: 200ms ease-out

### 2.3 Components

#### Header Bar
- App title "Athena" with AI icon
- Status indicator (Online/Offline mode)
- Settings gear icon
- Minimize/Maximize/Close buttons (custom styled)

#### Voice Input Panel (Left)
- Circular microphone button (80px diameter)
- Animated waveform visualization when listening
- Wake word indicator: "Say 'Hey Athena' to activate"
- Current listening status text
- Mode toggle: Continuous / Single command

#### Main Display (Center)
- **Input Display:** Large text showing recognized speech
- **Expression Display:** Parsed mathematical expression
- **Result Display:** Large calculated result with animation
- **Explanation Button:** "Explain how I got this"

#### History Panel (Right)
- Scrollable list of past calculations
- Each entry shows: expression, result, timestamp
- Click to restore previous calculation
- Clear history button
- Export to file button

#### Control Buttons
- Start/Stop listening (primary action)
- Clear display
- Settings
- History toggle

### 2.4 Component States

| Component | Default | Hover | Active | Disabled |
|-----------|---------|-------|--------|----------|
| Mic Button | #21262D | #30363D | #00D9FF (pulsing) | #161B22 |
| Action Button | #21262D | #30363D | #00D9FF | #161B22 |
| History Item | transparent | #21262D | #30363D | - |

---

## 3. Functional Specification

### 3.1 Core Features

#### Voice Input System
- **Speech Recognition:** Using Google Speech Recognition (with offline fallback)
- **Wake Word Detection:** "Hey Athena" or "Athena" to activate
- **Continuous Mode:** Continuous listening with keyword detection
- **Single Command Mode:** One query at a time
- **Audio Feedback:** Sound cues for activation/deactivation

#### Text-to-Speech System
- **Engine:** pyttsx3 (offline TTS)
- **Voice Personality:** Configurable (Friendly, Professional, Casual)
- **Response Templates:** Natural language responses
- **Volume Control:** Adjustable

#### Natural Language Processing Engine
The NLP engine must parse and convert natural language to mathematical expressions:

**Number Recognition:**
- Spoken numbers: "twenty five" → 25
- Ordinals: "first", "second", "third"
- Large numbers: "one thousand five hundred"
- Decimals: "point five"
- Fractions: "three quarters"

**Operation Recognition:**
| Natural Language | Operation | Symbols |
|------------------|-----------|---------|
| add, plus, increase, sum | Addition | + |
| subtract, minus, decrease, less | Subtraction | - |
| multiply, times, product | Multiplication | × |
| divide, quotient, divided by | Division | ÷ |
| percent, percentage of | Percentage | % |
| square root, root | Square Root | √ |
| squared, to the power of | Exponent | ^ |
| cubed | Cube | ^3 |

**Complex Query Patterns:**
- "What is X percent of Y?"
- "Calculate X plus Y"
- "Find the square root of X"
- "X divided by Y, then multiply by Z"
- "Add X to the previous result"
- "What was the last answer?"

### 3.2 Smart Features

#### Context Memory
- Store last 10 calculations in memory
- Reference previous results with:
  - "previous result"
  - "last answer"
  - "that"
  - "it"
- Context persists until cleared

#### Multi-Step Commands
- Process multiple operations in sequence:
  - "5 + 3 then multiply by 2" → (5 + 3) × 2 = 16
  - "10 divided by 2 plus 5" → (10 ÷ 2) + 5 = 10
- Support nested operations with parentheses

#### Synonym Understanding
- Mathematical synonyms mapped to operations
- Contextual word understanding
- Handle common speech variations

#### Error Handling
- **Ambiguous Input:** Ask for clarification
  - "I heard 'fifty' - did you mean 50 or 15?"
- **Unrecognized:** "I didn't catch that. Please try again."
- **Calculation Error:** "I couldn't calculate that. Please check the expression."
- **No Internet:** Switch to offline mode automatically

### 3.3 User Interactions

#### Primary Flow
1. User activates app (click or wake word)
2. App listens for voice input
3. Speech converted to text
4. NLP parses expression
5. Calculate result
6. Display result (GUI + TTS)
7. Store in history

#### Wake Word Flow
1. App in standby mode
2. User says "Hey Athena"
3. App activates, visual feedback
4. User speaks query
5. Process as primary flow

#### Error Correction Flow
1. App detects ambiguous input
2. Ask clarification question via TTS
3. User provides correction
4. Re-process expression

### 3.4 Data Flow & Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Athena Calculator                       │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   GUI Layer  │    │ Speech Layer │    │  NLP Engine  │  │
│  │   (Tkinter)  │◄───│ (speech_rec) │◄───│   (Parser)   │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         │                   │                   │           │
│         ▼                   ▼                   ▼           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Context Manager (Memory)                 │  │
│  └──────────────────────────────────────────────────────┘  │
│         │                   │                   │           │
│         ▼                   ▼                   ▼           │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   Display    │    │  TTS Output  │    │   Calculator │  │
│  │   (Result)   │    │  (pyttsx3)   │    │   (eval)     │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

#### Key Modules

**1. NLPEngine (nlp_engine.py)**
- `parse_expression(text: str) -> dict`: Parse natural language to math
- `extract_numbers(text: str) -> list`: Extract all numbers from text
- `identify_operations(text: str) -> list`: Identify mathematical operations
- `resolve_context(text: str, context: dict) -> str`: Resolve references

**2. SpeechHandler (speech_handler.py)**
- `listen() -> str`: Capture and convert speech to text
- `activate_wake_word()`: Start wake word detection
- `is_wake_word(audio) -> bool`: Check for wake word

**3. TTSEngine (tts_engine.py)**
- `speak(text: str)`: Convert text to speech
- `set_voice(personality: str)`: Change voice personality
- `set_rate(speed: int)`: Adjust speech rate

**4. ContextManager (context_manager.py)**
- `store_result(expression: str, result: float)`: Store calculation
- `get_previous(index: int) -> dict`: Get previous calculation
- `resolve_reference(ref: str) -> float`: Resolve "previous" references

**5. Calculator (calculator.py)**
- `evaluate(expression: str) -> float`: Safely evaluate math expression
- `format_result(result: float) -> str`: Format result for display

**6. GUI (gui.py)**
- Main Tkinter application
- All visual components
- Event handlers

### 3.5 Edge Cases

| Scenario | Handling |
|----------|----------|
| No speech detected for 10s | Show "Listening..." timeout message |
| Multiple numbers unclear | Ask "Did you mean X or Y?" |
| Division by zero | "Cannot divide by zero" |
| Very large numbers | Use scientific notation |
| Negative results | Display normally with negative sign |
| Empty input | "Please say a calculation" |
| Network unavailable | Switch to offline mode, notify user |
| Invalid expression | "I couldn't understand that expression" |

---

## 4. Acceptance Criteria

### 4.1 Core Functionality
- [ ] Voice input correctly recognizes speech and converts to text
- [ ] Natural language queries are parsed into valid mathematical expressions
- [ ] Calculations produce correct results
- [ ] Voice output reads results aloud
- [ ] GUI displays input, expression, and result in real-time

### 4.2 Smart Features
- [ ] "Add 10 to previous result" correctly uses last answer
- [ ] Multi-step commands like "5 + 3 then multiply by 2" work correctly
- [ ] Synonyms (plus/add/increase) are all recognized
- [ ] Context memory maintains last 10 calculations

### 4.3 UI/UX
- [ ] Dark mode displays correctly with specified colors
- [ ] All panels (voice, display, history) are visible
- [ ] History panel shows past calculations
- [ ] Animations work smoothly (pulse, transitions)

### 4.4 Error Handling
- [ ] Ambiguous input triggers clarification question
- [ ] Unrecognized speech shows error message
- [ ] Invalid expressions handled gracefully

### 4.5 Visual Checkpoints
1. App launches with dark theme
2. Microphone button visible and clickable
3. Voice input shows as text in display
4. Result appears with animation
5. History updates after each calculation
6. TTS speaks the result

---

## 5. Technical Requirements

### 5.1 Dependencies
```
speech_recognition>=3.8.0
pyttsx3>=2.7
tkinter (built-in)
threading (built-in)
re (built-in)
math (built-in)
```

### 5.2 Platform
- Windows 10/11
- Python 3.8+

### 5.3 Performance
- Response time: < 2 seconds for typical queries
- Memory usage: < 200MB
- CPU usage: < 10% idle, < 30% active
