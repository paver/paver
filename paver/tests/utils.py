from paver import setuputils, defaults, tasks

class FakeModule(object):
    def __init__(self, **kw):
        for name, value in kw.items():
            setattr(self, name, value)

def _set_environment(**kw):
    pavement = FakeModule(**kw)
    tasks.environment = tasks.Environment(pavement)
    return tasks.environment

