FROM node:20-alpine AS frontend

WORKDIR /app/frontend
COPY fullstack/frontend/package.json fullstack/frontend/package-lock.json ./
RUN npm ci
COPY fullstack/frontend/ ./
RUN npm run build

FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=7860

# Buat non-root user (id 1000) sesuai standar Hugging Face Spaces
RUN useradd -m -u 1000 user

WORKDIR /app

COPY fullstack/backend/requirements.txt ./fullstack/backend/requirements.txt
RUN pip install --no-cache-dir -r ./fullstack/backend/requirements.txt

COPY src ./src
COPY sql ./sql
COPY data ./data
COPY fullstack/backend ./fullstack/backend
COPY --from=frontend /app/frontend/dist ./fullstack/frontend/dist

# Beri permission ke non-root user
RUN chown -R user:user /app
USER user

WORKDIR /app/fullstack/backend

EXPOSE 7860

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-7860}"]
