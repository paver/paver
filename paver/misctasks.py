"""Miscellaneous tasks that don't fit into one of the other groupings."""
import importlib
import pkgutil
import zipfile
import six
from os.path import join, dirname, exists, abspath
from paver.easy import dry, task, path
from paver.tasks import VERSION, cmdopts

_docsdir = join(dirname(__file__), "docs")
if exists(_docsdir):
    @task
    def paverdocs():
        """Open your web browser and display Paver's documentation."""
        import webbrowser
        webbrowser.open("file://%s"  % join(abspath(_docsdir), 'index.html') )

@task
@cmdopts([('versioned_name', '', 'Determine if minilib uses version in its name')],
            share_with=['generate_setup'])
def minilib(options):
    """Create a Paver mini library that contains enough for a simple
    pavement.py to be installed using a generated setup.py. This
    is a good temporary measure until more people have deployed paver.
    The output file is 'paver-minilib.zip' in the current directory.

    Options:

    versioned_name
        if set to True, paver version will be added into minilib's filename
        (ie paver-minilib-1.1.0.zip)
        purpose is to avoid import error while using different versions of minilib
        with easy_install
        (default False)

    extra_files
        list of other paver modules to include (don't include the .py
        extension). By default, the following modules are included:
        defaults, path, release, setuputils, misctasks, options,
        tasks, easy

    extra_packages
        list of unrelated packages to include. By default, Paver's own
        dependencies are included. Package must be installed and importable
    """
    filelist = ['__init__', '__main__', 'defaults', 'release', 'path',
                'version', 'setuputils', "misctasks", "options", "tasks",
                "easy", 'shell', 'deps/__init__', 'deps/path2', 'deps/path3']
    filelist.extend(options.get('extra_files', []))

    packagelist = ['six']
    packagelist.extend(options.get('extra_packages', []))
    packagelist = set(packagelist)

    output_version = ""
    if 'versioned_name' in options:
        output_version = "-%s" % VERSION

    output_file = 'paver-minilib%s.zip' % output_version

    def generate_zip():
        # Write the mini library to a buffer.
        buf = six.BytesIO()
        destfile = zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED)
        for filename in filelist:
            destfile.writestr("paver/%s.py" % filename,
                pkgutil.get_data('paver', "%s.py" % filename))

        def add_package(package_name, prefix_path='', prefix_fqn=''):
            package = importlib.import_module(prefix_fqn + package_name)
            destfile.writestr(
                prefix_path + package_name + "/__init__.py",
                pkgutil.get_data(prefix_fqn + package_name, "__init__.py")
            )

            for loader, module, is_package in pkgutil.iter_modules(package.__path__):
                if is_package:
                    add_package(
                        module,
                        prefix_path=prefix_path + package_name + '/',
                        prefix_fqn=prefix_fqn + package_name + '.'
                    )
                else:
                    destfile.writestr(
                        prefix_path + package_name + "/%s.py" % module,
                        pkgutil.get_data(prefix_fqn + package_name, "%s.py" % module)
                    )


        for package_name in packagelist:
            # Special case: package to be added is just a module
            # In that case, just write to zipfile and move on
            package = importlib.import_module(package_name)
            if len(package.__path__) == 0:
                destfile.writestr(
                    "%s.py" % package_name,
                    pkgutil.get_data(package_name, "%s.py" % package_name)
                )
            else:
                add_package(package_name)
        
        
        # allow minilib to be invoked directly by Python
        destfile.writestr("__main__.py",
            "import paver.tasks; paver.tasks.main()\n")
        destfile.close()

        # Write the buffer to disk.
        f = open(output_file, "wb")
        f.write(buf.getvalue())
        f.close()
    
    dry("Generate %s" % output_file, generate_zip)

@task
@cmdopts([('versioned_name', '', 'Determine if setup refers to minilib with version in its name')],
            share_with=['minilib'])
def generate_setup(options):
    """Generates a setup.py file that uses paver behind the scenes. This
    setup.py file will look in the directory that the user is running it
    in for a paver-minilib.zip and will add that to sys.path if available.
    Otherwise, it will just assume that paver is available."""
    if 'versioned_name' in options:
        minilib_name = "paver-minilib-%s.zip" % VERSION
        is_versioned_msg = ', referring versioned minilib: %s' % minilib_name
    else:
        is_versioned_msg = ""
        minilib_name = 'paver-minilib.zip'

    def write_setup():
        setup = open("setup.py", "w")
        setup.write("""try:
    import paver.tasks
except ImportError:
    from os.path import exists
    if exists("%(minilib_name)s"):
        import sys
        sys.path.insert(0, "%(minilib_name)s")
    import paver.tasks

paver.tasks.main()
""" % {'minilib_name': minilib_name})
        setup.close()

    dry("Write setup.py%s" % is_versioned_msg, write_setup)
