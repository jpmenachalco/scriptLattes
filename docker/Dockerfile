FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# baixaLattes.py usa os.path.abspath("chromedriver") esperando o binário em /app/
RUN ln -s /usr/bin/chromedriver /app/chromedriver

COPY . .

ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["python3", "scriptLattes.py"]
