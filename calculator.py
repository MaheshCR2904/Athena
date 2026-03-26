"""
Calculator Engine for Athena Voice Calculator
Safely evaluates mathematical expressions
"""

import math
import re
from typing import Tuple, Optional


class Calculator:
    """Mathematical expression evaluator"""
    
    def __init__(self):
        # Define safe operations
        self.safe_operations = {
            'sqrt': math.sqrt,
            'sin': math.sin,
            'cos': math.cos,
            'tan': math.tan,
            'log': math.log10,
            'ln': math.log,
            'abs': abs,
            'pow': pow,
            'pi': math.pi,
            'e': math.e
        }
    
    def evaluate(self, expression: str) -> Tuple[float, str]:
        """
        Evaluate a mathematical expression
        Returns: (result, error_message)
        """
        if not expression or not expression.strip():
            return 0, "Empty expression"
        
        try:
            # Preprocess expression
            processed = self._preprocess(expression)
            
            # Replace sqrt with math.sqrt
            processed = self._handle_sqrt(processed)
            
            # Handle power operations
            processed = self._handle_power(processed)
            
            # Evaluate the expression
            result = eval(processed, {"__builtins__": {}}, self.safe_operations)
            
            # Check for valid result
            if math.isnan(result):
                return 0, "Invalid result (not a number)"
            if math.isinf(result):
                return 0, "Result is infinite"
                
            return result, ""
            
        except ZeroDivisionError:
            return 0, "Cannot divide by zero"
        except SyntaxError as e:
            return 0, f"Invalid expression: {str(e)}"
        except Exception as e:
            return 0, f"Calculation error: {str(e)}"
    
    def _preprocess(self, expression: str) -> str:
        """Preprocess the expression"""
        # Remove whitespace
        expression = expression.replace(" ", "")
        
        # Replace common symbols
        expression = expression.replace("×", "*")
        expression = expression.replace("÷", "/")
        expression = expression.replace("−", "-")
        
        # Handle percentage (already converted by NLP)
        
        return expression
    
    def _handle_sqrt(self, expression: str) -> str:
        """Handle square root operations"""
        # Replace sqrt(X) with math.sqrt(X)
        pattern = r'sqrt\((\d+\.?\d*)\)'
        return re.sub(pattern, r'math.sqrt(\1)', expression)
    
    def _handle_power(self, expression: str) -> str:
        """Handle power/exponent operations"""
        # Replace X^Y with pow(X, Y)
        # But be careful with negative numbers
        pattern = r'\((\d+\.?\d*)\)\*\*(\d+\.?\d*)'
        return re.sub(pattern, r'pow(\1,\2)', expression)
    
    def format_result(self, result: float, precision: int = 10) -> str:
        """Format result for display"""
        # Handle special cases
        if math.isnan(result):
            return "Error"
        if math.isinf(result):
            return "Infinity" if result > 0 else "-Infinity"
        
        # Check if it's a whole number
        if result == int(result):
            return str(int(result))
        
        # Round to precision
        rounded = round(result, precision)
        
        # Format as string, removing trailing zeros
        formatted = f"{rounded:.{precision}f}".rstrip('0').rstrip('.')
        
        # Use scientific notation for very large/small numbers
        if abs(result) >= 1e10 or (abs(result) < 1e-6 and result != 0):
            formatted = f"{result:.2e}"
        
        return formatted
    
    def explain_calculation(self, expression: str, result: float) -> str:
        """Generate explanation for a calculation"""
        # Parse the expression and generate a human-readable explanation
        explanation = f"Calculating: {expression}\n"
        
        # Try to break down the calculation
        if 'sqrt' in expression.lower():
            match = re.search(r'sqrt\((\d+\.?\d*)\)', expression)
            if match:
                num = float(match.group(1))
                explanation += f"The square root of {num} is √{num} = {result}"
        
        elif '**' in expression or '^' in expression:
            explanation += f"Raising to a power gives {result}"
        
        elif '/' in expression:
            parts = expression.split('/')
            if len(parts) == 2:
                try:
                    a, b = float(parts[0]), float(parts[1])
                    explanation += f"{a} divided by {b} = {result}"
                except:
                    pass
        
        elif '*' in expression:
            parts = expression.split('*')
            if len(parts) == 2:
                try:
                    a, b = float(parts[0]), float(parts[1])
                    explanation += f"{a} multiplied by {b} = {result}"
                except:
                    pass
        
        elif '+' in expression:
            parts = expression.split('+')
            if len(parts) == 2:
                try:
                    a, b = float(parts[0]), float(parts[1])
                    explanation += f"{a} plus {b} = {result}"
                except:
                    pass
        
        elif '-' in expression:
            # Handle subtraction (be careful with negative numbers)
            match = re.match(r'(-?\d+\.?\d*)-(\d+\.?\d*)', expression)
            if match:
                a, b = float(match.group(1)), float(match.group(2))
                explanation += f"{a} minus {b} = {result}"
        
        else:
            explanation += f"The result is {result}"
        
        return explanation
    
    def validate_expression(self, expression: str) -> Tuple[bool, str]:
        """Validate an expression before evaluation"""
        if not expression:
            return False, "Empty expression"
        
        # Check for dangerous patterns
        dangerous = ['import', 'os.', 'sys.', 'subprocess', 'eval(', 'exec(']
        for pattern in dangerous:
            if pattern in expression.lower():
                return False, "Invalid characters in expression"
        
        # Check for balanced parentheses
        if expression.count('(') != expression.count(')'):
            return False, "Unbalanced parentheses"
        
        return True, ""


# Demo usage
if __name__ == "__main__":
    calc = Calculator()
    
    test_expressions = [
        "(25/100)*480",
        "120+50",
        "sqrt(144)*3",
        "5+3*2",
        "(5+3)*2",
        "10/4",
        "2**8",
        "sqrt(2)",
    ]
    
    print("Calculator Tests:")
    print("-" * 40)
    
    for expr in test_expressions:
        result, error = calc.evaluate(expr)
        if error:
            print(f"{expr}: Error - {error}")
        else:
            formatted = calc.format_result(result)
            print(f"{expr} = {formatted}")
