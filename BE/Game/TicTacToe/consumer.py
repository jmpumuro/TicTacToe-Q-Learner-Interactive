import pika
from game_manager import GameManager

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.queue_declare(queue='moves')

game_manager = GameManager()

def callback(ch, method, properties, body):
    print("Received board state:", body)
    # Here, you can perform any additional processing based on the received board state
    # For example, you can update the UI or make decisions based on the agent's move
    
    # If it's the user's turn, you can prompt for their move and call `send_user_move(position)`
    # If it's the agent's turn, you can call `send_agent_move()` to make the agent's move
    
channel.basic_consume(queue='moves', on_message_callback=callback, auto_ack=True)

print('Waiting for moves...')
channel.start_consuming()
