"""
Ant class for the anthill simulator.
Each ant has AI-driven behavior, memory, needs, and social bonds.
"""

import random
import math
import time
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, field
import config
from ai_brain import ai_brain


@dataclass
class Memory:
    """Represents a memory that an ant can have."""
    content: str
    memory_type: str
    importance: float
    timestamp: float
    location: Optional[Tuple[int, int]] = None


@dataclass
class Relationship:
    """Represents a relationship between two ants."""
    ant_id: int
    strength: float = 0.0
    interactions: int = 0
    last_interaction: float = 0.0


class Ant:
    """
    An AI-powered ant with memory, needs, and social behaviors.
    """
    
    def __init__(self, x: int, y: int, ant_id: int):
        self.id = ant_id
        self.x = x
        self.y = y
        self.prev_x = x
        self.prev_y = y
        
        # Basic stats
        self.energy = 100.0
        self.max_energy = 100.0
        self.age = 0
        self.carrying_food = 0
        self.alive = True
        
        # AI and behavior
        self.current_task = 'explore'
        self.target_x = None
        self.target_y = None
        self.ai_decision_cooldown = 0
        
        # Memory system
        self.memories: List[Memory] = []
        self.relationships: Dict[int, Relationship] = {}
        
        # Pheromones
        self.pheromone_strength = 0.0
        self.following_pheromone = None
        
        # Learning and adaptation
        self.experience_points = 0
        self.task_success_rate = 0.5
        self.preferred_tasks = []
        
        # Movement history for pathfinding
        self.path_history = []
        self.stuck_counter = 0
        
    def update(self, world):
        """Main update loop for the ant."""
        if not self.alive:
            return
            
        self.age += 1
        self.energy -= 0.1  # Basic energy decay
        
        # Check if ant dies from lack of energy
        if self.energy <= 0:
            self.alive = False
            return
        
        # Update AI decision making
        self._update_ai_decision(world)
        
        # Execute current action
        self._execute_action(world)
        
        # Update movement history
        self._update_movement_history()
        
        # Decay pheromones
        self.pheromone_strength *= config.PHEROMONE_DECAY_RATE
        
        # Age memories (older memories become less important)
        self._age_memories()
    
    def _update_ai_decision(self, world):
        """Update AI decision making based on current state."""
        self.ai_decision_cooldown -= 1
        
        if self.ai_decision_cooldown <= 0:
            # Gather context about the world
            world_context = self._gather_world_context(world)
            ant_state = self._get_ant_state()
            
            # Get AI decision
            new_action = ai_brain.make_decision(ant_state, world_context)
            
            # Only change task if it's different and makes sense
            if new_action != self.current_task:
                self.current_task = new_action
                self.target_x = None
                self.target_y = None
            
            # Reset cooldown (performance optimization)
            self.ai_decision_cooldown = config.AI_UPDATE_FREQUENCY + random.randint(-5, 5)
    
    def _gather_world_context(self, world) -> Dict[str, Any]:
        """Gather context about the surrounding world."""
        context = {
            'near_food': False,
            'near_home': False,
            'near_ants': [],
            'tunnel_nearby': False,
            'pheromone_trails': [],
        }
        
        # Check vision range for relevant objects
        for dx in range(-config.ANT_VISION_RANGE, config.ANT_VISION_RANGE + 1):
            for dy in range(-config.ANT_VISION_RANGE, config.ANT_VISION_RANGE + 1):
                check_x = self.x + dx
                check_y = self.y + dy
                
                if not world.is_valid_position(check_x, check_y):
                    continue
                
                # Check for food
                if world.get_food_at(check_x, check_y) > 0:
                    context['near_food'] = True
                
                # Check for tunnels (home)
                if world.is_tunnel(check_x, check_y):
                    context['near_home'] = True
                    context['tunnel_nearby'] = True
                
                # Check for other ants
                for ant in world.ants:
                    if ant != self and ant.x == check_x and ant.y == check_y:
                        context['near_ants'].append(ant.id)
        
        return context
    
    def _get_ant_state(self) -> Dict[str, Any]:
        """Get current ant state for AI decision making."""
        recent_memories = [mem.content for mem in self.memories[-5:]]
        
        return {
            'energy': self.energy,
            'carrying_food': self.carrying_food,
            'current_task': self.current_task,
            'recent_memories': recent_memories,
            'x': self.x,
            'y': self.y,
            'age': self.age,
            'experience': self.experience_points
        }
    
    def _execute_action(self, world):
        """Execute the current action/task."""
        actions = {
            'explore': self._action_explore,
            'move_to_food': self._action_move_to_food,
            'collect_food': self._action_collect_food,
            'return_home': self._action_return_home,
            'dig_tunnel': self._action_dig_tunnel,
            'follow_ant': self._action_follow_ant,
            'rest': self._action_rest,
            'help_ant': self._action_help_ant
        }
        
        action_func = actions.get(self.current_task, self._action_explore)
        action_func(world)
    
    def _action_explore(self, world):
        """Random exploration with some intelligence."""
        if self.target_x is None or self.target_y is None:
            # Choose a random target within reasonable distance
            angle = random.uniform(0, 2 * math.pi)
            distance = random.randint(10, 30)
            self.target_x = self.x + int(distance * math.cos(angle))
            self.target_y = self.y + int(distance * math.sin(angle))
        
        self._move_towards_target(world)
        
        # If reached target or stuck, pick new target
        if self._reached_target() or self.stuck_counter > 10:
            self.target_x = None
            self.target_y = None
            self.stuck_counter = 0
    
    def _action_move_to_food(self, world):
        """Move towards detected food."""
        food_location = self._find_nearest_food(world)
        if food_location:
            self.target_x, self.target_y = food_location
            self._move_towards_target(world)
        else:
            self.current_task = 'explore'
    
    def _action_collect_food(self, world):
        """Collect food at current location."""
        food_amount = world.get_food_at(self.x, self.y)
        if food_amount > 0 and self.carrying_food < config.ANT_CARRYING_CAPACITY:
            collected = min(food_amount, config.ANT_CARRYING_CAPACITY - self.carrying_food)
            world.remove_food_at(self.x, self.y, collected)
            self.carrying_food += collected
            
            # Add memory of successful food collection
            memory = ai_brain.process_memory(
                f"Collected {collected} food at {self.x},{self.y}",
                'task_success'
            )
            self.add_memory(memory)
            
            # Switch to returning home
            self.current_task = 'return_home'
        else:
            self.current_task = 'explore'
    
    def _action_return_home(self, world):
        """Return to the nearest tunnel with food."""
        home_location = self._find_nearest_tunnel(world)
        if home_location:
            self.target_x, self.target_y = home_location
            self._move_towards_target(world)
            
            # If at home, drop off food
            if world.is_tunnel(self.x, self.y) and self.carrying_food > 0:
                world.add_food_storage(self.carrying_food)
                self.carrying_food = 0
                self.current_task = 'explore'
                
                # Add memory of successful food delivery
                memory = ai_brain.process_memory(
                    f"Delivered food to colony at {self.x},{self.y}",
                    'task_success'
                )
                self.add_memory(memory)
        else:
            # No tunnel found, start digging
            self.current_task = 'dig_tunnel'
    
    def _action_dig_tunnel(self, world):
        """Dig a tunnel at current location."""
        if self.energy >= config.DIGGING_ENERGY_COST:
            if world.can_dig_at(self.x, self.y):
                world.dig_tunnel_at(self.x, self.y)
                self.energy -= config.DIGGING_ENERGY_COST
                
                # Add memory of tunnel creation
                memory = ai_brain.process_memory(
                    f"Dug tunnel at {self.x},{self.y}",
                    'task_success'
                )
                self.add_memory(memory)
                
                self.current_task = 'explore'
        else:
            self.current_task = 'rest'
    
    def _action_follow_ant(self, world):
        """Follow another ant."""
        target_ant = self._find_nearest_ant(world)
        if target_ant:
            self.target_x = target_ant.x
            self.target_y = target_ant.y
            self._move_towards_target(world)
            
            # Interact with ant if close enough
            distance = math.sqrt((self.x - target_ant.x)**2 + (self.y - target_ant.y)**2)
            if distance <= 2:
                self._interact_with_ant(target_ant)
        else:
            self.current_task = 'explore'
    
    def _action_rest(self, world):
        """Rest to recover energy."""
        self.energy = min(self.max_energy, self.energy + 2.0)
        if self.energy >= self.max_energy * 0.8:
            self.current_task = 'explore'
    
    def _action_help_ant(self, world):
        """Help another ant with their task."""
        target_ant = self._find_nearest_ant(world)
        if target_ant and target_ant.current_task in ['collect_food', 'dig_tunnel']:
            # Move closer to help
            self.target_x = target_ant.x
            self.target_y = target_ant.y
            self._move_towards_target(world)
            
            # If close enough, provide help
            distance = math.sqrt((self.x - target_ant.x)**2 + (self.y - target_ant.y)**2)
            if distance <= 1:
                if target_ant.current_task == 'dig_tunnel':
                    # Help with digging
                    if self.energy >= config.DIGGING_ENERGY_COST:
                        self.energy -= config.DIGGING_ENERGY_COST
                        target_ant.energy += 5  # Give some energy to helped ant
                        
                        # Strengthen relationship
                        self._strengthen_relationship(target_ant.id)
        else:
            self.current_task = 'explore'
    
    def _move_towards_target(self, world):
        """Move one step towards the current target."""
        if self.target_x is None or self.target_y is None:
            return
        
        # Calculate direction
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        
        # Normalize to single step
        if dx != 0:
            dx = 1 if dx > 0 else -1
        if dy != 0:
            dy = 1 if dy > 0 else -1
        
        new_x = self.x + dx
        new_y = self.y + dy
        
        # Check if movement is valid
        if world.can_move_to(new_x, new_y):
            self.prev_x = self.x
            self.prev_y = self.y
            self.x = new_x
            self.y = new_y
            self.stuck_counter = 0
        else:
            self.stuck_counter += 1
    
    def _find_nearest_food(self, world) -> Optional[Tuple[int, int]]:
        """Find the nearest food source."""
        min_distance = float('inf')
        nearest_food = None
        
        for x in range(max(0, self.x - config.ANT_VISION_RANGE), 
                      min(world.width, self.x + config.ANT_VISION_RANGE + 1)):
            for y in range(max(0, self.y - config.ANT_VISION_RANGE),
                          min(world.height, self.y + config.ANT_VISION_RANGE + 1)):
                if world.get_food_at(x, y) > 0:
                    distance = math.sqrt((x - self.x)**2 + (y - self.y)**2)
                    if distance < min_distance:
                        min_distance = distance
                        nearest_food = (x, y)
        
        return nearest_food
    
    def _find_nearest_tunnel(self, world) -> Optional[Tuple[int, int]]:
        """Find the nearest tunnel."""
        min_distance = float('inf')
        nearest_tunnel = None
        
        for x in range(max(0, self.x - config.ANT_VISION_RANGE),
                      min(world.width, self.x + config.ANT_VISION_RANGE + 1)):
            for y in range(max(0, self.y - config.ANT_VISION_RANGE),
                          min(world.height, self.y + config.ANT_VISION_RANGE + 1)):
                if world.is_tunnel(x, y):
                    distance = math.sqrt((x - self.x)**2 + (y - self.y)**2)
                    if distance < min_distance:
                        min_distance = distance
                        nearest_tunnel = (x, y)
        
        return nearest_tunnel
    
    def _find_nearest_ant(self, world):
        """Find the nearest other ant."""
        min_distance = float('inf')
        nearest_ant = None
        
        for ant in world.ants:
            if ant != self and ant.alive:
                distance = math.sqrt((ant.x - self.x)**2 + (ant.y - self.y)**2)
                if distance < min_distance and distance <= config.ANT_VISION_RANGE:
                    min_distance = distance
                    nearest_ant = ant
        
        return nearest_ant
    
    def _reached_target(self) -> bool:
        """Check if ant has reached its target."""
        if self.target_x is None or self.target_y is None:
            return True
        return abs(self.x - self.target_x) <= 1 and abs(self.y - self.target_y) <= 1
    
    def _interact_with_ant(self, other_ant):
        """Interact with another ant, building relationship."""
        self._strengthen_relationship(other_ant.id)
        other_ant._strengthen_relationship(self.id)
        
        # Share some information
        if len(self.memories) > 0 and len(other_ant.memories) < config.ANT_MEMORY_SIZE:
            shared_memory = random.choice(self.memories)
            other_ant.add_memory({
                'type': 'social_interaction',
                'content': f"Learned from ant {self.id}: {shared_memory.content}",
                'timestamp': time.time(),
                'importance': shared_memory.importance * 0.5
            })
    
    def _strengthen_relationship(self, other_ant_id: int):
        """Strengthen relationship with another ant."""
        if other_ant_id not in self.relationships:
            self.relationships[other_ant_id] = Relationship(other_ant_id)
        
        rel = self.relationships[other_ant_id]
        rel.strength = min(config.RELATIONSHIP_STRENGTH_MAX, rel.strength + 5.0)
        rel.interactions += 1
        rel.last_interaction = time.time()
    
    def add_memory(self, memory_data: Dict[str, Any]):
        """Add a new memory to the ant."""
        memory = Memory(
            content=memory_data['content'],
            memory_type=memory_data['type'],
            importance=memory_data['importance'],
            timestamp=memory_data['timestamp'],
            location=(self.x, self.y)
        )
        
        self.memories.append(memory)
        
        # Keep memory size manageable
        if len(self.memories) > config.ANT_MEMORY_SIZE:
            # Remove least important memories
            self.memories.sort(key=lambda m: m.importance)
            self.memories = self.memories[-config.ANT_MEMORY_SIZE:]
    
    def _age_memories(self):
        """Age memories, making older ones less important."""
        current_time = time.time()
        for memory in self.memories:
            age_factor = max(0.1, 1.0 - (current_time - memory.timestamp) / 3600)  # 1 hour decay
            memory.importance *= age_factor
    
    def _update_movement_history(self):
        """Update movement history for pathfinding."""
        self.path_history.append((self.x, self.y))
        if len(self.path_history) > 20:  # Keep last 20 positions
            self.path_history.pop(0)