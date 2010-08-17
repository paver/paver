..
    ********************
    Foreword: Why Paver?
    ********************

**********************
序文: どうして Paver？
**********************

..
    I didn't want to make a new build tool. Honestly. The main reason that I created Paver
    is...

正直に言うと私は新たなビルドツールを作りたくなかった。私が Paver を作成した主な理由は...

..
    The Declarative/Imperative Divide
    ---------------------------------

宣言型/命令型の分割
-------------------

..
    When you solve the same problem repeatedly, patterns emerge and you're able to easily
    see ways to reduce how much effort is involved in solving that problem. Often
    times, you'll end up with a `declarative solution`_. Python's standard distutils
    is a declarative solution. In your call to the ``setup()`` function, you declare
    some metadata about your project and provide a list of the parts and you end
    up with a nice command line interface. That command line interface knows how to
    make redistributable tarballs (and eggs if you have setuptools), install the
    package, build C extensions and more.

あなたが繰り返し起こる同じ問題を解決するとき、そこにはパターンがあり、その問題を解決するのにかかるコストを減らす方法はすぐに分かります。あなたは最終的に `declarative solution`_ (`宣言型の解決方法`_) に落ち着くことがよくあるでしょう。Python 標準の distutils は宣言型の解決方法です。 ``setup()`` 関数を呼び出す過程で、プロジェクトに関するメタデータの宣言、その部品となるリストの提供や使い勝手の良いコマンドラインインタフェースに辿り着きます。そのコマンドラインインタフェースは再配布可能な tarball(setuptools があれば egg) の作成方法やパッケージのインストール、C 言語拡張のビルド等を知っています。

..
    zc.buildout does a similar thing for deployments. Declare the parts of your system
    and specify a recipe for each part (each recipe with its own collection of options)
    and you can build up a consistent system with one command.

zc.buildout はデプロイのためによく似たことを実現します。システムの部品を宣言し、各部品のレシピ(その独自オプションのコレクションによる各レシピ)を指定して、1つのコマンドで統合システムを構築することができます。

..
    These tools sound great, don't they? They are great. As long as you don't need
    to customize the capabilities they provide. For example, it's not uncommon that
    you'll need to move some file here, create some directory there, etc. Then what?

これらのツールは素晴らしいですよね？そう素晴らしいのですよ。これらのツールが提供する機能をカスタマイズする必要がない限りね。例えば、ここにファイルを移動する、そこにディレクトリを作成するといったことが必要になるのは一般的ではありません。それじゃあ？

..
    In an `imperative system`_, you'd just add the few lines of code you need.

`imperative system`_ (`命令型システム`_) では、必要に応じてコードに数行追加するだけで良いです。

..
    For distutils and zc.builout and other similar tools, the answer usually involves
    extra boilerplate surrounding the code in question and then installing that code somewhere. 
    You basically have to create declarative syntax for something that is a one-off rather 
    than a larger, well-understood problem. And, for distutils and zc.buildout, 
    you have to use two entirely different mechanisms.

distutils, zc.builout やその他の類似ツールでの答えは通常、問題になるコード周りでどこかからコードをインストールする追加の定型文を実行します。あなたは大きな、十分理解された問題というよりはちょっとした作業のために宣言型の構文を基本的に作成する必要があります。そして distutils や zc.buildout では宣言型と命令型という2つの完全に違う仕組みを使用する必要があります。

.. _`declarative solution`: http://en.wikipedia.org/wiki/Declarative_programming
.. _`imperative system`: http://en.wikipedia.org/wiki/Imperative_programming
.. _`宣言型の解決方法`: http://ja.wikipedia.org/wiki/宣言型プログラミング
.. _`命令型システム`: http://ja.wikipedia.org/wiki/命令型プログラミング

..
    Consistency for Project Related Tasks
    -------------------------------------

プロジェクトに関するタスクの統合性
----------------------------------

..
    And that's the next thing that bothered me with the state of Python tools. It 
    would be nice to have a consistent interface in command line and configuration 
    for the tools that I use to work with my projects. Every tool I bring in to 
    the project adds new command line interfaces, more config files (and some of
    those config files duplicate project metadata!).

次に私を悩ませたのは Python ツールの状態です。私のプロジェクトで使用するツールの設定とコマンドラインで統合インタフェースを持つことは良いことです。私がプロジェクトに取り入れた全てのツールは新たなコマンドラインインタフェースと、さらに設定ファイル(そういった設定ファイルはプロジェクトのメタデータが重複する)を追加します。

..
    That's Why Paver Is Here
    ------------------------

それが Paver が今日に存在する理由
---------------------------------

..
    Paver is set up to provide declarative handling of common tasks with as easy
    an escape hatch to imperative programming as possible (just add a function
    with a decorator in the same file). Your project-related configuration
    options are all together and all accessible to different parts of your
    build and deployment setup. And the language used for everything is Python,
    so you're not left guessing how to do a ``for`` loop.

Paver はできるだけ(同じファイルにデコレータで関数を追加するだけで)命令型プログラミングに対して宣言型の簡単なエスケープハッチで共通タスクを扱えるように設定します。あなたのプロジェクトに関連する設定オプションはビルドやデプロイ環境を構築する部品から全て同時にアクセスできます。そして全てが Python で記述されるので ``for`` ループのやり方を推測しなくて済みます。

..
    Of course, rebuilding the great infrastructure provided by tools like distutils
    makes no sense. So, Paver just uses distutils and other tools directly.

もちろん distutils のようなツールで提供された優れたインフラを再構築することには意味がありません。そのため Paver は実際に distutils やその他のツールを直接使用します。

..
    Paver also goes beyond just providing an extension mechanism for distutils.
    It adds a bunch of useful capabilities for things like working with files
    and directories, elegantly handling sample code for your documentation and 
    building bootstrap scripts to allow your software to easily be installed
    in an isolated virtualenv.

Paver は実際に distutils の拡張の仕組みも提供します。ファイルやディレクトリを操作する、サンプルコードをドキュメントの中で洗練して扱う、隔離された virtualenv 環境へソフトウェアが簡単にインストールされるようにブートストラップスクリプトをビルドするといったような便利な機能セットを追加します。

..
    I'm already using Paver for SitePen's Support service user interface
    project and I use Paver to manage Paver itself! It's been working out
    great for me, and it's set up in such a way that whatever kind of scripting
    your project needs it should be pretty simple with Paver.

私は既に SitePen のサポートでプロジェクトのユーザインタフェースで Paver を使用しています。さらに私は Paver そのものを管理するために Paver を使用しています！それは私にとってはとても便利で、プロジェクトで必要とされるどんなスクリプティングでも Paver でとても簡単に行うように設定します。

..
    Making the Switch is Easy
    -------------------------

移行を簡単にする
----------------

..
    Finally, I've put some time into making sure that moving a project from
    distutils to Paver is easy for everyone involved (people making the
    projects and people using the projects). Check out the
    :ref:`Getting Started Guide <gettingstarted>` to see an example of how
    a project moves from distutils to Paver (even maintaining the
    ``python setup.py install`` command that everyone's used to!)

最後に、誰でも(プロジェクトを作る人も使う人も)簡単に distutils から Paver へ移行する方法を紹介します。プロジェクトを distutils から Paver へ移行する方法(みんなが慣れ親しんでいる ``python setup.py install`` コマンドを維持した状態で！)の例を理解するために :ref:`スタートガイド <gettingstarted>` をチェックアウトしてください。

..
    Thanks for reading!

読んで頂いてありがとうございました！

Kevin Dangoor
May 2008
