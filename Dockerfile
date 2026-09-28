FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY bot.py .

CMD ["gunicorn", "--bind", "0.0.0.0:10000", "bot:app"]
