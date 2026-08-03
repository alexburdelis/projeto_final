import json
import time
import pika
import sys
import os

# Adiciona a raiz do projeto no path para conseguir importar o banco
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import get_rabbitmq_connection, FILA_PROCESSAMENTO
from database.connection import SessionLocal
from database.models import TarefaProcessamento, StatusTarefa

def callback(ch, method, properties, body):
    dados = json.loads(body.decode("utf-8"))
    tarefa_id = dados.get("tarefa_id")
    
    print(f"\n[*] Recebi a Tarefa {tarefa_id}. Iniciando conversão...")
    
    db = SessionLocal()
    try:
        # 1. Busca a tarefa no banco e muda pra PROCESSANDO
        tarefa = db.query(TarefaProcessamento).filter(TarefaProcessamento.id == tarefa_id).first()
        if tarefa:
            tarefa.status = StatusTarefa.PROCESSANDO
            db.commit()
            
            # 2. Simula o processamento pesado do vídeo
            time.sleep(5) 
            
            # 3. Finaliza a tarefa
            tarefa.status = StatusTarefa.CONCLUIDO
            db.commit()
            print(f"[v] Tarefa {tarefa_id} CONCLUÍDA e salva no banco!")
            
            # NOTA 100: Avisa o RabbitMQ que deu tudo certo. Pode apagar da fila.
            ch.basic_ack(delivery_tag=method.delivery_tag)
        else:
            print(f"[x] Tarefa {tarefa_id} não encontrada no banco!")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            
    except Exception as e:
        print(f"[ERRO] Falha ao processar: {e}")
        db.rollback()
        # Se der erro no Python, devolve a mensagem pra fila tentar de novo depois
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
    finally:
        db.close()

def iniciar_worker():
    conexao = get_rabbitmq_connection()
    canal = conexao.channel()
    canal.queue_declare(queue=FILA_PROCESSAMENTO, durable=True)
    
    # auto_ack=False exige confirmação manual (basic_ack)
    canal.basic_consume(queue=FILA_PROCESSAMENTO, on_message_callback=callback, auto_ack=False)
    
    print(' [*] Worker StreamFlix aguardando vídeos. CTRL+C para sair')
    canal.start_consuming()

if __name__ == '__main__':
    iniciar_worker()