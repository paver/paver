..
    ===========================================
    Paver: Easy Scripting for Software Projects
    ===========================================

===========================================================
Paver: ソフトウェアプロジェクトのための簡易スクリプティング
===========================================================

.. image:: ../_static/paver_banner.jpg
    :height: 126
    :width: 240

..
    Paver is a Python-based software project scripting tool along the
    lines of Make or Rake. It is not designed to handle the dependency
    tracking requirements of, for example, a C program. It *is* designed
    to help out with all of your other repetitive tasks (run documentation
    generators, moving files about, downloading things), all with the
    convenience of Python's syntax and massive library of code.

Paver は Make や Rake によく似た Python ベースのソフトウェアプロジェクトのスクリプティングツールです。例えば C 言語のプログラムのように必要な依存関係を追跡して扱うようには設計されていません。Python 構文と豊富なライブラリコードの利便性により、雑多な全ての繰り返しタスク(ドキュメントを生成する、関連ファイルを移動する、ダウンロードする)に対して
補助するように *設計されています* 。

..
    If you're developing applications in Python, you get even more...
    Most public Python projects use distutils or setuptools to create source
    tarballs for distribution. (Private projects can take advantage of
    this, too!) Have you ever wanted to generate the docs before building the
    source distribution? With Paver, you can, trivially. Here's a complete
    pavement.py::

もしあなたが Python でアプリケーションを開発しているなら、なおさら使用してみましょう。大半の Python のパブリックプロジェクトは再配布向けのソース tarball を作成するために distutils か setuptools を使用します(プライベートプロジェクトもこの利点を得ることができる！)。あなたはこれまでにソースディストリビューションを作成する前にドキュメントを生成したことがありますか？Paver を使えばまさにそれができます。次に完全な pavement.py があります。

::

    from paver.easy import *
    from paver.setuputils import setup
    
    setup(
        name="MyCoolProject",
        packages=['mycool'],
        version="1.0",
        url="http://www.blueskyonmars.com/",
        author="Kevin Dangoor",
        author_email="dangoor@gmail.com"
    )
    
    @task
    @needs(['html', "distutils.command.sdist"])
    def sdist():
        """Generate docs and source distribution."""
        pass

