from distutils.core import Command

from paver.setuputils import install_distutils_tasks, \
                            DistutilsTaskFinder, _get_distribution, \
                            DistutilsTask
from paver import tasks, options
from paver.tests.utils import _set_environment

class _sdist(Command):
    called = False
    foo_set = False
    fin = None
    user_options = [("foo", "f", "Foo"), ("no-foo", None, "No Foo")]
    boolean_options = ['foo']
    negative_opt = {'no-foo' : 'foo'}
    
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


class _sdist_with_default_foo(_sdist):
    def initialize_options(self):
        self.foo = True

#----------------------------------------------------------------------
def test_override_distutils_command():
    @tasks.task
    def sdist():
        pass
    
    env = _set_environment(sdist=sdist)
    env.options = options.Bunch(setup=options.Bunch())
    
    install_distutils_tasks()
    d = _get_distribution()
    
    d.cmdclass['sdist'] = _sdist
    tasks._process_commands(['sdist', 'paver.tests.test_setuputils.sdist', '-f'])
    assert sdist.called
    assert _sdist.called
    assert _sdist.foo_set
    assert isinstance(_sdist.fin, _sdist)

def test_distutils_task_finder():
    env = _set_environment()
    env.options = options.Bunch(setup=options.Bunch())
    dist = _get_distribution()
    dutf = DistutilsTaskFinder()
    task = dutf.get_task('distutils.command.install')
    assert task
    task = dutf.get_task('install')
    assert task
    task = dutf.get_task('foo')
    assert task is None

def test_task_with_distutils_dep():
    _sdist.reset()
    
    @tasks.task
    @tasks.needs("paver.tests.test_setuputils.sdist")
    def sdist():
        assert _sdist.called
        
    env = _set_environment(sdist=sdist)
    env.options = options.Bunch(setup=options.Bunch())
    install_distutils_tasks()
    d = _get_distribution()
    d.cmdclass['sdist'] = _sdist
    
    task_obj = env.get_task('sdist')
    assert task_obj == sdist
    needs_obj = env.get_task(task_obj.needs[0])
    assert isinstance(needs_obj, DistutilsTask)
    assert needs_obj.command_class == _sdist
    
    tasks._process_commands(['sdist', "-f"])
    assert sdist.called
    assert _sdist.called
    cmd = d.get_command_obj('sdist')
    print "Cmd is: %s" % cmd
    assert cmd.foo
    assert _sdist.foo_set
    
def test_distutils_tasks_should_not_get_extra_options():
    _sdist.reset()
    env = _set_environment()
    env.options = options.Bunch(setup=options.Bunch())
    install_distutils_tasks()
    d = _get_distribution()
    d.cmdclass['sdist'] = _sdist
    
    tasks._process_commands(['sdist'])
    assert _sdist.called
    assert not _sdist.foo_set
    opts = d.get_option_dict('sdist')
    assert 'foo' not in opts

def test_needs_sdist_without_options():
    """Test that a custom sdist can be used in needs() w/o options.setup"""
    _sdist.reset()

    @tasks.task
    @tasks.needs("paver.tests.test_setuputils.sdist")
    def sdist():
        assert _sdist.called

    @tasks.task
    @tasks.needs("sdist")
    def t1():
        pass

    env = _set_environment(sdist=sdist, t1=t1)
    env.options = options.Bunch()
    install_distutils_tasks()
    d = _get_distribution()
    d.cmdclass['sdist'] = _sdist

    tasks._process_commands(['t1'])
    assert sdist.called
    assert _sdist.called
    assert t1.called
    cmd = d.get_command_obj('sdist')
    assert not cmd.foo
    assert not _sdist.foo_set

def test_negative_opts_handled_for_distutils():
    _sdist.reset()
    env = _set_environment()
    env.options = options.Bunch(setup=options.Bunch())
    install_distutils_tasks()
    d = _get_distribution()
    d.cmdclass['sdist'] = _sdist_with_default_foo

    tasks._process_commands(['sdist', '--no-foo'])

    assert _sdist.called
    assert not _sdist.foo_set
