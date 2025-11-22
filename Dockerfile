FROM python:3.12-slim-bullseye
COPY ./requirements.txt ./requirements.txt
RUN  pip install --no-cache-dir --upgrade -r ./requirements.txt

COPY . .
EXPOSE 80
CMD  ["python", "./app.py"]