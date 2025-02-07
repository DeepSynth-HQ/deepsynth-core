FROM python:3.11-slim 

ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH /agent

WORKDIR /agent

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD ["/bin/bash", "entrypoint.sh"]