import psycopg2
import os
from datetime import datetime

def inserir_dados_diploma(dados):
    # Conexão com o banco de dados usando variáveis de ambiente
    conn = psycopg2.connect(
        dbname=os.getenv("POSTGRES_DB", "certificates_db"),
        user=os.getenv("POSTGRES_USER", "rm93262"),
        password=os.getenv("POSTGRES_PASSWORD", "senha_muito_dificil"),
        host="db",  # Nome do serviço do banco de dados no Docker Compose
        port="5432"
    )
    cursor = conn.cursor()

    # Query de inserção
    insert_query = """
        INSERT INTO dados_diploma (
            nome,
            nacionalidade,
            estado,
            data_nascimento,
            documento,
            data_conclusao,
            curso,
            carga_horaria,
            data_emissao,
            nome_assinatura,
            cargo
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    try:
        # Executa a query com data_emissao usando a data atual
        cursor.execute(insert_query, (
            dados["nome"],
            dados["nacionalidade"],
            dados["estado"],
            dados["data_nascimento"],
            dados["documento"],
            dados["data_conclusao"],
            dados["curso"],
            dados["carga_horaria"],
            dados["data_emissao"],
            dados["nome_assinatura"],
            dados["cargo"]
        ))
        
        # Confirma a transação
        conn.commit()
        print("Dados inseridos com sucesso!")

    except Exception as e:
        print("Erro ao inserir dados:", e)
        conn.rollback()
        raise e

    finally:
        # Fecha a conexão
        cursor.close()
        conn.close()
