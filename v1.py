class Robot:
    def __init__(self, start_x, start_y):
        self.x = start_x
        self.y = start_y

    def teleport(self, new_x, new_y):
        self.x = new_x
        self.y = new_y

# Dictionary to map robot names to their instances
robots = {
    'robotInst': Robot(0, 0)
}

# Function to get the current position of a robot by its name
def current_position(name):
    robot = robots.get(name)
    if robot is None:
        return "Robot not found"
    return [robot.x, robot.y]

# AutoGen setup (example configuration)
import autogen

config_list = [
    {
        "model": "gpt-4",
        "api_key": "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",
    }
]

llm_config = {
    # ... Your configuration here ...
    "functions": [
        {
            "name": "current_position",
            "description": "Get the current position of the robot",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name of the robot instance",
                    },
                },
                "required": ['name'],
            },
        },
    ],
    "config_list": config_list,
    # ... Other configurations ...
}

# Create AutoGen agents
user = autogen.UserProxyAgent(
    name="User",
    # ... Other configurations ...
)

robot = autogen.AssistantAgent(
    name="Robot",
    llm_config=llm_config,
    # ... Other configurations ...
)

# Register the function with the UserProxyAgent
user.register_function(
    function_map={
        "current_position": current_position,
    }
)

# Example usage
robots['robotInst'].teleport(20, 30)

# Initiate chat with AutoGen agents
user.initiate_chat(
    robot,
    message="What's the current position of robotInst",
)