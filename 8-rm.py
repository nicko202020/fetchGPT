import autogen
import pygame
import threading 
import random
import datetime
import time
class User:
    def __init__(self, node_id, preferred_side='left', image_path=None, target_size=(50, 50)):
        self.node_id = node_id
        self.preferred_side = preferred_side  # 'left' or 'right'
        self.image_path = image_path
        self.target_size = target_size
        self.image = pygame.image.load(image_path).convert_alpha() if image_path else None
        if self.image:
            self.image = pygame.transform.scale(self.image, target_size)

    def draw(self, screen, position):
        if self.image:
            # Determine the offset based on the preferred side
            if self.preferred_side == 'left':
                offset_x = -self.target_size[0]
            else:
                offset_x = self.target_size[0]
                
            image_position = (position[0] + offset_x, position[1] - self.target_size[1] // 2)
            screen.blit(self.image, image_position)
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
class BlockedNode:
    def __init__(self):
        self.node_id = None  # Initially, no node is blocked

    def set_blocked_node(self, node_id):
        self.node_id = node_id

    def is_node_blocked(self, node_id):
        return self.node_id == node_id
class Robot:
    def __init__(self, start_node, graph, image_path=None, logger=None):
        self.current_node = start_node
        self.graph = graph
        self.logger = logger
        self.x, self.y = self.graph.get_node_coordinates(start_node)
        self.path = []
        self.blocked_nodes = []
        self.blockage_encountered = False
        self.image = pygame.image.load(image_path).convert_alpha() if image_path else None
        if self.image:
            # Optionally, scale the image
            self.image = pygame.transform.scale(self.image, (50, 50))  # Resize to 50x50 or any appropriate size
        self.held_item = None  # Initialize held_item as None
    def move_to_node(self, target_node):
        path = self.graph.find_path(self.current_node, target_node)
        if path:
            for node in path[1:]:
                # If moving to the graph's blocked node, record and report the blockage
                if node == self.graph.blocked_node:
                    # Here, we assume blocked_nodes is a list attribute of the Robot
                    if node not in self.blocked_nodes:
                        self.blocked_nodes.append(node)
                        if self.logger:
                            self.logger.log(f"Node {node} blocked")
                        return f"Node {node} blocked"
                
                # Continue if the node is in the blocked_nodes list
                if node in self.blocked_nodes:
                    if self.logger:
                        self.logger.log(f"Node {node} previously blocked")
                    continue

                # Update the robot's current position if not blocked
                self.current_node = node
                self.x, self.y = self.graph.get_node_coordinates(node)
                if self.logger:
                    self.logger.log(f"Moved to node {node}")
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
        """Attempts to pick up a specified item.

        Args:
            item_manager (ItemLocationManager): The manager controlling item locations.
            item_id (str): The ID of the item to pick up.

        Returns:
            str: A message indicating the result of the pick-up attempt.
        """
        if item_manager.get_item_location(item_id) == self.current_node:
            self.held_item = items[item_id]  # Assume item is identified by its ID for simplicity
            item_manager.remove_item(item_id)
            if self.logger:
                self.logger.log(f"Picked up item {item_id} at {self.current_node}")
            return f"Picked up item {item_id}"
        else:
            if self.logger:
                self.logger.log(f"Failed to pick up item {item_id} at {self.current_node}")
            return f"Failed to pick up item {item_id}. Item not at robot's current location."

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
        self.blocked_node = 'lr5'

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
    def find_path_avoiding_blocked_nodes(self, start, end, blocked_nodes):
        if start == end:
            return [start]
        visited = {start}
        queue = [[start]]
        while queue:
            path = queue.pop(0)
            node = path[-1]
            if node in blocked_nodes:
                continue  # Skip this node as it's blocked, but continue searching other paths
            for adjacent in self.edges.get(node, {}):
                if adjacent not in visited and adjacent not in blocked_nodes:
                    new_path = list(path)
                    new_path.append(adjacent)
                    queue.append(new_path)
                    if adjacent == end:
                        return new_path  # Return this path as soon as end node is reached
                    visited.add(adjacent)
        return None  # Return None if no path is found avoiding the blocked nodes
    def get_node_coordinates(self, node_id):
        for room, nodes in self.nodes.items():
            if node_id in nodes:
                return nodes[node_id]
        return None
    def get_all_nodes(self):
        """Retrieves all nodes from the graph."""
        return {node for room_nodes in self.nodes.values() for node in room_nodes}
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
    global graph, living_room, kitchen, dining_room, study_room, bedroom, bathroom, guest_room, gym, library, office
    
    
    # Initialize the graph
    graph = Graph()

    # Define centered room boundaries
    library = Room("library", 60, 240, 360, 540, graph)  # New room adjacent to the guest room on the left
    library.add_node("li1", (110, 290))
    library.add_node("li2", (310, 290))
    library.add_node("li3", (110, 490))
    library.add_node("li4", (310, 490))
    library.add_node("li5", (310, 390))
    library.add_edge("li1", "li2")
    library.add_edge("li2", "li5")
    library.add_edge("li5", "li4")
    library.add_edge("li4", "li3")
    library.add_edge("li3", "li1")
    graph.add_edge("li4", "of2") 

    graph.add_edge("gr6", "li5")  

    office = Room("office", 60, 540, 360, 840, graph)  # New room adjacent to the gym on the left
    office.add_node("of1", (110, 590))
    office.add_node("of2", (310, 590))
    office.add_node("of3", (110, 790))
    office.add_node("of4", (310, 790))
    office.add_node("of5", (310, 690))
    office.add_edge("of1", "of2")
    office.add_edge("of2", "of5")
    office.add_edge("of5", "of4")
    office.add_edge("of4", "of3")
    office.add_edge("of3", "of1")
    graph.add_edge("of5", "gy6")  

    guest_room = Room("guest room", 360, 240, 660, 540, graph)  # New room on the left of living room
    guest_room.add_node("gr1", (410, 290))  # Similar placement as lr1 but shifted left
    guest_room.add_node("gr2", (610, 290))  # Aligned horizontally with lr2
    guest_room.add_node("gr3", (410, 490))  # Aligned vertically with lr3
    guest_room.add_node("gr4", (610, 490))  # Similar to lr4 position
    guest_room.add_node("gr5", (610, 390))  # Similar to lr4 position
    guest_room.add_node("gr6", (410, 390))  # Similar to lr4 position
    guest_room.add_edge("gr1", "gr2")
    guest_room.add_edge("gr2", "gr5")
    guest_room.add_edge("gr5", "gr4")
    guest_room.add_edge("gr3", "gr4")
    guest_room.add_edge("gr3", "gr6")
    guest_room.add_edge("gr1", "gr6")
    

    graph.add_edge("gr4", "gy2")  

    graph.add_edge("lr6", "gr5")  
    gym = Room("gym", 360, 540, 660, 840, graph)   
    gym.add_node("gy1", (410, 590))  # Similar placement as s1 but shifted left
    gym.add_node("gy2", (610, 590))  # Aligned horizontally with s2
    gym.add_node("gy3", (410, 790))  # Aligned vertically with s3
    gym.add_node("gy4", (610, 790))  # Similar to s4 positio
    gym.add_node("gy5", (610, 690))  # Similar to s4 position
    gym.add_node("gy6", (410, 690))  # Similar to s4 position
    gym.add_edge("gy1", "gy2")
    gym.add_edge("gy2", "gy5")
    gym.add_edge("gy5", "gy4")
    gym.add_edge("gy3", "gy4")
    gym.add_edge("gy3", "gy6")
    gym.add_edge("gy1", "gy6")
    graph.add_edge("gy5", "s6")  
    
    living_room = Room("living room", 660, 240, 960, 540, graph)  # Left-top room
    living_room.add_node("lr1", (710, 290))  # Adjusted from (150, 150)
    living_room.add_node("lr2", (910, 290))  # Adjusted from (350, 150)
    living_room.add_node("lr3", (710, 490))  # Adjusted from (150, 350)
    living_room.add_node("lr4", (910, 490))  # Adjusted from (350, 350)
    living_room.add_node("lr5", (910, 390))  # Node near the boundary towards the Kitchen
    living_room.add_node("lr6", (710, 390))  # Node near the boundary towards the Kitchen
    living_room.add_edge("lr1", "lr2")
    living_room.add_edge("lr3", "lr6")
    living_room.add_edge("lr2", "lr5")
    living_room.add_edge("lr5", "lr4")
    living_room.add_edge("lr3", "lr4")
    living_room.add_edge("lr6", "lr1")
    graph.add_edge("lr5", "k5")
    graph.add_edge("lr4", "s2")
    
    study_room = Room("study room", 660, 540, 960, 840, graph)    # Left-bottom room
    
        # # Update nodes within Study Room (Left-Bottom)
    study_room.add_node("s1", (710, 590))  # Adjusted from (150, 450)
    study_room.add_node("s2", (910, 590))  # Adjusted from (350, 450)
    study_room.add_node("s3", (710, 790))  # Adjusted from (150, 650)
    study_room.add_node("s4", (910, 790))  # Adjusted from (350, 650)
    study_room.add_node("s5", (910, 690))  # Node near the boundary towards the Living Room
    study_room.add_node("s6", (710, 690))  # Node near the boundary towards the Living Room
    study_room.add_edge("s1", "s2")
    study_room.add_edge("s2", "s5")
    study_room.add_edge("s5", "s4")
    study_room.add_edge("s4", "s3")
    study_room.add_edge("s3", "s6")
    study_room.add_edge("s1", "s6")

    graph.add_edge("d5", "s5")



    kitchen = Room("kitchen", 960, 240, 1260, 540, graph)         # Right-top room
    kitchen.add_node("k1", (1010, 290))  # Adjusted from (450, 150)
    kitchen.add_node("k2", (1210, 290))  # Adjusted from (650, 150)
    kitchen.add_node("k3", (1010, 490))  # Adjusted from (450, 350)
    kitchen.add_node("k4", (1210, 490))  # Adjusted from (650, 350)
    kitchen.add_node("k5", (1010, 390))  # Node near the boundary towards the Living Room
    kitchen.add_node("k6", (1210, 390))  # Node near the boundary towards the Living Room
    kitchen.add_edge("k1", "k5")
    kitchen.add_edge("k5", "k3")
    kitchen.add_edge("k3", "k4")
    kitchen.add_edge("k4", "k6")
    kitchen.add_edge("k6", "k2")
    kitchen.add_edge("k1", "k2")
    graph.add_edge("k4", "d2")

    
    dining_room = Room("dining room", 960, 540, 1260, 840, graph) # Right-bottom room
    dining_room.add_node("d1", (1010, 590))  # Adjusted from (450, 450)
    dining_room.add_node("d2", (1210, 590))  # Adjusted from (650, 450)
    dining_room.add_node("d3", (1010, 790))  # Adjusted from (450, 650)
    dining_room.add_node("d4", (1210, 790))  # Adjusted from (650, 650)
    dining_room.add_node("d5", (1010, 690))  # Node near the boundary towards the Kitchen
    dining_room.add_node("d6", (1210, 690))  # Node near the boundary towards the Kitchen
    dining_room.add_edge("d1", "d2")
    dining_room.add_edge("d2", "d6")
    dining_room.add_edge("d6", "d4")
    dining_room.add_edge("d4", "d3")
    dining_room.add_edge("d3", "d5")
    dining_room.add_edge("d5", "d1")

    









def initialize_robot(start_node="lr1"):
    """Initializes the robot at a given start node."""
    global robot, logger
    logger = Logger()  
    image_path = r'C:\Users\oeini\OneDrive\Documents\GitHub\current\robot-llm\143b8e1550deda3eadf5a8c0045cbb0f-robot-toy-flat-removebg-preview.png'
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
def draw_user_on_map(screen, user, graph):
    node_position = graph.get_node_coordinates(user.node_id)
    
    if user.image:
        # Adjust the x coordinate based on the preferred side
        if user.preferred_side == 'left':
            offset_x = -user.image.get_width()  # Offset to the left
        else:
            offset_x = 0  # No offset to the right; already at the node's edge

        # Calculate the position to place the image beside the node
        user_position_x = node_position[0] + offset_x
        user_position_y = node_position[1] - user.image.get_height() // 2  # Vertically centered

        # Adjust position to not overlap the node
        image_position = (user_position_x, user_position_y)

        # Draw the user image at the calculated position
        screen.blit(user.image, image_position)
    else:
        # Fallback: Draw a simple circle if no image is provided
        offset_x = -20 if user.preferred_side == 'left' else 20  # Offset for the circle representation
        pygame.draw.circle(screen, (0, 0, 255), (node_position[0] + offset_x, node_position[1]), 10)
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

def move_robot(next_node):
    """Global function to move the robot to the next node."""
    global robot  # Ensure global access to the robot instance
    return robot.move_to_node(next_node)
def get_current_position():
    """Get the current position of the robot."""
    global robot  # Assuming 'robot' is an instance of the Robot class
    return robot.current_position()

def get_robot_current_room():
    """Get the name of the room where the robot currently is."""
    global robot  # Assuming 'robot' is an instance of the Robot class
    return robot.current_room()

def get_path(start_node, target_node):
    """Global function to find a path from the start node to the target node."""
    global robot, graph
    assert start_node in graph.get_all_nodes(), "Start must be a valid node identifier."
    assert target_node in graph.get_all_nodes(), "Target must be a valid node identifier."

    path = graph.find_path(start_node, target_node)
    return path if path else "Path not found."
def get_alternative_path(target_node, blocked_nodes):
    """Global function to find an alternative path avoiding certain nodes."""
    global robot, graph
    start_node = robot.current_node
    return graph.find_path_avoiding_blocked_nodes(start_node, target_node, blocked_nodes)
def get_node_info(room_name):
    """
    Retrieves information about the specified room, including its nodes and the connecting edges between those nodes.

    Args:
    room_name (str): The name of the room for which information is requested.

    Returns:
    dict: A dictionary containing the nodes within the specified room and the edges connecting those nodes.
    """
    global graph  # Ensure the 'graph' instance is globally accessible.

    # Initialize an empty dictionary for room info
    room_info = {}

    # Check if the room exists in the graph
    if room_name in graph.nodes:
        # Extract node names and their connecting edges within the room
        node_names = list(graph.nodes[room_name].keys())
        edges = {}
        for node in node_names:
            if node in graph.edges:
                # Only include edges that are within the same room
                edges[node] = {edge: graph.edges[node][edge] for edge in graph.edges[node] if edge in node_names}
        
        room_info = {
            'nodes': node_names,
            'edges': edges
        }
    
    return room_info
def draw_edges(graph, screen):
    for start_node, connections in graph.edges.items():
        start_pos = graph.get_node_coordinates(start_node)
        for end_node, _ in connections.items():
            end_pos = graph.get_node_coordinates(end_node)
            pygame.draw.line(screen, (0, 255, 0), start_pos, end_pos, 1)
def draw_nodes(graph, robot):
    RED = (255, 0, 0)
    GRAY = (192, 192, 192)
    for room, nodes in graph.nodes.items():
        for node_id, coordinates in nodes.items():
            node_color = RED if node_id in robot.blocked_nodes else GRAY
            pygame.draw.circle(screen, node_color, coordinates, 5)
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
def get_room_nodes(room_name):
    """Retrieves nodes within a specified room."""
    global graph  # Ensure the 'graph' instance is globally accessible.
    
    if room_name in graph.nodes:
        return list(graph.nodes[room_name].keys())
    else:
        return "Room not found"
def get_user_node():
    """Retrieves the node at which the user is currently located."""
    global me  # Assuming 'user' is globally accessible
    return me.node_id
def draw_item_on_map(screen, robot, item_manager, items, graph, user):
    for item_id, node_id in item_manager.get_all_items().items():
        item = items.get(item_id)

        if robot.held_item and robot.held_item.item_id == item_id:
            # Center the item on the robot's position
            robot_position = (robot.x, robot.y - item.image.get_height() // 2)
            item.draw(screen, robot_position, is_held=True)
        else:
            node_position = graph.get_node_coordinates(node_id)
            connected_nodes = graph.edges[node_id].keys()

            # Logic to determine item and user positioning
            # This logic assumes horizontal arrangement; adjust if your graph is more complex
            offset_x = 30
            item_x = node_position[0]
            user_x = node_position[0]

            # Check if the user is at the same node and decide on positions
            if user and user.node_id == node_id:
                # User is present at the node; decide where to place user and item
                # This simple logic places the user to the left and the item to the right
                user_x -= offset_x
                item_x += offset_x
            else:
                # No user at the node; item can be placed directly at the node
                item_x += offset_x  # Default placement to the right for simplicity

            user_position = (user_x, node_position[1])
            item_position = (item_x, node_position[1] - item.image.get_height() // 2)

            # Draw item based on calculated position
            item.draw(screen, item_position, is_held=False)
# AutoGen configuration
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
            "description": " Directs the robot to sequentially advance to the next specified node within its navigation path. This function is instrumental for continuous movement, based on paths generated by 'get_path' or 'get_alternative_path'. The function is iteratively called to navigate node by node, handling dynamic obstructions by flagging any encountered blocked nodes.",
            "parameters": {
                "type": "object",
                "properties": {
                    "next_node": {"type": "string", "description": " Identifier of the subsequent node in the robot's navigational route."}
                },
                "required": ["next_node"]
            }
        },
        {
            "name": "get_room_nodes",
            "description": "Obtains a collection of nodes within a designated room, enabling the robot to execute room-specific maneuvers or tasks. This function supports spatial awareness within the confined area, aiding in effective navigation or object interaction within that space.",
            "parameters": {
                "type": "object",
                "properties": {
                    "room_name": {"type": "string", "description": " Name of the room for which to retrieve nodes."}
                },
                "required": ["room_name"]
            }
        },
        {
            "name": "get_current_position",
            "description": "Determines the robot's present node, a fundamental aspect for initializing navigation or assessing the robot's progression toward its objective. This function is essential for situational awareness and path planning.",
            "parameters": {}
        },
        {
            "name": "get_path",
            "description": "Computes the most direct path from the robot's current location to the specified target node using the shortest available route. This function is used for initial path calculations before any blocked nodes are encountered or when there are no known obstructions. Should a path returned include any previously identified blocked nodes, 'get_alternative_path' should be used instead.",
            "parameters": {
                "type": "object",
                "properties": {
                    "start_node": {
                        "type": "string",
                        "description": "The starting node from which the path calculation initiates."
                    },
                    "target_node": {
                        "type": "string",
                        "description": "The endpoint node to which the path is calculated."
                    }
                },
                "required": ["start_node", "target_node"]
            }
        },
        {
            "name": "get_alternative_path",
            "description": "Calculates an alternative path to the given target node, specifically designed to avoid any known blocked nodes. This function is essential after encountering a blocked node during navigation, ensuring the robot can reroute around the obstruction. It is vital for the system to maintain an updated list of blocked nodes and to use this function for recalculating routes whenever the original path is compromised.",
            "parameters": {
                "type": "object",
                "properties": {

                    "target_node": {
                        "type": "string",
                        "description": "The destination node for the recalculated path, avoiding blocked nodes."
                    },
                    "blocked_nodes": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "An array of node identifiers that the recalculated path must avoid."
                    }
                },
                "required": ["target_node", "blocked_nodes"]
            }
        },
        {
            "name": "get_user_node",
            "description": "Identifies the user's current node, crucial for user-centric tasks or interactions, enabling the robot to localize the user within its operational domain.",
            "parameters": {}
        },
        {
            "name": "pick_up_item_robot",
            "description": "Commands the robot to acquire a specified item within its reach, essential for object retrieval missions. This function underpins the robot's ability to interact with and transport physical objects.",
            "parameters": {
                "type": "object",
                "properties": {
                    "item_id": {"type": "string", "description": "Identifier for the item to be picked up."}
                },
                "required": ["item_id"]
            }
        },
        {
            "name": "drop_off_item_robot",
            "description": " Instructs the robot to deposit an item at a given node, integral to delivery or item placement tasks. This function is pivotal for transferring objects to designated locations.",
            "parameters": {
                "type": "object",
                "properties": {
                    "node_id": {"type": "string", "description": "Identifiers for the drop-off location"},
                    "item_id": {"type": "string", "description": "Identifiers for the item"}
                },
                "required": ["node_id", "item_id"]
            }
        },
        {
            "name": "get_item_location_robot",
            "description": "Locates a specific item's node, facilitating retrieval or interaction strategies. This function is key for integrating object localization into the robot's task execution framework.",
            "parameters": {
                "type": "object",
                "properties": {
                    "item_id": {"type": "string", "description": "Identifier of the item to locate."}
                },
                "required": ["item_id"]
            }
        },
    ],
    "config_list": config_list,
}
# Initialize AutoGen agents
user = autogen.UserProxyAgent(name="User", 
human_input_mode="NEVER",
is_termination_msg=lambda x: x.get("content", "") and x.get("content", "").rstrip().endswith("TERMINATE"), 
max_consecutive_auto_reply=45)
robot_agent = autogen.AssistantAgent(name="Robot", 
llm_config=llm_config, 
system_message = """
Contextual Analysis:
  - Notable Nodes: 
      List nodes relevant to the current task, including the robot's position, 
      target item locations, and user or destination nodes.
  - Task Implications: 
      Analyze how the notable nodes influence the planned task, such as 
      movement paths or item retrieval/delivery strategies.

Decision-Making:
  - Chosen Path: 
      Describe the selected path for the robot's navigation, considering 
      initial or known blockages.
  - Interaction Plan: 
      Outline the plan for item interactions, including pick-up and drop-off 
      points, and how these plans may adapt to changes in the robot's navigable path.

Dynamic Response to Blockages:
  - On Blocked Node Encounter: 
      When move_robot signals a blocked node, document this node, halt current 
      movement, and invoke get_alternative_path with the known blocked nodes 
      to determine a new navigable route.
  - Subsequent Path Planning: 
      For any further path calculations, maintain awareness of all identified 
      blocked nodes. If the standard get_path returns a path including any 
      known blocked nodes, immediately seek an alternative using 
      get_alternative_path, ensuring the robot does not attempt to traverse 
      these blocked paths.

Output:
  - Movement Commands: 
      Provide updated move_robot commands to navigate the robot along the revised 
      path, avoiding all known blockages.
  - Interaction Commands: 
      Adjust commands like pick_up_item_robot and drop_off_item_robot to reflect 
      the robot's updated route and tasks, ensuring all actions are feasible 
      given the current navigational context.

Once the task is complete, respond with "TERMINATE".
""")

