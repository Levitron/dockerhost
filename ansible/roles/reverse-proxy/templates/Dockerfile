FROM traefik:v2.5

RUN apk add py-pip python3-dev libffi-dev openssl-dev gcc libc-dev make libxml2-dev libxslt-dev
COPY ./requirements.txt /tmp/requirements.txt
RUN pip3 install -r /tmp/requirements.txt
COPY ./update-dns.py /update-dns.py
RUN chmod 777 /update-dns.py
COPY ./config.json /config.json
