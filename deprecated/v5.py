class Graph:
    def __init__(self):
        self.nodes = {}
        self.edges = {}

    def add_node(self, node, data=None):
        """Add a new node to the graph.
        
        Args:
            node (str): The identifier for the node.
            data (optional): Additional data associated with the node.
        """
        self.nodes[node] = data
        self.edges[node] = []

    def add_edge(self, node1, node2, bidirectional=True):
        """Add an edge between two nodes in the graph.
        
        Args:
            node1 (str): The identifier for the first node.
            node2 (str): The identifier for the second node.
            bidirectional (bool, optional): If True, adds an undirected edge between node1 and node2.
                                             If False, adds a directed edge from node1 to node2.
        """
        self.edges[node1].append(node2)
        if bidirectional:
            self.edges[node2].append(node1)

    def get_neighbors(self, node):
        """Retrieve the neighbors of a node.
        
        Args:
            node (str): The identifier for the node.
        
        Returns:
            list: A list of identifiers for the neighbors of the node.
        """
        return self.edges[node]

    def node_data(self, node):
        """Get the data associated with a node.
        
        Args:
            node (str): The identifier for the node.
        
        Returns:
            The data associated with the node.
        """
        return self.nodes[node]

    def find_path(self, start, goal):
        """Find a path from a start node to a goal node using BFS.
        
        Args:
            start (str): The identifier for the start node.
            goal (str): The identifier for the goal node.
        
        Returns:
            list or None: A list of nodes representing the path from start to goal, or None if no path exists.
        """
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
    def __init__(self, name, boundaries, graph_nodes=None):
        """
        Initialize a room with a name, boundaries, and associated graph nodes.

        Args:
            name (str): Name of the room.
            boundaries (tuple): A tuple of (x1, y1, x2, y2) representing the room's rectangular boundaries.
            graph_nodes (list, optional): A list of names for the associated graph nodes. Defaults to None.
        """
        self.name = name
        self.boundaries = boundaries  # (x1, y1, x2, y2)
        self.graph_nodes = graph_nodes if graph_nodes is not None else []

    def is_inside(self, x, y):
        """
        Check if a point (x, y) is inside the room's boundaries.

        Args:
            x (int): X coordinate of the point.
            y (int): Y coordinate of the point.

        Returns:
            bool: True if inside, False otherwise.
        """
        x1, y1, x2, y2 = self.boundaries
        return x1 <= x <= x2 and y1 <= y <= y2

    def add_graph_node(self, graph_node):
        """
        Add a graph node to the room.

        Args:
            graph_node (str): The name of the graph node to add.
        """
        if graph_node not in self.graph_nodes:
            self.graph_nodes.append(graph_node)

    def remove_graph_node(self, graph_node):
        """
        Remove a graph node from the room.

        Args:
            graph_node (str): The name of the graph node to remove.
        """
        if graph_node in self.graph_nodes:
            self.graph_nodes.remove(graph_node)

    def update_graph_nodes(self, graph_nodes):
        """
        Update the list of graph nodes associated with the room.

        Args:
            graph_nodes (list of str): The new list of graph node names.
        """
        self.graph_nodes = graph_nodes

class Robot:
    def __init__(self, graph, start_node):
        """
        Initialize the robot with a reference to the graph and a starting node.

        Args:
            graph (Graph): The graph representing the navigation map.
            start_node (str): The starting node identifier in the graph.
        """
        self.graph = graph
        self.current_node = start_node
        self.room = None  # Room will be determined by the current node's associated room
        self.x, self.y = 0, 0  # Position will be updated based on graph node data
        self.update_position_and_room()
    def navigate_to(self, destination_node):
        """
        Navigate the robot to a specified destination node.
        
        Args:
            destination_node (str): The identifier of the destination node in the graph.
        
        Returns:
            bool: True if navigation was successful, False otherwise.
        """
        path = self.graph.find_path(self.current_node, destination_node)
        if path:
            for node in path[1:]:  # Skip the current node since it's the starting point
                self.move_to(node)
            return True
        else:
            print("No path found to the destination.")
            return False
    def move_to(self, destination_node):
        """
        Move the robot to a destination node, if a path exists.

        Args:
            destination_node (str): The destination node identifier in the graph.

        Returns:
            bool: True if the robot successfully moved, False otherwise.
        """
        path = self.graph.find_path(self.current_node, destination_node)
        if path:
            for node in path:
                self.current_node = node
                self.update_position_and_room()
                print(f"Moved to {node}, Current Room: {self.room}")
            return True
        return False

    def update_position_and_room(self):
        """
        Update the robot's position and room based on its current node.
        """
        node_data = self.graph.node_data(self.current_node)
        if node_data:
            self.room = node_data.get('room', 'Unknown')
            self.x, self.y = node_data.get('position', (0, 0))
        else:
            self.room = 'Unknown'
            self.x, self.y = 0, 0

    def current_position(self):
        """
        Return the current position of the robot.

        Returns:
            tuple: The current (x, y) position of the robot.
        """
        return self.x, self.y

    def current_room(self):
        """
        Return the name of the current room where the robot is.

        Returns:
            str: The name of the current room.
        """
        return self.room

# Assuming Graph, Room, and Robot classes are already defined as provided

# Create the graph instance
navigation_graph = Graph()

# Add nodes for each room. Each node could represent a different area or point of interest within the room
rooms = {
    "Kitchen": [(100, 100), (150, 100), (100, 150)],
    "Living Room": [(200, 200), (250, 200), (200, 250)],
    "Bedroom": [(300, 300), (350, 300), (300, 350)]
}

# Initialize rooms and nodes within the graph
for room_name, positions in rooms.items():
    for i, position in enumerate(positions, start=1):
        node_name = f"{room_name}{i}"
        navigation_graph.add_node(node_name, {"room": room_name, "position": position})

# Manually add edges between nodes to simulate paths. This is an example; modify according to your room layout
# For Kitchen
navigation_graph.add_edge("Kitchen1", "Kitchen2")
navigation_graph.add_edge("Kitchen2", "Kitchen3")
navigation_graph.add_edge("Kitchen3", "Kitchen1")

# For Living Room
navigation_graph.add_edge("Living Room1", "Living Room2")
navigation_graph.add_edge("Living Room2", "Living Room3")
navigation_graph.add_edge("Living Room3", "Living Room1")

# For Bedroom
navigation_graph.add_edge("Bedroom1", "Bedroom2")
navigation_graph.add_edge("Bedroom2", "Bedroom3")
navigation_graph.add_edge("Bedroom3", "Bedroom1")

# Assuming connections between rooms, add edges between room nodes
# Example: Connecting Kitchen3 to Living Room1
navigation_graph.add_edge("Kitchen3", "Living Room1")

# Initialize the robot at a starting node
robot = Robot(navigation_graph, "Kitchen1")

# Note: Modify node connections based on your specific room layout and desired pathways