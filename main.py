"""
Main game loop for the anthill simulator.
Handles rendering, user input, and game state management.
"""

import pygame
import sys
import time
from typing import Optional
import config
from world import World
from ant import Ant


class AntHillSimulator:
    """Main game class for the anthill simulator."""
    
    def __init__(self):
        # Initialize Pygame
        pygame.init()
        
        # Create display
        self.screen = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
        pygame.display.set_caption("AI Anthill Simulator")
        
        # Game state
        self.world = World(config.WORLD_WIDTH, config.WORLD_HEIGHT)
        self.clock = pygame.time.Clock()
        self.running = True
        self.paused = False
        
        # Rendering optimization
        self.world_surface = pygame.Surface((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        
        # UI state
        self.show_debug = True
        self.show_pheromones = True
        self.selected_ant: Optional[Ant] = None
        self.camera_x = 0
        self.camera_y = 0
        
        # Performance tracking
        self.frame_times = []
        self.last_fps_update = time.time()
        self.fps_display = 60
        
        print("🐜 Anthill Simulator initialized!")
        print("Controls:")
        print("  SPACE - Pause/Resume")
        print("  D - Toggle debug info")
        print("  P - Toggle pheromone display")
        print("  Click - Select ant")
        print("  Arrow keys - Move camera")
        print("  ESC - Exit")
    
    def run(self):
        """Main game loop."""
        while self.running:
            frame_start = time.time()
            
            # Handle events
            self._handle_events()
            
            # Update game state
            if not self.paused:
                self.world.update()
            
            # Render
            self._render()
            
            # Performance tracking
            frame_time = time.time() - frame_start
            self.frame_times.append(frame_time)
            if len(self.frame_times) > 60:
                self.frame_times.pop(0)
            
            # Update FPS display periodically
            if time.time() - self.last_fps_update > 1.0:
                if self.frame_times:
                    avg_frame_time = sum(self.frame_times) / len(self.frame_times)
                    self.fps_display = int(1.0 / max(0.001, avg_frame_time))
                self.last_fps_update = time.time()
            
            # Maintain target FPS
            self.clock.tick(config.FPS)
        
        pygame.quit()
        sys.exit()
    
    def _handle_events(self):
        """Handle user input events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                    print("⏸️ Paused" if self.paused else "▶️ Resumed")
                elif event.key == pygame.K_d:
                    self.show_debug = not self.show_debug
                elif event.key == pygame.K_p:
                    self.show_pheromones = not self.show_pheromones
                elif event.key == pygame.K_r:
                    # Reset simulation
                    self.world = World(config.WORLD_WIDTH, config.WORLD_HEIGHT)
                    self.selected_ant = None
                    print("🔄 Simulation reset")
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    self._handle_mouse_click(event.pos)
        
        # Handle continuous keyboard input for camera movement
        keys = pygame.key.get_pressed()
        camera_speed = 5
        
        if keys[pygame.K_LEFT]:
            self.camera_x = max(0, self.camera_x - camera_speed)
        if keys[pygame.K_RIGHT]:
            self.camera_x = min(config.WORLD_WIDTH - config.WINDOW_WIDTH // config.CELL_SIZE,
                               self.camera_x + camera_speed)
        if keys[pygame.K_UP]:
            self.camera_y = max(0, self.camera_y - camera_speed)
        if keys[pygame.K_DOWN]:
            self.camera_y = min(config.WORLD_HEIGHT - config.WINDOW_HEIGHT // config.CELL_SIZE,
                               self.camera_y + camera_speed)
    
    def _handle_mouse_click(self, pos):
        """Handle mouse clicks for ant selection."""
        # Convert screen coordinates to world coordinates
        world_x = pos[0] // config.CELL_SIZE + self.camera_x
        world_y = pos[1] // config.CELL_SIZE + self.camera_y
        
        # Find ant near click position
        clicked_ant = None
        min_distance = float('inf')
        
        for ant in self.world.ants:
            if ant.alive:
                distance = ((ant.x - world_x) ** 2 + (ant.y - world_y) ** 2) ** 0.5
                if distance < 3 and distance < min_distance:  # Within 3 cells
                    min_distance = distance
                    clicked_ant = ant
        
        if clicked_ant:
            self.selected_ant = clicked_ant
            print(f"🐜 Selected ant {clicked_ant.id} - Task: {clicked_ant.current_task}")
        else:
            self.selected_ant = None
    
    def _render(self):
        """Render the current game state."""
        # Clear screen
        self.screen.fill(config.COLORS['background'])
        
        # Render world
        self._render_world()
        
        # Render ants
        self._render_ants()
        
        # Render UI
        if self.show_debug:
            self._render_debug_info()
        
        # Render selected ant info
        if self.selected_ant and self.selected_ant.alive:
            self._render_ant_info()
        
        # Update display
        pygame.display.flip()
    
    def _render_world(self):
        """Render the world terrain, food, and pheromones."""
        for x in range(self.camera_x, 
                      min(config.WORLD_WIDTH, self.camera_x + config.WINDOW_WIDTH // config.CELL_SIZE)):
            for y in range(self.camera_y,
                          min(config.WORLD_HEIGHT, self.camera_y + config.WINDOW_HEIGHT // config.CELL_SIZE)):
                
                # Get cell color (includes terrain, food, pheromones)
                color = self.world.get_cell_color(x, y)
                
                # If not showing pheromones, remove pheromone overlay
                if not self.show_pheromones:
                    # Get base color without pheromones
                    terrain_type = self.world.terrain[x, y]
                    if terrain_type == 0:  # Air
                        color = config.COLORS['background']
                    elif terrain_type == 1:  # Soil
                        color = config.COLORS['soil']
                    elif terrain_type == 2:  # Tunnel
                        color = config.COLORS['tunnel']
                    
                    # Add food overlay
                    if self.world.food[x, y] > 0:
                        food_intensity = min(1.0, self.world.food[x, y] / 5.0)
                        food_color = config.COLORS['food']
                        color = self.world._blend_colors(color, food_color, food_intensity * 0.8)
                
                # Calculate screen position
                screen_x = (x - self.camera_x) * config.CELL_SIZE
                screen_y = (y - self.camera_y) * config.CELL_SIZE
                
                # Draw cell
                pygame.draw.rect(
                    self.screen,
                    color,
                    (screen_x, screen_y, config.CELL_SIZE, config.CELL_SIZE)
                )
    
    def _render_ants(self):
        """Render all ants."""
        for ant in self.world.ants:
            if not ant.alive:
                continue
            
            # Check if ant is visible on screen
            screen_x = (ant.x - self.camera_x) * config.CELL_SIZE
            screen_y = (ant.y - self.camera_y) * config.CELL_SIZE
            
            if (screen_x < -config.CELL_SIZE or screen_x > config.WINDOW_WIDTH or
                screen_y < -config.CELL_SIZE or screen_y > config.WINDOW_HEIGHT):
                continue
            
            # Choose ant color based on state
            if ant == self.selected_ant:
                color = (255, 255, 0)  # Yellow for selected ant
            elif ant.carrying_food > 0:
                color = (255, 150, 50)  # Orange for carrying food
            else:
                color = config.COLORS['ant']
            
            # Draw ant
            ant_size = max(2, config.CELL_SIZE - 1)
            pygame.draw.circle(
                self.screen,
                color,
                (screen_x + config.CELL_SIZE // 2, screen_y + config.CELL_SIZE // 2),
                ant_size // 2
            )
            
            # Draw ant ID for selected ant
            if ant == self.selected_ant:
                id_text = self.small_font.render(str(ant.id), True, (255, 255, 255))
                self.screen.blit(id_text, (screen_x, screen_y - 15))
            
            # Draw energy bar for selected ant
            if ant == self.selected_ant:
                bar_width = config.CELL_SIZE * 2
                bar_height = 3
                energy_ratio = ant.energy / ant.max_energy
                
                # Background bar
                pygame.draw.rect(
                    self.screen,
                    (100, 100, 100),
                    (screen_x - bar_width // 4, screen_y - 8, bar_width, bar_height)
                )
                
                # Energy bar
                pygame.draw.rect(
                    self.screen,
                    (0, 255, 0) if energy_ratio > 0.5 else (255, 255, 0) if energy_ratio > 0.2 else (255, 0, 0),
                    (screen_x - bar_width // 4, screen_y - 8, int(bar_width * energy_ratio), bar_height)
                )
    
    def _render_debug_info(self):
        """Render debug information."""
        stats = self.world.get_statistics()
        
        debug_info = [
            f"FPS: {self.fps_display}",
            f"Frame: {stats['frame_count']}",
            f"Ants: {stats['alive_ants']}",
            f"Food Storage: {stats['food_storage']:.1f}",
            f"Food Collected: {stats['total_food_collected']:.1f}",
            f"Food Carried: {stats['food_being_carried']:.1f}",
            f"Tunnels: {stats['tunnels_dug']}",
            f"Avg Energy: {stats['average_energy']:.1f}",
            f"Generation: {stats['generation']}",
            "",
            "Controls:",
            "SPACE - Pause/Resume",
            "D - Toggle debug",
            "P - Toggle pheromones",
            "R - Reset",
            "Click - Select ant",
            "Arrows - Move camera"
        ]
        
        y_offset = 10
        for line in debug_info:
            if line:  # Skip empty lines for spacing
                text = self.font.render(line, True, (255, 255, 255))
                self.screen.blit(text, (10, y_offset))
            y_offset += 25
    
    def _render_ant_info(self):
        """Render information about the selected ant."""
        ant = self.selected_ant
        if not ant or not ant.alive:
            return
        
        # Create semi-transparent background
        info_surface = pygame.Surface((300, 200))
        info_surface.set_alpha(200)
        info_surface.fill((0, 0, 0))
        
        x_pos = config.WINDOW_WIDTH - 310
        y_pos = 10
        
        self.screen.blit(info_surface, (x_pos, y_pos))
        
        # Ant information
        ant_info = [
            f"Ant #{ant.id}",
            f"Task: {ant.current_task}",
            f"Energy: {ant.energy:.1f}/{ant.max_energy}",
            f"Age: {ant.age}",
            f"Carrying Food: {ant.carrying_food}",
            f"Position: ({ant.x}, {ant.y})",
            f"Experience: {ant.experience_points}",
            f"Memories: {len(ant.memories)}",
            f"Relationships: {len(ant.relationships)}",
        ]
        
        # Add recent memories
        if ant.memories:
            ant_info.append("")
            ant_info.append("Recent Memories:")
            for i, memory in enumerate(ant.memories[-3:]):
                if i < 2:  # Limit to 2 memories for space
                    short_memory = memory.content[:30] + "..." if len(memory.content) > 30 else memory.content
                    ant_info.append(f"  {short_memory}")
        
        # Add relationships
        if ant.relationships:
            strong_relationships = [
                rel for rel in ant.relationships.values() 
                if rel.strength > 20
            ]
            if strong_relationships:
                ant_info.append("")
                ant_info.append(f"Strong bonds: {len(strong_relationships)}")
        
        # Render ant info
        y_offset = y_pos + 10
        for line in ant_info:
            if y_offset > config.WINDOW_HEIGHT - 30:  # Don't render off screen
                break
            
            text = self.small_font.render(line, True, (255, 255, 255))
            self.screen.blit(text, (x_pos + 10, y_offset))
            y_offset += 18


def main():
    """Main entry point."""
    try:
        print("🚀 Starting AI Anthill Simulator...")
        print("⚠️  Make sure you have Ollama installed and llama3.2:1b model downloaded")
        print("   Run: ollama pull llama3.2:1b")
        print()
        
        simulator = AntHillSimulator()
        simulator.run()
        
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()