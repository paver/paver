#!/usr/bin/env python

# This is imported from here: https://svn.openplans.org/svn/PoachEggs/trunk/poacheggs.py
# The plan is for this to go away once PoachEggs has a 0.3 release.

from optparse import OptionParser
import sys
import os
import pkg_resources
import logging
import re
import urlparse
import urllib2
import urllib
import subprocess

class BadCommand(Exception):
    """
    Raised when the command is improperly invoked
    """

    def __init__(self, message, returncode=2):
        Exception.__init__(self, message)
        self.returncode = returncode

    def catcher(cls, func):
        def replacement(args=None):
            if args is None:
                args = sys.argv[1:]
            try:
                return func(args)
            except cls, e:
                if str(e):
                    print str(e)
                sys.exit(e.returncode)
        return replacement
    catcher = classmethod(catcher)

class SpecSyntaxError(Exception):
    """Raised when there's an error with the specification"""
    def __init__(self, message, source=None, line_number=None):
        Exception.__init__(self, message)
        self.source = source
        self.line_number = line_number

class CommandError(OSError):
    pass

# Will get redefined in main():
logger = None

@BadCommand.catcher
def main(initial_args):
    global logger
    options, args = parser.parse_args(initial_args)
    if args and args[-1] == '___VENV_RESTART___':
        venv_location = args[-2]
        args = args[:-2]
        options.venv = None
        if not options.src:
            options.src = os.path.join(venv_location, 'src')
    if options.venv:
        if options.verbose > 0 or 1:
            # The logger isn't setup yet
            print 'Running in environment %s' % options.venv
        restart_in_venv(options.venv, initial_args)
        # restart_in_venv should actually never return, but for clarity...
        return
    if options.distutils_cfg:
        if args or options.requirements or options.editable:
            raise BadCommand('If you use --distutils-cfg you cannot install any packages')
    elif options.freeze_filename:
        if args or options.requirements or options.editable:
            raise BadCommand('If you use --freeze you cannot install any packages')
    elif not args and not options.requirements and not options.editable:
        raise BadCommand('You must provide at least one url or file to find install requirements')
    level = 1 # Notify
    level += options.verbose
    level -= options.quiet
    level = Logger.level_for_integer(3-level)
    logger = Logger([(level, sys.stdout)])
    if not options.src:
        for i in 'VIRTUAL_ENV', 'WORKING_ENV':
            if os.environ.has_key(i):
                directory = os.environ[i]
                break
        else:
            directory = '.'
        options.src = os.path.join(directory, 'src')
    options.src = os.path.expanduser(options.src)
    if options.distutils_cfg:
        main_distutils_cfg(options.distutils_cfg)
        return

    if options.freeze_filename:
        srcs = [options.src] + options.find_src
        srcs = [dir for dir in srcs if dir]
        main_freeze(options.freeze_filename, srcs, options.freeze_find_tags, options.find_links)
        ## FIXME: why is this after main_freeze?
        warn_global_eggs()
        return

    warn_global_eggs()
    env = Environment(src=options.src, cache_only=options.cache_only)
    try:
        spec = InstallSpec.parse_requirements(options.requirements, args, options.editable)
    except SpecSyntaxError, e:
        logger.fatal('Cannot read requirements: %s' % str(e))
        if e.source and e.source != '<command-line>':
            msg = 'in file %s' % e.source
            if e.line_number:
                msg += ' line %s' % e.line_number
            logger.fatal(msg)
        raise BadCommand('', returncode=3)
    logger.debug('Complete requirements:\n%s' % indent(str(spec), 2))

    if options.confirm:
        spec.check_requirements(env)
    elif options.collect:
        if options.cache_only:
            raise BadCommand('--collect and --cache-only do not make sense to use together')
        if not options.egg_cache:
            raise BadCommand('If using --collect you must provide --egg-cache')
        if not os.path.exists(options.egg_cache):
            logger.notify('Creating egg cache directory %s' % options.egg_cache)
            os.makedirs(options.egg_cache)
        spec.cache_eggs(env, options.egg_cache)
    elif spec.items:
        logger.debug('Installing with prefix %s' % sys.prefix)
        if not sys.executable.startswith(sys.prefix):
            logger.debug('Python interpreter: %s' % sys.executable)
        if options.egg_cache:
            #spec.find_links.append(make_file_url(options.egg_cache))
            spec.find_links.append(options.egg_cache)
        spec.install(env)
    else:
        logger.notify('Nothing to install')

help = """\
A list of files or URLs that should be installed in the new
environment, and/or '-r REQUIREMENT_FILE' for lists of requirements.

A requirement with -e will install the requirement as 'editable'
(source unpacked and install in develop mode).

In a list of requirements: one requirement per line, optionally with
-e for editable packages).  This file can also contain lines starting
with -Z, -f, and -r; -Z to always unzip, -f to add to --find-links, -r
to reference another requirements file.

If you use --freeze then the requirements file will be overwritten
with the exact packages currently installed.
"""

parser = OptionParser(version="PoachEggs 0.3 r20055",
                      usage="%%prog [OPTIONS] [REQUIREMENT...]\n\n%s" % help)

parser.add_option('-e', '--editable',
                  action="append",
                  dest="editable",
                  default=[],
                  metavar="REQUIREMENT",
                  help="Install this package as editable")

parser.add_option('-r', '--requirement',
                  action='append',
                  dest='requirements',
                  default=[],
                  metavar="REQUIREMENT_FILE",
                  help="Install requirements listed in the file")

