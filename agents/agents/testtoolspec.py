def extract_function_spec_and_call(function_code, function_name, *args, **kwargs):
    """
    Evaluates a function from a code string, generates its specification,
    and calls the function with provided arguments.

    Args:
        function_code (str): The entire code of the function as a string.
        function_name (str): The name of the function to extract and call.
        *args: Positional arguments to pass to the function.
        **kwargs: Keyword arguments to pass to the function.

    Returns:
        tuple: The specification string and the function's return value.
    """
    # Step 1: Define the function in the current namespace
    local_namespace = {}
    exec(function_code, {}, local_namespace)

    # Step 2: Get the function object
    if function_name not in local_namespace:
        raise ValueError(f"Function '{function_name}' not found in the provided code.")
    func = local_namespace[function_name]

    # Step 3: Generate the function specification
    spec = generate_function_spec(func)

    # Step 4: Call the function
    result = func(*args, **kwargs)

    return spec, result


# Function specification generator (same as before)
def generate_function_spec(func):
    """
    Generates a function specification string based on the function's docstring.

    Args:
        func (callable): The function for which the specification is to be generated.

    Returns:
        str: The formatted function specification string.
    """
    if not func.__doc__:
        raise ValueError("The provided function does not have a docstring.")

    docstring = func.__doc__.strip()
    spec = f"""
    {{
        "name": "{func.__name__}",
        "description": "{docstring}",
        "parameters": {{
            "type": "object",
            "properties": {{
    """

    lines = docstring.split("\n")
    args_section = False
    for line in lines:
        line = line.strip()
        if line.lower().startswith("args:"):
            args_section = True
        elif line.lower().startswith(("returns:", "raises:")):
            args_section = False
        elif args_section and ":" in line:
            arg_name, arg_desc = line.split(":", 1)
            arg_name = arg_name.strip()
            arg_desc = arg_desc.strip()
            spec += f"""
                "{arg_name}": {{
                    "type": "string", 
                    "description": "{arg_desc}"
                }},
            """

    spec = spec.rstrip(",\n") + "\n"
    spec += """
            },
            "required": []
        }
    }
    """

    return spec


# Example function code as a string
function_code = """
def example_function(name, age):
    \"""
    Example function that greets a user.
    
    Args:
        name (str): The name of the user.
        age (int): The age of the user.
    
    Returns:
        str: A greeting message.
    \"""
    return f"Hello {name}, you are {age} years old!"
"""

# Evaluate and call the function
spec, result = extract_function_spec_and_call(
    function_code, "example_function", "Alice", 30
)

print("Function Specification:")
print(spec)
print("\nFunction Result:")
print(result)
