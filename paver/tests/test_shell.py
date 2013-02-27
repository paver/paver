import sys
from paver.deps.six import b
from mock import patch, Mock
from paver import easy
from subprocess import PIPE, STDOUT

@patch('subprocess.Popen')
def test_sh_raises_BuildFailure(popen):
    popen.return_value.returncode = 1
    popen.return_value.communicate.return_value = [b('some stderr')]

    try:
        easy.sh('foo')
    except easy.BuildFailure:
        e = sys.exc_info()[1]
        args = e.args
        assert args == ('Subprocess return code: 1', )
    else:
        assert False, 'Failed to raise BuildFailure'

    assert popen.called
    assert popen.call_args[0][0] == 'foo'
    assert popen.call_args[1]['shell'] == True
    assert 'stdout' not in popen.call_args[1]

@patch('paver.shell.error')
@patch('subprocess.Popen')
def test_sh_with_capture_raises_BuildFailure(popen, error):
    popen.return_value.returncode = 1
    popen.return_value.communicate.return_value = [b('some stderr')]
    try:
        easy.sh('foo', capture=True)
    except easy.BuildFailure:
        e = sys.exc_info()[1]
        args = e.args
        assert args == ('Subprocess return code: 1', )
    else:
        assert False, 'Failed to raise BuildFailure'

    assert popen.called
    assert popen.call_args[0][0] == 'foo'
    assert popen.call_args[1]['shell'] == True
    assert popen.call_args[1]['stdout'] == PIPE
    assert popen.call_args[1]['stderr'] == STDOUT

    assert error.called
    assert error.call_args == (('some stderr', ), {})

@patch('subprocess.Popen')
def test_sh_ignores_error(popen):
    popen.return_value.communicate.return_value = [b('some stderr')]
    popen.return_value.returncode = 1
    easy.sh('foo', ignore_error=True)

    assert popen.called
    assert popen.call_args[0][0] == 'foo'
    assert popen.call_args[1]['shell'] == True
    assert 'stdout' not in popen.call_args[1]

@patch('subprocess.Popen')
def test_sh_ignores_error_with_capture(popen):
    popen.return_value.returncode = 1
    popen.return_value.communicate.return_value = [b('some stderr')]
    easy.sh('foo', capture=True, ignore_error=True)

    assert popen.called
    assert popen.call_args[0][0] == 'foo'
    assert popen.call_args[1]['shell'] == True
    assert popen.call_args[1]['stdout'] == PIPE
    assert popen.call_args[1]['stderr'] == STDOUT

@patch('subprocess.Popen')
def test_sh_with_multi_command(popen):
    popen.return_value.returncode = 0

    easy.sh(['foo', ' bar', 'fi"zz'])

    assert popen.called
    assert popen.call_args[0][0] == "foo ' bar' 'fi\"zz'"
    assert popen.call_args[1]['shell'] == True
