FROM python:3.12.9-bookworm

ENV MOUNT_PATH=/mount
ENV SCRIPTS_PATH=/scripts

WORKDIR /mount

RUN apt update -y && \
    apt -y install bash gcc dos2unix

COPY mount/ .

COPY scripts/ /scripts/

RUN dos2unix /scripts/*

ENV PYTHONUNBUFFERED=1

RUN python -m pip install --upgrade pip

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

RUN chmod +x /scripts/*

CMD ["/scripts/start.sh"]