from unittest2 import TestCase

from os import chdir, getcwd, pardir, environ
from os.path import join, dirname, exists
from shutil import rmtree, copyfile
from subprocess import check_call, PIPE, STDOUT, CalledProcessError
import sys

from .venvtest import VirtualenvTestCase

class TestMinilib(VirtualenvTestCase):

    def test_minilib_generated(self):
        self.install_paver()
        self.paver_execute('minilib')

        assert exists('paver-minilib.zip') == True
