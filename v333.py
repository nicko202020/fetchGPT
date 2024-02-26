import autogen
import pygame
import threading 
import random
import datetime

class Robot:
    def __init__(self, start_node, graph, logger=None):
        self.current_node = start_node
        self.graph = graph
        self.logger = logger
        self.x, self.y = self.graph.get_node_coordinates(start_node)
        self.path = [start_node]

    def move_to_node(self, target_node):
        path = self.graph.find_path(self.current_node, target_node)
        if path:
            for node in path[1:]:
                self.current_node = node
                self.x, self.y = self.graph.get_node_coordinates(node)
                if self.logger:
                    self.logger.log(f"Moved to node {node} at position {self.x}, {self.y}")
            return f"Moved to {target_node}"
        return "Path not found"

    def move_to_coordinates(self, x, y):
        """Updates the robot's position based on coordinates. Not typically used with graph navigation."""
        self.x, self.x = x, y
        if self.logger:
            self.logger.log(f"Robot moved to new coordinates: ({x}, {y})")

    def current_position(self):
        """Returns the current position of the robot."""
        return [self.x, self.y]

    def current_room(self):
        """Determines the current room based on the robot's node."""
        for room_name, room_nodes in self.graph.nodes.items():
            if self.current_node in room_nodes:
                return room_name
        return "Unknown room"

class Graph:
    def __init__(self):
        self.nodes = {}
        self.edges = {}

    def add_node(self, room_name, node_id, coordinates):
        if room_name not in self.nodes:
            self.nodes[room_name] = {}
        self.nodes[room_name][node_id] = coordinates

    def add_edge(self, node1, node2, weight=1):
        if node1 not in self.edges:
            self.edges[node1] = {}
        if node2 not in self.edges:
            self.edges[node2] = {}
        self.edges[node1][node2] = weight
        self.edges[node2][node1] = weight

    def find_path(self, start, end):
        if start == end:
            return [start]
        visited = {start}
        queue = [[start]]
        while queue:
            path = queue.pop(0)
            node = path[-1]
            for adjacent in self.edges.get(node, {}):
                if adjacent not in visited:
                    new_path = list(path)
                    new_path.append(adjacent)
                    queue.append(new_path)
                    if adjacent == end:
                        return new_path
                    visited.add(adjacent)
        return []

    def get_node_coordinates(self, node_id):
        for room, nodes in self.nodes.items():
            if node_id in nodes:
                return nodes[node_id]
        return None

class Room:
    def __init__(self, name, x1, y1, x2, y2, graph):
        self.name = name
        self.bounds = (x1, y1, x2, y2)
        self.graph = graph
        self.nodes = []

    def is_inside(self, x, y, margin=0):
        """Check if a given point is inside the room considering an optional margin."""
        x1, y1, x2, y2 = self.bounds
        return (x1 - margin) <= x <= (x2 + margin) and (y1 - margin) <= y <= (y2 + margin)

    def add_node(self, node_id, coordinates):
        """Adds a node to the room and the associated graph."""
        self.nodes.append(node_id)
        self.graph.add_node(self.name, node_id, coordinates)

    def add_edge(self, node1, node2, weight=1):
        """Adds an edge between two nodes within the room in the graph."""
        if node1 in self.nodes and node2 in self.nodes:
            self.graph.add_edge(node1, node2, weight)

    def get_node_coordinates(self, node_id):
        """Get the coordinates of a specific node within the room."""
        return self.graph.get_node_coordinates(node_id)

class Logger:
    def __init__(self, log_file="simulation_log.txt"):
        self.log_file = log_file
        with open(self.log_file, "w") as file:
            file.write("Simulation Log\n")

    def log(self, message):
        with open(self.log_file, "a") as file:
            file.write(f"{message}\n")

    def log_action(self, action, details=""):
        """Logs an action with an optional detailed description."""
        action_message = f"Action: {action}"
        if details:
            action_message += f", Details: {details}"
        self.log(action_message)

    def log_error(self, error_message):
        """Logs an error message."""
        self.log(f"ERROR: {error_message}")

    def log_info(self, info_message):
        """Logs an informational message."""
        self.log(f"INFO: {info_message}")


