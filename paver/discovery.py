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
