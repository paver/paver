import os
from pprint import pprint

from nose.tools import assert_equals

from paver import setuputils, misctasks, tasks, options

from paver.tests.mock import Mock
from paver.tests.utils import _set_environment, FakeExitException

OP_T1_CALLED = 0
subpavement = os.path.join(os.path.dirname(__file__), "other_pavement.py")

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

def test_backwards_compatible_needs():
    @tasks.task
    def t():
        pass
    
    @tasks.task
    @tasks.needs(['t'])
    def t2():
        pass
    
    @tasks.task
    @tasks.needs('t')
    def t3():
        pass
    
    env = _set_environment(t=t, t2=t2, t3=t3)
    t3()
    assert t.called
    t.called = False
    
    t2()
    assert t.called

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


def test_longname_access():
    environment = _set_environment(tasks=tasks)
    task = environment.get_task("paver.tasks.help")
    assert task is not None

    task = environment.get_task("nosuchmodule.nosuchtask")
    assert task is None

    task = environment.get_task("paver.tasks.nosuchtask")
    assert task is None


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

def test_options_inherited_via_needs_even_from_grandparents():
    @tasks.task
    @tasks.cmdopts([('foo=', 'f', "Foo!")])
    def t1(options):
        assert options.t1.foo == "1"
    
    @tasks.task
    @tasks.needs('t1')
    @tasks.cmdopts([('bar=', 'b', "Bar!")])
    def t2(options):
        assert options.t2.bar == '2'

    @tasks.task
    @tasks.needs('t2')
    @tasks.cmdopts([('spam=', 's', "Spam!")])
    def t3(options):
        assert options.t3.spam == '3'
        
    environment = _set_environment(t1=t1, t2=t2, t3=t3)
    tasks._process_commands("t3 --foo 1 -b 2 -s 3".split())
    assert t1.called
    assert t2.called
    assert t3.called
    
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

def test_dry_run():
    environment = _set_environment()
    tasks._process_commands(['-n'])
    assert environment.dry_run
    
def test_consume_args():
    @tasks.task
    @tasks.consume_args
    def t1(options):
        assert options.args == ["1", "t2", "3"]
    
    @tasks.task
    def t2(options):
        assert False, "Should not have run t2 because of consume_args"
        
    env = _set_environment(t1=t1, t2=t2)
    tasks._process_commands("t1 1 t2 3".split())
    assert t1.called

    @tasks.task
    @tasks.consume_args
    def t3(options):
        assert options.args[0] == '-v'
        assert options.args[1] == '1'

    env = _set_environment(t3=t3)
    tasks._process_commands("t3 -v 1".split())
    assert t3.called

def test_optional_args_in_tasks():
    @tasks.task
    def t1(options, optarg=None):
        assert optarg is None

    @tasks.task
    def t2(options, optarg1='foo', optarg2='bar'):
        assert optarg1 is 'foo'
        assert optarg2 is 'bar'

    env = _set_environment(t1=t1, t2=t2)
    tasks._process_commands(['t1', 't2'])
    assert t1.called
    assert t2.called
    
def test_debug_logging():
    @tasks.task
    def t1(debug):
        debug("Hi %s", "there")
        
    env = _set_environment(t1=t1, patch_print=True)
    tasks._process_commands(['-v', 't1'])
    assert env.patch_captured[-1] == "Hi there"
    env.patch_captured = []
    
    tasks._process_commands(['t1'])
    assert env.patch_captured[-1] != "Hi there"

def test_base_logging():
    @tasks.task
    def t1(info):
        info("Hi %s", "you")
    
    env = _set_environment(t1=t1, patch_print=True)
    tasks._process_commands(['t1'])
    assert env.patch_captured[-1] == 'Hi you'
    env.patch_captured = []
    
    tasks._process_commands(['-q', 't1'])
    assert not env.patch_captured
    
