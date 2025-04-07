FROM python:3.13

WORKDIR /service
COPY . /service
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "main.py"]
