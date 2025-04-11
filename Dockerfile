FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1
    
WORKDIR /app

#RUN apt update
#RUN apt-get install -f vim -y

RUN useradd -m -s /bin/bash httpd
RUN usermod -aG root httpd

# add required Python modules
COPY ./rest_api/requirements.txt /app/
RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY webtrit_common /app/webtrit_common/
COPY rest_api /app/rest_api/
RUN chmod 755 /app/rest_api/start-web-server.sh

USER httpd

# the port uvicorn will be listening in the container
ARG API_PORT
ENV API_PORT=${API_PORT:-8080}

ARG BASE_PATH
ENV BASE_PATH=${BASE_PATH:-"/"}

ENV PYTHONPATH=/app

EXPOSE $API_PORT

CMD ["/app/start-web-server.sh"]
#CMD ["tail", "-f", "/dev/null"]
