import new

from paver import setuputils, tasks

class FakeModule(object):
    def __init__(self, **kw):
        for name, value in kw.items():
            setattr(self, name, value)

def patched_print(self, output):
    self.patch_captured.append(output)

class FakeExitException(Exception):
    """ Fake out tasks.Environment._exit to avoid interupting tests """

def patched_exit(self, code):
    self.exit_code = 1
    raise FakeExitException(code)


def _set_environment(patch_print=False, **kw):
    pavement = FakeModule(**kw)
    env = tasks.Environment(pavement)
    tasks.environment = env
    env._exit = new.instancemethod(patched_exit, env, tasks.Environment)
    if patch_print:
        env._print = new.instancemethod(patched_print, env, tasks.Environment)
        env.patch_captured = []
    return env

