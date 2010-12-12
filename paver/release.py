"""Release metadata for Paver."""

from paver.options import Bunch
from paver.tasks import VERSION

setup_meta=Bunch(
    name='Paver',
    version=VERSION,
    description='Easy build, distribution and deployment scripting',
    long_description="""Paver is a Python-based build/distribution/deployment scripting tool along the
lines of Make or Rake. What makes Paver unique is its integration with 
commonly used Python libraries. Common tasks that were easy before remain 
easy. More importantly, dealing with *your* applications specific needs and 
requirements is also easy.""",
    author='Kevin Dangoor',
    author_email='dangoor+paver@gmail.com',
    maintainer='Lukas Linhart',
    maintainer_email='bugs@almad.net',
    url='http://paver.github.com/',
    packages=['paver', 'paver.cog']
)
