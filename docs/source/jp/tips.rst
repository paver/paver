..
    ***************
    Tips and Tricks
    ***************

***************
Tips と Tricks
***************

..
    Using a Config File For Settings
    --------------------------------

設定ファイルを使用する
----------------------

..
    Many people like to have their configuration metadata available in a 
    *data file*, rather than a Python program. This is easy to do with
    Paver::

多くの人は Python プログラムというよりも *データファイル* で利用できる設定ファイルのメタデータを持つのを好みます。これは Paver で行うと簡単です。

::

    from paver.easy import *
    
    @task
    def auto():
        config_data = (read config data using config parser of choice)
        # assuming config_data is a dictionary
        options.update(config_data)

..
    The auto task is automatically run when the pavement is launched. You can
    use Python's standard ConfigParser module, if you'd like to store the
    information in an .ini file.

auto タスクは pavement が起動されるときに自動的に実行されます。もし .ini ファイルにその情報を格納したいなら Python 標準の ConfigParser モジュールを使用することができます。
