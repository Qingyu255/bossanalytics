FROM python:3.9-slim-bookworm

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ["analytics.py", "api.py", "./"]

RUN mkdir ./data
COPY data/merged_file.xlsx ./data

EXPOSE 8080

# CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8080"]

CMD ["python", "api.py"]