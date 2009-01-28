from paver.easy import *

from paver.tests import test_tasks

options(foo=1)

@task
def t1(options):
    test_tasks.OP_T1_CALLED = options.foo
