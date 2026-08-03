import json
import pika
from .config import get_rabbitmq_connection, FILA_PROCESSAMENTO

def enviar_para_fila(tarefa_id: int, formato_destino: str):
    conexao = get_rabbitmq_connection()
    canal = conexao.channel()
    
    canal.queue_declare(queue=FILA_PROCESSAMENTO, durable=True)
    
    mensagem = {"tarefa_id": tarefa_id, "formato_destino": formato_destino}
    
    canal.basic_publish(
        exchange='',
        routing_key=FILA_PROCESSAMENTO,
        body=json.dumps(mensagem),
        properties=pika.BasicProperties(
            delivery_mode=2,  # NOTA 100: Mensagem persistente (não some se o RabbitMQ cair)
        )
    )
    conexao.close()