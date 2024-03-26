import autogen
import pygame
import threading 
import random

class Room:
    def __init__(self, name, x1, y1, x2, y2):
        self.name = name
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

    def is_inside(self, x, y, margin=0):
        return (self.x1 - margin) <= x <= (self.x2 + margin) and (self.y1 - margin) <= y <= (self.y2 + margin)

class Robot:
    def __init__(self, start_x, start_y, room):
        self.x = start_x
        self.y = start_y
        self.room = room

    def teleport(self, new_x, new_y):
        self.x = new_x
        self.y = new_y
        return f"Moved to ({new_x}, {new_y})"


    def current_position(self):
        return [self.x, self.y]

    def current_room(self):
        if self.room.is_inside(self.x, self.y):
            return self.room.name
        return "Unknown room"

#Functions used by agent
def move_robot(new_x, new_y):
    global robot
    return robot.teleport(new_x, new_y)

def get_current_position():
    global robot
    return robot.current_position()

def get_robot_current_room():
    global robot
    return robot.current_room()

def get_map_info():
    return {"Rooms": map, "Nodes": nodes}

def navigate_path(start, end):
    global robot, nodes, paths
    path_key = start + " to " + end
    if path_key in paths:
        for node in paths[path_key]:
            node_info = nodes[node]
            robot.teleport(node_info["x"], node_info["y"])
            # Optionally, update the Pygame display here
        return f"Robot moved from {start} to {end}"
    return "Path not found"

# Function to draw dashboard
def draw_dashboard():
    pygame.draw.rect(screen, BLACK, [0, SCREEN_HEIGHT - DASHBOARD_HEIGHT, SCREEN_WIDTH, DASHBOARD_HEIGHT])
    current_room_text = font.render(f"Current Room: {get_robot_current_room()}", True, WHITE)
    current_position_text = font.render(f"Position: {get_current_position()}", True, WHITE)
    screen.blit(current_room_text, (10, SCREEN_HEIGHT - DASHBOARD_HEIGHT + 10))
    screen.blit(current_position_text, (10, SCREEN_HEIGHT - DASHBOARD_HEIGHT + 50))


def draw_room(room):
    # Draw the room with a contrasting color
    pygame.draw.rect(screen, (0, 0, 255), [room.x1, room.y1, room.x2 - room.x1, room.y2 - room.y1], 1)

def handle_command_input(command):
    def llm_thread():
        # Initiating chat with the AutoGen agent using the provided command
        response = user.initiate_chat(
            robot_agent,
            message=command
        )

    # Use seperate thread for agent conversation
    threading.Thread(target=llm_thread).start()
def draw_button():
    pygame.draw.rect(screen, button_color, button)  # Draw the button
    button_text = font.render('Send', True, WHITE)
    screen.blit(button_text, (button.x + 20, button.y + 5))


#Pathfinding functions 
def find_path(start_room, end_room):
    if start_room in waypoints and end_room in waypoints:
        start_point = waypoints[start_room][0]  # Starting from the first waypoint of the room
        end_points = waypoints[end_room]
        # Find path to each endpoint in the destination room, choose the shortest
        paths = [a_star(start_point, end_point, waypoints[start_room] + end_points) for end_point in end_points]
        return min(paths, key=len) if paths else []
    return []

def get_path_to_room(end_room):
    current_room = get_robot_current_room()
    return find_path(current_room, end_room)

def distance_between_points(p1, p2):
    """Calculate the Euclidean distance between two points."""
    return ((p1['x'] - p2['x'])**2 + (p1['y'] - p2['y'])**2)**0.5
def a_star(start, end, waypoints):

    # Initialize both open and closed list
    open_list = []
    closed_list = set()

    # Add the start node
    open_list.append((start, [start]))

    # Loop until you find the end
    while open_list:
        # Get the current node (node with lowest f = g + h)
        current_node, path = min(open_list, key=lambda x: distance_between_points(x[0], end))
        open_list.remove((current_node, path))

        # Found the goal
        if current_node == end:
            return path

        # Generate children (adjacent waypoints)
        children = [wp for wp in waypoints if wp != current_node]

        # Loop through children
        for child in children:

            # Child is on the closed list
            if child in closed_list:
                continue

            # Create the f, g, and h values
            g = distance_between_points(start, child)
            h = distance_between_points(child, end)
            f = g + h

            # Add the child to the open list
            open_list.append((child, path + [child]))

        # Add current node to the closed list
        closed_list.add(current_node)

    return []

# Screen dimensions
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
DASHBOARD_HEIGHT = 150  # Height of the dashboard area

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)


screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

center_x = SCREEN_WIDTH // 2
center_y = SCREEN_HEIGHT // 2


room_width = 100
room_height = 100

living_room_x1 = center_x - room_width // 2
living_room_y1 = center_y - room_height // 2
living_room_x2 = center_x + room_width // 2
living_room_y2 = center_y + room_height // 2
living_room = Room("Living Room", living_room_x1, living_room_y1, 
                   living_room_x2, living_room_y2)

