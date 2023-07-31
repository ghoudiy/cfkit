import inspect

def get_current_function_name():
    frame = inspect.currentframe().f_back
    try:
        # The name of the currently executing function is stored in f_code.co_name
        function_name = frame.f_code.co_name
        return function_name
    finally:
        # Always make sure to clean up the frame to avoid reference cycles
        # and potential memory leaks
        del frame

# Example usage:
def example_function():
    print("Current function:", get_current_function_name())
  
example_function()