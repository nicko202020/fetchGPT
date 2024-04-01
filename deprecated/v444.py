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
class Robot:
    def __init__(self, start_node, graph, image_path=None, logger=None):
        self.current_node = start_node
        self.graph = graph
        self.logger = logger
        self.x, self.y = self.graph.get_node_coordinates(start_node)
        self.path = []
        self.image = pygame.image.load(image_path).convert_alpha() if image_path else None
        if self.image:
            self.image = pygame.transform.scale(self.image, (50, 50))
        self.held_item = None

    def move_to_node(self, target_node):
        """Sets a path for the robot towards the target node."""
        path = self.graph.find_path(self.current_node, target_node)
        if path:
            self.path = path
            self.update_position()
            return f"Moving to {target_node}"
        else:
            return "Path not found"

    def update_position(self):
        """Updates the robot's current position along the path."""
        if self.path:
            self.current_node = self.path.pop(0)
            self.x, self.y = self.graph.get_node_coordinates(self.current_node)
            if self.logger:
                self.logger.log(f"Moved to node {self.current_node} at position {self.x}, {self.y}")

    def pick_up_item(self, item_manager, item_id):
        """Picks up an item if the robot is at the correct location."""
        if item_manager.get_item_location(item_id) == self.current_node:
            self.held_item = item_id
            item_manager.remove_item(item_id)
            if self.logger:
                self.logger.log(f"Picked up item {item_id} at {self.current_node}")
            return f"Picked up {item_id}"
        else:
            return f"Cannot pick up {item_id}; not at the correct location."

    def drop_off_item(self, item_manager, item_id, node_id):
        """Drops off an item at a specific node if the robot is there and holds the item."""
        if self.held_item == item_id and self.current_node == node_id:
            self.held_item = None
            item_manager.update_item_location(item_id, node_id)
            if self.logger:
                self.logger.log(f"Dropped off item {item_id} at {node_id}")
            return f"Dropped off {item_id}"
        else:
            return f"Cannot drop off {item_id}; conditions not met."

    def current_position(self):
        """Returns the current position of the robot."""
        return self.current_node
    def current_room(self):
        """Determines and returns the current room based on the robot's node."""
        for room_name, room_nodes in self.graph.nodes.items():
            if self.current_node in room_nodes:
                return room_name
        return "Unknown room"

    def draw(self, screen):
        """Draws the robot's current image at its position."""
        if self.image:
            screen.blit(self.image, (self.x - self.image.get_width() // 2, self.y - self.image.get_height() // 2))
        else:
            # If no image is provided, fall back to a simple representation.
            pygame.draw.circle(screen, (255, 0, 0), (int(self.x), int(self.y)), 10)


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
    def get_map_info(self):
        """Returns information about the map including rooms and their nodes."""
        return {
            room_name: {
                'nodes': {node_id: coordinates for node_id, coordinates in room.items()}
                for room_name, room in self.nodes.items()
            }
        }

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

def move_robot(target_node):
    global robot
    result = robot.move_to_node(target_node)
    if result:
        return f"Robot moved to {target_node}"
    return "Movement failed; path not found."

def get_current_robot_position():
    """Retrieves the robot's current position."""
    global robot
    robot.current_position()
    return robot.current_position()

def get_robot_current_room():
    """Identifies the room where the robot is currently located."""
    global robot
    return robot.current_room()

def get_map_info():
    global graph
    map_info = {}
    for room_name, nodes in graph.nodes.items():
        map_info[room_name] = {'nodes': nodes}
    return map_info

def get_path_to_room(end_room):
    """Calculates a path to a specified room and directs the robot to follow it."""
    global robot, graph
    if end_room in graph.nodes:
        start_node = robot.current_node
        end_node = next(iter(graph.nodes[end_room]))  # Pick an arbitrary node within the target room
        path = robot.move_to_node(end_node)
        if robot.logger:
            robot.logger.log_info(f"Path to room '{end_room}' requested: {path}")
        return path
    else:
        if robot.logger:
            robot.logger.log_error(f"Path to unknown room '{end_room}' requested.")
        return "Unknown room"

def pick_up_item_robot(item_id):
    global robot, item_manager, items
    if robot.current_node == item_manager.get_item_location(item_id):
        robot.pick_up_item(item_manager, item_id)
        return f"Picked up {item_id}"
    return "Item not picked up; robot is not at the correct location."

def drop_off_item_robot(item_id, node_id):
    global robot, item_manager
    if robot.held_item and robot.held_item.item_id == item_id and robot.current_node == node_id:
        robot.drop_off_item(item_manager, item_id, node_id)
        return f"Dropped off {item_id} at {node_id}"
    return "Cannot drop off; conditions not met."

def get_item_location_robot(item_id):
    """Fetches the location of a specified item."""
    global item_manager
    return item_manager.get_item_location(item_id)

def get_all_items_robot():
    """Retrieves locations for all items being tracked."""
    global item_manager
    return item_manager.get_all_items()

    
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
    """Draws the dashboard area with information about the robot's status."""
    global robot, font, SCREEN_HEIGHT  # Ensure all necessary globals are referenced
    pygame.draw.rect(screen, (0, 0, 0), [0, SCREEN_HEIGHT - 150, 1920, 150])
    current_room_text = font.render(f"Current Room: {robot.current_room()}", True, (255, 255, 255))
    current_position_text = font.render(f"Position: {robot.current_position()}", True, (255, 255, 255))
    screen.blit(current_room_text, (10, SCREEN_HEIGHT - 140))
    screen.blit(current_position_text, (10, SCREEN_HEIGHT - 100))
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
def draw_edges(graph, screen):
    for start_node, connections in graph.edges.items():
        start_pos = graph.get_node_coordinates(start_node)
        for end_node, _ in connections.items():
            end_pos = graph.get_node_coordinates(end_node)
            pygame.draw.line(screen, (0, 255, 0), start_pos, end_pos, 1)
def draw_nodes(graph, screen):
    """Draws nodes on the screen."""
    for room, nodes in graph.nodes.items():
        for node_id, coordinates in nodes.items():
            # Assuming a simple representation with circles for nodes
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


def draw_item_on_map(screen, robot, item_manager, items, graph):
    for item_id, node_id in item_manager.get_all_items().items():
        item = items.get(item_id)
        
        # Check if the robot holds the item and the item object is valid
        if robot.held_item and robot.held_item.item_id == item_id:
            robot_position = (robot.x, robot.y - item.image.get_height() // 2)
            item.draw(screen, robot_position, is_held=True)
        else:
            node_position = graph.get_node_coordinates(node_id)
            offset_position = (node_position[0], node_position[1] - item.image.get_height() // 2)
            item.draw(screen, offset_position, is_held=False)
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
            "description": "Move the robot to a specified node",
            "parameters": {
                "type": "object",
                "properties": {
                    "target_node": {"type": "string", "description": "Target node identifier"}
                },
                "required": ["target_node"]
            }
        },
        {
            "name": "get_current_robot_position",
            "description": "Get the current position of the robot",
            "parameters": {}
        },
        {
            "name": "get_robot_current_room",
            "description": "Get the name of the room where the robot currently is",
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
            }
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
            }
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
            }
        },
        {
            "name": "get_all_items_robot",
            "description": "Retrieve all available items and their locations",
            "parameters": {}
        }
    ],
    "config_list": config_list
}

