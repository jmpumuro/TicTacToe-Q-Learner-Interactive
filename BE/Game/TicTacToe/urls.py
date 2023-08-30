from django.urls import path
from .views import AgentMoveView, UserMoveView,GameBoardView,TrainAgentView,ResetGameView,DownloadModelView

urlpatterns = [
    path('train-agent/',TrainAgentView.as_view(),name='train-agent'),
    path('agent-move/', AgentMoveView.as_view(), name='agent-move'),
    path('user-move/', UserMoveView.as_view(), name='user-move'),
    path('game-board/', GameBoardView.as_view(), name='game-board'),
    path('reset-game/', ResetGameView.as_view(), name='reset-game'),
    path('download-model/', DownloadModelView.as_view(), name='download-model'),
]