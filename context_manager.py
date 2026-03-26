"""
Context Manager for Athena Voice Calculator
Handles calculation history and context memory
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional


class ContextManager:
    """Manages calculation history and context memory"""
    
    def __init__(self, max_history: int = 50):
        self.max_history = max_history
        self.history: List[Dict] = []
        self.current_context: Optional[Dict] = None
        
        # File for persistence
        self.history_file = "athena_history.json"
        
        # Load existing history
        self._load_history()
    
    def store_result(self, expression: str, result: float, raw_input: str = "") -> Dict:
        """
        Store a calculation result in history
        Returns: The stored record
        """
        record = {
            'id': len(self.history) + 1,
            'timestamp': datetime.now().isoformat(),
            'expression': expression,
            'result': result,
            'raw_input': raw_input,
            'formatted_result': self._format_result(result)
        }
        
        # Add to history
        self.history.append(record)
        
        # Update current context
        self.current_context = {
            'expression': expression,
            'result': result,
            'raw_input': raw_input
        }
        
        # Trim history if needed
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]
        
        # Save to file
        self._save_history()
        
        return record
    
    def get_previous(self, index: int = 0) -> Optional[Dict]:
        """
        Get a previous calculation
        index: 0 = most recent, 1 = second most recent, etc.
        """
        if not self.history:
            return None
            
        if index < 0:
            index = 0
            
        if index >= len(self.history):
            return None
            
        return self.history[-(index + 1)]
    
    def get_last_result(self) -> Optional[float]:
        """Get the most recent result"""
        if self.current_context:
            return self.current_context['result']
        return None
    
    def get_last_expression(self) -> Optional[str]:
        """Get the most recent expression"""
        if self.current_context:
            return self.current_context['expression']
        return None
    
    def resolve_reference(self, reference: str) -> Optional[float]:
        """
        Resolve a reference like 'previous' or 'last' to a value
        """
        reference = reference.lower()
        
        if reference in ['previous', 'last', 'that', 'it', 'answer', 'result']:
            return self.get_last_result()
        
        # Try to parse as index
        try:
            index = int(reference)
            record = self.get_previous(index)
            if record:
                return record['result']
        except:
            pass
        
        return None
    
    def clear_history(self):
        """Clear all history"""
        self.history = []
        self.current_context = None
        self._save_history()
    
    def get_history(self, limit: int = 10) -> List[Dict]:
        """Get recent history"""
        return self.history[-limit:] if self.history else []
    
    def get_all_history(self) -> List[Dict]:
        """Get all history"""
        return self.history
    
    def export_to_file(self, filepath: str = None) -> bool:
        """Export history to a file"""
        if filepath is None:
            filepath = f"athena_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        try:
            with open(filepath, 'w') as f:
                f.write("Athena Calculator History\n")
                f.write("=" * 50 + "\n\n")
                
                for record in self.history:
                    f.write(f"#{record['id']} - {record['timestamp']}\n")
                    f.write(f"Input: {record['raw_input'] or record['expression']}\n")
                    f.write(f"Result: {record['formatted_result']}\n")
                    f.write("-" * 30 + "\n\n")
                    
            return True
        except Exception as e:
            print(f"Export error: {e}")
            return False
    
    def _format_result(self, result: float) -> str:
        """Format result for display"""
        if result == int(result):
            return str(int(result))
        else:
            # Round to reasonable precision
            rounded = round(result, 10)
            # Remove trailing zeros
            formatted = f"{rounded:.10f}".rstrip('0').rstrip('.')
            return formatted
    
    def _save_history(self):
        """Save history to file"""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.history, f, indent=2)
        except Exception as e:
            print(f"Could not save history: {e}")
    
    def _load_history(self):
        """Load history from file"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r') as f:
                    self.history = json.load(f)
                    
                # Set current context to last result
                if self.history:
                    last = self.history[-1]
                    self.current_context = {
                        'expression': last['expression'],
                        'result': last['result'],
                        'raw_input': last.get('raw_input', '')
                    }
        except Exception as e:
            print(f"Could not load history: {e}")
            self.history = []
    
    def search_history(self, query: str) -> List[Dict]:
        """Search history for matching records"""
        query = query.lower()
        results = []
        
        for record in self.history:
            if (query in record['expression'].lower() or
                query in record['raw_input'].lower() or
                query in str(record['result'])):
                results.append(record)
                
        return results
    
    def get_statistics(self) -> Dict:
        """Get statistics about calculations"""
        if not self.history:
            return {
                'total_calculations': 0,
                'today_count': 0,
                'most_common_operation': None
            }
        
        # Count today's calculations
        today = datetime.now().date()
        today_count = sum(
            1 for r in self.history 
            if datetime.fromisoformat(r['timestamp']).date() == today
        )
        
        return {
            'total_calculations': len(self.history),
            'today_count': today_count,
            'last_calculation': self.history[-1] if self.history else None
        }


# Demo usage
if __name__ == "__main__":
    cm = ContextManager()
    
    # Test storing results
    cm.store_result("25/100*480", 120, "What is 25 percent of 480")
    cm.store_result("120+50", 170, "Add 50 to the previous result")
    cm.store_result("sqrt(144)*3", 36, "Calculate the square root of 144 and multiply it by 3")
    
    print("History:")
    for record in cm.get_history():
        print(f"  {record['expression']} = {record['formatted_result']}")
    
    print(f"\nLast result: {cm.get_last_result()}")
    print(f"Previous result: {cm.get_previous(1)}")
    
    print(f"\nStatistics: {cm.get_statistics()}")
