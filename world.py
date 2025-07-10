"""
World class for the anthill simulator.
Manages the environment, terrain, food sources, pheromones, and world state.
"""

import random
import numpy as np
from typing import List, Tuple, Optional
import config
from ant import Ant


class World:
    """
    Represents the game world with terrain, food, pheromones, and ants.
    """
    
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        
        # Terrain layers
        self.terrain = np.full((width, height), 1, dtype=np.uint8)  # 0=air, 1=soil, 2=tunnel
        self.food = np.zeros((width, height), dtype=np.float32)
        self.pheromone_food = np.zeros((width, height), dtype=np.float32)
        self.pheromone_home = np.zeros((width, height), dtype=np.float32)
        
        # Game entities
        self.ants: List[Ant] = []
        self.food_storage = 0.0
        self.generation = 1
        
        # Statistics
        self.total_food_collected = 0.0
        self.total_tunnels_dug = 0
        self.frame_count = 0
        
        # Initialize world
        self._generate_initial_terrain()
        self._spawn_initial_food()
        self._create_initial_ants()
    
    def _generate_initial_terrain(self):
        """Generate the initial terrain with a starting chamber."""
        # Create underground soil
        ground_level = self.height // 4
        self.terrain[:, :ground_level] = 0  # Air above ground
        self.terrain[:, ground_level:] = 1  # Soil below ground
        
        # Create starting chamber in the center
        center_x = self.width // 2
        center_y = ground_level + config.STARTING_CHAMBER_SIZE
        
        chamber_size = config.STARTING_CHAMBER_SIZE
        for x in range(center_x - chamber_size//2, center_x + chamber_size//2):
            for y in range(center_y - chamber_size//2, center_y + chamber_size//2):
                if self.is_valid_position(x, y):
                    self.terrain[x, y] = 2  # Tunnel
        
        # Create entrance tunnel to surface
        for y in range(ground_level, center_y):
            if self.is_valid_position(center_x, y):
                self.terrain[center_x, y] = 2
    
    def _spawn_initial_food(self):
        """Spawn initial food sources on the surface."""
        ground_level = self.height // 4
        
        for _ in range(config.INITIAL_FOOD_AMOUNT):
            x = random.randint(0, self.width - 1)
            y = random.randint(max(0, ground_level - 10), ground_level + 5)
            
            if self.is_valid_position(x, y) and self.terrain[x, y] == 0:  # Air
                self.food[x, y] += random.uniform(1, 5)
    
    def _create_initial_ants(self):
        """Create the initial ant colony."""
        center_x = self.width // 2
        center_y = self.height // 4 + config.STARTING_CHAMBER_SIZE
        
        for i in range(config.INITIAL_ANTS):
            # Place ants near the starting chamber
            offset_x = random.randint(-3, 3)
            offset_y = random.randint(-3, 3)
            
            ant_x = center_x + offset_x
            ant_y = center_y + offset_y
            
            # Ensure ant is in a tunnel
            if self.is_valid_position(ant_x, ant_y) and self.terrain[ant_x, ant_y] == 2:
                ant = Ant(ant_x, ant_y, len(self.ants))
                self.ants.append(ant)
        
        # If no ants were placed in tunnels, place them in the center chamber
        if len(self.ants) == 0:
            for i in range(config.INITIAL_ANTS):
                ant = Ant(center_x, center_y, i)
                self.ants.append(ant)
    
    def update(self):
        """Update the world state for one frame."""
        self.frame_count += 1
        
        # Update all ants
        for ant in self.ants[:]:  # Copy list to avoid modification during iteration
            ant.update(self)
            
            # Remove dead ants
            if not ant.alive:
                self.ants.remove(ant)
        
        # Spawn new food occasionally
        self._spawn_food()
        
        # Update pheromones
        self._update_pheromones()
        
        # Check for colony growth conditions
        self._check_colony_growth()
    
    def _spawn_food(self):
        """Randomly spawn food on the surface."""
        if random.random() < config.FOOD_SPAWN_RATE:
            ground_level = self.height // 4
            
            x = random.randint(0, self.width - 1)
            y = random.randint(max(0, ground_level - 5), ground_level + 3)
            
            if (self.is_valid_position(x, y) and 
                self.terrain[x, y] == 0 and  # Air
                self.food[x, y] < 10):  # Not too much food in one spot
                
                self.food[x, y] += random.uniform(0.5, 2.0)
    
    def _update_pheromones(self):
        """Update pheromone decay and ant pheromone dropping."""
        # Decay existing pheromones
        self.pheromone_food *= config.PHEROMONE_DECAY_RATE
        self.pheromone_home *= config.PHEROMONE_DECAY_RATE
        
        # Ants drop pheromones based on their current task
        for ant in self.ants:
            if ant.alive:
                x, y = ant.x, ant.y
                if self.is_valid_position(x, y):
                    if ant.carrying_food > 0:
                        # Drop home pheromone when carrying food
                        self.pheromone_home[x, y] = min(
                            config.MAX_PHEROMONE_STRENGTH,
                            self.pheromone_home[x, y] + 10.0
                        )
                    elif ant.current_task == 'move_to_food':
                        # Drop food pheromone when searching for food
                        self.pheromone_food[x, y] = min(
                            config.MAX_PHEROMONE_STRENGTH,
                            self.pheromone_food[x, y] + 5.0
                        )
    
    def _check_colony_growth(self):
        """Check conditions for colony growth and evolution."""
        # If colony is successful (lots of food), spawn new ants
        if (self.food_storage > 50 and 
            len(self.ants) < 30 and 
            self.frame_count % 1800 == 0):  # Every 30 seconds at 60 FPS
            
            self._spawn_new_ant()
    
    def _spawn_new_ant(self):
        """Spawn a new ant in the colony."""
        # Find a tunnel location for the new ant
        tunnel_locations = []
        for x in range(self.width):
            for y in range(self.height):
                if self.terrain[x, y] == 2:  # Tunnel
                    tunnel_locations.append((x, y))
        
        if tunnel_locations:
            spawn_location = random.choice(tunnel_locations)
            new_ant = Ant(spawn_location[0], spawn_location[1], len(self.ants))
            
            # New ants might inherit some traits from successful ants
            if self.ants:
                successful_ant = max(self.ants, key=lambda a: a.experience_points)
                new_ant.preferred_tasks = successful_ant.preferred_tasks.copy()
                
                # Share some memories
                if len(successful_ant.memories) > 0:
                    shared_memories = random.sample(
                        successful_ant.memories, 
                        min(3, len(successful_ant.memories))
                    )
                    for memory in shared_memories:
                        new_ant.add_memory({
                            'type': 'inherited_knowledge',
                            'content': f"Inherited: {memory.content}",
                            'timestamp': memory.timestamp,
                            'importance': memory.importance * 0.3
                        })
            
            self.ants.append(new_ant)
            print(f"New ant born! Colony size: {len(self.ants)}")
    
    # World interaction methods
    def is_valid_position(self, x: int, y: int) -> bool:
        """Check if position is within world bounds."""
        return 0 <= x < self.width and 0 <= y < self.height
    
    def can_move_to(self, x: int, y: int) -> bool:
        """Check if an ant can move to this position."""
        if not self.is_valid_position(x, y):
            return False
        
        # Ants can move through air and tunnels, but not solid soil
        return self.terrain[x, y] != 1
    
    def can_dig_at(self, x: int, y: int) -> bool:
        """Check if an ant can dig a tunnel at this position."""
        if not self.is_valid_position(x, y):
            return False
        
        # Can only dig in soil
        return self.terrain[x, y] == 1
    
    def dig_tunnel_at(self, x: int, y: int):
        """Dig a tunnel at the specified position."""
        if self.can_dig_at(x, y):
            self.terrain[x, y] = 2  # Convert soil to tunnel
            self.total_tunnels_dug += 1
    
    def is_tunnel(self, x: int, y: int) -> bool:
        """Check if position is a tunnel."""
        if not self.is_valid_position(x, y):
            return False
        return self.terrain[x, y] == 2
    
    def get_food_at(self, x: int, y: int) -> float:
        """Get amount of food at position."""
        if not self.is_valid_position(x, y):
            return 0.0
        return self.food[x, y]
    
    def remove_food_at(self, x: int, y: int, amount: float):
        """Remove food from position."""
        if self.is_valid_position(x, y):
            removed = min(amount, self.food[x, y])
            self.food[x, y] -= removed
            return removed
        return 0.0
    
    def add_food_storage(self, amount: float):
        """Add food to colony storage."""
        self.food_storage += amount
        self.total_food_collected += amount
    
    def get_pheromone_strength(self, x: int, y: int, pheromone_type: str) -> float:
        """Get pheromone strength at position."""
        if not self.is_valid_position(x, y):
            return 0.0
        
        if pheromone_type == 'food':
            return self.pheromone_food[x, y]
        elif pheromone_type == 'home':
            return self.pheromone_home[x, y]
        return 0.0
    
    # Rendering helpers
    def get_cell_color(self, x: int, y: int) -> Tuple[int, int, int]:
        """Get the display color for a cell."""
        if not self.is_valid_position(x, y):
            return config.COLORS['background']
        
        # Base terrain color
        terrain_type = self.terrain[x, y]
        if terrain_type == 0:  # Air
            color = config.COLORS['background']
        elif terrain_type == 1:  # Soil
            color = config.COLORS['soil']
        elif terrain_type == 2:  # Tunnel
            color = config.COLORS['tunnel']
        else:
            color = config.COLORS['background']
        
        # Overlay food
        if self.food[x, y] > 0:
            food_intensity = min(1.0, self.food[x, y] / 5.0)
            food_color = config.COLORS['food']
            color = self._blend_colors(color, food_color, food_intensity * 0.8)
        
        # Overlay pheromones
        pheromone_food_strength = self.pheromone_food[x, y] / config.MAX_PHEROMONE_STRENGTH
        pheromone_home_strength = self.pheromone_home[x, y] / config.MAX_PHEROMONE_STRENGTH
        
        if pheromone_food_strength > 0.1:
            pheromone_color = config.COLORS['pheromone_food']
            color = self._blend_colors(color, pheromone_color, pheromone_food_strength * 0.3)
        
        if pheromone_home_strength > 0.1:
            pheromone_color = config.COLORS['pheromone_home']
            color = self._blend_colors(color, pheromone_color, pheromone_home_strength * 0.3)
        
        return color
    
    def _blend_colors(self, base_color: Tuple[int, int, int], 
                     overlay_color: Tuple[int, int, int], 
                     alpha: float) -> Tuple[int, int, int]:
        """Blend two colors with alpha blending."""
        alpha = max(0.0, min(1.0, alpha))
        
        blended = (
            int(base_color[0] * (1 - alpha) + overlay_color[0] * alpha),
            int(base_color[1] * (1 - alpha) + overlay_color[1] * alpha),
            int(base_color[2] * (1 - alpha) + overlay_color[2] * alpha)
        )
        
        return blended
    
    def get_statistics(self) -> dict:
        """Get current world statistics."""
        alive_ants = len([ant for ant in self.ants if ant.alive])
        total_energy = sum(ant.energy for ant in self.ants if ant.alive)
        avg_energy = total_energy / max(1, alive_ants)
        
        carrying_food = sum(ant.carrying_food for ant in self.ants)
        
        return {
            'alive_ants': alive_ants,
            'total_food_collected': self.total_food_collected,
            'food_storage': self.food_storage,
            'food_being_carried': carrying_food,
            'tunnels_dug': self.total_tunnels_dug,
            'average_energy': avg_energy,
            'generation': self.generation,
            'frame_count': self.frame_count
        }