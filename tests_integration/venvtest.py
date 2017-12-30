from unittest2 import TestCase

from os import chdir, getcwd, pardir, environ
from os.path import join, dirname, exists
from shutil import rmtree, copyfile
from subprocess import check_call, PIPE, STDOUT, CalledProcessError #, check_output
import sys
from tempfile import mkdtemp

class VirtualenvTestCase(TestCase):

    def setUp(self):
        super(VirtualenvTestCase, self).setUp()

        if 'TRAVIS_PYTHON_VERSION' in environ and environ['TRAVIS_PYTHON_VERSION'] in ('jython', 'pypy'):
            from nose import SkipTest
            raise SkipTest("%s virtual tests not yet supported" % environ['TRAVIS_PYTHON_VERSION'])

        if 'APPVEYOR' in environ:
            from nose import SkipTest
            raise SkipTest("Integration tests not (yet) running on Windows/Appveor. Patches welcome.")

    def prepare_virtualenv(self):
        """
        Prepare paver virtual environment in self.basedir.
        Use distribution's bootstrap to do so.
        """

        self.basedir = mkdtemp(prefix="test_paver_venv")
        self.oldcwd = getcwd()

        copyfile(join(dirname(__file__), pardir, "bootstrap.py"), join(self.basedir, "bootstrap.py"))
        # Use check_output instead of check_call once py26 and py32 support is dropped
        try:
            # check_output([sys.executable, join(self.basedir, "bootstrap.py")], stderr=STDOUT, cwd=self.basedir)
            check_call([sys.executable, join(self.basedir, "bootstrap.py")], stderr=STDOUT, cwd=self.basedir)
        except CalledProcessError as err:
            # print(err.output)
            raise

        if sys.platform == 'win32':
            self.site_packages_path = join(self.basedir, 'virtualenv', 'Lib', 'site-packages')
        else:
            self.site_packages_path = join(self.basedir, 'virtualenv', 'lib', 'python%s' % sys.version[:3], 'site-packages')

    def tearDown(self):
        chdir(self.oldcwd)
        rmtree(self.basedir)

        super(VirtualenvTestCase, self).tearDown()
