import json
import autogen

# Define the Robot class
class Robot:
    def __init__(self, start_x, start_y):
        self.x = start_x
        self.y = start_y

    def teleport(self, new_x, new_y):
        self.x = new_x
        self.y = new_y

# Function to update the robot's position in the JSON database
def update_position(name, x, y):
    with open('robot_data.json', 'r+') as file:
        data = json.load(file)
        data[name] = {"x": x, "y": y}
        file.seek(0)
        json.dump(data, file, indent=4)

# Function to get the robot's position from the JSON database
def get_position(name):
    with open('robot_data.json', 'r') as file:
        data = json.load(file)
        return data.get(name, {"x": None, "y": None})

# Initialize the JSON file with the initial position of the robot
init_data = {"robotInst": {"x": 0, "y": 0}}
with open('robot_data.json', 'w') as file:
    json.dump(init_data, file, indent=4)

# AutoGen configuration (example configuration)
config_list = [
    {
        "model": "gpt-4",
        "api_key": "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",
    }
]


llm_config = {
    "functions": [
        {
            "name": "get_position",
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
    # ... other configurations ...
}

# Create AutoGen agents
user = autogen.UserProxyAgent(
    name="User",
    # ... other configurations ...
)

robot = autogen.AssistantAgent(
    name="Robot",
    llm_config=llm_config,
    # ... other configurations ...
)

# Register the function with the UserProxyAgent
user.register_function(
    function_map={
        "get_position": get_position,
    }
)

# Example usage
robotInst = Robot(0, 0)
robotInst.teleport(20, 30)
update_position("robotInst", robotInst.x, robotInst.y)

# Initiate chat with AutoGen agents
user.initiate_chat(
    robot,
    message="What's the current position of robotInst",
)