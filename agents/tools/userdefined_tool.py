import ast
import json
from typing import Optional

from shared.bookstack_client import AgentBookStackClient
from shared.utils import extract_code


class UserdefinedTool:
    def __init__(self, tool_name: Optional[str], tool_id: Optional[int]):
        tool_code = self.get_tool_code_from_page(tool_name=tool_name, tool_id=tool_id)
        self.function_name = self.extract_function_name(tool_code)
        self.function, self.spec_dict, self.spec_str = self.extract_spec(tool_code)

    def get_tool_code_from_page(self, tool_name: Optional[str], tool_id: Optional[int]):
        client = AgentBookStackClient("WikiAgent")
        if tool_id:
            page = client.get_page(tool_id)
            return extract_code(page["markdown"])
        elif tool_name:
            pass  # TODO
        else:
            raise ValueError("Either tool_name or tool_id must be given")

    def extract_function_name(self, tool_code: str):
        """
        Extracts the name of the first function in the given code string.

        Args:
            tool_code (str): The entire code of the function as a string.

        Returns:
            str: The name of the first function found in the code.
        """
        tree = ast.parse(tool_code)
        for node in tree.body:
            if isinstance(node, ast.FunctionDef):
                return node.name
        raise ValueError("No function definition found in the provided code.")

    def extract_spec(self, tool_code: str):
        local_namespace = {}
        exec(tool_code, {}, local_namespace)
        if self.function_name not in local_namespace:
            raise ValueError(
                f"Function '{self.function_name}' not found in the provided code."
            )
        func = local_namespace[self.function_name]
        return self.generate_function_spec(func)

    def generate_function_spec(self, func):
        """
        Generates a function specification as a dictionary and string based on the function's docstring.

        Args:
            func (callable): The function for which the specification is to be generated.

        Returns:
            tuple: A dictionary and string representation of the function specification.
        """
        if not func.__doc__:
            raise ValueError("The provided function does not have a docstring.")

        docstring = func.__doc__.strip()
        description_lines = []
        for line in docstring.split("\n"):
            stripped_line = line.strip()
            if stripped_line.lower().startswith(("args:", "returns:", "raises:")):
                break
            description_lines.append(stripped_line)
        description = " ".join(description_lines).strip()

        spec_dict = {
            "name": func.__name__,
            "description": description,
            "parameters": {},
        }
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
                arg_type = "string"
                if "(" in arg_name and ")" in arg_name:
                    arg_name, annotation = arg_name.split("(")
                    arg_name = arg_name.strip()
                    annotation = annotation.strip(")")
                    arg_type = annotation
                spec_dict["parameters"][arg_name] = {
                    "type": arg_type,
                    "description": arg_desc,
                }
        spec_str = json.dumps(spec_dict, indent=4)
        return func, spec_dict, spec_str

    def run(self, *args, **kwargs):
        """
        Executes the function stored in the class with the given arguments.

        Args:
            *args: Positional arguments for the function.
            **kwargs: Keyword arguments for the function.

        Returns:
            Any: The result of the function execution.
        """
        return self.function(*args, **kwargs)


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


t = UserdefinedTool(function_code)

t.run(name="Alice", age=30)
