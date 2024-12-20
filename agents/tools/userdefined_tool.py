from shared.tools_redis_cache import ToolsRedisCache, ToolParser


def run(tool_name: str, parameters: dict):
    from tools.rate_limiter import rate_limiter

    tool = ToolsRedisCache().get_tool(tool_name)
    globals()["rate_limiter"] = rate_limiter
    exec(tool.code, globals())
    func = globals()[tool.function_name]
    result = func(**parameters)
    return result


def validate(code: str):
    parser = ToolParser(code)
    return parser.function_name, parser.spec_dict
