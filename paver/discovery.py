from paver.path import path
from paver import tasks

class DjangoTaskFinder(object):
    def __init__(self, options):
        self.options = options

    def get_task(self, taskname):
        from django.core.management import call_command
        from django.core.management.base import BaseCommand
        if taskname.startswith('django.'):
            taskname = taskname[len('django.'):]

        task = tasks.Task(lambda: call_command(taskname))
        task.user_options = BaseCommand.option_list
        return task


    def get_tasks(self):
        from django.core.management import get_commands

        return set(tasks.Task(t) for t in get_commands.key())

def discover_django(options):
    """ Look for manage.py and import it's task into main pavement """
    import os, sys
    os.environ['DJANGO_SETTINGS_MODULE'] = getattr(options.discovery.django, "settings_module", "settings")
    if getattr(options.discovery.django, "settings_path", None):
        sys.path.append(options.discovery.django.settings_path)
    
    env = tasks.environment
    if not hasattr(env, "_django_tasks_installed"):
        env.task_finders.append(DjangoTaskFinder(options))
        env._django_tasks_installed = True


class FabricTaskFinder(object):
    def __init__(self, options):
        super(FabricTaskFinder, self).__init__()

        self.options = options

    def _load_fabfile(self):
        from fabric import state
        from fabric.main import load_fabfile

        result = load_fabfile(self.options.fabfile)
        state.commands.update(result[1])
        return result

    def get_task(self, taskname):
        if taskname.startswith('fab.'):
            taskname = taskname[len('fab.'):]

        taskinfo = self._load_fabfile()

        try:
            from fabric.tasks import execute
            return tasks.Task(lambda: execute(taskname))
        except ImportError:
            task = taskinfo[1][taskname]

            # First, try class-based tasks
            if hasattr(task, 'run') and callable(task.run):
                return tasks.Task(lambda: task.run())
                # Fallback to callable behavior
            return tasks.Task(lambda: task())

    def get_tasks(self):
        self._load_fabfile()

        from fabric import state
        return set(tasks.Task(t) for t in state.commands.values())

def discover_fabric(options):
    """ Look for manage.py and import it's task into main pavement """
    fabfile = getattr(options, "fabfile", None)
    if not fabfile:
        from fabric.main import find_fabfile
        fabfile = find_fabfile()

    if fabfile:
        fabfile = path(fabfile)

    if not fabfile or not fabfile.exists():
        raise tasks.BuildFailure("fabric.py cannot be found")

    #FIXME: use options.discovery.fabric.fabfile
    options.fabfile = path(fabfile.abspath())

    env = tasks.environment
    if not hasattr(env, "_fabric_tasks_installed"):
        env.task_finders.append(FabricTaskFinder(options))
        env._fabric_tasks_installed = True
