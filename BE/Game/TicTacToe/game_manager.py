from .game import TicTacToe
from .agent import TicTacToeQLearning

class GameManager:
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super(GameManager, cls).__new__(cls)
            cls._instance.board = TicTacToe()
            cls._instance.q_learning = TicTacToeQLearning()
            cls._instance.is_agent_turn = True
        return cls._instance

    def get_board_state(self):
        return self.board.get_state()
    def reset_game(self):
        return self.board.reset_board()
    def get_game_status(self):
        return self.board.get_game_status()
    def make_user_move(self, board, position):
            board.make_move(position)
            return position

    def make_agent_move(self, board, q_learning):
            try:
                # Load the Q-values from a file
                q_learning.load_model('../agentmodel.h5')

                # Get the current game state
                state = board.get_state()
                # Get the agent's move
                action = q_learning.get_action(state)
                # Make the agent's move on the game board
                board.make_move(action)
                return action
            except Exception as e:
                return 'agent needs to be trained'
