FROM debian:jessie
MAINTAINER Lukas Linhart "bugs@almad.net"


RUN apt-get update
RUN apt-get -y -q install python-virtualenv python-pip python-sphinx python-markupsafe python-nose python-docutils python-pygments python-jinja2 python-wheel python-gdbm python-tk python-dev

# Debian bug workaround
RUN ln -s /usr/lib/python2.7/plat-*/_sysconfigdata_nd.py /usr/lib/python2.7/

ADD paver/ /paver-base/paver/
ADD tests_integration/ /paver-base/tests_integration/
ADD distutils_scripts/ /paver-base/distutils_scripts/
ADD *requirements.txt /paver-base/
ADD bootstrap.py pavement.py setup.py paver-minilib.zip /paver-base/

RUN virtualenv /paver-venv
RUN /paver-venv/bin/pip install -r /paver-base/release-requirements.txt
RUN /paver-venv/bin/pip install -r /paver-base/test-requirements.txt

RUN ls /paver-base

WORKDIR /paver-base

CMD ["/paver-venv/bin/python", "setup.py", "test"]

