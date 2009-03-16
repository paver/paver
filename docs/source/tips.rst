***************
Tips and Tricks
***************

Using a Config File For Settings
--------------------------------

Many people like to have their configuration metadata available in a 
*data file*, rather than a Python program. This is easy to do with
Paver::

    from paver.easy import *
    
    @task
    def auto():
        config_data = (read config data using config parser of choice)
        # assuming config_data is a dictionary
        options.update(config_data)
        
The auto task is automatically run when the pavement is launched. You can
use Python's standard ConfigParser module, if you'd like to store the
information in an .ini file.