parser.add_option('-f', '--find-links',
                  action="append",
                  dest="find_links",
                  default=[],
                  metavar="URL",
                  help="Extra locations/URLs where packages can be found (sets up your distutils.cfg for future installs)")

parser.add_option('--confirm',
                  dest='confirm',
                  action='store_true',
                  help="Confirm that the requirements have been installed, but don't do anything else (don't set up environment, don't install packages)")

parser.add_option('-v', '--verbose',
                  action="count",
                  dest="verbose",
                  default=0,
                  help="Be verbose (use multiple times for more effect)")

parser.add_option('-q', '--quiet',
                  action="count",
                  dest="quiet",
                  default=0,
                  help="Be more and more quiet")

parser.add_option('--src',
                  action='store',
                  metavar="SRC_DIR",
                  dest='src',
                  help="Directory to install source/editable packages into (default $VIRTUAL_ENV | $WORKING_ENV | ./src/)")

parser.add_option('--distutils-cfg',
                  action='append',
                  metavar='SECTION:OPTION:VALUE',
                  dest='distutils_cfg',
                  help='Update a setting in distutils.cfg, for example, --distutils-cfg=easy_install:index_url:http://download.zope.org/ppix/; '
                  'this option is exclusive of all other options.')

parser.add_option('--egg-cache',
                  dest='egg_cache',
                  metavar='DIR',
                  help='A directory where a cache of eggs is found (or if you use --collect, where they should be placed)')

parser.add_option('--collect',
                  dest='collect',
                  action='store_true',
                  help='Collect the eggs for this installation, but do not install them')

parser.add_option('--cache-only',
                  dest='cache_only',
                  action='store_true',
                  help='Get eggs from the cache only (do not look on the network)')

parser.add_option('--find-src',
                  dest='find_src',
                  metavar='DIR',
                  action='append',
                  default=[],
                  help='A directory where source checkouts can be found')

parser.add_option('--freeze',
                  dest='freeze_filename',
                  metavar='FILENAME',
                  help='Freeze the currently-installed packages into a new requirements file FILENAME (use - for stdout)')

parser.add_option('--freeze-find-tags',
                  dest='freeze_find_tags',
                  action='store_true',
                  help='If freezing a trunk, see if there\'s a workable tag (can be slow)')

parser.add_option('-E', '--environment',
                  dest='venv',
                  metavar='DIR',
                  help='virtualenv to run poacheggs in (either the interpreter or base directory')

def restart_in_venv(venv, args):
    """
    Restart this script using the interpreter in the given virtual environment
    """
    venv = os.path.abspath(venv)
    if sys.platform == 'win32':
        python = os.path.join(venv, 'Scripts', 'python')
    else:
        python = os.path.join(venv, 'bin', 'python')
    if not os.path.exists(python):
        python = venv
    if not os.path.exists(python):
        raise BadCommand('Cannot find virtual environment interpreter at %s' % python)
    base = os.path.dirname(os.path.dirname(python))
    os.execv(python, [python, __file__] + args + [base, '___VENV_RESTART___'])
    

def warn_global_eggs():
    if hasattr(sys, 'real_prefix'):
        # virtualenv
        ## FIXME: this isn't right on Windows
        check_prefix = os.path.join(sys.real_prefix, 'lib', 'python'+sys.version[:3])
    elif os.environ.get('WORKING_ENV'):
        # workingenv
        check_prefix = os.path.join(sys.prefix, 'lib', 'python'+sys.version[:3])
    else:
        # normal global environ, no need to warn
        return
    for path in sys.path:
        if not path.endswith('.egg'):
            continue
        if os.path.basename(path).startswith('setuptools'):
            # This is okay.
            continue
        if path.startswith(check_prefix):
            logger.notify(
                "global eggs may cause problems: %s" % path)

############################################################
## distutils.cfg editing

def main_distutils_cfg(new_options):
    new_settings = []
    for new_option in new_options:
        try:
            section, name, value = new_option.split(':', 2)
            if name.startswith('+'):
                append = True
                name = name[1:]
            else:
                append = False
        except ValueError:
            print 'Bad option: --distutils-cfg=%s' % new_option
            sys.exit(2)
        new_settings.append((section, name, value, append))
    distutils_file = find_distutils_file()
    for section, name, value, append in new_settings:
        update_distutils_file(distutils_file, section, name, value, append)
    logger.info('Updated %s' % distutils_file)

def find_distutils_file():
    import distutils.dist
    dist = distutils.dist.Distribution(None)
    files = dist.find_config_files()
    writable_files = []
    for file in files:
        if not os.path.exists(file):
            logger.info('Distutils config file %s does not exist' % file)
            continue
        if os.access(file, os.W_OK):
            logger.debug('Distutils config %s is writable' % file)
            writable_files.append(file)
        else:
            logger.notify('Distutils config %s is not writable' % file)
    if not files:
        logger.fatal(
            'Could not find any existing writable config file (tried options %s)'
            % ', '.join(files))
        raise IOError("No config files found")
    if len(files) > 1:
        logger.notify(
            "Choosing file %s among writable options %s"
            % (files[0], ', '.join(files[1:])))
    return files[0]

