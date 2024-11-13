# Emissor de Certificados

Este projeto é um sistema desenvolvido para emissão de certificados digitais. Ele utiliza uma API construída em Flask para receber dados, um worker para processar as solicitações e gerar certificados em formato PDF, e RabbitMQ para gerenciar a fila de processamento. Todo o projeto é containerizado com Docker, permitindo configuração e execução simplificadas.

## Estrutura do Projeto

### 1. API
- **Local:** `api/app.py`
- **Porta:** `8000`
- **Endpoint Disponível:**
  - **POST /criar_diploma:** Recebe os dados do certificado e envia para a fila.

### 2. Worker
- **Local:** `worker/worker.py`
- **Diretório de Saída:** `diplomas/`

### 3. RabbitMQ
- **Porta Padrão:** `5672`
- **Painel de Administração:** [http://localhost:15672](http://localhost:15672)
- **Credenciais:**
  - Usuário: `rm93262`
  - Senha: `senha_muito_dificil`

### 4. PostgreSQL
- **Porta Padrão:** `5432`
- **Banco de Dados:** `certificates_db`

---

## Configuração e Execução

### 1. Clone o Repositório
```bash
git clone <link-do-repositorio>
cd <nome-do-repositorio>
```

### 2. Inicie o Projeto com Docker Compose
```bash
docker-compose up --build
```

### 3. Verifique os Logs
Certifique-se de que todos os serviços (API, worker, RabbitMQ, banco de dados) foram iniciados corretamente:
```bash
docker-compose logs
```

### 4. Envie uma Requisição para a API
Utilize `curl` ou o Postman para enviar uma requisição `POST` ao endpoint `/criar_diploma`:
```bash
curl -X POST http://localhost:8000/criar_diploma ^
-H "Content-Type: application/json" ^
-d "{\"nome\": \"João Silva\", \"nacionalidade\": \"Brasileiro\", \"estado\": \"SP\", \"data_nascimento\": \"1990-05-10\", \"documento\": \"123456789\", \"data_conclusao\": \"2023-08-01\", \"curso\": \"Engenharia de Software\", \"carga_horaria\": 3600, \"nome_assinatura\": \"Maria Oliveira\", \"cargo\": \"Diretora Acadêmica\"}"
```

## Certificados Gerados

Após o processamento, os arquivos `.html` e `.pdf` dos certificados serão salvos no diretório `diplomas/`.