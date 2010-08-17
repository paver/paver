.. _pavement:

..
    pavement.py in depth
    ====================

徹底的に pavement.py 
====================

..
    Paver is meant to be a hybrid declarative/imperative system for getting stuff done.
    You declare things via the options in pavement.py. And, in fact, many projects
    can get away with nothing but options in pavement.py. Consider, for example,
    an early version of Paver's own pavement file::

Paver は作業を行うために宣言型/命令型のハイブリッドシステムになるように意図されて作られています。pavement.py のオプションを通して定義することができます。そして、実際、多くのプロジェクトは pavement.py にオプションがありますが何もせずに使用します。例えば Paver 自身の pavement ファイル初期バージョンを考えてみてください。

::

  from paver.easy import *
  import paver.doctools

  options(
      setup=dict(
      name='paver',
      version="0.3",
      description='Python build tool',
      author='Kevin Dangoor',
      author_email='dangoor+paver@gmail.com',
      #url='',
      packages=['paver'],
      package_data=setuputils.find_package_data("paver", package="paver",
                                              only_in_packages=False),
      install_requires=[],
      test_suite='nose.collector',
      zip_safe=False,
      entry_points="""
      [console_scripts]
      paver = paver.command:main
      """,
      ),
    
      sphinx=Bunch(
          builddir="build",
          sourcedir="source"
      )
    
  )

  @task
  @needs('paver.doctools.html')
  def html():
      """Build Paver's documentation and install it into paver/docs"""
      builtdocs = path("docs") / options.sphinx.builddir / "html"
      destdir = path("paver") / "docs"
      destdir.rmtree()
      builtdocs.move(destdir)


..
    This file has both declarative and imperative aspects. The options define 
    enough information for distutils, setuptools and Sphinx to do their
    respective jobs. This would function just fine without requiring you
    to define any tasks.

このファイルは宣言型と命令型両方の様相を持っています。そのオプションは distutils, setuptools や Sphinx がそれぞれのジョブを行うために十分な情報を定義します。これはタスクを定義することを必要とせず実際に機能します。

..
    However, for Paver's 'paverdoc' built-in task to work, we need
    Sphinx's generated HTML to end up inside of Paver's package tree.
    So, we override the html task to move the generated files.

しかし、Paver の 'paverdoc' ビルトインタスクが動作するために Paver のパッケージツリー内部に Sphinx が生成した HTML が必要になります。そのため、生成された HTML ファイルを移動するために html タスクを上書きします。

..
    Defining Tasks
    --------------

タスクを定義する
----------------

..
    Tasks are just simple functions. You designate a function as being a
    task by using the @task decorator.

タスクは単純なただの関数です。@task デコレータを使用してタスクとしての関数を指定します。

..
    You can also specify that a task depends on another task running
    first with the @needs decorator. A given task will only run once
    as a dependency for other tasks.

さらにあるタスクが他のタスクの実行に依存するときは最初に @needs デコレータを指定することもできます。そのタスクは他のタスクのための依存関係として同時に実行されます。

..
    Manually Calling Tasks
    ----------------------

手動でタスクを呼び出す
----------------------

..
    Sometimes, you need to do something `before` running another task, so
    the @needs decorator doesn't quite do the job.

時々、他のタスクを実行する `前に` 何かを行う必要があります。そのため @needs デコレータはそのジョブを実行できません。

..
    Of course, tasks are just Python functions. So, you can just call the
    other task like a function! 

もちろん、タスクはただの Python 関数です。そのため、関数呼び出しのように他のタスクを実際に呼び出すこともできます！

..
    How Task Names Work
    ---------------------

どのようにタスク名が動作するか
------------------------------

..
    Tasks have both a long name and a short name. The short name is just
    the name of the function. The long name is the fully qualified Python
    name for the function object.

タスクは長い名前と短い名前の両方を持ちます。短い名前は実際の関数の名前です。長い名前は Python の関数オブジェクトの省略されていない名前です。

..
    For example, the Sphinx support includes a task function called "html".
    That task's long name is "paver.doctools.html".

例えば、Sphinx は "html" というタスク機能をサポートします。そのタスクの長い名前は "paver.doctools.html" です。

..
    If you ```import paver.doctools``` in your pavement.py, you'll be able 
    to use either name to refer to that task.

