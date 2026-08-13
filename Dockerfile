# ---- Frontend build stage ----
FROM node:20-alpine AS frontend

WORKDIR /app/client

COPY client/package.json client/package-lock.json ./
RUN npm ci

COPY client/ ./
RUN npm run build

# ---- Backend stage ----
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

COPY --from=frontend /app/client/dist ./static/dist

EXPOSE 8000

# Seed initial users (idempotent; only creates roles not already present),
# then start the app. Requires SEED_* vars in .env for users to be created.
CMD ["sh", "-c", "python seed.py && exec uvicorn server:app --host 0.0.0.0 --port 8000 --workers 4"]

