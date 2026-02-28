# Kutcut Video Processor

Microserviço **worker** que processa vídeos em background: consome mensagens de uma fila RabbitMQ, baixa o vídeo do Azure Blob Storage, extrai snapshots (thumbnails) em intervalos definidos, compacta em ZIP, faz upload do ZIP de volta ao blob e publica o resultado em outra fila.

Parte do ecossistema **Kutcut** (SOAT Eleven) para processamento assíncrono de vídeos.

---

## Funcionamento

1. **Consumo da fila**  
   O worker escuta a fila `video_uploaded` (configurável). Cada mensagem contém:
   - `userId`: identificador do usuário
   - `filename`: nome do arquivo de vídeo
   - `messageId`: identificador da mensagem

2. **Download do vídeo**
   ![Estrutura de armazenamento do vídeo no blob](docs/paste_structure.png)

   O vídeo é buscado no Azure Blob Storage no caminho `{userId}/videos/{filename}`. Se não existir, é publicada mensagem de erro na fila de conclusão.

3. **Geração de snapshots**  
   Usando **PyAV** e **Pillow**:
   - Calcula a duração do vídeo
   - Extrai um frame a cada **15 segundos** (intervalo configurável no código), em um único passe de decodificação
   - Converte cada frame para JPEG (qualidade 85)

4. **Upload do ZIP**  
   Os frames são compactados em um arquivo ZIP e enviados ao blob no caminho `{userId}/thumbnails/{filename}.zip`.

5. **Resposta na fila**  
   Na fila `processamento_de_videos` (configurável) é publicada uma mensagem com:
   - **Sucesso**: `userId`, `filename`, `messageId`, `thumbnailsPath` (caminho do ZIP), `result: "success"`, `code: "S200"`
   - **Erro**: `userId`, `filename`, `messageId`, `result: "error"`, `code: "E404"` (vídeo não encontrado) ou `"E500"` (erro genérico)

---

## Stack e dependências

| Tecnologia | Uso |
|------------|-----|
| **Python** | 3.12+ |
| **Gerenciador de pacotes** | uv |
| **RabbitMQ** (aio-pika) | Filas de entrada e saída |
| **Azure Blob Storage** | Armazenamento de vídeos e ZIPs de thumbnails |
| **PyAV** (av) | Leitura de vídeo e extração de frames |
| **Pillow** | Conversão de frames para JPEG |
| **Pydantic** | Modelos e configuração |
| **Loguru** | Logs |

---

## Estrutura do projeto

Arquitetura em camadas (Domain, Application, Infrastructure) e Clean Architecture:

```
src/
├── main.py                    # Entrada: inicia worker RabbitMQ
├── containers.py              # Injeção de dependências (services, blob, publisher)
└── modules/
    ├── shared/                # Adaptadores, exceções, serviços compartilhados
    │   ├── adapters/          # BlobStorageAdapter, MessageBrokerAdapter, etc.
    │   ├── services/          # Settings, Logger, Azure Blob, PublishMessage, Video (av/Pillow)
    │   └── ...
    └── video/
        ├── controllers/       # VideoController (consome mensagens e orquestra)
        ├── entities/          # VideoEntity
        ├── models/            # VideoMessageModel (payload da fila)
        ├── services/
        │   ├── application/   # GetVideoProcessApplicationService (orquestração)
        │   └── domain/        # DownloadVideoDomainService, GenerateSnapshotsDomainService
        └── exceptions/       # VideoNotFoundException
```

- **VideoController**: consome mensagens da fila, deserializa para `VideoMessageModel` e chama o application service.
- **GetVideoProcessApplicationService**: coordena download → geração de snapshots → upload do ZIP → publicação do resultado.
- **Domain services**: regras de negócio (download do blob, extração de frames, zip e upload).

---

## Configuração

Variáveis de ambiente (ex.: `.env`):

| Variável | Descrição | Exemplo |
|----------|-----------|--------|
| `RABBITMQ_URL` | URL de conexão ao RabbitMQ | `amqp://guest:guest@localhost:5672/` |
| `ENVIRONMENT` | Ambiente (ex.: `development`) | `development` |
| `BLOB_STORAGE_CONNECTION_STRING` | Connection string da conta Azure Storage | `DefaultEndpointsProtocol=https;AccountName=...;AccountKey=...;EndpointSuffix=core.windows.net` |
| `BLOB_STORAGE_CONTAINER_NAME` | Nome do container de blobs | `hackathon` |

No código (Settings):

- `rabbitmq_queue_video_process`: fila consumida (default: `video_uploaded`)
- `rabbitmq_queue_video_process_completed`: fila onde o resultado é publicado (default: `processamento_de_videos`)
- `rabbitmq_prefetch_count`: prefetch da fila (default: 10)

---

## Como executar

### Pré-requisitos

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) instalado
- RabbitMQ acessível
- Conta Azure Storage (se for usar blob)

### Instalação e execução local

```bash
# Clonar e entrar no diretório
cd soat.eleven.kutcut.videoprocessor

# Instalar dependências
uv sync

# Desenvolvimento (sobe o worker)
uv run task run_dev
```

O worker fica aguardando mensagens na fila configurada. Para processar um vídeo, publique uma mensagem nessa fila no formato:

```json
{
  "userId": "id-do-usuario",
  "filename": "meu-video.mp4",
  "messageId": "id-da-mensagem"
}
```

O vídeo deve existir no blob em `{userId}/videos/{filename}`.

### Docker

Build e execução:

```bash
docker build -t kutcut-videoprocessor .
docker run --env-file .env kutcut-videoprocessor
```

A imagem é multi-stage (builder + runtime), usa usuário não-root e executa `python src/main.py`.

---

## Testes e qualidade

```bash
# Testes com cobertura
uv run task test

# Linting (ruff, black, isort)
uv run task lint

# Testes em modo watch
uv run task test_watch
```

---

## Licença

Uso interno / acadêmico (FIAP SOAT Eleven).
