import pika
import requests
from .game_manager import GameManager

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.queue_declare(queue='moves')

game_manager = GameManager()

# Update the URL to match your API endpoint
USER_MOVE_URL = 'http://localhost:8000/user_move/'
AGENT_MOVE_URL = 'http://localhost:8000/agent_move/'

def send_agent_move():
    response = requests.get(AGENT_MOVE_URL)
    if response.status_code == 200:
        board_state = response.json().get('state')
        channel.basic_publish(exchange='', routing_key='moves', body=board_state)

def send_user_move(position):
    data = {'position': position}
    response = requests.post(USER_MOVE_URL, data=data)
    if response.status_code == 200:
        board_state = response.json().get('state')
        channel.basic_publish(exchange='', routing_key='moves', body=board_state)

channel.basic_publish(exchange='', routing_key='moves', body='Game Started')

connection.close()
