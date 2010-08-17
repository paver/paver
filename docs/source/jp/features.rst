..
    Paver's Features
    ================

Paver の機能
============

.. _justpython:

..
    Files Are Just Python
    ---------------------

ファイルはただの Python プログラム
----------------------------------

..
    Python has a very concise, readable syntax. There's no need to create some
    mini-language for describing your builds. Quite often it seems like these
    mini-languages are missing features that you need. By using Python as its
    syntax, you can always be sure that you can express whatever it is you
    need to do easily. A for loop is just a for loop::

Python はとても簡潔で読み易い構文を持っています。わざわざビルドを記述するためのミニ言語を作成する必要がありません。こういったミニ言語は必要な機能がなくて不自由することがよくあるように思います。Python とその構文を使用することで、いつでも何でもやりたいことを簡単に表現できるということを保証できます。例えば for ループはただの for ループです。

::

    for fn in ["f1.txt", "f2.txt", "f3.txt"]:
        p = path(fn)
        p.remove()

.. _onefile:

..
    One File with One Syntax
    ------------------------

1つの構文で1つのファイル
------------------------

..
    When putting together a Python project today, you get into a collection of
    tools to get the job done. distutils and setuptools are the standards for
    getting packages put together. zc.buildout and virtualenv are used for
    installation into isolated deployment environments. Sphinx provides
    a great way to document Python projects.

今日 Python プロジェクトを構成する場合、ツールのあるコレクションを取得してそのジョブを行います。distutils や setuptools はパッケージを取得してまとめて配置するための標準的なツールです。zc.buildout や virtualenv は隔離したデプロイ環境にインストールするために使用されます。Sphinx は Python プロジェクトのドキュメントを書くための優れた方法を提供します。

..
    To put together a total system, you need each of these parts. But they
    each have their own way of working. The goal with the 
    :ref:`Paver Standard Library <stdlib>`
    is to make the common tools have a more integrated feel, so you don't
    have to guess as much about how to get something done.

システム全体を構成するためにこれらのツールが必要です。しかし、これらのツールはそれぞれ独自の方法で動作します。 :ref:`Paver 標準ライブラリ <stdlib>` の目的はもっと統合された感覚で使える共通ツールを作ることです。そのため、やりたいことを行う方法を推測する必要はありません。

..
    As of today, Paver is tightly integrated with distutils and setuptools,
    and can easily work as a drop-in, more easily scriptable replacement for
    setup.py.

今日では Paver は distutils と setuptools でしっかりと結合して、他のツールを簡単に取り付けられるように動作し、もっと簡単にスクリプトが書ける setup.py に置き換わるものです。

.. _pathmodule:

..
    Easy file operations
    --------------------

簡単なファイル操作
------------------

..
    Paver includes a customized version of Jason Orendorff's awesome path.py
    module. Operations on files and directories could hardly be easier,
    and the methods have been modified to support "dry run" behavior.

Paver は Jason Orendorff がカスタマイズした素晴らしい path.py モジュールを含みます。ファイルやディレクトリの操作がこれ以上簡単にはならないです。またそのメソッドは "dry run" 操作をサポートするように変更されています。

.. _fivelines:

..
    Small bits of behavior take small amounts of work
    -------------------------------------------------

小さな作業をするのに小さな変更
------------------------------

..
    Imagine you need to do something that will take you 5 lines of Python code.
    With some of the tools that Paver augments, it'll take you a lot more
    effort than those 5 lines of code. You have to read about the API for
    making new commands or recipes or otherwise extending the package.
    The goal when using Paver is to have a five line change take about five
    lines to make.

Python コードだと5行でできることを行うことを想像してください。Paver が使用するツールだと、それは5行のコード以上に労力が必要になります。あなたは新たなコマンドを作るためにその API、レシピ、もしくはパッケージの拡張方法について調べなければなりません。Paver を使用する目的は5行で行えることは5行の変更で済むことです。

..
    For example, let's say you need to perform some extra work when and 'sdist'
    is run. Good luck figuring out the best way to do that with distutils. With
    Paver, it's just::

例えば 'sdist' が実行されるときに追加の作業を実行する必要があると仮定します。distutils で行うための最善の方法が解明できるようにがんばってください。Paver だと次のように記述するだけです。

::

    @task
    def sdist():
        # perform fancy file manipulations
        blah.blah.blah()
        
        # *now* run the sdist
        call_task("setuptools.command.sdist")

.. _nodeps:

..
    Can Take Advantage of Libraries But Doesn't Require Them
    --------------------------------------------------------

ライブラリは利用しますが依存はしません
--------------------------------------

..
    The Paver Standard Library includes support for a lot of the common tools,
    but you don't necessarily need all of those tools, and certainly not on
    every project. Paver is designed to have no other requirements but to
    automatically take advantage of other tools when they're available.

Paver 標準ライブラリは多くの共通ツールのサポートを含みますが、そういった全てのツールは全てのプロジェクトで必要ありません。Paver はそれらのツールに依存せずに利用可能な場合に自動的に利用するように設計されています。
