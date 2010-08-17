.. _cmdline:

..
    Paver Command Line
    ==================

Paver コマンドライン
====================

..
    Paver does sophisticated command line parsing globally and for each task::

Paver はグローバルに解析する洗練されたコマンドラインと各タスクを提供します。

  paver [-q] [-n] [-v] [-f pavement] [-h] [option.name=key] [taskname] [taskoptions] [taskname...]

..
    The command line options are:

コマンドラインオプションは次の通りです。

-q
  .. quiet... don't display much info (info and debug messages are not shown)

  quiet... 情報をたくさん表示しない (デバッグ情報は表示されません)

-n
  .. dry run... don't actually run destructive commands

  dry run... 破壊的なコマンドを実際には実行しない

-v
  .. verbose... display debug level output

  verbose... デバッグレベルの出力を表示する

-h
  ..  display the command line options and list of available tasks. Note
      that -h can be provided for any task to display the command line options
      and detailed help for that task.

  コマンドラインオプションと利用可能なタスクのリストを表示する、-h はどのようなタスクに対してもそのタスクの詳細ヘルプとコマンドラインオプションを表示するために提供されることに注意してください

-f <pavement>
  .. use a different file than "pavement.py"

  "pavement.py" ではなく違うファイルを使用する

..
    If you run paver without a task, it will only run the "auto" task, if there
    is one. Otherwise, Paver will do nothing.

タスクなしで paver を実行するなら "auto" タスクが存在すればそれのみを実行します。もしくは Paver は何もしません。

..
    ``paver help`` is the equivalent of ``paver -h``, and ``paver help taskname``
    is the equivalent of ``paver taskname -h``.

``paver help`` は ``paver -h`` と等価です。そして ``paver help taskname`` は ``paver taskname -h`` と等価です。

..
    You can set build options via the command line by providing optionname=value.
    The option names can be in dotted notation, so ``foo.bar.baz=something`` will
    set options['foo']['bar']['baz'] = 'something' in the options. If you need
    to enter a value with multiple words, put quotes around the part with the space.

optionname=value を提供することでコマンドラインを通してビルドオプションをセットすることができます。
オプション名はドット表記なので ``foo.bar.baz=something`` はオプションの options['foo']['bar']['baz'] = 'something' にセットされます。
複数の単語で値を入力する必要があるなら、クォートでスペースを含む部分を囲んでください。

..
    `Important and useful`: Options are set at the point in which they appear in
    the command line. That means that you can set an option before one task
    and then set it to another value for the next task.

`重要且つ役に立つ`: オプションはコマンドラインに現れる位置でセットされます。最初のタスクの前にオプションをセットして、次のタスクのために別の値をオプションにセットすることができます。
