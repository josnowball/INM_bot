FROM python:3.12-slim

WORKDIR /app

COPY backend/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY bot/ ./bot/
COPY backend/app/ ./app/

CMD ["python", "bot/bot.py"]
