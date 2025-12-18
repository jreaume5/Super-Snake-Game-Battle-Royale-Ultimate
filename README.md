# Super-Snake-Game-Battle-Royale-Ultimate
Super Snake Game Battle Royale Ultimate is a spin on the classic snake game that integrates battle royale elements to reshape the playing field. Unlike the original version of the game, SSGBRU aims to support up to 4 snakes competing in the same arena to be the last one standing. Fans of the traditional game will appreciate how familiar the gameplay is while also being introduced to entirely new mechanics. SSGBRU's methodology includes using deep reinforcement learning (DRL) to train the AI agent snakes to develop their own unique playstyles, specifically rewarding the bots for the longer they survive, eating food, and avoiding obstacles.

This project demonstrates multi-agents reinforcement learning, game-state encoding, reward shaping, and real-time visualization using Python and Pygame. 

## Repository
```bash 
git clone https://github.com/jreaume5/Super-Snake-Game-Battle-Royale-Ultimate.git
cd Super-Snake-Game-Battle-Royale-Ultimate
```

## Requirements
- Python 3.9+ (Python 3.10+ recommended)
- Works on Windows and macOS

## Setup Instructions
### 1) Create a virtual environment (recommended but not required)
**macOS / Linux**
```bash
python3 -m venv .venv
source .venv/bin/activate
```
**Windows (PowerShell)**
```bash
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```
### 2) Install dependencies
```bash
pip install -r requirements.txt
```
### 3) Run the program
**macOS / Linux**
```bash
python3 game.py
```
**Windows alternative**
```bash
py game.py
```
A game window titled “Super Snake Game Battle Royale Ultimate” will open.

## Using the Game
### Main Menu Options
- Start Game (Human-controlled mode — currently not used for grading; Simulation mode should be used instead)
- Simulation (Primary mode — used for training and demonstrating the neural-network agents)
- Settings (Volume control)
- Quit (Exit the program)

## Simulation Mode (Neural Network Training)
### 1. From the main menu, select Simulation
### 2. On the Simulation screen:
- Press T to train the AI agents
    - Training progress prints in the terminal (episode rewards)
- After training completes, press R to run a visual simulation using the trained agent
### 3. Press ESC at any time to return to the main menu

## Controls
### Simulation Mode
- T – Train AI agents
- R – Run trained agent visually
- ESC – Return to main menu

