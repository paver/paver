from paver import easy
from paver.tests.mock import patch, Mock
import subprocess # for easy.sh tests


@patch(subprocess, "call")
def test_sh_raises_BuildFailure(call):
    call.return_value = 1
    try:
        easy.sh('foo')
    except easy.BuildFailure, e:
        args = e.args
        assert args == ('Subprocess return code: 1', )
    else:
        assert False, 'Failed to raise BuildFailure'

    assert call.called
    assert call.call_args[0][0] == 'foo'
    assert call.call_args[1]['shell'] == True

@patch(subprocess, "Popen")
def test_sh_with_capture_raises_BuildFailure(popen):
    popen.return_value = Mock()
    popen.return_value.returncode = 1
    try:
        easy.sh('foo', capture=True)
    except easy.BuildFailure, e:
        args = e.args
        assert args == (1, )
    else:
        assert False, 'Failed to raise BuildFailure'

    assert popen.called
    assert popen.call_args[0][0] == 'foo'
    assert popen.call_args[1]['shell'] == True
    assert popen.call_args[1]['stdout'] == subprocess.PIPE

@patch(subprocess, "call")
def test_sh_ignores_error(call):
    call.return_value = 1
    easy.sh('foo', ignore_error=True)

    assert call.called
    assert call.call_args[0][0] == 'foo'
    assert call.call_args[1]['shell'] == True

@patch(subprocess, "Popen")
def test_sh_ignores_with_capture(popen):
    popen.return_value = Mock()
    popen.return_value.returncode = 1
    easy.sh('foo', capture=True, ignore_error=True)

    assert popen.called
    assert popen.call_args[0][0] == 'foo'
    assert popen.call_args[1]['shell'] == True
    assert popen.call_args[1]['stdout'] == subprocess.PIPE

