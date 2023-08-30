from rest_framework import serializers

class TicTacToeSerializer(serializers.Serializer):
    board = serializers.ListField(child=serializers.IntegerField())
