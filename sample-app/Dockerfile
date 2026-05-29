FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY sample_app.py .
EXPOSE 5050
CMD ["python", "sample_app.py"]
