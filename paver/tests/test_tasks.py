from pprint import pprint

from paver import command, runtime, defaults, setuputils, misctasks

from paver.tests.mock import Mock
from paver.tests.utils import reset_runtime

def test_tasks_are_pruned_when_options_are_missing():
    cmdopts = reset_runtime()
    reload(misctasks)
    reload(defaults)
    assert runtime.TASKS, "Tasks should have repopulated"
    assert 'setup' not in runtime.options
    command.finalize_env(cmdopts)
    assert 'setup' not in runtime.options
    # develop should go away because there are no 'setup'
    # options
    assert 'develop' not in runtime.TASKS, "develop command should be missing"

def test_task_overrides_work_properly():
    cmdopts = reset_runtime()
    reload(setuputils)
    
    @runtime.task
    def f1():
        pass
    first = f1
    
    @runtime.task
    def f1():
        pass
    
    command.load_build("")
    command.finalize_env(cmdopts)
    d = setuputils.Distribution()
    
    assert runtime.TASKS['f1'].func == f1, \
        runtime.TASKS['f1'].longname
    assert runtime.TASKS['paver.tests.test_tasks.f1'].func == first
    
def test_basic_dependencies():
    cmdopts = reset_runtime()
    cmdopts.quiet = False
    runtime.options.update(cmdopts)
    
    @runtime.task
    def t1():
        t1.called = True
    
    t1.called = False
    t1.t2_was_called = False
    
    @runtime.task
    @runtime.needs('t1')
    def t2():
        assert t1.called
        t1.t2_was_called = True
    
    d = setuputils.Distribution()
    runtime.call_task('t2')
    assert t1.t2_was_called

def test_longname_resolution_in_dependencies():
    cmdopts = reset_runtime()
    cmdopts.quiet = False
    runtime.options.update(cmdopts)
    
    @runtime.task
    def t1():
        t1.called = True
    
    t1.called = False
    t1.t2_was_called = False
    
    @runtime.task
    @runtime.needs('paver.tests.test_tasks.t1')
    def t2():
        assert t1.called
        t1.t2_was_called = True
    
    d = setuputils.Distribution()
    pprint(d.cmdclass)
    runtime.call_task('t2')
    assert t1.t2_was_called
    
def test_chained_dependencies():
    cmdopts = reset_runtime()
    cmdopts.quiet = False
    runtime.options.update(cmdopts)
    
    called = [False, False, False, False]
    
    @runtime.task
    def t1():
        assert called == [False, False, False, False]
        called[0] = True
    
    @runtime.task
    @runtime.needs('t1')
    def t2():
        assert called == [True, False, False, False]
        called[1] = True
    
    @runtime.task
    def t3():
        assert called == [True, True, False, False]
        called[2] = True
    
    @runtime.task
    @runtime.needs(['t2', 't3'])
    def t4():
        assert called == [True, True, True, False]
        called[3] = True
    
    d = setuputils.Distribution()
    runtime.call_task('t4')
    assert called == [True, True, True, True], "Called was: %s" % (called)

def test_tasks_dont_repeat():
    cmdopts = reset_runtime()
    cmdopts.quiet = False
    runtime.options.update(cmdopts)
    
    called = [0, 0, 0, 0]
    
    @runtime.task
    def t1():
        assert called == [0, 0, 0, 0]
        called[0] += 1
    
    @runtime.task
    @runtime.needs('t1')
    def t2():
        assert called == [1, 0, 0, 0]
        called[1] += 1
    
    @runtime.task
    @runtime.needs('t1')
    def t3():
        assert called == [1, 1, 0, 0]
        called[2] += 1
    
    @runtime.task
    @runtime.needs(['t2', 't3'])
    def t4():
        assert called == [1, 1, 1, 0]
        called[3] += 1
    
    d = setuputils.Distribution()
    runtime.call_task('t4')
    assert called == [1, 1, 1, 1]

