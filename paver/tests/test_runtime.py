from paver import runtime
from paver.tests.mock import patch, Mock
import subprocess # for runtime.sh tests


@patch(subprocess, "call")
def test_sh_raises_BuildFailure(call):
    call.return_value = 1
    try:
        runtime.sh('foo')
    except runtime.BuildFailure, e:
        assert e.args == (1, )
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
        runtime.sh('foo', capture=True)
    except runtime.BuildFailure, e:
        assert e.args == (1, )
    else:
        assert False, 'Failed to raise BuildFailure'

    assert popen.called
    assert popen.call_args[0][0] == 'foo'
    assert popen.call_args[1]['shell'] == True
    assert popen.call_args[1]['stdout'] == subprocess.PIPE

@patch(subprocess, "call")
def test_sh_ignores_error(call):
    call.return_value = 1
    runtime.sh('foo', ignore_error=True)

    assert call.called
    assert call.call_args[0][0] == 'foo'
    assert call.call_args[1]['shell'] == True

@patch(subprocess, "Popen")
def test_sh_ignores_with_capture(popen):
    popen.return_value = Mock()
    popen.return_value.returncode = 1
    runtime.sh('foo', capture=True, ignore_error=True)

    assert popen.called
    assert popen.call_args[0][0] == 'foo'
    assert popen.call_args[1]['shell'] == True
    assert popen.call_args[1]['stdout'] == subprocess.PIPE

