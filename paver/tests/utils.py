from paver import runtime, setuputils, defaults

def reset_runtime():
    runtime.TASKS.clear()
    runtime.options.clear()
    reload(defaults)
    return runtime.Bunch(dry_run=True)