def initialize_pygame():
    """Initializes the Pygame environment, including display settings and resources."""
    global screen, font
    pygame.init()
    SCREEN_WIDTH, SCREEN_HEIGHT = 1920, 1080
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Robot Room Simulator")
    font = pygame.font.Font(None, 36)  # Basic font for text rendering

def create_rooms_and_graph():
    """Creates room objects and initializes the graph for navigation."""
    global graph, living_room, kitchen  # More rooms can be added as needed
    graph = Graph()  # Assuming Graph class is defined earlier

    # Example room definitions with their positions and adding them to the graph
    living_room = Room("Living Room", 100, 100, 500, 400, graph)
    kitchen = Room("Kitchen", 510, 100, 910, 400, graph)

    # Adding nodes within rooms (example positions)
    living_room.add_node("LR1", (150, 150))
    living_room.add_node("LR2", (450, 350))
    kitchen.add_node("K1", (550, 150))
    kitchen.add_node("K2", (850, 350))

    # Connecting nodes with edges to represent possible paths
    living_room.add_edge("LR1", "LR2")
    kitchen.add_edge("K1", "K2")
    graph.add_edge("LR2", "K1")  # Assuming doors or pathways between rooms

def initialize_robot(start_node="LR1"):
    """Initializes the robot at a given start node."""
    global robot, logger
    logger = Logger()  # Assuming Logger class is defined earlier
    robot = Robot(start_node, graph, logger)  # Assuming Robot class is defined earlier

def setup_simulation():
    """Combines all initialization steps to set up the simulation environment."""
    initialize_pygame()
    create_rooms_and_graph()
    initialize_robot()
def navigate_robot_to_node(target_node):
    """Instructs the robot to navigate to a specified target node."""
    global robot  # Ensure the robot instance is accessible
    result = robot.move_to_node(target_node)
    if robot.logger:
        robot.logger.log_info(f"Navigation result: {result}")
    return result

def find_shortest_path(start_node, end_node):
    """Finds the shortest path between two nodes using the graph's pathfinding algorithm."""
    global graph  # Ensure the graph instance is accessible
    path = graph.find_path(start_node, end_node)
    if not path:
        return "No path found."
    # Optionally, log the found path
    if robot.logger:
        robot.logger.log_info(f"Found path from {start_node} to {end_node}: {path}")
    return path

def update_robot_position(new_x, new_y):
    """Updates the robot's position. This function might be less used with graph navigation but is here for completeness."""
    global robot  # Ensure the robot instance is accessible
    robot.x = new_x
    robot.y = new_y
    if robot.logger:
        robot.logger.log_info(f"Updated position to ({new_x}, {new_y})")

def get_current_robot_position():
    """Returns the current position of the robot."""
    global robot
    return robot.current_position()

def get_current_robot_room():
    """Returns the name of the room in which the robot currently is."""
    global robot
    return robot.current_room()

def draw_room(room):
    """Draws a room on the screen."""
    pygame.draw.rect(screen, (0, 0, 255), [room.bounds[0], room.bounds[1], room.bounds[2] - room.bounds[0], room.bounds[3] - room.bounds[1]], 1)

def draw_robot(robot):
    """Draws the robot at its current position."""
    pygame.draw.circle(screen, (255, 0, 0), (int(robot.x), int(robot.y)), 10)

def draw_path(path):
    """Draws the path the robot plans to take."""
    if len(path) > 1:
        for i in range(len(path) - 1):
            start_pos = graph.get_node_coordinates(path[i])
            end_pos = graph.get_node_coordinates(path[i+1])
            pygame.draw.line(screen, (0, 255, 0), start_pos, end_pos, 2)

def highlight_decision_point(node):
    """Highlights a node where a decision is made."""
    coordinates = graph.get_node_coordinates(node)
    pygame.draw.circle(screen, (255, 255, 0), coordinates, 15, 2)

def draw_subtask_paths(subtasks):
    """Draws visual cues for subtasks, assuming subtasks are represented as paths."""
    for subtask in subtasks:
        start_node, end_node = subtask
        start_pos = graph.get_node_coordinates(start_node)
        end_pos = graph.get_node_coordinates(end_node)
        pygame.draw.line(screen, (255, 165, 0), start_pos, end_pos, 1)

