import pygame
import autogen
from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent
from autogen import AssistantAgent
import chromadb
config_list = [
    {
        "model": "gpt-4",
        "api_key": "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",
    }
]

llm_config = {
    "functions": [
        {
            "name": "current_pos",
            "description": "Uses the object robot and check's the current position based on the values in self.x and self.y",
            "parameters": {
                "type": "object",
                "properties": {
                    "hops": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "description": "The function checks the robot's current position by looking at the self.x and self.y values in the class",
                    }
                },
            },
        },

    ],
    "config_list": config_list,
    "request_timeout": 120,
    "seed": 100,
    "temperature":0.7
}

autogen.ChatCompletion.start_logging()
termination_msg = lambda x: isinstance(x, dict) and "TERMINATE" == str(x.get("content", ""))[-9:].upper()

class Room:
    def __init__(self, x, y, width, height, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.contents = []  # List to store items or other features in the room

    def contains_point(self, x, y):
        return self.rect.collidepoint(x, y)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        # Optionally, draw items or features within the room
        for item in self.contents:
            item.draw(screen)
class Robot:
    def __init__(self, start_x, start_y):
        self.x = start_x
        self.y = start_y
        self.size = 10  # Size of the robot for visualization


    def teleport(self, new_x, new_y):
        self.x = new_x
        self.y = new_y

    def current_room(self, rooms):
        for room in rooms:
            if room.contains_point(self.x, self.y):
                return room
        return None
    def draw(self, screen):
        # Draw the robot as a circle
        pygame.draw.circle(screen, (0, 0, 255), (self.x, self.y), self.size)



# Initialize Pygame
pygame.init()

# Set up the display
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Environment Simulation")


living_room = Room(100, 100, 300, 300, (255, 0, 0))  # Example room
kitchen = Room(400, 100, 200, 200, (0, 255, 0))      # Example room adjacent to the living room
rooms = [living_room, kitchen]

robot = Robot(0, 0)
def current_position(robot):
    current_pos = (robot.x, robot.y)
    return current_pos
not_llm_post = current_position(robot)
print(f"not llm {not_llm_post}")
boss = autogen.UserProxyAgent(
    name="Boss",
    is_termination_msg=termination_msg,
    human_input_mode="TERMINATE",
    system_message="The boss who ask questions and give tasks.",
    code_execution_config=False,  # we don't want to execute code in this case.
    )
robot = autogen.AssistantAgent(
    name="Robot",
    is_termination_msg=termination_msg,
    system_message="You are the brain of the robot. You will take a task, plan and execute it",
    llm_config=llm_config,
)
robot.register_function(
    function_map={
        "current_position": current_position,
    }
)
groupchat = autogen.GroupChat(
    agents=[boss, robot], messages=[], max_round=2
)
manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=llm_config)

# Start chatting with boss as this is the user proxy agent.
boss.initiate_chat(
    manager,
    message="What's the robot's current location",
)
# Main game loop
# running = True
# while running:
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             running = False

#     screen.fill((0, 0, 0))  # Clear screen

#     # Draw rooms
#     for room in rooms:
#         room.draw(screen)

#     # Teleport robot and draw it
#     # Modify the teleportation coordinates as needed for testing
#     robot.teleport(150, 150)
#     robot.draw(screen)

#     pygame.display.flip()  # Update the display
# pygame.quit()