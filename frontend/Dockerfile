FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . ./frontend
ENV PYTHONPATH=/app

EXPOSE 8501

CMD ["streamlit", "run", "frontend/streamlit_app/Home.py", "--server.port=8501", "--server.address=0.0.0.0"]
