from unittest2 import TestCase

from os import chdir, getcwd, pardir, environ
from os.path import join, dirname, exists
from shutil import rmtree, copyfile
from subprocess import check_call, PIPE, STDOUT, CalledProcessError #, check_output
import sys
from tempfile import mkdtemp

from venvtest import VirtualenvTestCase

class TestVirtualenvTaskSpecification(VirtualenvTestCase):

    def test_running_task_in_specified_virtualenv(self):
        self.prepare_virtualenv()
        if sys.platform == 'win32':
            site_packages = join(self.basedir, 'virtualenv', 'Lib', 'site-packages')
        else:
            site_packages = join(self.basedir, 'virtualenv', 'lib', 'python%s' % sys.version[:3], 'site-packages')

        # just create the file
        with open(join(self.site_packages_path,  "some_venv_module.py"), "w"):
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

            paver_bin = join(dirname(__file__), pardir, 'distutils_scripts', 'paver')

            # FIXME: Will this work on windows?
            if 'VIRTUAL_ENV' in environ and exists(join(environ['VIRTUAL_ENV'], "bin", "python")):
                python_bin = join(environ['VIRTUAL_ENV'], "bin", "python")
            else:
                python_bin = "python"
            check_call([python_bin, paver_bin, "t1"],
                env={
                    'PYTHONPATH' : join(dirname(__file__), pardir),
                    'PATH': environ['PATH']
                })

        finally:
            rmtree(pavement_dir)