..
    With that pavement file, you can just run ``paver sdist``, and your docs
    will be rebuilt automatically before creating the source distribution.
    It's also easy to move the generated docs into some other directory
    (and, of course, you can tell Paver where your docs are stored,
    if they're not in the default location.)

この pavement ファイルを使用して、ただ ``paver sdist`` を実行するだけでドキュメントがソースディストリビューションを作成する前に自動的にリビルドされます。そして、生成したドキュメントを他のディレクトリへ移動することも簡単です(もちろん Paver にそのドキュメントをデフォルトの場所以外にどこへ置くかを教えることができます)。

..
    Features
    --------

機能
----

..
    * Build files are :ref:`just Python <justpython>`
    * :ref:`One file with one syntax <onefile>`, pavement.py, knows how to manage
      your project
    * :ref:`File operations <pathmodule>` are unbelievably easy, thanks to the 
      built-in version of Jason Orendorff's path.py.
    * Need to do something that takes 5 lines of code? 
      :ref:`It'll only take 5 lines of code. <fivelines>`.
    * Completely encompasses :ref:`distutils and setuptools  <setuptools>` so 
      that you can customize behavior as you need to.
    * Wraps :ref:`Sphinx <doctools>` for generating documentation, and adds utilities
      that make it easier to incorporate fully tested sample code.
    * Wraps :ref:`Subversion <svn>` for working with code that is checked out.
    * Wraps :ref:`virtualenv <virtualenv>` to allow you to trivially create a
      bootstrap script that gets a virtual environment up and running. This is
      a great way to install packages into a contained environment.
    * Can use all of these other libraries, but :ref:`requires none of them <nodeps>`
    * Easily transition from setup.py without making your users learn about or
      even install Paver! (See the :ref:`Getting Started Guide <gettingstarted>` 
      for an example).

* ビルドファイルは :ref:`ただの Python <justpython>` プログラムです
* :ref:`1つの構文で1つのファイル <onefile>` , pavement.py はプロジェクトの管理方法を知っています
* :ref:`File 操作 <pathmodule>` は Jason Orendorff が作成した path.py のビルトインを使用して信じられないぐらい簡単です
* 5行でできることに必要なコードは？ :ref:`やはり5行だけです <fivelines>`
* 必要に応じてカスタマイズできるように完全に :ref:`distutils と setuptools <setuptools>` を内包します
* ドキュメントを生成するために :ref:`Sphinx <doctools>` をラップして、テストされたサンプルコードを組み込み易くするためのユーティリティを追加します
* チェックアウトするコードと共に動作する :ref:`Subversion <svn>` をラップする

* 仮想環境を構築して実行するブートストラップスクリプトの作成を許容する :ref:`virtualenv <virtualenv>` をラップする、これは影響範囲が制限された環境にパッケージをインストールするための素晴らしい方法です
* これらのうち全てのライブラリを使用できますが :ref:`依存関係がありません <nodeps>`
* Paver のインストールや関連内容をユーザが学習することなく簡単に setup.py から変換します！(サンプルは :ref:`スタートガイド <gettingstarted>` を参照)

..
    See how it works! Check out the :ref:`Getting Started Guide <gettingstarted>`.

Paver がどのように動作するかを見てください！ :ref:`スタートガイド <gettingstarted>` をチェックアウトしよう。

..
    Paver was created by `Kevin Dangoor <http://blueskyonmars.com>`_ of `SitePen <http://sitepen.com>`_.

Paver は `SitePen <http://sitepen.com>`_ に所属する `Kevin Dangoor <http://blueskyonmars.com>`_ が作成しました。

..
    Status
    ------

ステータス
----------

..
    Paver has been in use in production settings since mid-2008, and significant 
    attention is paid to backwards compatibility since the release of 1.0.

Paver は2008年中頃に本番環境で使用されています。そして1.0 リリースから後方互換性に大きな注意が払われています。

..
    See the :ref:`changelog <changelog>` for more information about recent improvements.
 
最新の改善内容は :ref:`changelog <changelog>` を参照してください。 

..
    Installation
    ------------

インストール
------------

..
    The easiest way to get Paver is if you have setuptools_ installed.

setuptools_ をインストールしているなら Paver をインストールする最も簡単な方法です。

``easy_install Paver``

..
    Without setuptools, it's still pretty easy. Download the Paver .tgz file from 
    `Paver's Cheeseshop page`_, untar it and run:

setuptools がなくても本当に簡単です。 `Paver の Cheeseshop ページ`_ から Paver の .tgz ファイルをダウンロードして解凍して次のように実行してください。

``python setup.py install``

.. _Paver の Cheeseshop ページ: http://pypi.python.org/pypi/Paver/
.. _setuptools: http://peak.telecommunity.com/DevCenter/EasyInstall

..
    Help and Development
    --------------------

ヘルプと開発
------------

..
    You can get help from the `mailing list`_.

困ったときは `メーリングリスト`_ で質問することができます。

..
    If you'd like to help out with Paver, you can check the code out from Googlecode:

Paver を支援したいなら Googlecode からそのコードをチェックアウトすることができます。

``svn checkout http://paver.googlecode.com/svn/trunk/ paver-read-only``

..
    You can also take a look at `Paver's project page on Googlecode <http://code.google.com/p/paver/>`_.

`Googlecode の Paver プロジェクト <http://code.google.com/p/paver/>`_ で見ることもできます。

.. _メーリングリスト: http://groups.google.com/group/paver

..
    License
    -------

ライセンス
----------

..
    Paver is licensed under a BSD license. See the LICENSE.txt file in the 
    distribution.

Paver は BSD ライセンスを採用します。配布に関しては LICENSE.txt を参照してください。

..
    Contents
    --------

コンテンツ
----------

.. toctree::
   :maxdepth: 2
   
   foreword
   features
   getting_started
   pavement
   paverstdlib
   cmdline
   tips
   articles
   changelog
   credits

..
    Indices and tables
    ------------------

インデックスとテーブル
----------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