def update_distutils_file(filename, section, name, value, append):
    f = open(filename, 'r')
    lines = f.readlines()
    f.close()
    section_index = None
    for index, line in enumerate(lines):
        if line.strip().startswith('[%s]' % section):
            section_index = index
            break
    if section_index is None:
        logger.info('Adding section [%s]' % section)
        lines.append('[%s]\n' % section)
        lines.append('%s = %s\n' % (name, value))
    else:
        start_item_index = None
        item_index = None
        name_regex = re.compile(r'^%s\s*[=:]' % re.escape(name))
        whitespace_regex = re.compile(r'^\s+')
        for index_offset, line in enumerate(lines[section_index+1:]):
            index = index_offset + section_index + 1
            if item_index is not None:
                if whitespace_regex.match(line):
                    # continuation; point to last line
                    item_index = index
                else:
                    break
            if name_regex.match(line):
                start_item_index = item_index = index
            if line.startswith('['):
                # new section
                break
        if item_index is None:
            logger.info('Added %s to section [%s]' % (name, section))
            lines.insert(section_index+1,
                         '%s = %s\n' % (name, value))
        elif append:
            logger.info('Appended value %s to setting %s' % (value, name))
            lines.insert(item_index+1,
                         '    %s\n' % value)
        else:
            logger.info('Replaced setting %s' % name)
            lines[start_item_index:item_index+1] = ['%s = %s\n' % (name, value)]
    f = open(filename, 'w')
    f.writelines(lines)
    f.close()

############################################################
## Basic objects

class Environment(object):
    """Represents the environment we are installing into.

    Contains:
    `src`: the directory to check out source to
    `python`: the interpreter to use in subcommands
    """

    def __init__(self, src=None, python=sys.executable, cache_only=False):
        self.src = src
        self.python = python
        self.cache_only = cache_only

    def install_dir(self, package_name):
        return os.path.join(self.src, package_name.lower())

class InstallSpec(object):
    """This object represents a specification for installing many
    packages.

    This includes a list of `InstallItem` items (``.items``)
    `find_links` options, and the `always_unzip` option.
    """

    def __init__(self, items, find_links, always_unzip=False):
        self.items = items
        self._items_by_package_name = {}
        for item in items:
            self._items_by_package_name[item.package_name] = item
        self.find_links = find_links
        self.always_unzip = always_unzip

    def install(self, env):
        editable = []
        for item in self.items:
            if item.editable:
                logger.notify('Preparing editable install for %s' % item)
                item.install_no_deps(self, env)
        for item in self.items:
            if not item.editable:
                logger.notify('easy_installing %s' % item)
                item.install(self, env)
        for item in self.items:
            if item.editable:
                logger.notify('Finishing editable install for %s' % item)
                item.install(self, env)

    def cache_eggs(self, env, cache_dir):
        for item in self.items:
            ## FIXME: I'm not sure what to do when caching an
            ## editable item
            item.cache_egg(self, env, cache_dir)

    def __str__(self):
        result = []
        for item in self.items:
            result.append(str(item))
        for link in self.find_links:
            result.append('-f %s' % link)
        if self.always_unzip:
            result.append('--always-unzip')
        return '\n'.join(result)

    #@classmethod
    def parse_lines(cls, lines):
        items = []
        find_links = []
        always_unzip = False
        for line, source, line_number in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            elif line == '-Z' or line == '--always-unzip':
                always_unzip = True
            elif line.startswith('-f') or line.startswith('--find-links'):
                if line.startswith('-f'):
                    line = line[2:].strip()
                else:
                    line = line[len('--find-links')].strip().lstrip('=')
                find_links.append(line)
            else:
                items.append(InstallItem.parse(line, source, line_number))
        return cls(items, find_links, always_unzip)

    parse_lines = classmethod(parse_lines)

    #@classmethod
    def parse_requirements(cls, requirements, args=(), editables=()):
        """Parses a list of filenames/URLs into an instance of InstallSpec"""
        lines = cls.read_requirements(requirements)
        for arg in args:
            lines.append((arg, '<command-line>', 0))
        for editable in editables:
            lines.append(('-e %s' % editable, '<command-line>', 0))
        return cls.parse_lines(lines)

    parse_requirements = classmethod(parse_requirements)

    #@staticmethod
    def read_requirements(requirements):
        """
        Read all the lines from the requirement files, including recursive
        reads.
        """
        lines = []
        req_re = re.compile(r'^(?:-r|--requirements=?)\s+')
        for fn in requirements:
            logger.info('Reading requirement %s' % fn)
            for line_index, line in enumerate(InstallSpec.get_lines(fn)):
                line_number = line_index + 1
                match = req_re.search(line)
                if match:
                    sub_fn = line[match.end():]
                    sub_fn = join_filename(fn, sub_fn)
                    lines.extend(InstallSpec.read_requirements([sub_fn]))
                    continue
                ## FIXME: should we be saving the line number too?
                lines.append((line, fn, line_number))
        return lines

    read_requirements = staticmethod(read_requirements)

    #@staticmethod
    def get_lines(fn_or_url):
        scheme = urlparse.urlparse(fn_or_url)[0]
        if not scheme:
            # Must be filename
            f = open(fn_or_url)
        else:
            f = urllib2.urlopen(fn_or_url)
        try:
            return f.readlines()
        finally:
            f.close()

    get_lines = staticmethod(get_lines)

    def check_requirements(self, env):
        """
        Check all the requirements found in the list of filenames
        """
        for item in self.items:
            if item.requirement is not None:
                name = str(item.requirement)
            else:
                name = item.package_name
            try:
                dist = pkg_resources.get_distribution(name)
                logger.notify("Found: %s" % dist)
                logger.info("  in location: %s" % dist.location)
            except pkg_resources.DistributionNotFound:
                ## FIXME: this should check for available packages with the wrong version
                logger.warn("Not Found: %s" % name)
            except pkg_resources.VersionConflict, e:
                logger.warn("Conflict for requirement %s" % name)
                logger.warn("  %s" % e)
            except ValueError, e:
                logger.warn("Cannot confirm %s" % name)
    

