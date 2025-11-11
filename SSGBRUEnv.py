
import numpy as np
import gymnasium as gym
from gymnasium import spaces
import pygame
from pygame.math import Vector2

# Import your existing game classes
# Adjust the import path based on your file structure
from game import (
    Snake,
    Food,
    ShrinkingBorder,
    Main,
    num_cells,
    cell_size,
    SHRINK_START_MS
)


class SSGBRUEnv(gym.Env):
    def __init__():
        actions = spaces.Discrete(4)
        observation_space = spaces.Box()


# Register the gymnasium environment
gym.register(
    id="SSGBRU",
    entry_point="__main__:SSGBRUEnv",
    max_episode_steps=1000,
)


if __name__ == "__main__":
    env = gym.make("SSGBRU")
    observation, info = env.reset(seed=42)

    total_reward = 0
    for step in range(1000):
        action = env.action_space.sample()
        observation, reward, terminated, truncated, info = env.step(action)
        total_reward += reward

        if step % 100 == 0:
            env.render()

        if terminated or truncated:
            print(
                f"Episode ended: {step} steps, Reward: {total_reward:.1f}, Length: {info['snake_length']}")
            observation, info = env.reset()
            total_reward = 0

    env.close()
