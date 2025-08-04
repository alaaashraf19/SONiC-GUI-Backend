FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org --no-cache-dir -r requirements.txt

#RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

ENV MONGO_DB=yourdbname
ENV MONGO_URI=mongodb://your-host:your-port


CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
