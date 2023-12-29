import autogen

# Room class definition
class Room:
    def __init__(self, name, x1, y1, x2, y2):
        self.name = name
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

    def is_inside(self, x, y):
        return self.x1 <= x <= self.x2 and self.y1 <= y <= self.y2

# Robot class definition
class Robot:
    def __init__(self, start_x, start_y, room):
        self.x = start_x
        self.y = start_y
        self.room = room

    def teleport(self, new_x, new_y):
        if self.room.is_inside(new_x, new_y):
            self.x = new_x
            self.y = new_y
            return f"Moved to ({new_x}, {new_y})"
        return "Cannot move outside the room boundaries."

    def current_position(self):
        return [self.x, self.y]

# Functions for interacting with the robot
def move_robot(new_x, new_y):
    return robot.teleport(new_x, new_y)

def get_current_position():
    return robot.current_position()

# Room setup
living_room = Room("Living Room", 0, 0, 100, 100)

# Single robot setup
robot = Robot(0, 0, living_room)

# AutoGen configuration (hypothetical setup)
config_list = [
    {
        "model": "gpt-4",
        "api_key": "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",
    }
]

llm_config = {
    "functions": [
        {
            "name": "move_robot",
            "description": "Move the robot to new coordinates",
            "parameters": {
                "type": "object",
                "properties": {
                    "new_x": {"type": "number", "description": "New X coordinate"},
                    "new_y": {"type": "number", "description": "New Y coordinate"}
                },
                "required": ["new_x", "new_y"],
            },
        },
        {
            "name": "get_current_position",
            "description": "Get the current position of the robot",
            "parameters": {}
        }
    ],
    "config_list": config_list,
}

# Initialize AutoGen agents
user = autogen.UserProxyAgent(name="User")
robot_agent = autogen.AssistantAgent(name="Robot", llm_config=llm_config)

# Register functions with the UserProxyAgent
user.register_function(
    function_map={
        "move_robot": move_robot,
        "get_current_position": get_current_position
    }
)

# Example AutoGen interaction (hypothetical usage)
user.initiate_chat(
    robot_agent,
    message="Move robot to position (30, 30) and tell me what room the robot is in now",
)