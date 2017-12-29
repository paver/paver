'''
fabric wrapper snippets

it is still a bit tricky to run fabric task
some discovery would be great ;)

usage::

  # create fabfile of your likings
  $ cat fabfile.py
  from fabric.api import run

  def host():
      run('uname -s')

  # and pavement file
  $ cat 
  from paver.easy import *
  from paver import fab

  @task
  def fab_host():
      # import your fabfile
      fabfile = fab.import_fabfile()
      # invoke fabric task
      fab.fab('localhost', fabfile['host'])

right now, you can invoke ``paver fab_host``
'''

from fabric.main import find_fabfile, load_fabfile
from fabric.network import normalize
from fabric import state


def resolve(host):
    "write similar function for eg: resolving from aws or ssh_config"
    return (host,) + normalize(host)

def fab(host, cmd, resolve=resolve, args=(), kwargs={}):
    "call one fabric task"
    host_string, username, hostname, port = resolve(host)
    state.env.host_string = host_string
    state.env.host = hostname
    state.env.user = username
    state.env.port = port
    return cmd(*args, **kwargs)

def import_fabfile(fabfile='fabfile.py'):
    "you have to call this first to enable fabric tasks"
    state.env.fabfile = fabfile
    _, fabfile = load_fabfile(find_fabfile())
    return fabfile

