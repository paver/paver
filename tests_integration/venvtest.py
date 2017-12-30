from unittest2 import TestCase

from os import chdir, getcwd, pardir, environ
from os.path import join, dirname, exists
from shutil import rmtree, copyfile
from subprocess import PIPE, STDOUT, CalledProcessError, check_output
import sys
from tempfile import mkdtemp

import paver
from paver.easy import path

class VirtualenvTestCase(TestCase):

    def setUp(self):
        super(VirtualenvTestCase, self).setUp()

        if 'TRAVIS_PYTHON_VERSION' in environ and environ['TRAVIS_PYTHON_VERSION'] in ('jython', 'pypy'):
            from nose import SkipTest
            raise SkipTest("%s virtual tests not yet supported" % environ['TRAVIS_PYTHON_VERSION'])

        if 'APPVEYOR' in environ:
            from nose import SkipTest
            raise SkipTest("Integration tests not (yet) running on Windows/Appveor. Patches welcome.")

        self.oldcwd = path(getcwd())
        self.basedir = path(mkdtemp(prefix="test_paver_venv"))
        self.paver_dev_dir = path(dirname(__file__)) / '..'

        self.prepare_virtualenv()

        chdir(self.basedir)


    def prepare_virtualenv(self):

        self.bootstrap_virtualenv()

        if sys.platform == 'win32':
            self.site_packages_path = join(self.basedir, 'virtualenv', 'Lib', 'site-packages')
            self.python_bin = self.basedir / 'virtualenv' / 'Scripts' / 'python.exe'
        else:
            self.site_packages_path = join(self.basedir, 'virtualenv', 'lib', 'python%s' % sys.version[:3], 'site-packages')
            self.python_bin = self.basedir / 'virtualenv' / 'bin' / 'python'


    def bootstrap_virtualenv(self):
        """
        Prepare paver virtual environment in self.basedir.
        Use distribution's bootstrap to do so.
        """

        chdir(self.basedir)

        paver.virtual._create_bootstrap(script_name="bootstrap.py",
                              packages_to_install=['six'],
                              paver_command_line=None,
                              install_paver=False,
                              dest_dir=self.basedir / 'virtualenv')

        try:
            check_output([sys.executable, self.basedir / "bootstrap.py"], stderr=STDOUT, cwd=self.basedir)
        except CalledProcessError as err:
            # print(err.output)
            raise

    def install_paver(self):
        with self.paver_dev_dir:
            check_output([self.python_bin, self.paver_dev_dir / 'setup.py', 'develop'])
            if sys.platform == 'win32':
                self.paver_bin = self.basedir / 'virtualenv' / 'Scripts' / 'paver'
            else:
                self.paver_bin = self.basedir / 'virtualenv' / 'bin' / 'paver'

    def paver_execute(self, *args):
        cmd = [self.paver_bin]
        cmd.extend(args)
        check_output(cmd)

    def tearDown(self):
        chdir(self.oldcwd)
        rmtree(self.basedir)

        super(VirtualenvTestCase, self).tearDown()
