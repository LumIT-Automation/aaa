FROM docker.io/amd64/debian:bullseye
LABEL AUTOMATION_CONTAINER_IMAGE="api-sso"
EXPOSE 80/tcp

ADD PACKAGE /
ADD bootstrap.sh /

RUN ["/bin/bash", "/bootstrap.sh"]
