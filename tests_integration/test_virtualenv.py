from unittest2 import TestCase

from os import chdir, getcwd, pardir, environ
from os.path import join, dirname, exists
from shutil import rmtree, copyfile
from subprocess import check_call, PIPE
import sys
from tempfile import mkdtemp

class TestVirtualenvTaskSpecification(TestCase):

    def setUp(self):
        super(TestVirtualenvTaskSpecification, self).setUp()

        self.basedir = mkdtemp(prefix="test_paver_venv")
        self.oldcwd = getcwd()

    def _prepare_virtualenv(self):
        """
        Prepare paver virtual environment in self.basedir.
        Use distribution's bootstrap to do so.
        """
        copyfile(join(dirname(__file__), pardir, "bootstrap.py"), join(self.basedir, "bootstrap.py"))
        check_call(["python", join(self.basedir, "bootstrap.py")], stdout=PIPE, stderr=PIPE, cwd=self.basedir)

    def test_running_task_in_specified_virtualenv(self):
        self._prepare_virtualenv()
        if sys.platform == 'win32':
            site_packages = join(self.basedir, 'virtualenv', 'Lib', 'site-packages')
        else:
            site_packages = join(self.basedir, 'virtualenv', 'lib', 'python%s' % sys.version[:3], 'site-packages')
        f = open(join(site_packages,  "some_venv_module.py"), "w")
        f.close()

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
            f = open(join(pavement_dir, "pavement.py"), "w")
            f.write(subpavement)
            f.close()

            chdir(pavement_dir)

            paver_bin = join(dirname(__file__), pardir, 'distutils_scripts', 'paver')
            # FIXME: Will this work on windows?
            if 'VIRTUAL_ENV' in environ and exists(join(environ['VIRTUAL_ENV'], "bin", "python")):
                python_bin = join(environ['VIRTUAL_ENV'], "bin", "python")
            else:
                python_bin = "python"
            check_call([python_bin, paver_bin, "t1"], env={'PYTHONPATH' : join(dirname(__file__), pardir)})

        finally:
            rmtree(pavement_dir)


    def tearDown(self):
        chdir(self.oldcwd)
        rmtree(self.basedir)

        super(TestVirtualenvTaskSpecification, self).tearDown()
