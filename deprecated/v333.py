import autogen
import pygame
import threading 
import random
import datetime

class Item:
    def __init__(self, item_id, image_path=None, target_size=(50, 50)):
        self.item_id = item_id
        self.image_path = image_path
        self.image = pygame.image.load(image_path).convert_alpha() if image_path else None
        if self.image:
            self.image = pygame.transform.scale(self.image, target_size)  # Resize the image

    def draw(self, screen, position, is_held=False):
        if self.image:
            if is_held:
                screen.blit(self.image, position)
            else:
                # Center the image above the node by adjusting both x and y
                # The x-coordinate needs to be offset by half the image's width
                # The y-coordinate is decreased by the image's height to move it above
                offset_position = (position[0] - self.image.get_width() // 2, position[1] - self.image.get_height())
                screen.blit(self.image, offset_position)
class ItemLocationManager:
    def __init__(self):
        self.item_locations = {}  # Key: item_id, Value: node_id

    def update_item_location(self, item_id, node_id):
        self.item_locations[item_id] = node_id

    def get_item_location(self, item_id):
        return self.item_locations.get(item_id)

    def remove_item(self, item_id):
        if item_id in self.item_locations:
            del self.item_locations[item_id]
    def get_item_location(self, item_id):
        return self.item_locations.get(item_id, None)
    def get_all_items(self):
        """Returns a dictionary of all item IDs and their locations."""
        return self.item_locations
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
class Robot:
    def __init__(self, start_node, graph, image_path=None, logger=None):
        self.current_node = start_node
        self.graph = graph
        self.logger = logger
        self.x, self.y = self.graph.get_node_coordinates(start_node)
        self.path = []
        self.image = pygame.image.load(image_path).convert_alpha() if image_path else None
        if self.image:
            # Optionally, scale the image
            self.image = pygame.transform.scale(self.image, (50, 50))  # Resize to 50x50 or any appropriate size
        self.held_item = None  # Initialize held_item as None
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
        return self.current_node

    def current_room(self):
        """Determines the current room based on the robot's node."""
        for room_name, room_nodes in self.graph.nodes.items():
            if self.current_node in room_nodes:
                return room_name
        return "Unknown room"

    def pick_up_item(self, item_manager, item_id):
        if item_manager.get_item_location(item_id) == self.current_node:
            self.held_item = items[item_id]  # Assume item is identified by its ID for simplicity
            item_manager.remove_item(item_id)
            if self.logger:
                self.logger.log(f"Picked up item {item_id} at {self.current_node}")

    def drop_off_item(self, item_manager, item_id, node_id):
        if self.held_item == items[item_id]:
            self.held_item = None  # The robot is no longer holding the item
            item_manager.update_item_location(item_id, node_id)
            if self.logger:
                self.logger.log(f"Dropped off item {item_id} at {node_id}")


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


def initialize_pygame():
    """Initializes the Pygame environment, including display settings and resources."""
    global screen, font
    pygame.init()
    SCREEN_WIDTH, SCREEN_HEIGHT = 1920, 1080
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    font = pygame.font.Font(None, 36)  # Basic font for text rendering

def create_rooms_and_graph():
    """Creates room objects and initializes the graph for navigation."""
    global graph, living_room, kitchen, items, item_manager
    
    # Initialize the graph and item manager
    graph = Graph()
    item_manager = ItemLocationManager()

    # Define room boundaries and initialize rooms
    living_room = Room("living Room", 100, 100, 500, 400, graph)
    kitchen = Room("kitchen", 510, 100, 910, 400, graph)

    # Adding nodes within the Living Room
    living_room.add_node("LR1", (150, 150))
    living_room.add_node("LR2", (450, 150))
    living_room.add_node("LR3", (150, 350))
    living_room.add_node("LR4", (450, 350))

    # Adding nodes within the Kitchen
    kitchen.add_node("K1", (550, 150))
    kitchen.add_node("K2", (850, 150))
    kitchen.add_node("K3", (550, 350))
    kitchen.add_node("K4", (850, 350))

    # Connecting nodes with edges to represent possible paths within rooms
    living_room.add_edge("LR1", "LR2")
    living_room.add_edge("LR2", "LR4")
    living_room.add_edge("LR3", "LR4")
    living_room.add_edge("LR1", "LR3")

    kitchen.add_edge("K1", "K2")
    kitchen.add_edge("K2", "K4")
    kitchen.add_edge("K3", "K4")
    kitchen.add_edge("K1", "K3")

    # Connecting a node between the two rooms
    graph.add_edge("LR4", "K1")
def initialize_robot(start_node="LR1"):
    """Initializes the robot at a given start node."""
    global robot, logger
    logger = Logger()  
    image_path = r'C:\Users\oeini\OneDrive\Documents\GitHub\creativeagency\robot-llm\143b8e1550deda3eadf5a8c0045cbb0f-robot-toy-flat-removebg-preview.png'
    robot = Robot(start_node, graph, image_path, logger)  

def setup_simulation():
    """Combines all initialization steps to set up the simulation environment."""
    initialize_pygame()
    create_rooms_and_graph()
    initialize_robot()
def navigate_robot_to_node(target_node):
    """Instructs the robot to navigate to a specified target node."""
    global robot  
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

def draw_robot(robot, screen):
    if robot.image:
        # Calculate the top-left corner coordinates to center the image on the robot's position
        image_rect = robot.image.get_rect(center=(int(robot.x), int(robot.y)))
        screen.blit(robot.image, image_rect.topleft)
    else:
        # Fallback to a simple circle if no image is provided
        pygame.draw.circle(screen, (255, 0, 0), (int(robot.x), int(robot.y)), 10)

def draw_path(path):
    """Draws the path the robot plans to take."""
    if len(path) > 1:
        for i in range(len(path) - 1):
            start_pos = graph.get_node_coordinates(path[i])
            end_pos = graph.get_node_coordinates(path[i+1])
            pygame.draw.line(screen, (0, 255, 0), start_pos, end_pos, 2)

def draw_item(screen, position, color, size):
    """Draws a square shape at the given position."""
    x, y = position
    # Define the top-left corner of the square based on the desired size
    top_left_x = x - size // 2
    top_left_y = y - size // 2
    # Draw a square using pygame.draw.rect
    pygame.draw.rect(screen, color, (top_left_x, top_left_y, size, size))

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
    global robot, font, SCREEN_HEIGHT  # Ensure all necessary globals are referenced
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
def log_message(message):
    global conversation_log
    conversation_log.append(message)
    if len(conversation_log) > MAX_MESSAGES:
        conversation_log.pop(0)  # Remove the oldest message
def draw_conversation(screen, font, conversation_log):
    start_y = 20  # Starting Y position to draw from
    line_height = 20  # Vertical space between lines
    for i, message in enumerate(conversation_log):
        text_surface = font.render(message, True, (255, 255, 255))
        screen.blit(text_surface, (20, start_y + i * line_height))
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
    """Calculates a path to a specified room without moving the robot."""
    global robot, graph
    if end_room in graph.nodes:
        # Pick an arbitrary node within the target room as the destination.
        start_node = robot.current_node
        end_node = next(iter(graph.nodes[end_room]))  # Pick an arbitrary node within the target room.

        # Find the path from the current node to the destination node.
        path = graph.find_path(start_node, end_node)

        # Log the found path for debugging or informational purposes.
        if robot.logger:
            robot.logger.log_info(f"Calculated path to room '{end_room}': {path}")
        return path
    else:
        # Handle the case where the specified room is unknown.
        if robot.logger:
            robot.logger.log_error(f"Path to unknown room '{end_room}' requested.")
        return "Unknown room"
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

def render_items(item_manager, graph, screen, robot):
    for item_id, node_id in item_manager.item_locations.items():
        node_coordinates = graph.get_node_coordinates(node_id)
        # Check if the item is not held by the robot
        if not (robot.held_item and robot.held_item.item_id == item_id):
            draw_item(screen, node_coordinates, (255, 255, 0), 20)  # Yellow color, size of 20

global item_manager

def pick_up_item_robot(item_id):
    """Global function to command the robot to pick up an item."""
    global robot
    return robot.pick_up_item(item_manager, item_id)

def drop_off_item_robot(item_id, node_id):
    """Global function to command the robot to drop off an item."""
    global robot
    return robot.drop_off_item(item_manager, item_id, node_id)

def get_item_location_robot(item_id):
    """Global function to get the location of an item."""
    global item_manager
    return item_manager.get_item_location(item_id)
def get_all_items_robot():
    """Global function to access all items and their locations from the item manager."""
    return item_manager.get_all_items()

def draw_item_on_map(screen, robot, item_manager, items, graph):
    for item_id, node_id in item_manager.get_all_items().items():
        item = items.get(item_id)
        
        # Adjust the drawing based on whether the robot holds the item
        if robot.held_item and robot.held_item.item_id == item_id:
            # Center the item on the robot's position
            robot_position = (robot.x, robot.y - item.image.get_height() // 2)
            item.draw(screen, robot_position, is_held=True)
        else:
            # Draw the item north of its node without touching it
            node_position = graph.get_node_coordinates(node_id)
            offset_position = (node_position[0], node_position[1] - item.image.get_height() // 2)
            item.draw(screen, offset_position, is_held=False)
# AutoGen configuration
config_list = [
    {
        "model": "gpt-4-1106-preview",
        "api_key": "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",
    }
]
#Autogen agent function descriptoons
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
            },
        },
        {
            "name": "pick_up_item_robot",
            "description": "Instruct the robot to pick up an item at its current node",
            "parameters": {
                "type": "object",
                "properties": {
                    "item_id": {"type": "string", "description": "Identifier of the item to pick up"}
                },
                "required": ["item_id"]
            },
        },
        {
            "name": "drop_off_item_robot",
            "description": "Instruct the robot to drop off an item at a specified node",
            "parameters": {
                "type": "object",
                "properties": {
                    "node_id": {"type": "string", "description": "Node identifier where to drop off the item"},
                    "item_id": {"type": "string", "description": "Identifier of the item to drop off"}
                },
                "required": ["node_id", "item_id"]
            },
        },
        {
            "name": "get_item_location_robot",
            "description": "Retrieve the location of a specified item",
            "parameters": {
                "type": "object",
                "properties": {
                    "item_id": {"type": "string", "description": "Identifier of the item to locate"}
                },
                "required": ["item_id"]
                },
        },
        {
    "name": "get_all_items_robot",
    "description": "Retrieve all available items and their locations",
    "parameters": {},
        },
    ],
    "config_list": config_list,  
}

