from rest_framework.views import APIView
from rest_framework.response import Response
from .game_manager import GameManager
from rest_framework import  status
import threading
import json
import os
from django.conf import settings
from django.http import HttpResponse



class GameBoardMixin:
    game_manager = GameManager()

    def get_game_manager(self):
        return self.game_manager

class GameBoardView(GameBoardMixin, APIView):
    def get(self, request):
        game_manager = self.get_game_manager()
        board_state = game_manager.get_board_state()
        game_status = game_manager.get_game_status()
        response_data = {
            'board_state': board_state,
            'game_status': game_status
        }
        return Response(response_data, status=status.HTTP_200_OK)

class AgentMoveView(GameBoardMixin, APIView):
    def get(self, request):
        game_manager = self.get_game_manager()
        agent_move = game_manager.make_agent_move(game_manager.board,game_manager.q_learning)
        if agent_move == 'agent needs to be trained':
            return Response({'agent_move': agent_move}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'agent_move': agent_move}, status=status.HTTP_200_OK)

    def post(self, request):
        game_manager = self.get_game_manager()
        game_manager.make_agent_move(game_manager.board,game_manager.q_learning)
        board_state = game_manager.get_board_state()
        return Response(board_state, status=status.HTTP_200_OK)

class UserMoveView(GameBoardMixin, APIView):
    def post(self, request):
        position = request.data.get('position')
        if position is None:
            return Response({'error': 'Position not provided'}, status=status.HTTP_400_BAD_REQUEST)

        game_manager = self.get_game_manager()
        user_move = game_manager.make_user_move(game_manager.board, position)
        return Response({'user_move': user_move}, status=status.HTTP_200_OK)
class ResetGameView(GameBoardMixin, APIView):
    def post(self, request):
        game_manager = self.get_game_manager()
        game_manager.reset_game()
        return Response({'message': 'Game board has been reset.'}, status=status.HTTP_200_OK)
# Define the TrainingState enum
class TrainingState:
    NOT_STARTED = 'not_started'
    TRAINING = 'training'
    FAILED = 'failed'
    COMPLETE = 'complete'


class TrainAgentView(GameBoardMixin, APIView):
    def __init__(self):
        super().__init__()
        self.training_state = TrainingState.NOT_STARTED
        self.stop_training = threading.Event()
        self.training_state_lock = threading.Lock()
        self.training_thread = None

    def get_training_state(self):
        with self.training_state_lock:
            return self.training_state

    def set_training_state(self, state):
        with self.training_state_lock:
            self.training_state = state

    def start_training_thread(self, episodes,epsilon,gamma):
        try:
            game_manager = self.get_game_manager()
            q_learning = game_manager.q_learning  # board's Q-learning agent

            self.set_training_state(TrainingState.TRAINING)
            # Parse episodes from JSON
            if isinstance(episodes, str):
                episodes = json.loads(episodes)
            if isinstance(epsilon, str):
                epsilon = json.loads(epsilon)
            if isinstance(gamma, str):
                gamma = json.loads(gamma)

            # Train the agent
            q_learning.train(episodes,epsilon,gamma)

            # Save the trained Q-values
            q_learning.save_model('../agentmodel')

            self.set_training_state(TrainingState.COMPLETE)
        except json.JSONDecodeError as e:
            print(f"JSON decoding error: {e}")
            self.set_training_state(TrainingState.FAILED)
            self.stop_training.set()
        except Exception as e:
            # Log the error for debugging
            print(f"Training failed with error: {e}")
            self.set_training_state(TrainingState.FAILED)
            self.stop_training.set()

    def post(self, request):
        episodes = request.data.get('episodes')
        epsilon = request.data.get('epsilon')
        gamma = request.data.get('gamma')
        if episodes is None:
            return Response({'error': 'Number of episodes not provided'}, status=status.HTTP_400_BAD_REQUEST)

        self.training_thread = threading.Thread(target=self.start_training_thread, args=(episodes,epsilon,gamma,))
        self.training_thread.start()
        self.training_thread.join()

        training_state = self.get_training_state()
        response_str = f"{training_state}"
        '''def event_stream():
            while thread.is_alive():
                training_state = self.get_training_state()

                yield f"STATUS: {training_state}, TIME: {elapsed_time:.2f} seconds\n\n"
                time.sleep(1)

            training_state = self.get_training_state()
            yield f"STATUS: {training_state}, TIME: {elapsed_time:.2f} seconds\n\n"
            return StreamingHttpResponse(event_stream(), content_type='text/event-stream')'''

        return Response(response_str,status=status.HTTP_200_OK)

class DownloadModelView(APIView):
    def get(self, request):
        # Define the path to the saved model
        model_path = '/Users/joempumuro/TicTacToe/BE/Game/TicTacToe/model.keras'  # Update the path accordingly

        # Check if the model file exists
        if os.path.exists(model_path):
            # Open the model file for reading
            file_pointer = open(model_path, "rb")
            response = HttpResponse(file_pointer, content_type='application/octet-stream')
            response['Content-Disposition'] = f'attachment; filename=model.keras'

            return response
        else:
            return Response({'error': 'Model file not found'}, status=status.HTTP_404_NOT_FOUND)