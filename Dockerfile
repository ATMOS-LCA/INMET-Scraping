FROM ubuntu:latest@sha256:6015f66923d7afbc53558d7ccffd325d43b4e249f41a6e93eef074c9505d2233

RUN apt-get update && apt-get -y install cron wget make build-essential libreadline-dev libncursesw5-dev libssl-dev libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev libffi-dev zlib1g-dev -y && rm -rf /var/lib/apt/lists/*
RUN apt update -y && apt install python3-venv -y
RUN wget https://www.python.org/ftp/python/3.13.3/Python-3.13.3.tar.xz
RUN tar -xvf Python-3.13.3.tar.xz
RUN cd /Python-3.13.3 && ./configure --enable-optimizations
RUN cd Python-3.13.3 && make altinstall
RUN /usr/bin/python3 -m venv venv
COPY cronconfig.txt /etc/cron.d/cronconfig
RUN chmod 0644 /etc/cron.d/cronconfig
RUN crontab -u root /etc/cron.d/cronconfig
RUN touch /var/log/cron.log
COPY SpiderINMET__DOCKER.py .
COPY Logger.py .
COPY requirements.txt .
RUN venv/bin/pip install -r requirements.txt

CMD cron && tail -f /var/log/cron.log