class InstallItem(object):
    """
    Represents one item to be installed as part of a plan.

    Attributes:

    `package_name`: the name of the package
    `source_location`: optionally, the location where the package is found
    `version`: optionally, the version located at the `source_location`
    `requirement`: optionally, the `pkg_resources.Requirement` object
    `editable`: if true, then install this package as editable
    `source`: the source file/URL that this was found in
    `line_number`: the line number of the source where this was found
    """

    def __init__(self, package_name, source_location=None,
                 version=None, requirement=None, editable=False,
                 source=None, line_number=None):
        self.package_name = package_name
        self.source_location = source_location
        self.version = version
        self.requirement = requirement
        self.editable = editable
        self.source = source
        self.line_number = line_number

    def __str__(self):
        if self.requirement is not None:
            s = str(self.requirement)
        else:
            s = self.package_name
            if self.version:
                s += '-' + self.version
        if self.source_location:
            s = self.source_location + '#egg=' + s
        if self.editable:
            s = '-e ' + s
        return s

    def install_no_deps(self, spec, env):
        """Install with --no-deps (for use with editable packages)"""
        assert self.editable
        dir = env.install_dir(self.package_name)
        self.svn_checkout(dir)
        self.develop(env, dir, no_deps=True)
    
    def install(self, spec, env):
        """Install this package

        If this is an editable packaged you must call
        ``.install_no_deps`` first
        """
        if self.editable:
            dir = env.install_dir(self.package_name)
            self.develop(env, dir, no_deps=False)
        else:
            self.easy_install(spec, env)

    def cache_egg(self, spec, env, cache_dir):
        if self.editable:
            ## FIXME: not sure what to do, but eh...
            return
        self.easy_install(spec, env, ['--zip-ok', '--multi-version', '--install-dir', cache_dir])

    _svn_url_re = re.compile(r'^URL: (.+)')

    ## FIXME: move to svn_checkout method:
    def svn_checkout(self, dir):
        href = self.source_location
        message = 'Checking out %s' % href
        if '@' in href:
            href, rev = href.split('@', 1)
            command.extend(['-r', rev])
            message = 'Checking out %s revision %s' % (href, rev)
        if os.path.exists(dir):
            result = call_subprocess(['svn', 'info', dir], show_stdout=False)
            match = self._svn_url_re.search(result)
            assert match, (
                "svn info %s gave unexpected output:\n%s"
                % (dir, result))
            prev_url = match.group(1)
            if prev_url != href:
                print 'The directory %s is already an svn checkout' % dir
                print 'The current checkout is from:   %s' % prev_url
                print 'The new checkout would be from: %s' % svn_location
                while 1:
                    answer = raw_input('Would you like to (s)witch, (i)gnore, (r)eplace/wipe, (b)ackup? ')
                    answer = answer.strip().lower()
                    if answer not in ['s', 'i', 'r', 'b']:
                        print 'I do not understand the answer: %r' % answer
                    else:
                        break
                if answer == 'i':
                    logger.notify('Ignoring the incorrect repository located at %s' % dir)
                    return
                elif answer == 's':
                    logger.notify('Switching the repository %s to the location %s' % (dir, svn_location))
                    call_subprocess(
                        ['svn', 'switch', svn_location, dir])
                elif answer == 'b':
                    n = 1
                    backup = dir + '.bak'
                    while os.path.exists(backup):
                        n += 1
                        backup = dir + 'bak%s' % n
                    logger.notify('Backing up directory %s to %s' % (dir, backup))
                    shutil.move(dir, backup)
                else:
                    logger.notify('Removing directory %s' % dir)
                    shutil.rmtree(dir)
        ## FIXME: The output here should be filtered in some fashion:
        if os.path.exists(dir):
            logger.notify('Updating svn checkout %s' % dir)
            call_subprocess(['svn', 'update', dir])
        else:
            logger.notify('Checking out %s to %s' % (svn_location, dir))
        call_subprocess(['svn', 'checkout', svn_location, dir])

    def svn_checkout(self, dir):
        """Check out this package into the given `dir` directory."""
        href = self.source_location
        command = ['svn', 'checkout']
        message = 'Checking out %s' % href
        if '@' in href:
            href, rev = href.split('@', 1)
            command.extend(['-r', rev])
            message = 'Checking out %s revision %s' % (href, rev)
        command.extend([href, dir])
        logger.notify(message)
        logger.indent += 2
        try:
            ## FIXME: this should use a filter function:
            call_subprocess(command)
        finally:
            logger.indent -= 2

    def develop(self, env, dir, no_deps):
        """Run ``python setup.py develop``"""
        setup_py = os.path.join(dir, 'setup.py')
        command = [env.python, '-c', 'import setuptools; __file__=%r; execfile(%r)' % (setup_py, setup_py),
                   'develop']
        if no_deps:
            command.append('--no-deps')
        logger.indent += 2
        try:
            call_subprocess(command, cwd=dir, show_stdout=False, filter_stdout=make_filter_develop())
        finally:
            logger.indent -= 2

    def easy_install(self, spec, env, options=None):
        command = [env.python, '-c', 'import setuptools.command.easy_install; setuptools.command.easy_install.main()']
        if not logger.stdout_level_matches(logger.DEBUG):
            command.append('-q')
        if env.cache_only:
            command.extend(['--allow-hosts', 'localhost'])
        if spec.always_unzip:
            command.append('--always-unzip')
        if spec.find_links:
            command.extend(['--find-links', ' '.join(spec.find_links)])
        if options:
            command.extend(options)
        if self.requirement is not None:
            command.append(str(self.requirement))
        elif self.source_location:
            command.append(self.source_location)
        else:
            command.append(self.package_name)
        logger.indent += 2
        try:
            try:
                call_subprocess(command, show_stdout=False, filter_stdout=make_filter_easy_install())
            except CommandError, e:
                logger.fatal('easy_install failed: %s' % e)
                raise BadCommand('')
        finally:
            logger.indent -= 2

    _egg_fragment_re = re.compile(r'#egg=(.*)')

    #@classmethod
    def parse(cls, line, source, line_number):
        """Parse an item from a line of source, returning an instance

        ``str(inst)`` inverts the parsing"""
        editable = False
        if line.startswith('--editable'):
            line = line[len('--editable'):].strip()
            editable = True
        elif line.startswith('-e'):
            line = line[len('-e'):].strip()
            editable = True
        match = cls._egg_fragment_re.search(line)
        req = None
        version = None
        source_location = None
        if match:
            source_location = line.split('#')[0]
            package_name = match.group(1)
        elif line.startswith('http:') or line.startswith('https:'):
            source_location = line
            package_name = line.split('/')[-1]
        else:
            package_req = line
            ## FIXME: catch error here:
            req = pkg_resources.Requirement.parse(package_req)
            package_name = req.project_name
        if not req and '-' in package_name:
            package_name, version = package_name.rsplit('-', 1)
        if not source_location and editable:
            raise SpecSyntaxError("Editable (-e) item doesn't give repository URL: %s" % (line),
                                  source=source, line_number=line_number)
        return cls(package_name, source_location, version, req, editable,
                   source=source, line_number=line_number)

    parse = classmethod(parse)

