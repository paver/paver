"""Paver's command-line driver"""

import warnings

warnings.warn("paver.command is deprecated. Please re-run the generate_setup task.",
    stacklevel=2)
import paver.tasks

def main():
    paver.tasks.main()
