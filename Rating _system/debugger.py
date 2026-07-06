# debugger.py
import logging
import traceback
from datetime import datetime
from typing import Any, Callable, Dict, Optional
import json

class Debugger:
    def __init__(self, log_file: str = 'debug.log', log_level: int = logging.DEBUG):
        self.log_file = log_file
        self.logger = logging.getLogger('RatingDebugger')
        self.logger.setLevel(log_level)
        
        # File handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        self.debug_messages = []
        self.error_count = 0
        self.warning_count = 0
    
    def debug(self, message: str, data: Optional[Dict] = None):
        """Log debug message"""
        self.logger.debug(f"{message} - Data: {data}")
        self.debug_messages.append({
            'type': 'debug',
            'message': message,
            'data': data,
            'timestamp': datetime.now().isoformat()
        })
    
    def info(self, message: str, data: Optional[Dict] = None):
        """Log info message"""
        self.logger.info(f"{message} - Data: {data}")
        self.debug_messages.append({
            'type': 'info',
            'message': message,
            'data': data,
            'timestamp': datetime.now().isoformat()
        })
    
    def warning(self, message: str, data: Optional[Dict] = None):
        """Log warning message"""
        self.logger.warning(f"{message} - Data: {data}")
        self.warning_count += 1
        self.debug_messages.append({
            'type': 'warning',
            'message': message,
            'data': data,
            'timestamp': datetime.now().isoformat()
        })
    
    def error(self, message: str, error: Optional[Exception] = None, data: Optional[Dict] = None):
        """Log error message"""
        self.error_count += 1
        error_info = {
            'message': message,
            'error': str(error) if error else None,
            'traceback': traceback.format_exc() if error else None,
            'data': data
        }
        self.logger.error(f"{message} - Error: {error} - Data: {data}")
        self.debug_messages.append({
            'type': 'error',
            **error_info,
            'timestamp': datetime.now().isoformat()
        })
    
    def trace_function_call(self, func: Callable, *args, **kwargs):
        """Trace function calls with arguments"""
        func_name = func.__name__
        self.debug(f"Called function: {func_name}", {
            'args': args,
            'kwargs': kwargs
        })
        
        try:
            result = func(*args, **kwargs)
            self.debug(f"Function {func_name} returned: {result}")
            return result
        except Exception as e:
            self.error(f"Function {func_name} raised exception", e, {
                'args': args,
                'kwargs': kwargs
            })
            raise
    
    def validate_data(self, data: Dict, schema: Dict) -> bool:
        """Validate data against a schema"""
        self.debug("Validating data", {'schema': schema, 'data': data})
        
        for key, expected_type in schema.items():
            if key not in data:
                self.warning(f"Missing required field: {key}", {'data': data})
                return False
            
            if not isinstance(data[key], expected_type):
                self.warning(
                    f"Invalid type for field {key}: expected {expected_type}, got {type(data[key])}",
                    {'data': data}
                )
                return False
        
        self.info("Data validation passed", {'data': data})
        return True
    
    def get_debug_report(self) -> Dict:
        """Generate debug report"""
        total_messages = len(self.debug_messages)
        errors = [m for m in self.debug_messages if m['type'] == 'error']
        warnings = [m for m in self.debug_messages if m['type'] == 'warning']
        
        return {
            'total_messages': total_messages,
            'error_count': len(errors),
            'warning_count': len(warnings),
            'error_rate': (len(errors) / total_messages * 100) if total_messages > 0 else 0,
            'logs': self.debug_messages[-100:],  # Last 100 messages
            'errors': errors[-20:],  # Last 20 errors
            'warnings': warnings[-20:]  # Last 20 warnings
        }
    
    def save_debug_report(self, filename: str = 'debug_report.json'):
        """Save debug report to file"""
        report = self.get_debug_report()
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        self.info(f"Debug report saved to {filename}")

class RatingDebugger(Debugger):
    """Specialized debugger for the rating system"""
    
    def __init__(self):
        super().__init__('rating_debug.log')
    
    def debug_rating_submission(self, rating_data: Dict):
        """Debug rating submission"""
        self.info("Processing rating submission", rating_data)
        
        # Validate rating data
        schema = {
            'service_id': int,
            'customer_id': int,
            'provider_id': int,
            'rating': (int, float),
            'category': str,
            'comment': str
        }
        
        if self.validate_data(rating_data, schema):
            self.info("Rating data validated successfully")
        else:
            self.error("Rating data validation failed", data=rating_data)
    
    def debug_review_submission(self, review_data: Dict):
        """Debug review submission"""
        self.info("Processing review submission", review_data)
        
        # Validate review data
        schema = {
            'rating_id': int,
            'reviewer_id': int,
            'review_text': str
        }
        
        if self.validate_data(review_data, schema):
            self.info("Review data validated successfully")
        else:
            self.error("Review data validation failed", data=review_data)
    
    def debug_provider_stats(self, provider_id: int, stats: Dict):
        """Debug provider statistics"""
        self.info(f"Provider {provider_id} statistics", stats)
        
        if stats.get('total_ratings', 0) > 0:
            self.debug(f"Average rating: {stats.get('average_rating', 0)}")
        else:
            self.warning(f"Provider {provider_id} has no ratings")
    
    def debug_database_operation(self, operation: str, success: bool, data: Dict = None):
        """Debug database operations"""
        if success:
            self.info(f"Database {operation} successful", data)
        else:
            self.error(f"Database {operation} failed", data=data)
    
    def debug_test_execution(self, test_name: str, passed: bool, details: str = ""):
        """Debug test execution"""
        if passed:
            self.info(f"Test '{test_name}' passed", {'details': details})
        else:
            self.error(f"Test '{test_name}' failed", {'details': details})