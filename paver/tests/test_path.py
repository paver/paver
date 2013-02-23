# -*- coding: utf-8 -*-
import paver.path
import os.path

def test_join_on_unicode_path():
    merged = b'something/ö'
    assert merged == os.path.join(paver.path.path(b'something'), u'ö')



