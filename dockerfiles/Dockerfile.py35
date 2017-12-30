FROM python:3.5
MAINTAINER Lukas Linhart "bugs@almad.net"


ADD paver/ /paver-base/paver/
ADD tests_integration/ /paver-base/tests_integration/
ADD distutils_scripts/ /paver-base/distutils_scripts/
ADD *requirements.txt /paver-base/
ADD bootstrap.py pavement.py setup.py paver-minilib.zip /paver-base/

RUN pyvenv /paver-venv
RUN /paver-venv/bin/pip install -r /paver-base/release-requirements.txt
RUN /paver-venv/bin/pip install -r /paver-base/test-requirements.txt

RUN ls /paver-base

WORKDIR /paver-base

CMD ["/paver-venv/bin/python", "setup.py", "test"]

