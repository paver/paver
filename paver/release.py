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
    url='https://github.com/paver/paver',
    packages=['paver', 'paver.deps'],
    install_requires=['six'],
    tests_require=['nose', 'virtualenv', 'mock', 'cogapp'],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: Implementation :: CPython",
        "Environment :: Console",
        "Topic :: Documentation",
        "Topic :: Utilities",
        "Topic :: Software Development :: Build Tools",
    ])
