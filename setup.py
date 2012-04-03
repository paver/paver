try:
    import paver.tasks
except ImportError:
    from os.path import exists
    if exists("paver-minilib-1.1.0.zip"):
        import sys
        sys.path.insert(0, "paver-minilib-1.1.0.zip")
    import paver.tasks

paver.tasks.main()
