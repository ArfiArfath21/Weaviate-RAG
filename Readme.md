# Weaviate RAG
This repository contains the files requried for hosting a Weaviate DB, to create/update/delete collections and to ingest, update, delete, query data.

## Prerequisites
- Docker
- Docker-compose (Podman-compose)
- Python3
- ollama

## Working with Weviate
1. Start ollama and download a embedding model to be used with Ollama. `nomic-embed-text` is a good choice.
```bash
ollama pull nomic-embed-text
```

2. Update the model name in `.env` and export the environment variables
```bash
export $(cat .env | xargs)
```

3. Run the following command to start the local Weaviate DB instance
```bash
podman-compose up -d
```

4. Run the following command to stop the local Weaviate DB instance
```bash
podman-compose stop
```