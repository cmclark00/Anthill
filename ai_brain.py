"""
AI Brain module for anthill simulator.
Handles LLM integration for ant decision making.
"""

import json
import time
from typing import Dict, List, Any, Optional
import config


class AIBrain:
    """Manages LLM interactions for ant decision making."""
    
    def __init__(self):
        self.ollama_available = False
        self.decision_cache = {}  # Cache decisions to reduce LLM calls
        self.last_llm_call = 0
        self._init_ollama()
    
    def _init_ollama(self):
        """Initialize connection to Ollama."""
        try:
            import ollama
            self.ollama = ollama
            # Test if model is available
            models = ollama.list()
            model_names = [model['name'] for model in models['models']]
            if config.LLM_MODEL in model_names:
                self.ollama_available = True
                print(f"✓ AI Brain initialized with {config.LLM_MODEL}")
            else:
                print(f"⚠ Model {config.LLM_MODEL} not found. Available models: {model_names}")
                print("Run: ollama pull llama3.2:1b")
        except ImportError:
            print("⚠ Ollama not available. Ants will use basic AI.")
        except Exception as e:
            print(f"⚠ Ollama connection failed: {e}")
    
    def make_decision(self, ant_state: Dict[str, Any], world_context: Dict[str, Any]) -> str:
        """
        Make a decision for an ant based on its state and world context.
        Returns an action string.
        """
        current_time = time.time()
        
        # Rate limiting for performance
        if current_time - self.last_llm_call < 0.1:  # Min 100ms between calls
            return self._fallback_decision(ant_state, world_context)
        
        # Check cache first
        cache_key = self._generate_cache_key(ant_state, world_context)
        if cache_key in self.decision_cache:
            return self.decision_cache[cache_key]
        
        if not self.ollama_available:
            return self._fallback_decision(ant_state, world_context)
        
        try:
            decision = self._query_llm(ant_state, world_context)
            self.decision_cache[cache_key] = decision
            self.last_llm_call = current_time
            
            # Keep cache small
            if len(self.decision_cache) > 100:
                self.decision_cache.clear()
            
            return decision
        
        except Exception as e:
            print(f"LLM decision failed: {e}")
            return self._fallback_decision(ant_state, world_context)
    
    def _generate_cache_key(self, ant_state: Dict, world_context: Dict) -> str:
        """Generate a cache key for similar situations."""
        key_data = {
            'energy': ant_state.get('energy', 0) // 10,  # Round energy to groups of 10
            'carrying_food': ant_state.get('carrying_food', 0),
            'near_food': world_context.get('near_food', False),
            'near_home': world_context.get('near_home', False),
            'task': ant_state.get('current_task', 'explore')
        }
        return str(hash(frozenset(key_data.items())))
    
    def _query_llm(self, ant_state: Dict[str, Any], world_context: Dict[str, Any]) -> str:
        """Query the LLM for decision making."""
        
        prompt = self._build_prompt(ant_state, world_context)
        
        response = self.ollama.generate(
            model=config.LLM_MODEL,
            prompt=prompt,
            options={
                'temperature': 0.7,
                'top_p': 0.9,
                'num_predict': 50,  # Short responses for performance
                'stop': ['\\n', '.']
            }
        )
        
        decision = response['response'].strip().lower()
        return self._parse_decision(decision)
    
    def _build_prompt(self, ant_state: Dict[str, Any], world_context: Dict[str, Any]) -> str:
        """Build a context-aware prompt for the ant."""
        
        # Summarize ant state
        energy = ant_state.get('energy', 100)
        food_carried = ant_state.get('carrying_food', 0)
        current_task = ant_state.get('current_task', 'explore')
        
        # Summarize world context
        near_food = world_context.get('near_food', False)
        near_home = world_context.get('near_home', False)
        near_ants = world_context.get('near_ants', [])
        tunnel_nearby = world_context.get('tunnel_nearby', False)
        
        # Recent memories
        recent_memories = ant_state.get('recent_memories', [])
        memory_summary = ", ".join(recent_memories[-3:]) if recent_memories else "no recent memories"
        
        prompt = f"""You are an ant in a colony. Your goal is survival and helping the colony thrive.

Current status:
- Energy: {energy}/100
- Carrying food: {food_carried}/{config.ANT_CARRYING_CAPACITY}
- Current task: {current_task}
- Recent memories: {memory_summary}

Environment:
- Food nearby: {near_food}
- Home/tunnel nearby: {near_home}  
- Other ants nearby: {len(near_ants)}
- Can dig tunnel here: {tunnel_nearby}

What should you do? Choose ONE action:
explore, move_to_food, collect_food, return_home, dig_tunnel, follow_ant, rest, help_ant

Action:"""
        
        return prompt
    
    def _parse_decision(self, llm_response: str) -> str:
        """Parse and validate LLM response."""
        valid_actions = [
            'explore', 'move_to_food', 'collect_food', 'return_home', 
            'dig_tunnel', 'follow_ant', 'rest', 'help_ant'
        ]
        
        # Extract action from response
        for action in valid_actions:
            if action in llm_response:
                return action
        
        # Default fallback
        return 'explore'
    
    def _fallback_decision(self, ant_state: Dict[str, Any], world_context: Dict[str, Any]) -> str:
        """Simple rule-based decision making when LLM is not available."""
        
        energy = ant_state.get('energy', 100)
        food_carried = ant_state.get('carrying_food', 0)
        near_food = world_context.get('near_food', False)
        near_home = world_context.get('near_home', False)
        
        # Low energy - rest or return home
        if energy < 30:
            return 'rest' if near_home else 'return_home'
        
        # Carrying food - return home
        if food_carried > 0:
            return 'return_home'
        
        # Food nearby - collect it
        if near_food:
            return 'collect_food'
        
        # Default - explore
        return 'explore'
    
    def process_memory(self, memory_text: str, memory_type: str) -> Dict[str, Any]:
        """Process and categorize a memory for an ant."""
        return {
            'type': memory_type,
            'content': memory_text,
            'timestamp': time.time(),
            'importance': self._calculate_importance(memory_text, memory_type)
        }
    
    def _calculate_importance(self, memory_text: str, memory_type: str) -> float:
        """Calculate the importance of a memory (0.0 to 1.0)."""
        importance_weights = {
            'food_location': 0.8,
            'danger': 0.9,
            'social_interaction': 0.6,
            'task_success': 0.7,
            'path_learned': 0.5
        }
        
        base_importance = importance_weights.get(memory_type, 0.5)
        
        # Adjust based on content keywords
        if 'food' in memory_text.lower():
            base_importance += 0.1
        if 'danger' in memory_text.lower() or 'threat' in memory_text.lower():
            base_importance += 0.2
        
        return min(1.0, base_importance)


# Global AI brain instance
ai_brain = AIBrain()