############################################################
## Freezing

rev_re = re.compile(r'-r(\d+)$')
date_re = re.compile(r'-(20\d\d\d\d\d\d)$')

def main_freeze(freeze_filename, srcs, find_tags, find_links):
    if freeze_filename == '-':
        logger.move_stdout_to_stderr()
    settings = dict(find_links=list(find_links), always_unzip=False,
                    egg_cache=None, variables={})
    dependency_links = []
    existing_projects = set()
    if os.path.exists(freeze_filename):
        logger.notify('Reading settings from %s' % freeze_filename)
        lines = read_requirements(logger, [freeze_filename])
        plan = parse_requirements(logger, lines, settings)
        for item in plan:
            if isinstance(item, tuple):
                assert item[0] == '--editable'
                continue
            if item.startswith('http:') or item.startswith('https:'):
                dependency_links.append(item)
            project_name = find_project_name_from_plan(item)
            if project_name:
                existing_projects.add(project_name)
            else:
                logger.notify(
                    'Cannot determine the project name for this item of the plan: %s' % item)
    if freeze_filename == '-':
        f = sys.stdout
    else:
        f = open(freeze_filename, 'w')
    srcs = [os.path.normcase(os.path.abspath(os.path.expanduser(src))) for src in srcs]
    for src in srcs:
        if not os.path.exists(src):
            logger.warn('src directory %s does not exist' % src)
    for dist in pkg_resources.working_set:
        if dist.has_metadata('dependency_links.txt'):
            dependency_links.extend(dist.get_metadata_lines('dependency_links.txt'))
    for link in settings['find_links']:
        if '#egg' in link:
            dependency_links.append(link)
    for setting_name, setting_value in sorted(settings['variables'].items()):
        print >> f, format_setting(setting_name, setting_value)
    for link in sorted(settings['find_links']):
        print >> f, '-f %s' % link
    if settings['always_unzip']:
        print >> f, '--always-unzip'
    # This will be a list of dicts, with the dicts looking like:
    #   {'editable': true/false, 'existing': true/false, 'project_name':..., 'lines':[...]}
    installations = []
    for dist in pkg_resources.working_set:
        lines = []
        if dist.key == 'setuptools' or dist.key == 'poacheggs':
            ## FIXME: also skip virtualenv?
            continue
        location = os.path.normcase(os.path.abspath(dist.location))
        if os.path.exists(os.path.join(location, '.svn')):
            for src in srcs:
                if location.startswith(src):
                    break
            else:
                logger.info('Note: svn checkout not in any src (%s): %s' % (', '.join(srcs), location))
            req = get_src_requirement(dist, location, find_tags)
            editable = 1
        else:
            editable = False
            req = dist.as_requirement()
            specs = req.specs
            assert len(specs) == 1 and specs[0][0] == '=='
            version = specs[0][1]
            match = rev_re.search(version)
            date_match = date_re.search(version)
            if match or date_match:
                svn_location = get_svn_location(dist, dependency_links)
                if not svn_location:
                    logger.warn(
                        'Warning: cannot find svn location for %s' % req)
                    lines.append('# FIXME: could not find svn URL in dependency_links for this package:')
                else:
                    lines.append('# installing as editable to satisfy requirement %s:' % req)
                    if match:
                        rev = match.group(1)
                    else:
                        rev = '{%s}' % date_match.group(1)
                    req = '-e %s@%s#egg=%s' % (svn_location, rev, dist.egg_name())
                    editable = 2
        assert req is not None, "Got None requirement for dist %r" % dist
        lines.append(req)
        existing = dist.project_name in existing_projects
        installations.append(dict(
            editable=editable, existing=existing, project_name=dist.project_name,
            lines=lines))
    installations.sort(
        key=lambda item: (-item['existing'], -item['editable'], item['project_name'].lower()))
    for item in installations:
        for line in item['lines']:
            print >> f, line
    if freeze_filename != '-':
        logger.notify('Put requirements in %s' % freeze_filename)
        f.close()

