# Configuration for Anthill Simulator
import pygame

# Display Settings
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 900
FPS = 60
CELL_SIZE = 4  # Size of each grid cell in pixels

# World Settings
WORLD_WIDTH = WINDOW_WIDTH // CELL_SIZE  # Grid cells
WORLD_HEIGHT = WINDOW_HEIGHT // CELL_SIZE  # Grid cells
INITIAL_ANTS = 12

# Colors (RGB)
COLORS = {
    'background': (50, 40, 30),
    'soil': (101, 67, 33),
    'tunnel': (30, 20, 15),
    'ant': (200, 50, 50),
    'food': (100, 200, 50),
    'pheromone_food': (100, 255, 100),
    'pheromone_home': (100, 100, 255),
    'queen': (255, 100, 100),
    'larva': (255, 255, 150),
    'water': (100, 150, 255)
}

# Ant Behavior Settings
ANT_SPEED = 1  # Cells per update
ANT_MEMORY_SIZE = 50  # Number of memories an ant can hold
ANT_VISION_RANGE = 8  # How far ants can see
ANT_CARRYING_CAPACITY = 3  # How much food an ant can carry

# AI Settings
LLM_MODEL = "llama3.2:1b"  # Lightweight model for 8GB VRAM
AI_UPDATE_FREQUENCY = 30  # Frames between AI decisions (performance optimization)
MAX_CONTEXT_LENGTH = 512  # Keep context short for performance

# Pheromone Settings
PHEROMONE_DECAY_RATE = 0.995
MAX_PHEROMONE_STRENGTH = 100

# Resource Settings
FOOD_SPAWN_RATE = 0.001  # Probability per cell per frame
INITIAL_FOOD_AMOUNT = 50

# Anthill Settings
STARTING_CHAMBER_SIZE = 10
DIGGING_ENERGY_COST = 5

# Memory and Learning
MEMORY_CATEGORIES = ['food_location', 'danger', 'social_interaction', 'task_success', 'path_learned']
RELATIONSHIP_STRENGTH_MAX = 100
LEARNING_RATE = 0.1