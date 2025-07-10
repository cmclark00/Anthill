#!/usr/bin/env python3
"""
Setup script for AI Anthill Simulator
Helps with dependency installation and environment setup.
"""

import subprocess
import sys
import os
import platform
from pathlib import Path


def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required!")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True


def install_pip_dependencies():
    """Install Python dependencies."""
    print("\n📦 Installing Python dependencies...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Python dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False


def check_ollama():
    """Check if Ollama is installed and accessible."""
    print("\n🤖 Checking Ollama installation...")
    
    try:
        result = subprocess.run(["ollama", "--version"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ Ollama found: {result.stdout.strip()}")
            return True
        else:
            print("❌ Ollama not found or not working properly")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("❌ Ollama not found in PATH")
        return False


def install_ollama():
    """Provide instructions for installing Ollama."""
    print("\n🔧 Ollama installation required:")
    
    system = platform.system().lower()
    
    if system == "linux":
        print("   Run: curl -fsSL https://ollama.ai/install.sh | sh")
    elif system == "darwin":  # macOS
        print("   Run: curl -fsSL https://ollama.ai/install.sh | sh")
        print("   Or download from: https://ollama.ai/download")
    elif system == "windows":
        print("   Download from: https://ollama.ai/download")
    else:
        print("   Visit: https://ollama.ai/download")
    
    print("\n   After installation, restart your terminal and run this setup again.")


def check_and_pull_model():
    """Check if the LLM model is available, pull if necessary."""
    print("\n🧠 Checking AI model...")
    
    try:
        # Check if model exists
        result = subprocess.run(["ollama", "list"], 
                              capture_output=True, text=True, timeout=10)
        
        if "llama3.2:1b" in result.stdout:
            print("✅ llama3.2:1b model found")
            return True
        else:
            print("📥 Downloading llama3.2:1b model (this may take a few minutes)...")
            
            # Pull the model
            pull_result = subprocess.run(["ollama", "pull", "llama3.2:1b"], 
                                       timeout=300)  # 5 minute timeout
            
            if pull_result.returncode == 0:
                print("✅ Model downloaded successfully")
                return True
            else:
                print("❌ Failed to download model")
                return False
    
    except subprocess.TimeoutExpired:
        print("❌ Timeout while checking/downloading model")
        return False
    except FileNotFoundError:
        print("❌ Ollama not found - please install it first")
        return False


def test_installation():
    """Test if everything is working by importing modules."""
    print("\n🧪 Testing installation...")
    
    try:
        import pygame
        print("✅ Pygame imported successfully")
    except ImportError:
        print("❌ Failed to import Pygame")
        return False
    
    try:
        import numpy
        print("✅ NumPy imported successfully")
    except ImportError:
        print("❌ Failed to import NumPy")
        return False
    
    try:
        import ollama
        print("✅ Ollama Python client imported successfully")
    except ImportError:
        print("❌ Failed to import Ollama Python client")
        return False
    
    # Test basic components
    try:
        import config
        print("✅ Configuration loaded")
    except ImportError:
        print("❌ Failed to import config")
        return False
    
    return True


def create_launch_script():
    """Create a simple launch script."""
    print("\n📝 Creating launch script...")
    
    script_content = '''#!/usr/bin/env python3
"""
Launch script for AI Anthill Simulator
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run the main simulator
from main import main

if __name__ == "__main__":
    main()
'''
    
    with open("run_simulator.py", "w") as f:
        f.write(script_content)
    
    # Make executable on Unix-like systems
    if hasattr(os, 'chmod'):
        os.chmod("run_simulator.py", 0o755)
    
    print("✅ Launch script created: run_simulator.py")


def main():
    """Main setup function."""
    print("🐜 AI Anthill Simulator Setup")
    print("=" * 40)
    
    success = True
    
    # Check Python version
    if not check_python_version():
        success = False
    
    # Install Python dependencies
    if success and not install_pip_dependencies():
        success = False
    
    # Check Ollama
    if success:
        if not check_ollama():
            install_ollama()
            success = False
        else:
            # Check and pull model
            if not check_and_pull_model():
                success = False
    
    # Test installation
    if success and not test_installation():
        success = False
    
    # Create launch script
    if success:
        create_launch_script()
    
    print("\n" + "=" * 40)
    
    if success:
        print("🎉 Setup completed successfully!")
        print("\nTo start the simulator:")
        print("   python main.py")
        print("   or")
        print("   python run_simulator.py")
        print("\nControls:")
        print("   SPACE - Pause/Resume")
        print("   D - Toggle debug info")
        print("   P - Toggle pheromones")
        print("   Click - Select ant")
        print("   ESC - Exit")
    else:
        print("❌ Setup incomplete. Please resolve the issues above and run setup again.")
        sys.exit(1)


if __name__ == "__main__":
    main()