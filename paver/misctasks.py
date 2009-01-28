"""Miscellaneous tasks that don't fit into one of the other groupings."""

from paver.easy import *

def _task_list(userdef_only):
    """Pull together a string list of tasks for help command output.
    The userdef_only parameter determines whether only tasks that
    were defined by the user belong in the list.
    """
    tasknames = sorted(TASKS.keys())
    
    # find the length of the longest task name for formatting purposes
    try:
        if userdef_only:
            maxlen = max(len(TASKS[tn].displayname) for tn in tasknames
                         if TASKS[tn].user_defined)
        else:
            maxlen = max(len(TASKS[tn].displayname) for tn in tasknames)
    except ValueError:
        # this is if the list is empty
        maxlen = 5
    fmt = "  %-" + str(maxlen) + "s - %s"
    for taskname in tasknames:
        task = TASKS[taskname]
        if userdef_only and not task.user_defined:
            continue
        print(fmt % (taskname, task.description))

#@task
#@consume_args
def help(options):
    """Displays the list of commands and the details."""
    args = options.args
    from paver import release
    print """Paver %s

Usage: paver [global options] [option.name=value] task [task options] [task...]

Run 'paver help [section]' to see the following sections of info:

options    global command line options
setup      available distutils/setuptools tasks
tasks      all tasks that have been imported by your pavement

'paver help taskname' will display details for a task.
""" % (release.setup_meta['version'])
    if not args:
        print "Tasks defined in your pavement:"
        _task_list(True)
        return
    
    section = args[0].lower()
    if section == 'options':
        dist = runtime.dist
        dist.script_args = ['-h']
        dist.parse_command_line()
    elif section == 'setup':
        dist = runtime.dist
        dist.script_args = ['--help-commands']
        dist.parse_command_line()
    elif section == 'tasks':
        print "Tasks defined in and imported by your pavement:"
        _task_list(False)
    else:
        task = runtime._ALL_TASKS.get(section)
        if not task:
            print "Could not find task %s to display help" % (section)
        else:
            print "Details for %s:" % (section)
            print task.doc
    

_docsdir = path(__file__).parent / "docs"
if _docsdir.exists():
    @task
    def paverdocs():
        """Open your web browser and display Paver's documentation."""
        import webbrowser
        webbrowser.open("file://" + (_docsdir.abspath() / 'index.html'))
        
@task
def minilib(options):
    """Create a Paver mini library that contains enough for a simple
    pavement.py to be installed using a generated setup.py. This
    is a good temporary measure until more people have deployed paver.
    The output file is 'paver-minilib.zip' in the current directory.
    
    Options:
    
    extra_files
        list of other paver modules to include (don't include the .py 
        extension). By default, the following modules are included:
        defaults, path, release, setuputils, misctasks, options,
        tasks, easy
    """
    import paver
    paverdir = path(paver.__file__).dirname()
    filelist = ['__init__', 'defaults', 'path', 'release',
                'setuputils', "misctasks", "options", "tasks", "easy"]
    filelist.extend(options.get('extra_files', []))
    output_file = 'paver-minilib.zip'

    def generate_zip():
        import zipfile
        destfile = zipfile.ZipFile(output_file, "w", zipfile.ZIP_DEFLATED)
        for filename in filelist:
            destfile.write(
                paverdir / (filename + ".py"),
                "paver/" + (filename + ".py"))
        destfile.close()
    dry("Generate %s" % output_file, generate_zip)
    
@task
def generate_setup():
    """Generates a setup.py file that uses paver behind the scenes. This 
    setup.py file will look in the directory that the user is running it
    in for a paver-minilib.zip and will add that to sys.path if available.
    Otherwise, it will just assume that paver is available."""
    def write_setup():
        setup = open("setup.py", "w")
        setup.write("""import os
if os.path.exists("paver-minilib.zip"):
    import sys
    sys.path.insert(0, "paver-minilib.zip")

import paver.tasks
paver.tasks.main()
""")
        setup.close()
        
    dry("Write setup.py", write_setup)
    