def draw_dashboard():
    """Draws the dashboard area with information about the robot's status."""
    pygame.draw.rect(screen, (0, 0, 0), [0, SCREEN_HEIGHT - DASHBOARD_HEIGHT, SCREEN_WIDTH, DASHBOARD_HEIGHT])
    current_room_text = font.render(f"Current Room: {get_current_robot_room()}", True, (255, 255, 255))
    current_position_text = font.render(f"Position: {get_current_robot_position()}", True, (255, 255, 255))
    screen.blit(current_room_text, (10, SCREEN_HEIGHT - DASHBOARD_HEIGHT + 10))
    screen.blit(current_position_text, (10, SCREEN_HEIGHT - DASHBOARD_HEIGHT + 50))
def handle_events():
    """Handles events such as input and quitting."""
    global running  # Assume 'running' is a flag controlling the main loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            handle_mouse_click(event.pos)
        elif event.type == pygame.KEYDOWN:
            handle_key_press(event.key)

def handle_mouse_click(position):
    """Handles mouse click events, potentially for interacting with the UI."""
    # Example: Check if a button is clicked
    if input_box.collidepoint(position):
        # Activate input box or handle button click
        pass  # Implement specific logic here

def handle_key_press(key):
    """Handles key press events, such as starting navigation or other commands."""
    if key == pygame.K_RETURN:
        # Example: Start navigation or execute a command
        pass  # Implement specific logic for handling return key or others

def handle_text_input(events):
    """Processes text input events for command execution."""
    global text  # Assume 'text' stores the current input string
    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                execute_command(text)
                text = ''  # Reset text input after executing the command
            elif event.key == pygame.K_BACKSPACE:
                text = text[:-1]  # Remove last character
            else:
                text += event.unicode  # Add character to text input

def execute_command(command):
    def llm_thread():
        # Initiating chat with the AutoGen agent using the provided command
        response = user.initiate_chat(
            robot_agent,
            message=command
        )

    # Start the LLM communication in a separate thread
    threading.Thread(target=llm_thread).start()

def log_info(message):
    """Logs informational messages to the log file."""
    if logger:  # Assuming 'logger' is the global Logger instance
        logger.log_info(message)

def log_action(action, details=""):
    """Logs actions taken by the robot or user, with optional details."""
    if logger:
        logger.log_action(action, details)

def log_error(error_message):
    """Logs error messages."""
    if logger:
        logger.log_error(error_message)

def move_robot(target_node):
    """Move the robot to a specified node."""
    global robot  # Ensure the 'robot' instance is globally accessible.
    return robot.move_to_node(target_node)
def get_current_position():
    """Get the current position of the robot."""
    global robot  # Assuming 'robot' is an instance of the Robot class
    return robot.current_position()

def get_robot_current_room():
    """Get the name of the room where the robot currently is."""
    global robot  # Assuming 'robot' is an instance of the Robot class
    return robot.current_room()

def get_path_to_room(end_room):
    global robot, graph
    if end_room in graph.nodes:
        start_node = robot.current_node
        end_node = next(iter(graph.nodes[end_room]))  # Assume we just pick the first node
        return robot.move_to_node(end_node)
    return []

def get_map_info():
    """
    Retrieves information about the map including rooms, their coordinates,
    and nodes within each room.
    """
    global graph  # Ensure the 'graph' instance is globally accessible.
    
    map_info = {}
    for room_name, room_nodes in graph.nodes.items():
        map_info[room_name] = {
            'name': room_name,
            'nodes': room_nodes
        }
    return map_info
def draw_edges(graph, screen):
    for start_node, connections in graph.edges.items():
        start_pos = graph.get_node_coordinates(start_node)
        for end_node, _ in connections.items():
            end_pos = graph.get_node_coordinates(end_node)
            pygame.draw.line(screen, (0, 255, 0), start_pos, end_pos, 1)
def draw_nodes(graph):
    for room, nodes in graph.nodes.items():
        for node_id, coordinates in nodes.items():
            pygame.draw.circle(screen, (192, 192, 192), coordinates, 5)

def draw_robot_path(robot, graph, color=(250, 255, 0)):
    if robot.path:
        for i in range(len(robot.path) - 1):
            start_pos = graph.get_node_coordinates(robot.path[i])
            end_pos = graph.get_node_coordinates(robot.path[i + 1])
            pygame.draw.line(screen, color, start_pos, end_pos, 5)
