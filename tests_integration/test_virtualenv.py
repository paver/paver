from unittest2 import TestCase

from os import chdir, pardir, environ
from os.path import join, dirname, exists
from shutil import rmtree, copyfile
from subprocess import check_call, PIPE, STDOUT, CalledProcessError #, check_output
import sys
from tempfile import mkdtemp

from .venvtest import VirtualenvTestCase

class TestVirtualenvTaskSpecification(VirtualenvTestCase):

    def test_running_task_in_specified_virtualenv(self):

        with open(join(self.site_packages_path, "some_venv_module.py"), "w"):
            pass

        subpavement = """
from paver import tasks
from paver.virtual import virtualenv

@tasks.task
@virtualenv(dir="%s")
def t1():
    import some_venv_module
""" % join(self.basedir, "virtualenv")

        pavement_dir = mkdtemp(prefix="unrelated_pavement_module_")

        try:
            with open(join(pavement_dir, "pavement.py"), "w") as f:
                f.write(subpavement)

            chdir(pavement_dir)
            nonvenv_paver_bin = join(dirname(__file__), pardir, 'distutils_scripts', 'paver')

            check_call([sys.executable, nonvenv_paver_bin, "t1"],
                env={
                    'PYTHONPATH' : join(dirname(__file__), pardir),
                    'PATH': environ['PATH']
                })

        finally:
            rmtree(pavement_dir)
