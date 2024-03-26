import logging
from datetime import datetime
import autogen
import pygame
import threading 
import random
from collections import deque
import sys
import os

class Graph:
    def __init__(self):
        self.nodes = {}
        self.edges = {}

    def add_node(self, node, data=None):
        self.nodes[node] = data
        self.edges[node] = []

    def add_edge(self, node1, node2, bidirectional=True):
        self.edges[node1].append(node2)
        if bidirectional:
            self.edges[node2].append(node1)

    def get_neighbors(self, node):
        return self.edges[node]

    def node_data(self, node):
        return self.nodes[node]

    def find_path(self, start, goal):
        visited = set()
        queue = deque([[start]])
        
        if start == goal:
            return [start]

        while queue:
            path = queue.popleft()
            node = path[-1]
            
            if node not in visited:
                neighbours = self.get_neighbors(node)
                
                for neighbour in neighbours:
                    new_path = list(path)
                    new_path.append(neighbour)
                    queue.append(new_path)
                    
                    if neighbour == goal:
                        return new_path
                visited.add(node)

        return None

class Room:
    def __init__(self, name, boundaries, graph_node=None):
        """
        Initialize a room with a name, boundaries, and an associated graph node.

        :param name: str - Name of the room.
        :param boundaries: tuple - A tuple of (x1, y1, x2, y2) representing the room's rectangular boundaries.
        :param graph_node: str - The name of the associated graph node.
        """
        self.name = name
        self.boundaries = boundaries  # (x1, y1, x2, y2)
        self.graph_node = graph_node

    def is_inside(self, x, y):
        """
        Check if a point (x, y) is inside the room's boundaries.

        :param x: int - X coordinate of the point.
        :param y: int - Y coordinate of the point.
        :return: bool - True if inside, False otherwise.
        """
        x1, y1, x2, y2 = self.boundaries
        return x1 <= x <= x2 and y1 <= y <= y2

    def update_graph_node(self, graph_node):
        """
        Update the graph node associated with the room.

        :param graph_node: str - The name of the graph node.
        """
        self.graph_node = graph_node

class Robot:
    def __init__(self, graph, start_node):
        self.graph = graph
        self.current_node = start_node
        self.room = self.graph.node_data(start_node)['room']
        self.x, self.y = self.graph.node_data(start_node)['position']

    def move_to(self, destination_node):
        path = self.graph.find_path(self.current_node, destination_node)
        if path:
            for node in path:
                self.current_node = node
                self.update_position_and_room()
                print(f"Moved to {node}, Current Room: {self.room}")
            return True
        return False

    def update_position_and_room(self):
        node_data = self.graph.node_data(self.current_node)
        self.room = node_data['room']
        self.x, self.y = node_data['position']

class UI:
    def __init__(self, screen, font, input_box, button):
        self.screen = screen
        self.font = font
        self.input_box = input_box
        self.button = button
        self.text = ''
        self.active = False
        self.color_inactive = pygame.Color('lightskyblue3')
        self.color_active = pygame.Color('dodgerblue2')
        self.color = self.color_inactive
        self.button_color = pygame.Color('dimgrey')

    def draw_dashboard(self, robot):
        pygame.draw.rect(self.screen, pygame.Color('black'), [0, 0, self.screen.get_width(), 100])
        room_text = self.font.render(f"Current Room: {robot.current_room()}", True, pygame.Color('white'))
        position_text = self.font.render(f"Position: {robot.current_position()}", True, pygame.Color('white'))
        self.screen.blit(room_text, (10, 10))
        self.screen.blit(position_text, (10, 50))

    def draw_input_box(self):
        txt_surface = self.font.render(self.text, True, self.color)
        width = max(200, txt_surface.get_width() + 10)
        self.input_box.w = width
        self.screen.blit(txt_surface, (self.input_box.x + 5, self.input_box.y + 5))
        pygame.draw.rect(self.screen, self.color, self.input_box, 2)

    def draw_button(self):
        pygame.draw.rect(self.screen, self.button_color, self.button)
        button_text = self.font.render('Send', True, pygame.Color('white'))
        self.screen.blit(button_text, (self.button.x + 20, self.button.y + 5))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.input_box.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            self.color = self.color_active if self.active else self.color_inactive
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    self.send_command()
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode

    def send_command(self):
        # Here you would handle sending the command
        # For example: handle_command_input(self.text)
        print(f"Command to send: {self.text}")
        self.text = ''  # Clear text after sending

