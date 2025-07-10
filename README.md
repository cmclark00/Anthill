# 🐜 AI Anthill Simulator

A fascinating "fishbowl" simulation where AI-powered ants build, learn, and evolve in their virtual anthill. Each ant uses a local Large Language Model (LLM) for decision-making, creating emergent behaviors as they collaborate, form memories, and develop relationships.

## ✨ Features

### 🧠 AI-Powered Ants
- **Local LLM Integration**: Each ant uses `llama3.2:1b` for intelligent decision-making
- **Memory System**: Ants remember locations, experiences, and social interactions
- **Relationship Building**: Ants form bonds and share knowledge with each other
- **Learning & Evolution**: Successful behaviors spread through the colony

### 🏗️ Dynamic Anthill
- **Terrain Modification**: Ants dig tunnels and expand their underground network
- **Food Collection**: Search for food on the surface and bring it back to storage
- **Pheromone Trails**: Chemical communication for coordination
- **Colony Growth**: Successful colonies spawn new ants over time

### 🎮 Interactive Experience
- **Real-time Simulation**: Watch ants make decisions and interact in real-time
- **Ant Selection**: Click on ants to see their thoughts, memories, and relationships
- **Debug Information**: Monitor colony statistics and individual ant details
- **Camera Controls**: Explore the anthill with smooth camera movement

### ⚡ Performance Optimized
- **Pixel Graphics**: Efficient 4x4 pixel cells for smooth performance
- **Smart Caching**: LLM decision caching to reduce computational load
- **Optimized for RTX 3070**: Designed for your 8GB VRAM + 32GB RAM setup

## 🛠️ Installation

### Prerequisites
1. **Python 3.8+**
2. **Ollama** (for local LLM)
3. **GPU Support** (recommended: RTX 3070 or better)

### Setup Instructions

1. **Clone or create the project:**
   ```bash
   # If you have this as a git repo:
   git clone <your-repo-url>
   cd anthill-simulator
   
   # Or create directory and copy files
   mkdir anthill-simulator
   cd anthill-simulator
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install and setup Ollama:**
   ```bash
   # Install Ollama (Linux/Mac)
   curl -fsSL https://ollama.ai/install.sh | sh
   
   # Or download from: https://ollama.ai/download
   
   # Pull the lightweight model (optimized for your 8GB VRAM)
   ollama pull llama3.2:1b
   ```

4. **Run the simulator:**
   ```bash
   python main.py
   ```

## 🎮 How to Play

### Controls
- **SPACE** - Pause/Resume simulation
- **D** - Toggle debug information
- **P** - Toggle pheromone visualization
- **R** - Reset simulation
- **Arrow Keys** - Move camera
- **Mouse Click** - Select ant to view details
- **ESC** - Exit

### What You'll See

1. **Brown Areas**: Soil that ants can dig through
2. **Dark Brown**: Tunnels and chambers
3. **Green Dots**: Food sources
4. **Red Dots**: Ants (turn orange when carrying food)
5. **Green/Blue Trails**: Pheromone trails (when enabled)
6. **Yellow Outline**: Selected ant

### Watching the Colony Evolve

- **Early Stage**: Ants explore randomly, learning the environment
- **Food Discovery**: Watch as ants find food and establish supply chains
- **Tunnel Expansion**: See the anthill grow as ants dig new passages
- **Social Learning**: Observe ants sharing knowledge and forming relationships
- **Colony Growth**: Successful colonies will spawn new ants over time

## 🧠 AI Behavior System

### Decision Making
Each ant uses the LLM to make contextual decisions based on:
- Current energy and health status
- Nearby food sources and obstacles
- Other ants in the vicinity
- Personal memories and experiences
- Current task and colony needs

### Memory Types
- **Food Locations**: Remember where food was found
- **Successful Paths**: Learn efficient routes
- **Social Interactions**: Track relationships with other ants
- **Danger Areas**: Avoid problematic locations
- **Task Successes**: Build expertise in specific activities

### Emergent Behaviors
Watch for these emergent patterns:
- **Food Chains**: Ants establishing efficient food collection routes
- **Specialization**: Some ants becoming better at specific tasks
- **Cooperation**: Ants helping each other with difficult tasks
- **Knowledge Sharing**: Information spreading through the colony
- **Adaptive Architecture**: Tunnel layouts evolving for efficiency

## ⚙️ Configuration

Edit `config.py` to customize the simulation:

```python
# Performance tuning
CELL_SIZE = 4          # Smaller = more detail, lower performance
FPS = 60               # Target framerate
AI_UPDATE_FREQUENCY = 30  # Frames between AI decisions

