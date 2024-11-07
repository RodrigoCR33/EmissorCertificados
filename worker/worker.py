import pika
import json
import os
import pdfkit
from jinja2 import Template
from datetime import datetime
import time

# Configurações do RabbitMQ
rabbitmq_host = os.getenv("RABBITMQ_HOST", "rabbitmq")
rabbitmq_user = os.getenv("RABBITMQ_DEFAULT_USER", "rm93262")
rabbitmq_password = os.getenv("RABBITMQ_DEFAULT_PASS", "senha_muito_dificil")

# Carrega o template HTML
try:
    with open("template_diploma.html", "r", encoding="utf-8") as file:
        template_html = file.read()
except FileNotFoundError:
    print("Erro: O arquivo template_diploma.html não foi encontrado.")
    exit(1)

def gerar_pdf(dados, output_path):
    """
    Substitui as variáveis no template HTML, salva o HTML gerado e converte para PDF.
    """
    try:
        template = Template(template_html)
        html_content = template.render(dados)
        
        # Salva o HTML renderizado para debug ou verificação futura
        html_output_path = output_path.replace(".pdf", ".html")
        with open(html_output_path, "w", encoding="utf-8") as html_file:
            html_file.write(html_content)
        print(f"HTML salvo com sucesso: {html_output_path}")
        
        # Opções do pdfkit
        pdf_options = {
            'page-size': 'A4',
            'orientation': 'Landscape',
            'margin-top': '0mm',
            'margin-right': '0mm',
            'margin-bottom': '0mm',
            'margin-left': '0mm',
            'encoding': "UTF-8",
            'quiet': '',
            'disable-smart-shrinking': ''
        }
        
        # Gera o PDF a partir do HTML
        pdfkit.from_string(html_content, output_path, options=pdf_options)
        print(f"PDF gerado com sucesso: {output_path}")
    except Exception as e:
        print(f"Erro ao gerar o PDF: {e}")
        raise

def callback(ch, method, properties, body):
    """
    Função de callback que processa a mensagem da fila e gera o PDF.
    """
    dados = json.loads(body)
    dados["data_emissao"] = datetime.now().strftime("%d/%m/%Y")

    try:
        # Define o caminho de saída do PDF e HTML
        output_path = f"diplomas/{dados['nome']}_diploma.pdf"
        
        # Gera o PDF e salva o HTML
        gerar_pdf(dados, output_path)
        
        # Confirma o processamento da mensagem
        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        print(f"Erro ao processar mensagem: {e}")
        # Não confirma a mensagem para que possa ser reprocessada
        ch.basic_nack(delivery_tag=method.delivery_tag)

def start_worker():
    """
    Função principal que conecta ao RabbitMQ e inicia o consumo de mensagens.
    """
    credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_password)
    connection = None

    # Tenta conectar ao RabbitMQ com várias tentativas
    for attempt in range(10):
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=rabbitmq_host, credentials=credentials)
            )
            print("Conectado ao RabbitMQ com sucesso.")
            break
        except pika.exceptions.AMQPConnectionError:
            print(f"Falha na conexão com o RabbitMQ, tentativa {attempt + 1} de 10. Retentando em 5 segundos...")
            time.sleep(5)
    
    if not connection:
        print("Não foi possível conectar ao RabbitMQ após várias tentativas. Saindo.")
        return

    # Criação e configuração do canal
    channel = connection.channel()
    channel.queue_declare(queue='diploma_queue', durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='diploma_queue', on_message_callback=callback)

    print("Worker iniciado e aguardando mensagens...")
    channel.start_consuming()

if __name__ == "__main__":
    os.makedirs("diplomas", exist_ok=True)  # Cria o diretório de saída para os PDFs, se necessário
    start_worker()
