from unittest2 import TestCase

from os import chdir, getcwd, pardir, environ
from os.path import join, dirname, exists
from shutil import rmtree, copyfile
from subprocess import check_call, PIPE, STDOUT, CalledProcessError
import sys
from zipfile import ZipFile

from .venvtest import VirtualenvTestCase

class TestMinilib(VirtualenvTestCase):

    def test_minilib_contains_paver(self):
        self.install_paver()
        self.paver_execute('minilib')

        minilib_path = self.basedir / 'paver-minilib.zip'

        assert exists(minilib_path) == True
        # sanity check to prevent false positives
        assert exists(self.basedir / 'paver') == False

        with ZipFile(minilib_path, 'r') as zip:
            zip.extractall(self.basedir)
        
        assert exists(self.basedir / 'paver') == True
        assert exists(self.basedir / 'paver' / 'tasks.py') == True


    def test_minilib_bundles_extra_files(self):
        self.install_paver()
        minilib_path = self.basedir / 'paver-minilib.zip'
        
        with open(self.basedir / 'pavement.py', 'w') as f:
            f.write("""
from paver.easy import *
options = environment.options
options(
    minilib=Bunch(
        extra_files=['ssh'],
        versioned_name=False
    )
)      
            """)

        self.paver_execute('minilib')

        with ZipFile(minilib_path, 'r') as zip:
            zip.extractall(self.basedir)
        
        assert exists(self.basedir / 'paver') == True
        assert exists(self.basedir / 'paver' / 'tasks.py') == True
        assert exists(self.basedir / 'paver' / 'ssh.py') == True


class TestMinilibExtraPackages(VirtualenvTestCase):

    def setUp(self):
        self.install_extra_packages = ['nose']
        super(TestMinilibExtraPackages, self).setUp()

    def test_minilib_bundles_extra_packages(self):
        self.install_paver()
        minilib_path = self.basedir / 'paver-minilib.zip'
        
        with open(self.basedir / 'pavement.py', 'w') as f:
            f.write("""
from paver.easy import *
options = environment.options
options(
    minilib=Bunch(
        extra_packages=['nose'],
        versioned_name=False
    )
)      
            """)

        self.paver_execute('minilib')

        with ZipFile(minilib_path, 'r') as zip:
            zip.extractall(self.basedir)
        
        assert exists(self.basedir / 'paver') == True
        assert exists(self.basedir / 'paver' / 'tasks.py') == True

        assert exists(self.basedir / 'nose') == True
        assert exists(self.basedir / 'nose' / '__init__.py') == True
        assert exists(self.basedir / 'nose' / 'commands.py') == True

class TestMinilibExtraModules(VirtualenvTestCase):

    def setUp(self):
        self.install_extra_packages = ['six']
        super(TestMinilibExtraModules, self).setUp()

    def test_minilib_bundles_extra_modules(self):
        self.install_paver()
        minilib_path = self.basedir / 'paver-minilib.zip'
        
        with open(self.basedir / 'pavement.py', 'w') as f:
            f.write("""
from paver.easy import *
options = environment.options
options(
    minilib=Bunch(
        extra_packages=['six'],
        versioned_name=False
    )
)      
            """)

        self.paver_execute('minilib')

        with ZipFile(minilib_path, 'r') as zip:
            zip.extractall(self.basedir)
        
        assert exists(self.basedir / 'paver') == True
        assert exists(self.basedir / 'paver' / 'tasks.py') == True

        assert exists(self.basedir / 'six.py') == True