def find_project_name_from_plan(line):
    match = egg_fragment_re.search(line)
    if match:
        return match.group(0).split('-')[0]
    req = pkg_resources.Requirement.parse(line)
    return req.project_name

def format_setting(name, value):
    lines = value.splitlines()
    result = '%s = %s' % (name, lines[0])
    # Lines up following ilnes with the first line value:
    padding = ' '*(len(name)+3)
    for line in lines[1:]:
        result += '\n%s%s' % (padding, line)
    return result

egg_fragment_re = re.compile(r'#egg=(.*)$')

def get_svn_location(dist, dependency_links):
    keys = []
    for link in dependency_links:
        match = egg_fragment_re.search(link)
        if not match:
            continue
        name = match.group(1)
        if '-' in name:
            key = '-'.join(name.split('-')[:-1]).lower()
        else:
            key = name
        if key == dist.key:
            return link.split('#', 1)[0]
        keys.append(key)
    return None

def get_src_requirement(dist, location, find_tags):
    if not os.path.exists(os.path.join(location, '.svn')):
        logger.warn('cannot determine version of editable source in %s (is not svn checkout)' % location)
        return dist.as_requirement()
    repo = get_svn_url(location)
    if repo is None:
        return None
    parts = repo.split('/')
    egg_project_name = dist.egg_name().split('-', 1)[0]
    if parts[-2] in ('tags', 'tag'):
        # It's a tag, perfect!
        return '-e %s#egg=%s-%s' % (repo, egg_project_name, parts[-1])
    elif parts[-2] in ('branches', 'branch'):
        # It's a branch :(
        rev = get_svn_revision(location)
        return '-e %s@%s#egg=%s%s-r%s' % (repo, rev, dist.egg_name(), parts[-1], rev)
    elif parts[-1] == 'trunk':
        # Trunk :-/
        rev = get_svn_revision(location)
        if find_tags:
            tag_url = '/'.join(parts[:-1]) + '/tags'
            tag_revs = get_tag_revs(tag_url)
            match = find_tag_match(rev, tag_revs)
            if match:
                logger.notify('trunk checkout %s seems to be equivalent to tag %s' % match)
                return '-e %s/%s#egg=%s-%s' % (tag_url, match, egg_project_name, match)
        return '-e %s@%s#egg=%s-dev' % (repo, rev, dist.egg_name())
    else:
        # Don't know what it is
        logger.warn('svn URL does not fit normal structure (tags/branches/trunk): %s' % repo)
        rev = get_svn_revision(location)
        return '-e %s@%s#egg=%s-dev' % (repo, rev, egg_project_name)

_svn_url_re = re.compile('url="([^"]+)"')
_svn_rev_re = re.compile('committed-rev="(\d+)"')

def get_svn_revision(location):
    """
    Return the maximum revision for all files under a given location
    """
    # Note: taken from setuptools.command.egg_info
    revision = 0

    for base, dirs, files in os.walk(location):
        if '.svn' not in dirs:
            dirs[:] = []
            continue    # no sense walking uncontrolled subdirs
        dirs.remove('.svn')
        entries_fn = os.path.join(base, '.svn', 'entries')
        if not os.path.exists(entries_fn):
            ## FIXME: should we warn?
            continue
        f = open(entries_fn)
        data = f.read()
        f.close()

        if data.startswith('8'):
            data = map(str.splitlines,data.split('\n\x0c\n'))
            del data[0][0]  # get rid of the '8'
            dirurl = data[0][3]
            revs = [int(d[9]) for d in data if len(d)>9 and d[9]]+[0]
            if revs:
                localrev = max(revs)
            else:
                localrev = 0
        elif data.startswith('<?xml'):
            dirurl = _svn_url_re.search(data).group(1)    # get repository URL
            revs = [int(m.group(1)) for m in _svn_rev_re.finditer(data)]+[0]
            if revs:
                localrev = max(revs)
            else:
                localrev = 0
        else:
            logger.warn("unrecognized .svn/entries format; skipping %s", base)
            dirs[:] = []
            continue
        if base == location:
            base_url = dirurl+'/'   # save the root url
        elif not dirurl.startswith(base_url):
            dirs[:] = []
            continue    # not part of the same svn tree, skip it
        revision = max(revision, localrev)

    return revision

def get_svn_url(location):
    # In cases where the source is in a subdirectory, not alongside setup.py
    # we have to look up in the location until we find a real setup.py
    orig_location = location
    while not os.path.exists(os.path.join(location, 'setup.py')):
        last_location = location
        location = os.path.dirname(location)
        if location == last_location:
            # We've traversed up to the root of the filesystem without finding setup.py
            logger.warn("Could not find setup.py for directory %s (tried all parent directories)"
                        % orig_location)
            return None
    f = open(os.path.join(location, '.svn', 'entries'))
    data = f.read()
    f.close()
    if data.startswith('8'):
        data = map(str.splitlines,data.split('\n\x0c\n'))
        del data[0][0]  # get rid of the '8'
        return data[0][3]
    elif data.startswith('<?xml'):
        return _svn_url_re.search(data).group(1)    # get repository URL
    else:
        logger.warn("unrecognized .svn/entries format in %s" % location)
        # Or raise exception?
        return None

def get_tag_revs(svn_tag_url):
    stdout = call_subprocess(
        ['svn', 'ls', '-v', svn_tag_url], show_stdout=False)
    results = []
    for line in stdout.splitlines():
        parts = line.split()
        rev = int(parts[0])
        tag = parts[-1].strip('/')
        results.append((tag, rev))
    return results

