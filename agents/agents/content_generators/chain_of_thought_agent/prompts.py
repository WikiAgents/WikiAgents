short_format_instruction = "DO NOT OUTPUT ANYTHING BESIDES THE JSON. It will break the system that processes the output."


ALLOWED_STEPS = """
You are allowed to produce ONLY steps with the following json schemas:
{allowed_steps}
Do not reproduce schema when producing the steps, use it as a reference.
"""


PLAN_SYSTEM_PROMPT = """Use as many relevant tools/actions as possible to include more details and facts in your responses.
You can use the following userdefined_actions:
{userdefined_actions}

DON'T MAKE UP USERDEFINED ACTIONS! ONLY USED USERDEFINED ACTIONS THAT ARE LISTED ABOVE!

"""

PLAN_GUIDANCE = f"Write a natural language plan on how to use tools to help the user. Respond with kind='plan'. {short_format_instruction}"

ACT_GUIDANCE = f"Follow the plan you created earlier. When you are done, output your response to the user with kind='assistant'. {short_format_instruction}"


class PromptRegistry:
    plan_system_prompt = PLAN_SYSTEM_PROMPT
    plan_guidance = PLAN_GUIDANCE
    act_guidance = ACT_GUIDANCE
    allowed_steps = ALLOWED_STEPS
