from __future__ import with_statement

import os
from shutil import rmtree
from subprocess import Popen, PIPE
from tempfile import mkdtemp

from nose.plugins.skip import SkipTest
from nose.tools import assert_equals, assert_true

class TestBasicFabricDiscovery(object):

    def setUp(self):
        try:
            import fabric
        except ImportError:
            raise SkipTest("Django must be installed for django discovery tests")

        self.testbed = mkdtemp(prefix="paver-test-fabric-")

        FABFILE = """
from fabric.api import local

def show_xxx():
    local('echo xxx')
"""

        with open(os.path.join(self.testbed, "fabfile.py"), 'w') as f:
            f.write(FABFILE)

        pavement = """
from paver.easy import *
from paver.setuputils import setup

from paver.discovery import discover_fabric

setup(
    name="MyCoolProject",
    packages=['mycool'],
    version="1.0",
    url="http://www.blueskyonmars.com/",
    author="Kevin Dangoor",
    author_email="dangoor@gmail.com"
)

discover_fabric(options)
        """

        with open(os.path.join(self.testbed, "pavement.py"), 'w') as f:
            f.write(pavement)


    def test_namespaced_django_commands_available(self):
        p = Popen(["fab", "show_xxx"], cwd=self.testbed, stdout=PIPE, stderr=PIPE)
        expected_output, _ = p.communicate()

        assert_equals(0, p.returncode, "Unexpected failure when communicating with fabric -- is it installed properly?")

        p = Popen(["paver", "fab.show_xxx"], cwd=self.testbed, stdout=PIPE, stderr=PIPE)
        output, stderr = p.communicate()

        assert_equals(0, p.returncode, "Command failed: stdout: %s, stderr: %s" % (output, stderr))

        assert_equals("xxx", output.splitlines()[0])


    def tearDown(self):
        rmtree(self.testbed)
