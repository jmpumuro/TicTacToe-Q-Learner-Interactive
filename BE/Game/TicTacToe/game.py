class TicTacToe:
    def __init__(self, starting_player='X'):
        self.board = [0] * 9  # 3x3 tic-tac-toe board
        self.current_player = starting_player

    def get_state(self):
        return self.board

    def reset_board(self):
        self.board = [0] * 9
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
            row = [str(x) if x != 0 else ' ' for x in self.board[i:i + 3]]
            print(' | '.join(row))
            if i < 6:
                print('---------')

    def is_draw(self):
        empty_positions = sum(1 for position in self.board if position == 0)
        return (empty_positions == 1 or empty_positions == 0) and not self.is_winner('X') and not self.is_winner('O')

    def get_game_status(self):
        if self.is_winner('X'):
            return 'X Wins'
        elif self.is_winner('O'):
            return 'O Wins'
        elif self.is_draw():
            return 'Draw'
        else:
            return 'In Progress'