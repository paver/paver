# -*- coding: utf-8 -*-
import paver.path

import sys
import os.path

def test_join_on_unicode_path():
    # This is why we should drop 2.5 asap :]
    # b'' strings are not supported in 2.5, while u'' string are not supported in 3.2
    # -- even syntactically, so if will not help you here
    if sys.version_info[0] < 3:
        expected = 'something/\xc3\xb6'
        unicode_o = '\xc3\xb6'.decode('utf-8')

        # path.py on py2 is inheriting from str instead of unicode under this
        # circumstances, therefore we have to expect string
        if os.path.supports_unicode_filenames:
            expected.decode('utf-8')

    else:
        expected = 'something/ö'
        unicode_o = 'ö'

    assert expected == os.path.join(paver.path.path('something'), unicode_o)



