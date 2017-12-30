#!/bin/bash

docker build -f dockerfiles/Dockerfile.py35 -t paver-py35 ./ && \
docker run --rm -it paver-py35
