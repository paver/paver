# -*- coding: utf-8 -*-
import paver.path

import sys
import os.path

def test_join_on_unicode_path():
    merged = b'something/\xc3\xb6'.decode('utf-8') # there is ö after something
    if not os.path.supports_unicode_filenames and sys.version_info[0] < 3:
        merged = merged.encode('utf-8')
    assert merged == os.path.join(paver.path.path('something'), (b'\xc3\xb6').decode('utf-8'))



