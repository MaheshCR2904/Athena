"""
NLP Engine for Athena Voice Calculator
Converts natural language to mathematical expressions
"""

import re
from typing import Dict, List, Tuple, Optional


class NLPEngine:
    """Natural Language Processing engine for mathematical expressions"""
    
    # Number words to digits mapping
    NUMBER_WORDS = {
        'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4,
        'five': 5, 'six': 6, 'seven': 7, 'eight': 8, 'nine': 9,
        'ten': 10, 'eleven': 11, 'twelve': 12, 'thirteen': 13,
        'fourteen': 14, 'fifteen': 15, 'sixteen': 16, 'seventeen': 17,
        'eighteen': 18, 'nineteen': 19, 'twenty': 20, 'thirty': 30,
        'forty': 40, 'fifty': 50, 'sixty': 60, 'seventy': 70,
        'eighty': 80, 'ninety': 90, 'hundred': 100, 'thousand': 1000,
        'million': 1000000, 'billion': 1000000000
    }
    
    # Operation synonyms
    OPERATION_SYNONYMS = {
        'add': '+', 'plus': '+', 'increase': '+', 'sum': '+', 'and': '+',
        'subtract': '-', 'minus': '-', 'decrease': '-', 'less': '-', 'take': '-',
        'multiply': '*', 'times': '*', 'product': '*', 'by': '*',
        'divide': '/', 'divided': '/', 'quotient': '/', 'over': '/',
        'percent': '%', 'percentage': '%', 'per cent': '%',
        'square root': 'sqrt', 'root': 'sqrt', 'sqrt': 'sqrt',
        'squared': '^2', 'cube': '^3', 'cubed': '^3',
        'power': '^', 'to the power': '^', 'exponent': '^'
    }
    
    # Context reference words
    CONTEXT_WORDS = ['previous', 'last', 'that', 'it', 'answer', 'result']
    
    def __init__(self):
        self.context_value = None
        self.last_expression = None
        
    def set_context(self, value: float, expression: str = None):
        """Set the context for reference words"""
        self.context_value = value
        if expression:
            self.last_expression = expression
            
    def clear_context(self):
        """Clear context memory"""
        self.context_value = None
        self.last_expression = None
        
    def parse(self, text: str) -> Dict:
        """
        Parse natural language text into a mathematical expression
        Returns: {
            'expression': str,  # The mathematical expression
            'numbers': list,    # Extracted numbers
            'operations': list, # Identified operations
            'is_valid': bool,   # Whether parsing was successful
            'needs_clarification': bool,  # Whether clarification is needed
            'clarification': str, # Clarification message if needed
            'explanation': str   # How the expression was interpreted
        }
        """
        text = text.lower().strip()
        
        # Check for context references
        text = self._resolve_context_references(text)
        
        # Handle multi-step commands
        if self._is_multi_step(text):
            return self._parse_multi_step(text)
            
        # Extract numbers from text
        numbers = self._extract_numbers(text)
        
        # Identify operations
        operations = self._identify_operations(text)
        
        # Check for ambiguous numbers
        clarification = self._check_ambiguity(text, numbers)
        if clarification:
            return {
                'expression': '',
                'numbers': numbers,
                'operations': operations,
                'is_valid': False,
                'needs_clarification': True,
                'clarification': clarification,
                'explanation': ''
            }
        
        # Build expression
        expression, explanation = self._build_expression(text, numbers, operations)
        
        return {
            'expression': expression,
            'numbers': numbers,
            'operations': operations,
            'is_valid': bool(expression),
            'needs_clarification': False,
            'clarification': '',
            'explanation': explanation
        }
    
    def _resolve_context_references(self, text: str) -> str:
        """Replace context references with actual values"""
        if self.context_value is None:
            return text
            
        for word in self.CONTEXT_WORDS:
            if word in text:
                # Replace with the context value
                text = re.sub(r'\b' + word + r'\b', str(self.context_value), text)
                break
        return text
    
    def _is_multi_step(self, text: str) -> bool:
        """Check if the text contains multi-step commands"""
        multi_step_keywords = ['then', 'after that', 'next', 'and then']
        return any(keyword in text for keyword in multi_step_keywords)
    
    def _parse_multi_step(self, text: str) -> Dict:
        """Parse multi-step commands into sequential operations"""
        # Split by "then" or similar keywords
        separators = [' then ', ' after that ', ' next ', ' and then ']
        parts = text
        for sep in separators:
            if sep in parts:
                parts = parts.split(sep)
                break
        else:
            parts = [text]
            
        if not isinstance(parts, list):
            parts = [parts]
            
        expressions = []
        explanations = []
        
        for i, part in enumerate(parts):
            part = part.strip()
            numbers = self._extract_numbers(part)
            operations = self._identify_operations(part)
            expr, expl = self._build_expression(part, numbers, operations)
            if expr:
                expressions.append(expr)
                explanations.append(f"Step {i+1}: {expl}")
        
        if len(expressions) == 1:
            return {
                'expression': expressions[0],
                'numbers': [],
                'operations': [],
                'is_valid': True,
                'needs_clarification': False,
                'clarification': '',
                'explanation': explanations[0]
            }
        
        # For multi-step, we need to evaluate sequentially
        # Combine into a single expression with proper order
        combined_expr = expressions[0]
        for expr in expressions[1:]:
            combined_expr = f"({combined_expr}) {expr}"
            
        return {
            'expression': combined_expr,
            'numbers': [],
            'operations': [],
            'is_valid': True,
            'needs_clarification': False,
            'clarification': '',
            'explanation': ' → '.join(explanations)
        }
    
    def _extract_numbers(self, text: str) -> List[float]:
        """Extract all numbers from text"""
        numbers = []
        
        # First, check for digit numbers
        digit_pattern = r'-?\d+\.?\d*'
        digit_matches = re.findall(digit_pattern, text)
        for match in digit_matches:
            try:
                numbers.append(float(match))
            except ValueError:
                pass
        
        # Then check for word numbers
        words = text.split()
        current_number = 0
        has_number = False
        
        for i, word in enumerate(words):
            word = word.rstrip('.,!?')
            if word in self.NUMBER_WORDS:
                val = self.NUMBER_WORDS[word]
                if val == 100:
                    if current_number == 0:
                        current_number = 100
                    else:
                        current_number *= 100
                    has_number = True
                elif val >= 1000:
                    if current_number == 0:
                        current_number = val
                    else:
                        current_number *= val
                    has_number = True
                else:
                    current_number += val
                    has_number = True
            else:
                if has_number and current_number != 0:
                    numbers.append(float(current_number))
                    current_number = 0
                    has_number = False
                    
        if has_number and current_number != 0:
            numbers.append(float(current_number))
            
        # Handle "point" for decimals
        text = self._handle_decimals(text, numbers)
        
        return numbers
    
    def _handle_decimals(self, text: str, numbers: List[float]) -> str:
        """Handle decimal number words like 'point five'"""
        # This is handled in the main extraction
        return text
    
    def _identify_operations(self, text: str) -> List[str]:
        """Identify mathematical operations in text"""
        operations = []
        text_lower = text.lower()
        
        # Check for each operation synonym
        for synonym, op in self.OPERATION_SYNONYMS.items():
            if synonym in text_lower:
                operations.append(op)
                
        return operations
    
    def _check_ambiguity(self, text: str, numbers: List[float]) -> Optional[str]:
        """Check for ambiguous input and return clarification message"""
        text_lower = text.lower()
        
        # Check for commonly confused number pairs
        ambiguous_pairs = [
            ('fifteen', 'fifty', 15, 50),
            ('thirteen', 'thirty', 13, 30),
            ('fourteen', 'forty', 14, 40),
            ('sixteen', 'sixty', 16, 60),
            ('seventeen', 'seventy', 17, 70),
            ('eighteen', 'eighty', 18, 80),
            ('nineteen', 'ninety', 19, 90)
        ]
        
        for word1, word2, val1, val2 in ambiguous_pairs:
            if word1 in text_lower and word2 in text_lower:
                return f"I heard both '{word1}' and '{word2}'. Did you mean {val1} or {val2}?"
                
        return None
    
    def _build_expression(self, text: str, numbers: List[float], operations: List[str]) -> Tuple[str, str]:
        """Build a mathematical expression from parsed components"""
        text_lower = text.lower()
        
        # Handle special operations first
        if 'percent' in text_lower or 'percentage' in text_lower:
            return self._handle_percentage(text, numbers)
            
        if 'sqrt' in text_lower or 'square root' in text_lower:
            return self._handle_sqrt(text, numbers)
            
        if '^2' in operations or 'squared' in text_lower:
            return self._handle_power(text, numbers, 2)
            
        if '^3' in operations or 'cube' in text_lower or 'cubed' in text_lower:
            return self._handle_power(text, numbers, 3)
            
        if '^' in operations:
            return self._handle_power(text, numbers, None)
        
        # Handle basic operations
        return self._handle_basic_operations(text, numbers, operations)
    
    def _handle_percentage(self, text: str, numbers: List[float]) -> Tuple[str, str]:
        """Handle percentage calculations like '25 percent of 480'"""
        if len(numbers) >= 2:
            # "X percent of Y" means X% of Y = (X/100) * Y
            percent = numbers[0]
            value = numbers[1]
            expression = f"({percent}/100)*{value}"
            explanation = f"{percent}% of {value} = ({percent}/100) × {value}"
            return expression, explanation
        elif len(numbers) == 1:
            # Just a percentage
            expression = f"{numbers[0]}/100"
            explanation = f"{numbers[0]}% = {numbers[0]}/100"
            return expression, explanation
        return "", "No numbers found for percentage calculation"
    
    def _handle_sqrt(self, text: str, numbers: List[float]) -> Tuple[str, str]:
        """Handle square root operations"""
        if numbers:
            num = numbers[-1]  # Use the last number
            expression = f"sqrt({num})"
            explanation = f"√{num}"
            return expression, explanation
        return "", "No number found for square root"
    
    def _handle_power(self, text: str, numbers: List[float], power: Optional[int]) -> Tuple[str, str]:
        """Handle power/exponent operations"""
        if numbers:
            if power is not None:
                base = numbers[0]
                expression = f"({base})**{power}"
                explanation = f"{base} to the power of {power}"
            elif len(numbers) >= 2:
                base = numbers[0]
                exp = numbers[1]
                expression = f"({base})**{exp}"
                explanation = f"{base} to the power of {exp}"
            return expression, explanation
        return "", "No number found for power calculation"
    
    def _handle_basic_operations(self, text: str, numbers: List[float], operations: List[str]) -> Tuple[str, str]:
        """Handle basic arithmetic operations"""
        if not numbers:
            return "", "No numbers found"
            
        if len(numbers) == 1:
            return str(numbers[0]), f"The number {numbers[0]}"
            
        if len(numbers) == 2:
            num1, num2 = numbers[0], numbers[1]
            
            # Determine the operation
            text_lower = text.lower()
            
            if any(op in text_lower for op in [' add', ' plus', ' increase', ' sum', ' and ']):
                return f"{num1}+{num2}", f"{num1} plus {num2}"
            elif any(op in text_lower for op in [' subtract', ' minus', ' decrease', ' less', ' take ']):
                return f"{num1}-{num2}", f"{num1} minus {num2}"
            elif any(op in text_lower for op in [' multiply', ' times', ' product']):
                return f"{num1}*{num2}", f"{num1} times {num2}"
            elif any(op in text_lower for op in [' divide', ' quotient', ' over', ' divided']):
                if num2 == 0:
                    return "", "Cannot divide by zero"
                return f"{num1}/{num2}", f"{num1} divided by {num2}"
            else:
                # Default to addition if unclear
                return f"{num1}+{num2}", f"{num1} plus {num2}"
                
        # For more than 2 numbers, chain operations
        expression = str(numbers[0])
        explanation = str(numbers[0])
        
        for i, op in enumerate(operations):
            if i + 1 < len(numbers):
                expression += op + str(numbers[i + 1])
                if op == '+':
                    explanation += f" + {numbers[i + 1]}"
                elif op == '-':
                    explanation += f" - {numbers[i + 1]}"
                elif op == '*':
                    explanation += f" × {numbers[i + 1]}"
                elif op == '/':
                    explanation += f" ÷ {numbers[i + 1]}"
                    
        return expression, explanation
    
    def get_explanation(self, expression: str, result: float) -> str:
        """Generate a human-readable explanation of how the result was calculated"""
        return f"The result of {expression} is {result}"


# Test the NLP engine
if __name__ == "__main__":
    nlp = NLPEngine()
    
    test_cases = [
        "What is 25 percent of 480",
        "Add 50 to the previous result",
        "Calculate the square root of 144",
        "5 plus 3 then multiply by 2",
        "What is fifteen percent of fifty",
        "Multiply 10 by 5",
        "Divide 100 by 4"
    ]
    
    for test in test_cases:
        print(f"\nInput: {test}")
        result = nlp.parse(test)
        print(f"Expression: {result['expression']}")
        print(f"Explanation: {result['explanation']}")
        print(f"Valid: {result['is_valid']}")
