import torch
import random
import numpy as np
from game import Main
from collections import deque

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001


class Agent:
    def __init__(self):
        self.num_games = 0
        self.epsilon = 0  # Controls randomness
        self.gamma = 0  # Discount rate
        self.memory = deque(maxlen=MAX_MEMORY)  # popleft()
        # TODO: Model, trainer

    def get_state(self, game):
        pass

    def remember(self, state, action, reward, next_state, done):
        pass

    def train_long_memory(self):
        pass

    def train_short_memory(self):
        pass

    def get_action(self, state):
        pass

    def train():
        plot_scores = []
        plot_avg_scores = []
        total_score = 0
        best_score = 0
        agent = agent()
        game = Main()
        while True:
            # Get old/current state
            old_state = agent.get_state(game)

            # Get move based on current state
            final_move = agent.get_action(old_state)

            # Perform move and get new state


if __name__ == '__main__':
    train()