# Assuming the necessary imports and initial setup
# AutoGen configuration (hypothetical setup)
config_list = [
    {
        "model": "gpt-4-1106-preview",
        "api_key": "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",
    }
]
# Configuration for the autogen agent's capabilities
llm_config = {
    "functions": [
        {
            "name": "move_robot",
            "description": "Move the robot to a specified node",
            "parameters": {
                "type": "object",
                "properties": {
                    "target_node": {"type": "string", "description": "Target node identifier"}
                },
                "required": ["target_node"],
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
                "required": ["end_room"]
            }
        }
    ],
    "config_list": config_list,  # Ensure config_list is defined appropriately
}

# Initialize AutoGen agents with updated or additional functionalities if needed
user = autogen.UserProxyAgent(name="User", human_input_mode="NEVER", max_consecutive_auto_reply=10)
robot_agent = autogen.AssistantAgent(name="Robot", llm_config=llm_config)

# Register functions with the UserProxyAgent
# Ensure each referenced function is defined and correctly implemented in the project
user.register_function(
    function_map={
        "move_robot": move_robot,  # Function to move the robot
        "get_current_position": get_current_position,  # Function to get the robot's current position
        "get_robot_current_room": get_robot_current_room,  # Function to get the robot's current room
        "get_map_info": get_map_info,  # Uncomment and define this function if needed
        "get_path_to_room": get_path_to_room  # Function to get a path to a specified room
    }
)

# Integration within the main loop or event handling system
# Make sure to call the appropriate agent functions based on user input or simulation events
# Additional Setup and Initialization

# Pygame window, colors, and fonts initialization
pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT, DASHBOARD_HEIGHT = 1920, 1080, 150
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Robot Room Simulator")
font = pygame.font.Font(None, 36)  # Basic font for text rendering
WHITE, RED, BLACK = (255, 255, 255), (255, 0, 0), (0, 0, 0)

# Initialize the graph for navigation
graph = Graph()  # Assuming Graph class is defined

# Create rooms and add them to the graph
living_room = Room("Living Room", 100, 100, 500, 400, graph)
kitchen = Room("Kitchen", 510, 100, 910, 400, graph)

# Add nodes to rooms
living_room.add_node("LR1", (150, 150))
living_room.add_node("LR2", (450, 350))
kitchen.add_node("K1", (550, 150))
kitchen.add_node("K2", (850, 350))

# Add edges between nodes to represent possible paths
living_room.add_edge("LR1", "LR2")
kitchen.add_edge("K1", "K2")
graph.add_edge("LR2", "K1")  # Assuming doors or pathways between rooms

# Initialize the robot at a given start node
logger = Logger()  # Assuming Logger class is defined
robot = Robot("LR1", graph, logger)  # Assuming Robot class is defined

# Main loop setup
running = True
active = False  # For text input box state
text = ''  # For storing input text

# Input box setup for command input
input_box = pygame.Rect(100, SCREEN_HEIGHT - 40, 140, 32)
color_inactive = pygame.Color('lightskyblue3')
color_active = pygame.Color('dodgerblue2')
color = color_inactive

while running:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if input_box.collidepoint(event.pos):
                active = not active
            else:
                active = False
            color = color_active if active else color_inactive
        elif event.type == pygame.KEYDOWN:
            if active:
                if event.key == pygame.K_RETURN:
                    execute_command(text)  # Assuming execute_command function exists
                    text = ''
                elif event.key == pygame.K_BACKSPACE:
                    text = text[:-1]
                else:
                    text += event.unicode

    # Fill the screen with white
    screen.fill(WHITE)
    draw_nodes(graph)  
    draw_edges(graph, screen)  
    draw_room(living_room)  
    draw_room(kitchen)
    draw_robot_path(robot, graph)  
    draw_robot(robot)  
    # Optional: draw planned path or highlight decision points here

    # Draw the dashboard and input box
    draw_dashboard()  # Assuming draw_dashboard function exists
    txt_surface = font.render(text, True, color)
    width = max(200, txt_surface.get_width() + 10)
    input_box.w = width
    screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
    pygame.draw.rect(screen, color, input_box, 2)

    pygame.display.flip()

pygame.quit()