from pprint import pprint

from paver import command, runtime, defaults, setuputils, misctasks, tasks, options

from paver.tests.mock import Mock
from paver.tests.utils import _set_environment

def test_basic_dependencies():
    @tasks.task
    def t1():
        pass
    
    t1.called = False
    t1.t2_was_called = False
    
    @tasks.task
    @tasks.needs('t1')
    def t2():
        assert t1.called
        t1.t2_was_called = True
    
    _set_environment(t1 = t1, t2=t2)
    
    assert hasattr(tasks.environment.pavement, 't1')
    t2()
    assert t1.t2_was_called

@tasks.task
def global_t1():
    pass

def test_longname_resolution_in_dependencies():
    global_t1.called = False
    global_t1.t2_was_called = False
    
    @tasks.task
    @tasks.needs('paver.tests.test_tasks.global_t1')
    def t2():
        assert global_t1.called
        global_t1.t2_was_called = True
    
    _set_environment(t2=t2)
    t2()
    assert global_t1.t2_was_called
    
def test_chained_dependencies():
    called = [False, False, False, False]
    
    @tasks.task
    def t1():
        assert called == [False, False, False, False]
        called[0] = True
    
    @tasks.task
    @tasks.needs('t1')
    def t2():
        assert called == [True, False, False, False]
        called[1] = True
    
    @tasks.task
    def t3():
        assert called == [True, True, False, False]
        called[2] = True
    
    @tasks.task
    @tasks.needs('t2', 't3')
    def t4():
        assert called == [True, True, True, False]
        called[3] = True
    
    _set_environment(t1=t1,t2=t2,t3=t3,t4=t4)
    t4()
    assert called == [True, True, True, True], "Called was: %s" % (called)

def test_tasks_dont_repeat():
    called = [0, 0, 0, 0]
    
    @tasks.task
    def t1():
        assert called == [0, 0, 0, 0]
        called[0] += 1
    
    @tasks.task
    @tasks.needs('t1')
    def t2():
        assert called == [1, 0, 0, 0]
        called[1] += 1
    
    @tasks.task
    @tasks.needs('t1')
    def t3():
        assert called == [1, 1, 0, 0]
        called[2] += 1
    
    @tasks.task
    @tasks.needs('t2', 't3')
    def t4():
        assert called == [1, 1, 1, 0]
        called[3] += 1
    
    _set_environment(t1=t1,t2=t2,t3=t3,t4=t4)
    t4()
    assert called == [1, 1, 1, 1]

def test_basic_command_line():
    @tasks.task
    def t1():
        pass
        
    _set_environment(t1=t1)
    try:
        tr, args = tasks._parse_command_line(['foo'])
        print tr
        assert False, "Expected BuildFailure exception for unknown task"
    except tasks.BuildFailure:
        pass
    
    task, args = tasks._parse_command_line(['t1'])
    assert task == t1
    
    task, args = tasks._parse_command_line(['t1', 't2'])
    assert task == t1
    assert args == ['t2']
    
def test_list_tasks():
    from paver import doctools
    
    @tasks.task
    def t1():
        pass
        
    _set_environment(t1=t1, doctools=doctools)
    task_list = tasks.environment.get_tasks()
    assert t1 in task_list
    assert doctools.html in task_list
    
def test_environment_insertion():
    @tasks.task
    def t1(env):
        pass
    
    _set_environment(t1=t1)
    t1()
    assert t1.called

def test_add_options_to_environment():
    @tasks.task
    def t1(options):
        assert options.foo == 1
        
    @tasks.task
    def t2(options, env):
        assert options.foo == 1
        assert env.options == options
        
    environment = _set_environment(t1=t1, t2=t2)
    environment.options.foo = 1
    
    t1()
    t2()
    assert t1.called
    assert t2.called
    
def test_shortname_access():
    environment = _set_environment(tasks=tasks)
    task = environment.get_task("help")
    assert task is not None
    

def test_task_command_line_options():
    @tasks.task
    @tasks.cmdopts([('foo=', 'f', 'Foobeedoobee!')])
    def t1(options):
        assert options.foo == "1"
        assert options.t1.foo == "1"
    
    environment = _set_environment(t1=t1)
    tasks._process_commands(['t1', '--foo', '1'])
    assert t1.called
    
def test_setting_of_options_with_equals():
    @tasks.task
    def t1(options):
        assert options.foo == '1'
        assert not hasattr(options, 'bar')
    
    @tasks.task
    def t2(options):
        assert options.foo == '1'
        assert options.bar == '2'
    
    environment = _set_environment(t1=t1, t2=t2)
    tasks._process_commands(['foo=1', 't1', 'bar=2', 't2'])
    assert t1.called
    assert t2.called
    
def test_options_inherited_via_needs():
    @tasks.task
    @tasks.cmdopts([('foo=', 'f', "Foo!")])
    def t1(options):
        assert options.t1.foo == "1"
    
    @tasks.task
    @tasks.needs('t1')
    @tasks.cmdopts([('bar=', 'b', "Bar!")])
    def t2(options):
        assert options.t2.bar == '2'
        
    environment = _set_environment(t1=t1, t2=t2)
    tasks._process_commands("t2 --foo 1 -b 2".split())
    assert t1.called
    assert t2.called
    
def test_options_shouldnt_overlap():
    @tasks.task
    @tasks.cmdopts([('foo=', 'f', "Foo!")])
    def t1(options):
        assert False
    
    @tasks.task
    @tasks.needs('t1')
    @tasks.cmdopts([('force=', 'f', "Force!")])
    def t2(options):
        assert False
        
    environment = _set_environment(t1=t1, t2=t2)
    try:
        tasks._process_commands("t2 -f 1".split())
        assert False, "shoudl have gotten a PavementError"
    except tasks.PavementError:
        pass

def test_dotted_options():
    environment = _set_environment()
    tasks._process_commands(['this.is.cool=1'])
    assert environment.options.this['is'].cool == '1'
