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
        assert False, "should have gotten a PavementError"
    except tasks.PavementError:
        pass

def test_options_shouldnt_overlap_when_bad_task_specified():
    @tasks.task
    @tasks.cmdopts([('foo=', 'f', "Foo!")])
    def t1(options):
        assert False
    
    @tasks.task
    @tasks.needs('t1')
    @tasks.cmdopts([('force=', 'f', "Force!")], share_with=['nonexisting_task'])
    def t2(options):
        assert False
        
    environment = _set_environment(t1=t1, t2=t2)
    try:
        tasks._process_commands("t2 -f 1".split())
        assert False, "should have gotten a PavementError"
    except tasks.PavementError:
        pass

def test_options_may_overlap_if_explicitly_allowed():
    @tasks.task
    @tasks.cmdopts([('foo=', 'f', "Foo!")])
    def t1(options):
        assert options.t1.foo == "1"
    
    @tasks.task
    @tasks.needs('t1')
    @tasks.cmdopts([('foo=', 'f', "Foo!")], share_with=['t1'])
    def t2(options):
        assert options.t2.foo == "1"
        
    environment = _set_environment(t1=t1, t2=t2)

    tasks._process_commands("t2 -f 1".split())

    assert t1.called
    assert t2.called

def test_exactly_same_parameters_must_be_specified_in_order_to_allow_sharing():
    @tasks.task
    @tasks.cmdopts([('foo=', 'f', "Foo!")])
    def t1(options):
        assert False
    
    @tasks.task
    @tasks.needs('t1')
    @tasks.cmdopts([('force=', 'f', "Force!")], share_with=['t1'])
    def t2(options):
        assert False
        
    environment = _set_environment(t1=t1, t2=t2)
    try:
        tasks._process_commands("t2 -f 1".split())
        assert False, "should have gotten a PavementError"
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

def test_depending_on_a_function_rather_than_task():
    def bar():
        pass

    @tasks.task
    @tasks.needs('bar')
    def foo():
        pass

    env = _set_environment(foo=foo, bar=bar)
    try:
        tasks._process_commands(['foo'])
        assert False, "Expected a BuildFailure when depending on something that is not a task."
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

def test_auto_task_is_not_run_with_noauto():
    @tasks.no_auto
    @tasks.task
    def t1():
        pass

    @tasks.task
    def auto():
        pass

    _set_environment(auto=auto, t1=t1)
    tasks._process_commands(['t1'], auto_pending=True)
    
    assert t1.called
    assert not auto.called, "t1 is decorated with no_auto, it should not be called"

def test_auto_task_is_run_when_present():
    @tasks.task
    def t1():
        pass

    @tasks.task
    def auto():
        pass

    _set_environment(auto=auto, t1=t1)
    tasks._process_commands(['t1'], auto_pending=True)

    assert t1.called
    assert auto.called

def test_task_can_be_called_repeatedly():
    @tasks.consume_args
    @tasks.task
    def t1(options, info):
        info(options.args[0])

    env = _set_environment(t1=t1, patch_print=True)
    
    tasks._process_commands(['t1', 'spam'])
    tasks._process_commands(['t1', 'eggs'])

    assert_equals('eggs', env.patch_captured[~0])
    assert_equals('spam', env.patch_captured[~2])


def test_options_passed_to_task():
    from optparse import make_option

    @tasks.task
    @tasks.cmdopts([
        make_option("-f", "--foo", help="foo")
    ])
    def t1(options):
        assert options.foo == "1"
        assert options.t1.foo == "1"

    environment = _set_environment(t1=t1)
    tasks._process_commands(['t1', '--foo', '1'])
    assert t1.called

# We could mock stdout/err, but seriously -- to integration test for this one
# once integration test suite is merged into master

