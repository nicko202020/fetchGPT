import autogen
import pygame
import threading 
import random
import logging
# Room class
class Room:
    
    #Room attributes
    def __init__(self, name, x1, y1, x2, y2):
        self.name = name
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
    
    #Room functions
    def is_inside(self, x, y, margin=0):
        return (self.x1 - margin) <= x <= (self.x2 + margin) and (self.y1 - margin) <= y <= (self.y2 + margin)
# Robot class 
class Robot:

    #Robot attributes
    def __init__(self, start_x, start_y, room):
        self.x = start_x
        self.y = start_y
        self.room = room

    #Robot functions
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
    def teleport(self, new_x, new_y):
        logging.info(f"Teleporting robot to ({new_x}, {new_y})")
        self.x = new_x
        self.y = new_y
        return f"Moved to ({new_x}, {new_y})"

# Functions for interacting with the robot
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