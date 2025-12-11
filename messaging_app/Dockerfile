FROM python:3.10-slim 

WORKDIR /app

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

EXPOSE 8000

# The app runs on port 8000, so we map it using: docker run -p 8000:8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]