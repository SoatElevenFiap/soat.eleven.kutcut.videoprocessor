# syntax=docker/dockerfile:1
# ------------------------------
# Stage 1: builder (deps + app install)
# ------------------------------
FROM python:3.12-slim-bookworm AS builder

# Evita criação de arquivos .pyc e garante output imediato de logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instala uv a partir da imagem oficial (fixe a tag para build reproduzível, ex.: :0.5)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Camada de dependências: altera menos que o código, melhora cache
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    UV_LINK_MODE=copy \
    uv sync --frozen --no-dev --no-install-project

# Código da aplicação
COPY src ./src
COPY containers.py ./

# Instala o projeto no ambiente virtual
RUN --mount=type=cache,target=/root/.cache/uv \
    UV_LINK_MODE=copy \
    uv sync --frozen --no-dev

# ------------------------------
# Stage 2: runtime (imagem final mínima)
# ------------------------------
FROM python:3.12-slim-bookworm AS runtime

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/app/.venv/bin:$PATH"

# Usuário não-root (boas práticas de segurança / SonarQube)
RUN groupadd --gid 1000 app \
    && useradd --uid 1000 --gid app --shell /bin/bash --create-home app

WORKDIR /app

# Copia apenas o venv e o código do builder (sem uv nem ferramentas de build)
COPY --from=builder --chown=app:app /app/.venv /app/.venv
COPY --from=builder --chown=app:app /app/src /app/src
COPY --from=builder --chown=app:app /app/containers.py /app/containers.py

USER app

# Exec form (evita shell, recomendado)
CMD ["python", "src/main.py"]
