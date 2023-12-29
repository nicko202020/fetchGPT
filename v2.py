import autogen
import pygame

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

    def current_room(self):
        if self.room.is_inside(self.x, self.y):
            return self.room.name
        return "Unknown room"
# Functions for interacting with the robot
def move_robot(new_x, new_y):
    return robot.teleport(new_x, new_y)

def get_current_position():
    return robot.current_position()

def get_robot_current_room():
    return robot.current_room()


# AutoGen configuration (hypothetical setup)
config_list = [
    {
        "model": "gpt-4-1106-preview",
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
            "name": "get_robot_current_room",
            "description": "Get the name of the room where the robot currently is",
            "parameters": {}
        },   
        {
            "name": "get_current_position",
            "description": "Get the current position of the robot",
            "parameters": {}
        }
    ],
    "config_list": config_list,
}

# # Initialize AutoGen agents
# user = autogen.UserProxyAgent(name="User")
# robot_agent = autogen.AssistantAgent(name="Robot", llm_config=llm_config)

# # Register functions with the UserProxyAgent
# user.register_function(
#     function_map={
#         "move_robot": move_robot,
#         "get_current_position": get_current_position,
#         "get_robot_current_room": get_robot_current_room
#     }
# )

# # Example AutoGen interaction (hypothetical usage)
# user.initiate_chat(
#     robot_agent,
#     message="Move robot to position (30, 30) and tell me which room the robot is in",
# )


# Pygame initialization
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
DASHBOARD_HEIGHT = 150  # Height of the dashboard area

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Robot Room Simulator")
# Calculate the center of the screen
center_x = SCREEN_WIDTH // 2
center_y = SCREEN_HEIGHT // 2

# Adjust the room position to be centered
room_width = 100
room_height = 100
living_room = Room("Living Room", center_x - room_width // 2, center_y - room_height // 2, 
                   center_x + room_width // 2, center_y + room_height // 2)

# Set the robot's initial position to be at the center of the room
robot = Robot(center_x, center_y, living_room)
# Font for dashboard text
font = pygame.font.Font(None, 36)

# Function to draw the dashboard on the screen
def draw_dashboard():
    pygame.draw.rect(screen, BLACK, [0, SCREEN_HEIGHT - DASHBOARD_HEIGHT, SCREEN_WIDTH, DASHBOARD_HEIGHT])
    current_room_text = font.render(f"Current Room: {get_robot_current_room()}", True, WHITE)
    current_position_text = font.render(f"Position: {get_current_position()}", True, WHITE)
    screen.blit(current_room_text, (10, SCREEN_HEIGHT - DASHBOARD_HEIGHT + 10))
    screen.blit(current_position_text, (10, SCREEN_HEIGHT - DASHBOARD_HEIGHT + 50))


def draw_room(room):
    # Draw the room with a contrasting color
    pygame.draw.rect(screen, (0, 0, 255), [room.x1, room.y1, room.x2 - room.x1, room.y2 - room.y1], 1)

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((255, 255, 255))  # Use a clearly visible color for the background

    # Draw the room and robot at visible coordinates
    draw_room(living_room)
    robot_position = robot.current_position()
    pygame.draw.circle(screen, (255, 0, 0), robot_position, 10)

    draw_dashboard()
    pygame.display.flip()

pygame.quit()