pavement.py で ```import paver.doctools``` する場合、"html" を参照するためにどちらの名前でも使用できます。

..
    Tasks that you define in your pavement are always available by their
    short names. Tasks defined elsewhere are available by their short names
    unless there is a conflict where two tasks are trying to use the same
    short name.

pavement.py で定義したタスクは短い名前でいつでも利用できます。そのタスクは同じ短い名前を使用する他のタスクと競合しない限りどこででも定義されます。

..
    Tasks are always available unambiguously via their long names.

タスクは長い名前で明示的に利用することもできます。

..
    Task Parameters
    ---------------

タスクパラメータ
----------------

..
    Tasks don't have to take any parameters. However, Paver allows you to work
    in a fairly clean, globals-free manner(*). Generally speaking, the easiest way
    to work with paver is to just do ``from paver.easy import *``, but if you
    don't like having so much in your namespace, you can have any attribute
    from tasks.environment sent into your function. For example::

タスクはどんなパラメータも持つ必要はありません。しかし、Paver は適切なクリーン、globals-free な方法(*)で動作するのを許容します。一般的に言うと paver を実行する最も簡単な方法は ``from paver.easy import *`` を行うだけです。しかし、あなたが名前空間を多く持つことを好まないなら、関数内に送られた tasks.environment の属性を持つことができます。例えば、次の通りです。

..
        # this task will get the options and the "info" logging function
        # sent in

::

    @task
    def my_task(options, info):
        # このタスクはオプションを取得して "info" ロギング関数へ送る
        pass

..
    (*): well, there *is* one global: tasks.environment.

(*): tasks.environment がグローバルです

..
    Command Line Arguments
    ----------------------

コマンドライン引数
------------------

..
    Tasks can specify that they accept command line arguments, via two 
    other decorators. The ``@consume_args`` decorator tells Paver that *all* 
    command line arguments following this task's name should be passed to the 
    task. You can either look up the arguments in ``options.args``, or just 
    specify args as a parameter to your function. For example, Paver's "help" 
    task is declared like this::

タスクは他の2つのデコレータを通してコマンドライン引数を受け取るように指定することができます。 ``@consume_args`` デコレータは Paver にこのタスク名に続く *全て* のコマンドライン引数を伝えます。 ``options.args`` か、関数へのパラメータとして args を指定するかのどちらでもその引数を見つけることができます。例えば Paver の "help" タスクは次のように定義されます。

::

    @task
    @consume_args
    def help(args, help_function):
        pass

..
    The "args" parameter is just an attribute on tasks.environment (as is
    help_function), so it is passed in using the same rules described in the
    previous section.

"args" パラメータは tasks.environment の属性です(help_function そのまま)。そのため、前のセクションで説明した同じルールを使用して渡されます。

..
    More generally, you're not trying to consume all of the remainder of the
    command line but to just accept certain specific arguments. That's what
    the cmdopts decorator is for::

もっと汎用的に、特定の指定した引数を受け取るために全てのコマンドラインの引数を調べる必要はありません。それは cmdopts デコレータで行います。

::

    @task
    @cmdopts([
        ('username=', 'u', 'Username to use when logging in to the servers')
    ])
    def deploy(options):
        pass

..
    @cmdopts takes a list of tuples, each with long option name, short option name
    and help text. If there's an "=" after the long option name, that means
    that the option takes a parameter. Otherwise, the option is assumed to be
    boolean. The command line options set in this manner are all added to
    the ``options`` under a namespace matching the name of the task. In the
    case above, options.deploy.username would be set if the user ran
    paver deploy -u my-user-name. Note that an equivalent command line would be
    paver deploy.username=my-user-name deploy

@cmdopts は長いオプション名、短いオプション名とヘルプテキストといった3つの要素を持つタプルのリストを受け取ります。長いオプション名の後に "=" があれば、そのオプションはパラメータを取ることになります。その他のオプションはブーリアンだと仮定されます。この方法のコマンドラインオプションセットは task の名前にマッチする名前空間の下で ``options`` に全て追加されます。上述したケースでは、ユーザが paver deploy -u my-user-name と実行したなら options.deploy.username がセットされます。コマンドラインで paver deploy.username=my-user-name deploy で実行するのも等価であることに注意してください。
