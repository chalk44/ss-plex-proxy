FROM alpine:latest
RUN apk add --no-cache python3 cmd:pip3
COPY . /app
WORKDIR /app
RUN pip3 install -r requirements.txt
RUN chmod 644 ss-plex-proxy.py
ENTRYPOINT ["python3"]
CMD ["ss-plex-proxy.py"]
