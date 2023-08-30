from game import TicTacToe
from agent import TicTacToeQLearning


def main():
    # Create and train the Q-learning model
    q_learning = TicTacToeQLearning()
    q_learning.train(100)

    # Save the Q-values to a file
    q_learning.save_model('model')
    q_learning.load_model('model.h5')
    # Play against the trained model
    game = TicTacToe()
    done = False

    while not done:
        state = game.get_state()
        print('state   ', state)
        action = q_learning.get_action(state)
        print(('action  ', action))
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
