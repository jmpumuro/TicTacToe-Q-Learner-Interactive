import numpy as np
import random
import tensorflow as tf
from tensorflow.keras import layers
from collections import deque
from .game import TicTacToe

class TicTacToeQLearning:
    def __init__(self, epsilon=1.0, epsilon_decay=0.995, epsilon_min=0.01, alpha=0.001, gamma=0.99, buffer_capacity=10000):
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        self.alpha = alpha
        self.gamma = gamma
        self.buffer_capacity = buffer_capacity

        self.model = self.create_model()
        self.target_model = self.create_model()
        self.target_model.set_weights(self.model.get_weights())

        self.replay_buffer = deque(maxlen=self.buffer_capacity)

    def create_model(self):
        model = tf.keras.Sequential([
            layers.Dense(128, activation='relu', input_shape=(9,)),
            layers.Dense(128, activation='relu'),
            layers.Dense(9)
        ])
        model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=self.alpha),
                      loss=tf.keras.losses.Huber())
        return model

    def normalize_state(self, state):
        return np.array([1 if val == 'X' else (-1 if val == 'O' else 0) for val in state], dtype=np.float32)

    def get_action(self, state):
        if random.random() < self.epsilon:
            available_actions = [i for i, value in enumerate(state) if value == 0]
            action = random.choice(available_actions)
        else:
            state_tensor = self.normalize_state(state).reshape(1, 9)
            q_values = self.model.predict(state_tensor).flatten()
            available_actions = [i for i, value in enumerate(state) if value == 0]
            q_vals_available = q_values * (np.array(state) == 0)
            available_q_vals = q_vals_available[available_actions]
            action = available_actions[np.argmax(available_q_vals)]
        return action

    def update_replay_buffer(self, state, action, reward, next_state):
        self.replay_buffer.append((state, action, reward, next_state))

    def train(self, episodes, epsilon =1.0,gamma =0.99, batch_size=32, target_network_update_freq=10):
        self.epsilon = epsilon
        self.gamma = gamma
        for episode in range(episodes):
            game = TicTacToe()
            done = False

            while not done:
                for player in ['X', 'O']:
                    state = game.get_state()
                    state_numeric = self.normalize_state(state)
                    action = self.get_action(state)

                    if action is None:
                        break

                    game.make_move(action)

                    if game.is_winner(player):
                        next_state = game.get_state()
                        next_state_numeric = self.normalize_state(next_state)
                        reward = 1 if player == 'X' else -1
                        self.update_replay_buffer(state_numeric, action, reward, next_state_numeric)
                        done = True
                        break
                    elif game.is_draw():
                        next_state = game.get_state()
                        next_state_numeric = self.normalize_state(next_state)
                        self.update_replay_buffer(state_numeric, action, 0, next_state_numeric)
                        done = True
                        break

            if len(self.replay_buffer) >= batch_size:
                batch = random.sample(self.replay_buffer, batch_size)
                states, actions, rewards, next_states = zip(*batch)
                states = np.array(states)
                actions = np.array(actions)
                rewards = np.array(rewards)
                next_states = np.array(next_states)

                next_q_values = np.max(self.target_model.predict(next_states), axis=1)
                target_q_values = rewards + self.gamma * next_q_values

                self.model.fit(states, target_q_values, verbose=0)

                if episode % target_network_update_freq == 0:
                    self.target_model.set_weights(self.model.get_weights())

            self.epsilon = max(self.epsilon * self.epsilon_decay, self.epsilon_min)

    def save_model(self, filename):
        self.model.save(f"{filename}.keras")

    def load_model(self, filename):
        self.model = tf.keras.models.load_model(filename)
        self.target_model.set_weights(self.model.get_weights())
