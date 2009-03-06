"""Miscellaneous tasks that don't fit into one of the other groupings."""
import os

from paver.easy import dry, path, task

_docsdir = os.path.join(os.path.dirname(__file__), "docs")
if os.path.exists(_docsdir):
    @task
    def paverdocs():
        """Open your web browser and display Paver's documentation."""
        import webbrowser
        webbrowser.open("file://" 
            + (os.path.join(os.path.abspath(_docsdir), 'index.html')))
        
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
    filelist = ['__init__', 'defaults', 'path', 'path25', 'release',
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
    from paver.easy import dry
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
    