kitchen_x1 = living_room.x2
kitchen_y1 = living_room.y1
kitchen_x2 = kitchen_x1 + room_width
kitchen_y2 = living_room.y2
kitchen = Room("Kitchen", kitchen_x1, kitchen_y1, kitchen_x2, kitchen_y2)
map = {
    "Living Room": {
        "bounds": {"x1": living_room_x1, "y1": living_room_y1, "x2": living_room_x2, "y2": living_room_y2},
        "waypoints": [
            {"x": living_room_x1 + 20, "y": living_room_y1 + 20},
            {"x": living_room_x1 + 20, "y": living_room_y2 - 20},
            {"x": living_room_x2 - 20, "y": living_room_y1 + 20},
            {"x": living_room_x2 - 20, "y": living_room_y2 - 20}
        ]
    },
    "Kitchen": {
        "bounds": {"x1": kitchen_x1, "y1": kitchen_y1, "x2": kitchen_x2, "y2": kitchen_y2},
        "waypoints": [
            {"x": kitchen_x1 + 20, "y": kitchen_y1 + 20},
            {"x": kitchen_x1 + 20, "y": kitchen_y2 - 20},
            {"x": kitchen_x2 - 20, "y": kitchen_y1 + 20},
            {"x": kitchen_x2 - 20, "y": kitchen_y2 - 20}
        ]
    }
    # Add more rooms with their bounds and waypoints as needed
}
# map = {
#     "Living Room": {"x1": living_room_x1, "y1": living_room_y1, "x2": living_room_x2, "y2": living_room_y2},
#     "Kitchen": {"x1": kitchen_x1, "y1": kitchen_y1, "x2": kitchen_x2, "y2": kitchen_y2}
# }
# waypoints = {
#     "Living Room": [
#         {"x": living_room_x1 + 20, "y": living_room_y1 + 20},
#         {"x": living_room_x1 + 20, "y": living_room_y2 - 20},
#         {"x": living_room_x2 - 20, "y": living_room_y1 + 20},
#         {"x": living_room_x2 - 20, "y": living_room_y2 - 20}
#     ],
#     "Kitchen": [
#         {"x": kitchen_x1 + 20, "y": kitchen_y1 + 20},
#         {"x": kitchen_x1 + 20, "y": kitchen_y2 - 20},
#         {"x": kitchen_x2 - 20, "y": kitchen_y1 + 20},
#         {"x": kitchen_x2 - 20, "y": kitchen_y2 - 20}
#     ]
# }



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
        },
        {
            "name": "get_map_info",
            "description": "Retrieve the map and node information",
            "parameters": {}
        },
        {
            "name": "get_path_to_room",
            "description": "Get a path to a specified room",
            "parameters": {
                "type": "object",
                "properties": {
                    "end_room": {"type": "string", "description": "Name of the destination room"}
                },
                "required": ["end_room"]}
        }
    ],
    "config_list": config_list,
}

# Initialize AutoGen agents
user = autogen.UserProxyAgent(name="User", human_input_mode="NEVER", max_consecutive_auto_reply=4)
robot_agent = autogen.AssistantAgent(name="Robot", llm_config=llm_config)

# Register functions with the UserProxyAgent
user.register_function(
    function_map={
        "move_robot": move_robot,
        "get_current_position": get_current_position,
        "get_robot_current_room": get_robot_current_room,
        # "get_map_info": get_map_info,
        "get_path_to_room": get_path_to_room
    }
)


# Pygame initialization
pygame.init()

# Set the robot's initial position to be at the center of the room
robot = Robot(living_room_x1+20, living_room_y1+20, living_room)
# Font for dashboard text
font = pygame.font.Font(None, 36)


# Input box and button setup
input_box = pygame.Rect(100, SCREEN_HEIGHT - 40, 140, 32)
button = pygame.Rect(250, SCREEN_HEIGHT - 40, 80, 32)  # Button position and size
button_color = pygame.Color('grey12')  # Button color
color_inactive = pygame.Color('lightskyblue3')
color_active = pygame.Color('dodgerblue2')
color = color_inactive
active = False
text = ''

# Main Pygame loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Check if the input box is clicked
            if input_box.collidepoint(event.pos):
                active = not active
            elif button.collidepoint(event.pos):
                # Handle the button click
                handle_command_input(text)
                text = ''  # Clear the text after sending the command
                active = False  # Deactivate the input box
            else:
                active = False
            color = color_active if active else color_inactive
        if event.type == pygame.KEYDOWN:
            if active:
                if event.key == pygame.K_RETURN:
                    handle_command_input(text)
                    text = ''  # Clear the text after sending the command
                elif event.key == pygame.K_BACKSPACE:
                    text = text[:-1]
                else:
                    text += event.unicode

    screen.fill(WHITE)  # Fill the screen with white

    # Draw the room and robot
    draw_room(living_room)
    draw_room(kitchen) 
    robot_position = robot.current_position()
    pygame.draw.circle(screen, RED, robot_position, 10)

    # Draw the dashboard and input box
    draw_dashboard()

    # Render the current text
    txt_surface = font.render(text, True, color)
    width = max(200, txt_surface.get_width() + 10)
    input_box.w = width
    screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
    pygame.draw.rect(screen, color, input_box, 2)

    # Draw the button
    # draw_button()  # Make sure this function is defined to draw the button

    pygame.display.flip()

pygame.quit()

