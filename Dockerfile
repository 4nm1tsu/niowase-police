FROM python:3.11-slim

RUN pip install uv

WORKDIR /app

# 依存レイヤー分離
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project

COPY app ./app

RUN uv sync --frozen

WORKDIR /app/app

CMD ["uv", "run", "python", "main.py"]