def test_error_show_up_no_matter_what():
    @tasks.task
    def t1(error):
        error("Hi %s", "error")
    
    env = _set_environment(t1=t1, patch_print=True)
    tasks._process_commands(['t1'])
    assert env.patch_captured[-1] == "Hi error"
    env.patch_captured = []
    
    tasks._process_commands(['-q', 't1'])
    assert env.patch_captured[-1] == "Hi error"
    
def test_all_messages_for_a_task_are_captured():
    @tasks.task
    def t1(debug, error):
        debug("This is debug msg")
        error("This is error msg")
        raise tasks.BuildFailure("Yo, problem, yo")
    
    env = _set_environment(t1=t1, patch_print=True)
    try:
        tasks._process_commands(['t1'])
    except FakeExitException:
        assert "This is debug msg" in "\n".join(env.patch_captured)
        assert env.exit_code == 1

def test_messages_with_formatting_and_no_args_still_work():
    @tasks.task
    def t1(error):
        error("This is a %s message")

    env = _set_environment(t1=t1, patch_print=True)
    tasks._process_commands(['t1'])
    assert env.patch_captured[-1] == "This is a %s message"
    env.patch_captured = []

    tasks._process_commands(['-q', 't1'])
    assert env.patch_captured[-1] == "This is a %s message"
    
def test_alternate_pavement_option():
    env = _set_environment()
    tasks._parse_global_options([])
    assert env.pavement_file == 'pavement.py'

    env = _set_environment()
    tasks._parse_global_options(['--file=foo.py'])
    set_pavement = env.pavement_file
    assert set_pavement == 'foo.py'

    env = _set_environment()
    tasks._parse_global_options(['-f', 'foo.py'])
    set_pavement = env.pavement_file
    assert set_pavement == 'foo.py'


def test_captured_output_shows_up_on_exception():
    @tasks.task
    def t1(debug, error):
        debug("Dividing by zero!")
        1/0
    
    env = _set_environment(t1=t1, patch_print=True, patch_exit=1)
    try:
        tasks._process_commands(['t1'])
        assert False and "Expecting FakeExitException"
    except FakeExitException:
        assert "Dividing by zero!" in "\n".join(env.patch_captured)
        assert env.exit_code == 1
    
def test_calling_subpavement():
    @tasks.task
    def private_t1(options):
        options.foo = 2
        tasks.call_pavement(subpavement, "t1")
        # our options should not be mangled
        assert options.foo == 2
    
    env = _set_environment(private_t1=private_t1)
    tasks._process_commands(['private_t1'])
    # the value should be set by the other pavement, which runs
    # in the same process
    assert OP_T1_CALLED == 1

class MyTaskFinder(object):
    def get_task(self, name):
        if name == "foo":
            return self.foo
        return None
        
    def get_tasks(self):
        return set([self.foo])
    
    @tasks.task
    def foo(self):
        self.foo_called = True
    
def test_task_finders():
    env = _set_environment()
    mtf = MyTaskFinder()
    env.task_finders.append(mtf)
    t = env.get_task("foo")
    assert t == mtf.foo
    all_tasks = env.get_tasks()
    assert mtf.foo in all_tasks
    
def test_calling_a_function_rather_than_task():
    def foo():
        pass
        
    env = _set_environment(foo=foo)
    try:
        tasks._process_commands(['foo'])
        assert False, "Expected a BuildFailure when calling something that is not a task."
    except tasks.BuildFailure:
        pass

def test_description_retrieval_trial():
    @tasks.task
    def t1():
        """ Task it is """
    
    assert_equals("Task it is", t1.description)

def test_description_empty_without_docstring():
    @tasks.task
    def t1():
        pass
    
    assert_equals("", t1.description)

def test_description_retrieval_first_sentence():
    @tasks.task
    def t1():
        """ Task it is. Not with another sentence. """
    
    assert_equals("Task it is", t1.description)

def test_description_retrieval_first_sentence_even_with_version_numbers():
    @tasks.task
    def t1():
        """ Task it is, installs Django 1.0. Not with another sentence. """
    
    assert_equals("Task it is, installs Django 1.0", t1.description)

