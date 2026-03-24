FROM python:3.12-slim

WORKDIR /app

RUN apt-get update \
	&& apt-get install -y --no-install-recommends openssh-client \
	&& rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p logs && if [ ! -f server.key ]; then ssh-keygen -t rsa -b 2048 -f server.key -N "" -q; fi
RUN useradd -r -s /bin/false honeypot
RUN chown -R honeypot:honeypot logs
USER honeypot

EXPOSE 2222
CMD ["python", "honeypot.py"]