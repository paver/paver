from __future__ import with_statement

import os
from shutil import rmtree
from subprocess import Popen, PIPE
from tempfile import mkdtemp

from nose.plugins.skip import SkipTest
from nose.tools import assert_equals, assert_true

DJANGO_MANAGE_PY = r"""
#!/usr/bin/env python
from django.core.management import execute_manager
import imp
try:
    imp.find_module('settings') # Assumed to be in the same directory.
except ImportError:
    import sys
    sys.stderr.write("Error: Can't find the file 'settings.py' in the directory containing %r. It appears you've customized things.\\nYou'll have to run django-admin.py, passing it your settings module.\\n" % __file__)
    sys.exit(1)

import settings

if __name__ == "__main__":
    execute_manager(settings)
"""

DJANGO_SETTINGS = """

"""

class TestBasicDjangoDiscovery(object):

    def setUp(self):
        try:
            import django
        except ImportError:
            raise SkipTest("Django must be installed for django discovery tests")

        pavement = """
from paver.easy import *
from paver.setuputils import setup

setup(
    name="MyCoolProject",
    packages=['mycool'],
    version="1.0",
    url="http://www.blueskyonmars.com/",
    author="Kevin Dangoor",
    author_email="dangoor@gmail.com"
)
        """

        self.testbed = mkdtemp(prefix="paver-test-django-")

        with open(os.path.join(self.testbed, "pavement.py"), 'w') as f:
            f.write(pavement)

        self.djangoroot = os.path.join(self.testbed, "cooldjangoproject")
        os.mkdir(self.djangoroot)

        with open(os.path.join(self.djangoroot, "__init__.py"), 'w') as f:
            f.write("")


        with open(os.path.join(self.djangoroot, "manage.py"), 'w') as f:
            f.write(DJANGO_MANAGE_PY)

        with open(os.path.join(self.djangoroot, "settings.py"), 'w') as f:
            f.write(DJANGO_SETTINGS)

    def test_namespaced_django_commands_available(self):

        p = Popen(["python", "manage.py", "help", "validate"], cwd=self.djangoroot, stdout=PIPE, stderr=PIPE)
        p.communicate()

        assert_equals(0, p.returncode, "Unexpected failure when communicating with django's manage.py -- is it installed properly?")

        expected_output = p.stdout

        p = Popen(["paver", "django.help", "validate"], cwd=self.testbed, stdout=PIPE, stderr=PIPE)
        p.communicate()

        assert_equals(0, p.returncode)

        assert_equals(expected_output, p.stdout)

    def tearDown(self):
        rmtree(self.testbed)
