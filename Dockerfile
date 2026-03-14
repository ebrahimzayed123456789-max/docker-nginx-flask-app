FROM python:3.11-alpine

WORKDIR /app

RUN apk add --no-cache libpq wget

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN addgroup -S appgroup && adduser -S appuser -G appgroup
USER appuser

HEALTHCHECK --interval=30s --timeout=5s \
  CMD wget -qO- http://localhost:8000/api/health || exit 1

CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:8000", "flask_app:app"]