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

