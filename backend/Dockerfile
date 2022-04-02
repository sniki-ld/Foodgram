FROM python:3.7-slim

WORKDIR /app

COPY foodgram/requirements.txt .

RUN pip3 install -r requirements.txt --trusted-host pypi.org --trusted-host files.pythonhosted.org --no-cache-dir


COPY foodgram/ .

CMD ["gunicorn", "foodgram.wsgi: application", "--bind", "0:8000"]