# Initialize AutoGen agents
user = autogen.UserProxyAgent(name="User", human_input_mode="NEVER", max_consecutive_auto_reply=10)
robot_agent = autogen.AssistantAgent(name="Robot", llm_config=llm_config)

# Register functions with the UserProxyAgent
user.register_function(
    function_map={
        "move_robot": move_robot,
        "get_current_robot_position": get_current_robot_position,
        "get_robot_current_room": get_robot_current_room,
        "get_map_info": get_map_info,
        "get_path_to_room": get_path_to_room,
        "pick_up_item_robot": pick_up_item_robot,
        "drop_off_item_robot": drop_off_item_robot,
        "get_item_location_robot": get_item_location_robot,
        "get_all_items_robot": get_all_items_robot
    }
)


# Initialize everything
initialize_pygame()

item_manager = ItemLocationManager()
# Initialize items and their locations
items = {
    'water': Item('water', r'C:\Users\oeini\OneDrive\Documents\GitHub\creativeagency\robot-llm\3105807.png', target_size=(25, 25)),
    'banana': Item('banana', r'C:\Users\oeini\OneDrive\Documents\GitHub\creativeagency\robot-llm\png-clipart-banana-powder-fruit-cavendish-banana-banana-yellow-banana-fruit-food-image-file-formats-thumbnail.png', target_size=(25, 25)),
}

# Update the locations for the items
item_manager.update_item_location('water', 'LR1')
item_manager.update_item_location('banana', 'K4')
create_rooms_and_graph()
initialize_robot("LR1")
WHITE, RED, BLACK = (255, 255, 255), (255, 0, 0), (0, 0, 0)
# Setting initial parameters for the simulation loop
running = True
active = False  # State for text input handling
text = ''  # To store input text
SCREEN_WIDTH, SCREEN_HEIGHT, DASHBOARD_HEIGHT = 1920, 1080, 150

# Define input box for command inputs in GUI
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
            # Toggle active state of input box on click
            if input_box.collidepoint(event.pos):
                active = not active
            else:
                active = False
            color = color_active if active else color_inactive
        elif event.type == pygame.KEYDOWN:
            if active:
                if event.key == pygame.K_RETURN:
                    # Execute the command and reset
                    execute_command(text)  # Placeholder for your command execution logic
                    text = ''
                elif event.key == pygame.K_BACKSPACE:
                    text = text[:-1]  # Remove last character
                else:
                    text += event.unicode  # Append character

    # Update robot's movement if it has a path
    if robot.path:
        robot.update_position()

    # Rendering
    screen.fill(BLACK)  # Or any other background color
    draw_edges(graph, screen)
    draw_nodes(graph, screen)
    draw_room(living_room)
    draw_room(kitchen)
    draw_item_on_map(screen, robot, item_manager, items, graph)
    draw_robot(robot, screen)
    draw_dashboard()

    # Render the command input box and current text
    txt_surface = font.render(text, True, color)
    width = max(200, txt_surface.get_width() + 10)
    input_box.w = width
    screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
    pygame.draw.rect(screen, color, input_box, 2)

    pygame.display.flip()  # Update the display

pygame.quit()