def find_tag_match(rev, tag_revs):
    best_match_rev = None
    best_tag = None
    for tag, tag_rev in tag_revs:
        if (tag_rev > rev and
            (best_match_rev is None or best_match_rev > tag_rev)):
            # FIXME: Is best_match > tag_rev really possible?
            # or is it a sign something is wacky?
            best_match_rev = tag_rev
            best_tag = tag
    return best_tag

############################################################
## Infrastructure


class Logger(object):

    """
    Logging object for use in command-line script.  Allows ranges of
    levels, to avoid some redundancy of displayed information.
    """

    DEBUG = logging.DEBUG
    INFO = logging.INFO
    NOTIFY = (logging.INFO+logging.WARN)/2
    WARN = WARNING = logging.WARN
    ERROR = logging.ERROR
    FATAL = logging.FATAL

    LEVELS = [DEBUG, INFO, NOTIFY, WARN, ERROR, FATAL]

    def __init__(self, consumers):
        self.consumers = consumers
        self.indent = 0
        self.in_progress = None
        self.in_progress_hanging = False

    def debug(self, msg, *args, **kw):
        self.log(self.DEBUG, msg, *args, **kw)
    def info(self, msg, *args, **kw):
        self.log(self.INFO, msg, *args, **kw)
    def notify(self, msg, *args, **kw):
        self.log(self.NOTIFY, msg, *args, **kw)
    def warn(self, msg, *args, **kw):
        self.log(self.WARN, msg, *args, **kw)
    def error(self, msg, *args, **kw):
        self.log(self.WARN, msg, *args, **kw)
    def fatal(self, msg, *args, **kw):
        self.log(self.FATAL, msg, *args, **kw)
    def log(self, level, msg, *args, **kw):
        if args:
            if kw:
                raise TypeError(
                    "You may give positional or keyword arguments, not both")
        args = args or kw
        rendered = None
        for consumer_level, consumer in self.consumers:
            if self.level_matches(level, consumer_level):
                if (self.in_progress_hanging
                    and consumer in (sys.stdout, sys.stderr)):
                    self.in_progress_hanging = False
                    sys.stdout.write('\n')
                    sys.stdout.flush()
                if rendered is None:
                    if args:
                        rendered = msg % args
                    else:
                        rendered = msg
                    rendered = ' '*self.indent + rendered
                if hasattr(consumer, 'write'):
                    consumer.write(rendered+'\n')
                else:
                    consumer(rendered)

    def start_progress(self, msg):
        assert not self.in_progress, (
            "Tried to start_progress(%r) while in_progress %r"
            % (msg, self.in_progress))
        if self.level_matches(self.NOTIFY, self._stdout_level()):
            sys.stdout.write(msg)
            sys.stdout.flush()
            self.in_progress_hanging = True
        else:
            self.in_progress_hanging = False
        self.in_progress = msg

    def end_progress(self, msg='done.'):
        assert self.in_progress, (
            "Tried to end_progress without start_progress")
        if self.stdout_level_matches(self.NOTIFY):
            if not self.in_progress_hanging:
                # Some message has been printed out since start_progress
                sys.stdout.write('...' + self.in_progress + msg + '\n')
                sys.stdout.flush()
            else:
                sys.stdout.write(msg + '\n')
                sys.stdout.flush()
        self.in_progress = None
        self.in_progress_hanging = False

    def show_progress(self):
        """If we are in a progress scope, and no log messages have been
        shown, write out another '.'"""
        if self.in_progress_hanging:
            sys.stdout.write('.')
            sys.stdout.flush()

    def stdout_level_matches(self, level):
        """Returns true if a message at this level will go to stdout"""
        return self.level_matches(level, self._stdout_level())

    def _stdout_level(self):
        """Returns the level that stdout runs at"""
        for level, consumer in self.consumers:
            if consumer is sys.stdout:
                return level
        return self.FATAL

    def level_matches(self, level, consumer_level):
        """
        >>> l = Logger()
        >>> l.level_matches(3, 4)
        False
        >>> l.level_matches(3, 2)
        True
        >>> l.level_matches(slice(None, 3), 3)
        False
        >>> l.level_matches(slice(None, 3), 2)
        True
        >>> l.level_matches(slice(1, 3), 1)
        True
        >>> l.level_matches(slice(2, 3), 1)
        False
        """
        if isinstance(level, slice):
            start, stop = level.start, level.stop
            if start is not None and start > consumer_level:
                return False
            if stop is not None or stop <= consumer_level:
                return False
            return True
        else:
            return level >= consumer_level

    #@classmethod
    def level_for_integer(cls, level):
        levels = cls.LEVELS
        if level < 0:
            return levels[0]
        if level >= len(levels):
            return levels[-1]
        return levels[level]

    level_for_integer = classmethod(level_for_integer)

    def move_stdout_to_stderr(self):
        to_remove = []
        to_add = []
        for consumer_level, consumer in self.consumers:
            if consumer == sys.stdout:
                to_remove.append((consumer_level, consumer))
                to_add.append((consumer_level, sys.stderr))
        for item in to_remove:
            self.consumers.remove(item)
        self.consumers.extend(to_add)

