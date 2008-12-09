"""The namespace for the pavement to run in, also imports default tasks."""

import warnings

warnings.warn("""paver.defaults is deprecated. Import from paver.easy instead.
Note that you will need to add additional declarations for exactly
equivalent behavior. Specifically:

from paver.easy import *
import paver.misctasks
from paver import setuputils

setuputils.install_distutils_tasks()
""", DeprecationWarning, 2)

from paver.easy import *
from paver.misctasks import *
from paver import setuputils

setuputils.install_distutils_tasks()
