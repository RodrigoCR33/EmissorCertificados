import pika
import json
import os
import pdfkit
from jinja2 import Template
from datetime import datetime

# Conexão com o RabbitMQ
rabbitmq_host = os.getenv("RABBITMQ_HOST", "rabbitmq")
rabbitmq_user = os.getenv("RABBITMQ_DEFAULT_USER", "rm93262")
rabbitmq_password = os.getenv("RABBITMQ_DEFAULT_PASS", "senha_muito_dificil")

# Carrega o template HTML
with open("template_diploma.html", "r", encoding="utf-8") as file:
    template_html = file.read()

def gerar_pdf(dados, output_path):
    # Substitui as variáveis no template HTML
    template = Template(template_html)
    html_content = template.render(dados)

    # Configuração para o pdfkit
    pdf_options = {
        'page-size': 'A4',
        'orientation': 'Landscape',
        'margin-top': '0mm',
        'margin-right': '0mm',
        'margin-bottom': '0mm',
        'margin-left': '0mm',
        'encoding': "UTF-8",
    }

    # Gera o PDF a partir do HTML
    pdfkit.from_string(html_content, output_path, options=pdf_options)

def callback(ch, method, properties, body):
    dados = json.loads(body)

    # Adiciona a data de emissão ao dados
    dados["data_emissao"] = datetime.now().strftime("%d/%m/%Y")

    try:
        # Define o caminho de saída do PDF
        output_path = f"diplomas/{dados['nome']}_diploma.pdf"
        
        # Gera o PDF
        gerar_pdf(dados, output_path)
        
        print(f"PDF gerado com sucesso: {output_path}")
        
        # Confirma que a mensagem foi processada com sucesso
        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        print("Erro ao gerar PDF:", e)
        # Em caso de erro, não confirma a mensagem para que possa ser reprocessada
        ch.basic_nack(delivery_tag=method.delivery_tag)

def start_worker():
    credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_password)
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host, credentials=credentials))
    channel = connection.channel()
    channel.queue_declare(queue='diploma_queue', durable=True)
    channel.basic_qos(prefetch_count=1)

    # Consome as mensagens
    channel.basic_consume(queue='diploma_queue', on_message_callback=callback)

    print("Worker iniciado. Aguardando mensagens...")
    channel.start_consuming()

if __name__ == "__main__":
    os.makedirs("diplomas", exist_ok=True)  # Cria o diretório de saída se não existir
    start_worker()
