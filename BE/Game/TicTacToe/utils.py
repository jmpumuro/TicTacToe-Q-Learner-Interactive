import numpy as np
import random

class TicTacToeQLearning:
    def __init__(self, epsilon=0.1, alpha=0.5, gamma=0.9):
        self.epsilon = epsilon  # Exploration rate
        self.alpha = alpha      # Learning rate
        self.gamma = gamma      # Discount factor

        self.q_values = {}      # Q-values dictionary
        self.state_history = [] # List to store state history for updating Q-values
        self.replay_buffer = [] # Replay buffer for storing experiences

    def get_state_key(self, state):
        # Convert the board state into a unique key for dictionary access
        return ''.join(str(x) for x in state)

    def get_action(self, state):
        # Explore (random action) or exploit (best known action)
        available_actions = [i for i, value in enumerate(state) if value == 0]
        if len(available_actions) == 0:
            return None

        if random.random() < self.epsilon:
            # Random action
            action = random.choice(available_actions)
        else:
            # Best known action
            state_key = self.get_state_key(state)
            if state_key not in self.q_values:
                # Initialize Q-values for this state if it's encountered for the first time
                self.q_values[state_key] = np.zeros(9)

            q_vals = self.q_values[state_key]
            q_vals_available = q_vals * (np.array(state) == 0)
            available_q_vals = q_vals_available[available_actions]
            max_q_val = np.max(available_q_vals)
            action = available_actions[np.where(available_q_vals == max_q_val)[0][0]]

        return action

    def update_q_values(self, reward):
        max_q_value = -np.Inf

        for state, action, next_state in reversed(self.state_history):
            state_key = self.get_state_key(state)
            if state_key not in self.q_values:
                self.q_values[state_key] = np.zeros(9)

            q_vals = self.q_values[state_key]
            q_vals[action] = q_vals[action] + self.alpha * (reward + self.gamma * max_q_value - q_vals[action])
            max_q_value = np.max(q_vals)  # Update max_q_value for the next state

        self.state_history = []

    def update_state_history(self, state, action, next_state):
        self.state_history.append((state, action, next_state))

        # Add the experience to the replay buffer
        self.replay_buffer.append((state, action, 0, next_state))

    def train(self, episodes):
     for episode in range(episodes):
        # Initialize the game
        game = TicTacToe()
        done = False

        while not done:
            # Player X's turn
            state = game.get_state()
            action = self.get_action(state)

            if action is None:
                break

            game.make_move(action)

            # Check if the game is over
            if game.is_winner('X'):
                self.update_state_history(state, action, game.get_state())
                self.update_q_values(1)
                done = True
                break
            elif game.is_draw():
                self.update_state_history(state, action, game.get_state())
                self.update_q_values(0)
                done = True
                break

            # Player O's turn
            state = game.get_state()
            action = self.get_action(state)

            if action is None:
                break

            game.make_move(action)

            # Check if the game is over
            if game.is_winner('O'):
                self.update_state_history(state, action, game.get_state())
                self.update_q_values(-1)
                done = True
                break

            self.update_state_history(state, action, game.get_state())

            # Sample experiences from the replay buffer and update Q-values
            batch_size = min(len(self.replay_buffer), 32)
            experiences = random.sample(self.replay_buffer, batch_size)
            for exp_state, exp_action, exp_reward, exp_next_state in experiences:
                exp_state_key = self.get_state_key(exp_state)
                exp_next_state_key = self.get_state_key(exp_next_state)

                if exp_state_key not in self.q_values:
                    self.q_values[exp_state_key] = np.zeros(9)

                q_vals = self.q_values[exp_state_key]
                max_q_value = np.max(self.q_values[exp_next_state_key])
                q_vals[exp_action] = q_vals[exp_action] + self.alpha * (exp_reward + self.gamma * max_q_value - q_vals[exp_action])

        # Learn from the game
        self.update_q_values(0)


    def save_q_values(self, filename):
        np.savez(filename, **self.q_values)

    def load_q_values(self, filename):
        self.q_values = dict(np.load(filename))

class TicTacToe:
    def __init__(self):
        self.board = [0] * 9  # 3x3 tic-tac-toe board
        self.current_player = 'X'

    def get_state(self):
        return self.board

    def make_move(self, position):
        if self.board[position] == 0:
            self.board[position] = self.current_player
            self.current_player = 'O' if self.current_player == 'X' else 'X'

    def is_winner(self, player):
        winning_combinations = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Rows
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Columns
            [0, 4, 8], [2, 4, 6]               # Diagonals
        ]

        for combination in winning_combinations:
            if all(self.board[i] == player for i in combination):
                return True

        return False

    def print_board(self):
        for i in range(0, 9, 3):
            row = [str(x) if x != 0 else ' ' for x in self.board[i:i+3]]
            print(' | '.join(row))
            if i < 6:
                print('---------')

    def is_draw(self):
        return all(position != 0 for position in self.board) and not self.is_winner('X') and not self.is_winner('O') and self.current_player == 'O'

def main():
    # Create and train the Q-learning model
    q_learning = TicTacToeQLearning()
    q_learning.train(10000)

    # Save the Q-values to a file
    q_learning.save_q_values('q_values.npz')

    # Play against the trained model
    game = TicTacToe()
    done = False

    while not done:
        state = game.get_state()
        print('state   ',state)
        action = q_learning.get_action(state)
        print(('action  ',action))
        if action is None:
            print("No available actions. It's a draw!")
            done = True
            break

        game.make_move(action)
        game.print_board()

        if game.is_winner('X'):
            print("You won!")
            done = True
            break

        if game.is_draw():
            print("It's a draw!")
            done = True
            break

        position = int(input("Enter your move (0-8): "))
        game.make_move(position)
        game.print_board()

        if game.is_winner('O'):
            print("You lost!")
            done = True
            break

        if game.is_draw():
            print("It's a draw!")
            done = True
            break

if __name__ == '__main__':
    main()