class Logger:
    def __init__(self, log_file_name):
        self.log_file_name = log_file_name
        logging.basicConfig(filename=self.log_file_name, level=logging.INFO,
                            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    def log_task(self, task):
        logging.info(f"Task: {task}")

    def log_decision(self, decision):
        logging.info(f"Decision made: {decision}")

    def log_function_call(self, function_name, args, return_value):
        logging.info(f"Function called: {function_name} - Args: {args} - Returned: {return_value}")

    def log_error(self, error_message):
        logging.error(f"Error: {error_message}")

    def log_warning(self, warning_message):
        logging.warning(f"Warning: {warning_message}")

# Example usage:
# logger = Logger('robot_log.txt')
# logger.log_task("Navigate to Kitchen")
# logger.log_decision("Path found")
# logger.log_function_call("move_to", {"destination_node": "Kitchen"}, True)

# Navigation and Pathfinding Functions

def find_path(graph, start, goal):
    visited = set()
    queue = deque([[start]])
    
    if start == goal:
        return [start]

    while queue:
        path = queue.popleft()
        node = path[-1]
        
        if node not in visited:
            neighbours = graph.get_neighbors(node)
            
            for neighbour in neighbours:
                new_path = list(path)
                new_path.append(neighbour)
                queue.append(new_path)
                
                if neighbour == goal:
                    return new_path
            visited.add(node)

    return None

def navigate_to(robot, graph, destination):
    path = find_path(graph, robot.current_node, destination)
    if path:
        robot.follow_path(path)
        print(f"Robot navigated to {destination} through path: {path}")
    else:
        print("Path not found.")

def dynamic_room_update(robot, graph):
    node_data = graph.node_data(robot.current_node)
    if 'room' in node_data:
        robot.room = node_data['room']
        print(f"Robot is now in {robot.room}.")
    else:
        print("Robot is in an unknown location.")

# Example usage:
# Assuming graph and robot instances are already created and initialized
# navigate_to(robot, graph, 'destination_node')
# dynamic_room_update(robot, graph)

# Environmental Interaction Functions

def pick_up(robot, item):
    """
    Simulate the robot picking up an item in its current location.
    """
    # Assuming each room or node has a list of items that can be interacted with.
    # This part of the code would involve checking if the item is in the current location
    # and then "picking it up", perhaps removing it from the room's item list.
    if item in robot.current_location_items():
        robot.current_location_items().remove(item)
        robot.inventory.append(item)
        print(f"{robot.name} picked up {item}.")
    else:
        print(f"{item} not found in {robot.current_location()}.")

def drop(robot, item):
    """
    Simulate the robot dropping an item in its current location.
    """
    if item in robot.inventory:
        robot.inventory.remove(item)
        robot.current_location_items().append(item)
        print(f"{robot.name} dropped {item} in {robot.current_location()}.")
    else:
        print(f"{item} not in inventory.")

def inspect(robot, item):
    """
    Simulate the robot inspecting an item in its current location or inventory.
    """
    if item in robot.inventory or item in robot.current_location_items():
        # Details about the item would be provided here, potentially affecting game state
        print(f"{robot.name} inspected {item}.")
    else:
        print(f"{item} not found in {robot.current_location()} or inventory.")

# Additional functions could include interacting with environment-specific objects or mechanisms
# such as opening doors, activating switches, or using items from the inventory in the environment.

# Example usage:
# Assuming robot instance is already created and initialized
# pick_up(robot, 'Keycard')
# drop(robot, 'Keycard')
# inspect(robot, 'Terminal')

# Visualization Functions

def draw_path(screen, path, graph):
    """
    Draw the robot's path on the screen.
    """
    for i in range(len(path) - 1):
        start_pos = graph.node_data(path[i])['position']
        end_pos = graph.node_data(path[i + 1])['position']
        pygame.draw.line(screen, pygame.Color('green'), start_pos, end_pos, 5)

def highlight_current_room(screen, robot, graph):
    """
    Highlight the room where the robot currently is.
    """
    node_data = graph.node_data(robot.current_node)
    if 'room_bounds' in node_data:
        pygame.draw.rect(screen, pygame.Color('lightblue'), node_data['room_bounds'], 2)

def visualize_decision_points(screen, decision_points, graph):
    """
    Visualize decision points on the path.
    """
    for point in decision_points:
        if point in graph.nodes:
            pos = graph.node_data(point)['position']
            pygame.draw.circle(screen, pygame.Color('red'), pos, 10)

# Additional visualization functionalities might include displaying the robot's status,
# drawing objects or items in the environment, or animating the robot's movements.

# Example usage:
# Assuming pygame screen and graph instances are already created and initialized,
# and path and decision_points are defined
# draw_path(screen, ['Node1', 'Node2', 'Node3'], graph)
# highlight_current_room(screen, robot, graph)
# visualize_decision_points(screen, ['Node2'], graph)

def handle_events(events, input_box, robot, graph):
    """
    Handle Pygame events for user input and interactions.
    """
    for event in events:
        if event.type == pygame.QUIT:
            return False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if input_box.collide_rect(event.pos):
                input_box.activate()
            else:
                input_box.deactivate()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                command = input_box.get_text()
                process_command(command, robot, graph)
                input_box.clear_text()
            elif event.key == pygame.K_BACKSPACE:
                input_box.remove_character()
            else:
                input_box.add_character(event.unicode)
    return True

def process_command(command, robot, graph):
    """
    Process the command input by the user.
    """
    # Parse the command and execute corresponding actions
    # Example command: "move Node2"
    args = command.split()
    if args[0] == "move" and len(args) > 1:
        navigate_to(robot, graph, args[1])
    elif args[0] == "pick" and len(args) > 1:
        pick_up(robot, ' '.join(args[1:]))
    # Add more command processing as needed

def draw_ui_elements(screen, input_box, button):
    """
    Draw UI elements such as input boxes and buttons on the screen.
    """
    input_box.draw(screen)
    button.draw(screen)

# Logging and Monitoring Functions (included in this group for completeness)

def log_action(action):
    """
    Log actions performed by the robot or user commands.
    """
    print(f"Action logged: {action}")
    # Implement logging to file or console as required

# Example usage:
# Assuming instances for input_box, button, and setup for Pygame event loop are already done
# while True:
#     events = pygame.event.get()
#     continue_running = handle_events(events, input_box, robot, graph)
#     if not continue_running:
#         break
#     draw_ui_elements(screen, input_box, button)
#     pygame.display.flip()\

# Assuming the Graph class is defined as previously shown

graph = Graph()

# Initialize nodes for rooms
graph.add_node("LivingRoom", data={"position": (100, 100), "room": "Living Room"})
graph.add_node("Kitchen", data={"position": (200, 100), "room": "Kitchen"})
graph.add_node("Bedroom", data={"position": (100, 200), "room": "Bedroom"})
graph.add_node("Bathroom", data={"position": (200, 200), "room": "Bathroom"})

# Initialize edges representing connections between rooms
graph.add_edge("LivingRoom", "Kitchen")
graph.add_edge("LivingRoom", "Bedroom")
graph.add_edge("Kitchen", "Bathroom")
graph.add_edge("Bedroom", "Bathroom")

# Example of setting up a more complex environment with more rooms or specific features
# can follow the same pattern: adding nodes for each room/location and edges to represent paths.

# Assuming the Robot class and Graph instance 'graph' are defined as previously shown

# Set the initial node for the robot, for example, "LivingRoom"
initial_node = "LivingRoom"

# Initialize the robot with the graph and its initial node
robot = Robot(graph, initial_node)

# Now, the robot is initialized and ready to navigate the graph from the Living Room

# Pygame initialization
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Robot Room Navigator")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
COLOR_INACTIVE = pygame.Color('lightskyblue3')
COLOR_ACTIVE = pygame.Color('dodgerblue2')
BUTTON_COLOR = pygame.Color('dimgrey')

# Font for UI elements
font = pygame.font.Font(None, 32)

# Input box setup
input_box = pygame.Rect(100, SCREEN_HEIGHT - 50, 140, 32)

# Button setup
button = pygame.Rect(250, SCREEN_HEIGHT - 50, 80, 32)

# Initial UI state
input_text = ''
input_active = False

# Main loop flag
running = True

# Placeholder for UI drawing and event handling functions
# These will be fleshed out with draw_dashboard, draw_input_box, draw_button, and handle_event functions

# Note: The main game loop and event handling that integrates these UI components
# will be defined in the main section of the application code.

# Logger setup
logging.basicConfig(filename='robot_navigation.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Example of logging an info message
logging.info('Robot navigation application started')

# Example of logging an error
logging.error('An error occurred while moving the robot')

# The logger is now set up and can be used throughout the application to log messages, warnings, errors, etc.