# Initialize AutoGen agents
user = autogen.UserProxyAgent(name="User", human_input_mode="NEVER", max_consecutive_auto_reply=10)
robot_agent = autogen.AssistantAgent(name="Robot", llm_config=llm_config)

# Register functions with the UserProxyAgent
# Ensure each referenced function is defined and correctly implemented in the project
user.register_function(
    function_map={
        "move_robot": move_robot,  # Presumed to correctly handle its context internally
        "get_current_position": get_current_position,  # Ditto
        "get_robot_current_room": get_robot_current_room,  # Ditto
        "get_map_info": get_map_info,  # Presumed available and correctly scoped
        "get_path_to_room": get_path_to_room,  # Presumed to correctly handle its context internally
        "pick_up_item_robot": pick_up_item_robot,  # Now also presumed to handle context and parameters correctly
        "drop_off_item_robot": drop_off_item_robot,  
        "get_item_location_robot": get_item_location_robot,
        "get_all_items_robot": get_all_items_robot,
    }
)


setup_simulation()
create_rooms_and_graph()
# Pygame window, colors, and fonts initialization
SCREEN_WIDTH, SCREEN_HEIGHT, DASHBOARD_HEIGHT = 1920, 1080, 150
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
font = pygame.font.Font(None, 36)  # Basic font for text rendering
WHITE, RED, BLACK = (255, 255, 255), (255, 0, 0), (0, 0, 0)





