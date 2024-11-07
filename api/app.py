from flask import Flask, request, jsonify
from db_utils import inserir_dados_diploma
from datetime import datetime
import pika
import json
import os

app = Flask(__name__)

# Configuração de conexão com o RabbitMQ
rabbitmq_host = os.getenv("RABBITMQ_HOST", "rabbitmq")
rabbitmq_user = os.getenv("RABBITMQ_DEFAULT_USER", "rm93262")
rabbitmq_password = os.getenv("RABBITMQ_DEFAULT_PASS", "senha_muito_dificil")

def enviar_para_fila(dados):
    # Configuração de conexão com o RabbitMQ
    credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_password)
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host, credentials=credentials))
    channel = connection.channel()

    # Declara a fila se ela ainda não existir
    channel.queue_declare(queue='diploma_queue', durable=True)

    # Publica a mensagem na fila
    channel.basic_publish(
        exchange='',
        routing_key='diploma_queue',
        body=json.dumps(dados),
        properties=pika.BasicProperties(
            delivery_mode=2,  # Faz a mensagem persistente
        )
    )
    connection.close()

@app.route('/criar_diploma', methods=['POST'])
def criar_diploma():
    data = request.json
    
    # Validação básica dos dados recebidos
    required_fields = [
        "nome", "nacionalidade", "estado", "data_nascimento",
        "documento", "data_conclusao", "curso", "carga_horaria",
        "nome_assinatura", "cargo"
    ]
    
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Campo {field} é obrigatório"}), 400

    # Adiciona a data de emissão como a data atual
    data["data_emissao"] = datetime.now().strftime("%Y-%m-%d")

    # Salva os dados no banco de dados
    try:
        inserir_dados_diploma(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    # Envia os dados para a fila do RabbitMQ
    try:
        enviar_para_fila(data)
        return jsonify({"message": "Pedido de criação de diploma enviado com sucesso"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
