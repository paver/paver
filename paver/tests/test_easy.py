from paver import easy
from paver.tests.mock import patch, Mock
import subprocess # for easy.sh tests


@patch(subprocess, "Popen")
def test_sh_raises_BuildFailure(popen):
    popen.return_value = Mock()
    popen.return_value.returncode = 1
    popen.return_value.communicate = Mock()
    popen.return_value.communicate.return_value = ['some stderr']

    try:
        easy.sh('foo')
    except easy.BuildFailure, e:
        args = e.args
        assert args == ('Subprocess return code: 1', )
    else:
        assert False, 'Failed to raise BuildFailure'

    assert popen.called
    assert popen.call_args[0][0] == 'foo'
    assert popen.call_args[1]['shell'] == True
    assert 'stdout' not in popen.call_args[1]

@patch(subprocess, "Popen")
@patch(easy, "error")
def test_sh_with_capture_raises_BuildFailure(popen, error):
    popen.return_value = Mock()
    popen.return_value.returncode = 1
    popen.return_value.communicate = Mock()
    popen.return_value.communicate.return_value = ['some stderr']
    try:
        easy.sh('foo', capture=True)
    except easy.BuildFailure, e:
        args = e.args
        assert args == ('Subprocess return code: 1', )
    else:
        assert False, 'Failed to raise BuildFailure'

    assert popen.called
    assert popen.call_args[0][0] == 'foo'
    assert popen.call_args[1]['shell'] == True
    assert popen.call_args[1]['stdout'] == subprocess.PIPE
    assert popen.call_args[1]['stderr'] == subprocess.STDOUT

    assert error.called
    assert error.call_args == (('some stderr', ), {})

@patch(subprocess, "Popen")
def test_sh_ignores_error(popen):
    popen.return_value = Mock()
    popen.return_value.communicate = Mock()
    popen.return_value.communicate.return_value = ['some stderr']
    popen.return_value.returncode = 1
    easy.sh('foo', ignore_error=True)

    assert popen.called
    assert popen.call_args[0][0] == 'foo'
    assert popen.call_args[1]['shell'] == True
    assert 'stdout' not in popen.call_args[1]

@patch(subprocess, "Popen")
def test_sh_ignores_error_with_capture(popen):
    popen.return_value = Mock()
    popen.return_value.returncode = 1
    popen.return_value.communicate = Mock()
    popen.return_value.communicate.return_value = ['some stderr']
    easy.sh('foo', capture=True, ignore_error=True)

    assert popen.called
    assert popen.call_args[0][0] == 'foo'
    assert popen.call_args[1]['shell'] == True
    assert popen.call_args[1]['stdout'] == subprocess.PIPE
    assert popen.call_args[1]['stderr'] == subprocess.STDOUT