initialize_robot("LR1")
# Initialize the robot at a given start node
logger = Logger()  
MAX_MESSAGES = 5  # Maximum number of messages to display
conversation_log = []  # Holds the most recent conversation lines
robot_image_path = r'C:\Users\oeini\OneDrive\Documents\GitHub\creativeagency\robot-llm\143b8e1550deda3eadf5a8c0045cbb0f-robot-toy-flat-removebg-preview.png'
robot = Robot("LR1", graph, robot_image_path, logger)
 
item_manager = ItemLocationManager()
# Initialize items and their locations
items = {
    'water': Item('water', r'C:\Users\oeini\OneDrive\Documents\GitHub\creativeagency\robot-llm\3105807.png', target_size=(25, 25)),
    'banana': Item('banana', r'C:\Users\oeini\OneDrive\Documents\GitHub\creativeagency\robot-llm\png-clipart-banana-powder-fruit-cavendish-banana-banana-yellow-banana-fruit-food-image-file-formats-thumbnail.png', target_size=(25, 25)),
}

# Update the locations for the items
item_manager.update_item_location('water', 'LR1')
item_manager.update_item_location('banana', 'K4')
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
                    # Here you might handle the command, possibly affecting the robot and items
                    execute_command(text)  # Modify to execute commands
                    text = ''
                elif event.key == pygame.K_BACKSPACE:
                    text = text[:-1]
                else:
                    text += event.unicode

    # Fill the screen with white
    screen.fill(BLACK)
    draw_nodes(graph)  
    draw_edges(graph, screen)  
    draw_room(living_room)  
    draw_room(kitchen)

    # Draw items on the map
    draw_item_on_map(screen, robot, item_manager, items, graph)

    draw_robot_path(robot, graph)  
    draw_robot(robot, screen)  
    # Optional: draw planned path or highlight decision points here
    # Draw the conversation

    # draw_conversation(screen, font, conversation_log)
    # Draw the dashboard and input box
    draw_dashboard()  
    txt_surface = font.render(text, True, color)
    width = max(200, txt_surface.get_width() + 10)
    input_box.w = width
    screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
    pygame.draw.rect(screen, color, input_box, 2)

    pygame.display.flip()   

pygame.quit()