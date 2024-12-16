import ast
import json
from typing import Optional

from shared.bookstack_client import AgentBookStackClient
from shared.utils import extract_code
from rq import Queue

from redis import Redis
import json
from shared.models import UserdefinedTool
import time


class ToolsRedisCache:
    def __init__(self):
        self.redis = Redis("redis", decode_responses=True)
        self.queue = Queue("agents-queue", Redis("redis", 6379), is_async=True)

    def update_tool(self, name: str, tool_id: int, code: str):
        validation = self.queue.enqueue(
            "tools.userdefined_tool.validate", kwargs={"code": code}
        )
        while validation.get_status() not in ["finished", "failed"]:
            time.sleep(0.5)
        if validation.get_status().value == "failed":
            return False, validation.exc_info
        function_name, spec_dict = validation.result
        self.redis.hset(
            f"tool:{name}",
            mapping={
                "name": name,
                "tool_id": tool_id,
                "code": code,
                "description": spec_dict["description"],
                "function_name": function_name,
                "parameters": json.dumps(spec_dict["parameters"]),
            },
        )
        return True, None

    def get_tool(self, name: str):
        tool = self.redis.hgetall(f"tool:{name}")
        if tool:
            tool["parameters"] = json.loads(tool.get("parameters", {}))
        else:
            return
        return UserdefinedTool(**tool)

    def delete_tool(self, name: str):
        self.redis.delete(f"tool:{name}")

    def get_all_tools(self):
        keys = []
        cursor = 0
        while True:
            cursor, batch = self.redis.scan(cursor=cursor, match="tool:*")
            keys.extend(batch)
            if cursor == 0:
                break
        pipeline = self.redis.pipeline()
        for tool_key in keys:
            pipeline.hgetall(tool_key)
        tools = pipeline.execute()
        for t in tools:
            t["parameters"] = json.loads(t["parameters"])
        tools = [UserdefinedTool(**t) for t in tools]
        return tools


class ToolParser:
    def __init__(self, tool_code: str):
        self.function_name = self.extract_function_name(tool_code)
        self.function, self.spec_dict, self.spec_str = self.extract_spec(tool_code)

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
        from tools.rate_limiter import rate_limiter

        globals()["rate_limiter"] = rate_limiter
        exec(tool_code, globals())
        func = globals()[self.function_name]
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
