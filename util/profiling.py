"""Utilities: Profiling

Contains profiling tools for performance measurement.
"""

import time
from functools import wraps

class Profiler:
    """Simple profiler for timing operations."""
    
    def __init__(self):
        self.timings = {}
    
    def time_operation(self, operation_name, func, *args, **kwargs):
        """Time a function call and store the result."""
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        duration_ms = (end_time - start_time) * 1000
        self.timings[operation_name] = duration_ms
        
        return result
    
    def get_timing(self, operation_name):
        """Get timing for an operation in milliseconds."""
        return self.timings.get(operation_name, 0)
    
    def get_all_timings(self):
        """Get all recorded timings."""
        return self.timings.copy()
    
    def clear(self):
        """Clear all recorded timings."""
        self.timings.clear()

def timer_decorator(operation_name=None):
    """Decorator to time function execution."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            name = operation_name or f"{func.__module__}.{func.__name__}"
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            
            duration_ms = (end_time - start_time) * 1000
            print(f"⏱️  {name}: {duration_ms:.1f}ms")
            
            return result
        return wrapper
    return decorator

# Global profiler instance
global_profiler = Profiler()

def time_it(operation_name):
    """Context manager for timing operations."""
    return TimingContext(operation_name, global_profiler)

class TimingContext:
    """Context manager for timing operations."""
    
    def __init__(self, operation_name, profiler):
        self.operation_name = operation_name
        self.profiler = profiler
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        end_time = time.time()
        duration_ms = (end_time - self.start_time) * 1000
        self.profiler.timings[self.operation_name] = duration_ms
        print(f"⏱️  {self.operation_name}: {duration_ms:.1f}ms")

class Profiling:
    """A placeholder Profiling class for profiling helpers."""
    pass