## FIXME: move to svn_checkout method:
def svn_checkout(req):
    match = egg_fragment_re.search(req)
    assert match
    package_name = match.group(1).rsplit('-', 1)[0]
    dir = os.path.join(os.getcwd(), package_name.lower())
    svn_location = req.split('#', 1)[0]
    if os.path.exists(dir):
        result = call_subprocess(['svn', 'info', dir])
        match = svn_url_re.search(result)
        assert match, (
            "svn info %s gave unexpected output:\n%s"
            % (dir, result))
        prev_url = match.group(1)
        if prev_url != svn_location:
            print 'The directory %s is already an svn checkout' % dir
            print 'The current checkout is from:   %s' % prev_url
            print 'The new checkout would be from: %s' % svn_location
            while 1:
                answer = raw_input('Would you like to (s)witch, (i)gnore, (r)eplace/wipe, (b)ackup? ')
                answer = answer.strip().lower()
                if answer not in ['s', 'i', 'r', 'b']:
                    print 'I do not understand the answer: %r' % answer
                else:
                    break
            if answer == 'i':
                logger.notify('Ignoring the incorrect repository located at %s' % dir)
                return dir
            elif answer == 's':
                logger.notify('Switching the repository %s to the location %s' % (dir, svn_location))
                call_subprocess(
                    ['svn', 'switch', svn_location, dir])
            else:
                if answer == 'b':
                    n = 1
                    backup = dir + '.bak'
                    while os.path.exists(backup):
                        n += 1
                        backup = dir + 'bak%s' % n
                    logger.notify('Backing up directory %s to %s' % (dir, backup))
                    shutil.move(dir, backup)
                else:
                    logger.notify('Removing directory %s' % dir)
                    shutil.rmtree(dir)
    if os.path.exists(dir):
        logger.notify('Updating svn checkout %s' % dir)
        call_subprocess(['svn', 'update', dir])
    else:
        logger.notify('Checking out %s to %s' % (svn_location, dir))
    call_subprocess(['svn', 'checkout', svn_location, dir])
    return dir

def make_file_url(path):
    path = os.path.abspath(path)
    path = path.replace(os.path.sep, '/').lstrip('/')
    return 'file:///'+urllib.quote(path)

############################################################
## Misc functions

def indent(text, indent):
    return ''.join(
        (' '*indent) + line for line in text.splitlines(True))

def join_filename(base, sub, only_req_uri=False):
    if only_req_uri and '#' not in sub:
        return sub
    if re.search(r'^https?://', base) or re.search(r'^https?://', sub):
        return urlparse.urljoin(base, sub)
    else:
        base = os.path.dirname(os.path.abspath(base))
        return os.path.join(base, sub)

def call_subprocess(cmd, show_stdout=True,
                    filter_stdout=None, cwd=None,
                    raise_on_returncode=True):
    cmd_parts = []
    for part in cmd:
        if ' ' in part or '\n' in part or '"' in part or "'" in part:
            part = '"%s"' % part.replace('"', '\\"')
        cmd_parts.append(part)
    cmd_desc = ' '.join(cmd_parts)
    if show_stdout:
        stdout = None
    else:
        stdout = subprocess.PIPE
    logger.debug("Running command %s" % cmd_desc)
    try:
        proc = subprocess.Popen(
            cmd, stderr=subprocess.STDOUT, stdin=None, stdout=stdout,
            cwd=cwd)
    except Exception, e:
        logger.fatal(
            "Error %s while executing command %s" % (e, cmd_desc))
        raise
    all_output = []
    if stdout is not None:
        stdout = proc.stdout
        while 1:
            line = stdout.readline()
            if not line:
                break
            line = line.rstrip()
            all_output.append(line)
            if filter_stdout:
                level = filter_stdout(line)
                if isinstance(level, tuple):
                    level, line = level
                logger.log(level, line)
                if not logger.stdout_level_matches(level):
                    logger.show_progress()
            else:
                logger.info(line)
    else:
        returned_stdout, returned_stderr = proc.communicate()
        all_output = [returned_stdout]
    proc.wait()
    if proc.returncode:
        if raise_on_returncode:
            if all_output:
                logger.notify('Complete output from command %s:' % cmd_desc)
                logger.notify('\n'.join(all_output) + '\n----------------------------------------')
            raise CommandError(
                "Command %s failed with error code %s"
                % (cmd_desc, proc.returncode))
        else:
            logger.warn(
                "Command %s had error code %s"
                % (cmd_desc, proc.returncode))
    if stdout is not None:
        return ''.join(all_output)

############################################################
## Filters for call_subprocess:

def make_filter_easy_install():
    context = []
    def filter_easy_install(line):
        adjust = 0
        level = Logger.NOTIFY
        prefix = 'Processing dependencies for '
        if line.startswith(prefix):
            requirement = line[len(prefix):].strip()
            context.append(requirement)
            adjust = -2
        prefix = 'Finished installing '
        if line.startswith(prefix):
            requirement = line[len(prefix):].strip()
            if not context or context[-1] != requirement:
                # For some reason the top-level context is often None from
                # easy_install.process_distribution; so we shouldn't worry
                # about inconsistency in that case
                if len(context) != 1 or requirement != 'None':
                    print 'Error: Got unexpected "%s%s"' % (prefix, requirement)
                    print '       Context: %s' % context
            context.pop()
        if not line.strip():
            level = Logger.DEBUG
        for regex in [r'references __(file|path)__$',
                      r'^zip_safe flag not set; analyzing',
                      r'MAY be using inspect.[a-zA-Z0-9_]+$',
                      #r'^Extracting .*to',
                      #r'^creating .*\.egg$',
                      r": top-level module may be 'python -m' script$",
                      ]:
            if re.search(regex, line.strip()):
                level = Logger.DEBUG
        indent = len(context)*2 + adjust
        return (level, ' '*indent + line)
    return filter_easy_install


def make_filter_develop():
    easy_filter = make_filter_easy_install()
    def filter_develop(line):
        for regex in [r'^writing.*egg-info']:
            if re.search(regex, line.strip()):
                return Logger.DEBUG
        return easy_filter(line)
    return filter_develop

if __name__ == '__main__':
    main()
