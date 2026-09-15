FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY server.py seed.py start.py ./
COPY static ./static
RUN mkdir -p /app/data && useradd -u 10001 app && chown -R app:app /app
USER app
EXPOSE 8000
CMD ["python", "start.py"]
