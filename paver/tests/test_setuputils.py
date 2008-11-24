from pprint import pprint
from distutils.core import Command

from paver.setuputils import Distribution, install_distutils_tasks, \
                            DistutilsTaskFinder
from paver import runtime, tasks
from paver.runtime import *

from paver.tests.utils import reset_runtime

class _sdist(Command):
    called = False
    foo_set = False
    fin = None
    user_options = [("foo", "f", "Foo")]
    
    def initialize_options(self):
        self.foo = False
        
    def finalize_options(self):
        pass
    
    def run(self):
        _sdist.called = True
        _sdist.foo_set = self.foo
        _sdist.fin = self.get_finalized_command("sdist")
    
    @classmethod
    def reset(cls):
        cls.called = False
        cls.foo_set = False
        cls.fin = None

class FakeModule(object):
    def __init__(self, **kw):
        for name, value in kw.items():
            setattr(self, name, value)
            
def _set_environment(**kw):
    pavement = FakeModule(**kw)
    tasks.environment = tasks.Environment(pavement)
    return tasks.environment


#----------------------------------------------------------------------
def tst_override_distutils_command():
    @tasks.task
    def sdist():
        pass
    
    env = _set_environment(sdist=sdist)
    
    install_distutils_tasks()
    
    d = env.distribution
    d.cmdclass['sdist'] = _sdist
    tasks._process_commands(['sdist', 'paver.tests.test_setuputils.sdist', '-f'])
    assert sdist.called
    assert _sdist.called
    assert _sdist.foo_set
    assert isinstance(_sdist.fin, _sdist)

def test_distutils_task_finder():
    dist = Distribution()
    dutf = DistutilsTaskFinder(dist)
    task = dutf.get_task('distutils.command.install')
    assert task
    task = dutf.get_task('install')
    assert task
    task = dutf.get_task('foo')
    assert task is None

def test_task_with_distutils_dep():
    reset_runtime()
    _sdist.reset()
    
    @task
    @needs("paver.tests.test_setuputils.sdist")
    def sdist():
        assert _sdist.called
        sdist.called = True
    sdist.called = False
    
    d = Distribution()
    d.cmdclass['sdist'] = _sdist
    d.cmdclass['sdist']._handle_dependencies()
    
    assert d.cmdclass['paver.tests.test_setuputils.sdist'] == _sdist
    d.script_args = ['sdist', "-f"]
    assert d.parse_command_line()
    assert d.commands == ['sdist']
    d.run_commands()
    assert sdist.called
    assert _sdist.called
    cmd = d.get_command_obj('sdist')
    print "Cmd is: %s" % cmd
    assert cmd.foo
    d.dump_option_dicts()
    assert _sdist.foo_set
    
#----------------------------------------------------------------------
def test_command_line_options_for_tasks():
    reset_runtime()
    
    @task
    @cmdopts([('foo=', 'f', 'Foo!')])
    def mytask():
        mytask.called = True
        foo = options['mytask'].foo 
        assert foo == 'bar', "Foo was: " + foo
    mytask.called = False
    
    d = Distribution()
    d.script_args = ['mytask', '-f', "bar"]
    d.parse_command_line()
    d.run_commands()
    assert mytask.called
    
def test_setting_options_via_command_line():
    reset_runtime()
    d = Distribution()
    d.script_args = ['this.is.cool=1']
    d.parse_command_line()
    d.run_commands()
    assert options.this['is'].cool == '1'

def test_call_task_with_options():
    reset_runtime()
    @task
    def mytask():
        assert options.foo == 1
        mytask.called = True
    mytask.called = False
    d = Distribution()
    call_task('mytask', Bunch(foo=1))
    assert mytask.called
    