import pytest
import sys
sys.path.append("..")
from sean.error import *
from sean import wrap, wrap_module


def test_wrap_Rados():
    a = wrap.rados.Rados()
    assert a['sean'] == 'wc'


def test_wrap_module():
    with pytest.raises(WrapError) as e:
        a = wrap_module.Rados()
    