# Colony settings
INITIAL_ANTS = 12      # Starting population
ANT_MEMORY_SIZE = 50   # How much ants can remember
ANT_VISION_RANGE = 8   # How far ants can see

# AI settings
LLM_MODEL = "llama3.2:1b"  # Local model to use
MAX_CONTEXT_LENGTH = 512   # LLM context size
```

## 🐛 Troubleshooting

### Common Issues

1. **"Model not found" error:**
   ```bash
   ollama pull llama3.2:1b
   ```

2. **Poor performance:**
   - Reduce `ANT_VISION_RANGE` in config.py
   - Increase `AI_UPDATE_FREQUENCY` for less frequent AI calls
   - Reduce `INITIAL_ANTS` for smaller colony

3. **Import errors:**
   ```bash
   pip install --upgrade pygame numpy ollama requests pillow
   ```

4. **Ollama connection issues:**
   - Ensure Ollama service is running: `ollama serve`
   - Check available models: `ollama list`

### Performance Tips

- **GPU Memory**: The llama3.2:1b model uses ~1.5GB VRAM, leaving plenty for other processes
- **CPU Usage**: Pygame rendering is CPU-bound; LLM inference uses GPU
- **Memory Usage**: Each ant stores ~50 memories; 100 ants = ~5000 memories in RAM

## 🔬 Technical Architecture

### Core Components
- **`main.py`**: Game loop, rendering, and user interface
- **`ant.py`**: Individual ant AI, memory, and behavior
- **`world.py`**: Environment simulation and physics
- **`ai_brain.py`**: LLM integration and decision making
- **`config.py`**: All configuration settings

### Data Flow
1. World updates all ants each frame
2. Ants gather context about their environment
3. AI brain processes context and returns decisions
4. Ants execute actions (move, dig, collect food, etc.)
5. Renderer displays current state to screen

## 🚀 Future Enhancements

Potential improvements for the simulation:
- **Predators**: Add challenges that require defensive behavior
- **Seasons**: Varying food availability and weather conditions
- **Evolution**: Genetic algorithms for ant trait inheritance
- **Multi-Colony**: Competing ant colonies
- **Advanced Architecture**: Specialized chambers (nurseries, storage, etc.)
- **Research Mode**: Data collection and analysis tools

## 📊 System Requirements

**Minimum:**
- Python 3.8+
- 4GB RAM
- OpenGL-capable graphics
- 2GB free disk space

**Recommended (Your Setup):**
- RTX 3070 (8GB VRAM) ✅
- 32GB RAM ✅
- Python 3.9+
- SSD storage

## 🎯 Educational Value

This simulator demonstrates:
- **Emergent AI Behavior**: How simple rules create complex patterns
- **Swarm Intelligence**: Collective problem-solving without central control
- **Memory and Learning**: How experience shapes future decisions
- **Social Dynamics**: Relationship formation and knowledge sharing
- **System Dynamics**: Feedback loops in complex systems

## 📝 License

This project is open source. Feel free to modify and experiment with the code to create your own AI ecosystem simulations!

---

**Enjoy watching your AI ant colony grow and evolve!** 🐜🧠✨