#def test_hiding_from_help():
#    @tasks.task
#    @tasks.no_help
#    def hidden_task(options):
#        pass
#
#    environment = _set_environment(hidden_task=hidden_task, help=tasks.help)
#    args = tasks._parse_global_options(['-h'])
#    output = tasks._process_commands(args)
#
#    assert 'hidden_task' not in output

def test_calling_task_with_option_arguments():
    @tasks.task
    @tasks.cmdopts([('foo=', 'f', "Foo!")])
    def t1(options):
        assert options.foo == 'true story'

    env = _set_environment(t1=t1)

    env.call_task('t1', options={
        'foo' : 'true story'
    })

def test_calling_task_with_arguments_do_not_overwrite_it_for_other_tasks():
    @tasks.task
    @tasks.cmdopts([('foo=', 'f', "Foo!")])
    def t3(options):
        assert options.foo == 'cool story'

    @tasks.task
    @tasks.cmdopts([('foo=', 'f', "Foo!")])
    def t2(options):
        assert options.foo == 'true'


    @tasks.task
    @tasks.needs('t2')
    def t1(options):
        env.call_task('t3', options={
            'foo' : 'cool story'
        })

    env = _set_environment(t1=t1, t2=t2, t3=t3)

    tasks._process_commands(['t1', '--foo', 'true'])


def test_options_might_be_provided_if_task_might_be_called():

    @tasks.task
    @tasks.cmdopts([('foo=', 'f', "Foo!")])
    def t1(options):
        assert options.foo == "YOUHAVEBEENFOOD"

    @tasks.task
    @tasks.might_call('t1')
    def t2(options):
        pass

    environment = _set_environment(t1=t1, t2=t2)
    tasks._process_commands("t2 -f YOUHAVEBEENFOOD".split())

def test_calling_task_with_arguments():
    @tasks.task
    @tasks.consume_args
    def t2(args):
        assert args[0] == 'SOPA'


    @tasks.task
    def t1(options):
        env.call_task('t2', args=['SOPA'])

    env = _set_environment(t1=t1, t2=t2)

    tasks._process_commands(['t1'])

def test_calling_nonconsuming_task_with_arguments():
    @tasks.task
    def t2():
        pass


    @tasks.task
    def t1():
        env.call_task('t2')

    env = _set_environment(t1=t1, t2=t2)

    try:
        env.call_task('t1', args=['fail'])
    except tasks.BuildFailure:
        pass
    else:
        assert False, ("Task without @consume_args canot be called with them "
                      "(BuildFailure should be raised)")

def test_options_may_overlap_between_multiple_tasks_even_when_specified_in_reverse_order():
    @tasks.task
    @tasks.cmdopts([('foo=', 'f', "Foo!")], share_with=['t2', 't3'])
    def t1(options):
        assert options.t1.foo == "1"

    @tasks.task
    @tasks.needs('t1')
    @tasks.cmdopts([('foo=', 'f', "Foo!")])
    def t2(options):
        assert options.t2.foo == "1"

    @tasks.task
    @tasks.needs('t1')
    @tasks.cmdopts([('foo=', 'f', "Foo!")])
    def t3(options):
        assert options.t3.foo == "1"

    environment = _set_environment(t1=t1, t2=t2, t3=t3)

    tasks._process_commands("t2 -f 1".split())

    assert t1.called
    assert t2.called

    tasks._process_commands("t3 -f 1".split())

    assert t1.called
    assert t3.called


def test_options_might_be_shared_both_way():
    @tasks.task
    @tasks.cmdopts([('foo=', 'f', "Foo!")], share_with=['t2'])
    def t1(options):
        assert options.t1.foo == "1"

    @tasks.task
    @tasks.needs('t1')
    @tasks.cmdopts([('foo=', 'f', "Foo!")], share_with=['t1'])
    def t2(options):
        assert options.t2.foo == "1"

    environment = _set_environment(t1=t1, t2=t2)

    tasks._process_commands("t2 -f 1".split())

    assert t1.called
    assert t2.called