# Register functions with the UserProxyAgent
# Ensure each referenced function is defined and correctly implemented in the project
user.register_function(
    function_map={
        "move_robot": move_robot,
        "get_current_position": get_current_position,
        # "get_room_nodes": get_room_nodes,
        "get_path": get_path,
        "get_alternative_path": get_alternative_path,  
        "pick_up_item_robot": pick_up_item_robot,
        "drop_off_item_robot": drop_off_item_robot,
        "get_item_location_robot": get_item_location_robot,
        "get_user_node": get_user_node
    }
)

setup_simulation()
create_rooms_and_graph()
# Pygame window, colors, and fonts initialization
SCREEN_WIDTH, SCREEN_HEIGHT, DASHBOARD_HEIGHT = 1920, 1080, 150
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
font = pygame.font.Font(None, 36)  # Basic font for text rendering
WHITE, RED, BLACK = (255, 255, 255), (255, 0, 0), (0, 0, 0)





initialize_robot("lr1")
user_image_path = r'C:\Users\oeini\OneDrive\Documents\GitHub\Current\robot-llm\pngtree-man-in-shirt-smiles-and-gives-thumbs-up-to-show-approval-png-image_10094381.png'
me = User(node_id='li3', preferred_side='left', image_path=user_image_path)
# Initialize the robot at a given start node
logger = Logger()  
MAX_MESSAGES = 5  # Maximum number of messages to display
conversation_log = []  # Holds the most recent conversation lines
robot_image_path = r'C:\Users\oeini\OneDrive\Documents\\GitHub\current\robot-llm\143b8e1550deda3eadf5a8c0045cbb0f-robot-toy-flat-removebg-preview.png'
robot = Robot("lr1", graph, robot_image_path, logger)
 
item_manager = ItemLocationManager()
# Initialize items and their locations
items = {
    'water': Item('water', r'C:\Users\oeini\OneDrive\Documents\GitHub\current\robot-llm\3105807.png', target_size=(25, 25)),
    'banana': Item('banana', r'C:\Users\oeini\OneDrive\Documents\GitHub\current\robot-llm\png-clipart-banana-powder-fruit-cavendish-banana-banana-yellow-banana-fruit-food-image-file-formats-thumbnail.png', target_size=(25, 25)),
}

# Update the locations for the items
item_manager.update_item_location('water', 'lr1')
item_manager.update_item_location('banana', 'k4')
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
    draw_nodes(graph, robot)  
    draw_edges(graph, screen)
    draw_room(library)  
    draw_room(office)  
    draw_room(guest_room)
    draw_room(gym)  


    draw_room(living_room)  
    draw_room(kitchen)
    draw_room(dining_room)
    draw_room(study_room)

    
    draw_user_on_map(screen, me, graph)
    # Draw items on the map
    draw_item_on_map(screen, robot, item_manager, items, graph, me)
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
    time.sleep(1)
pygame.quit()   