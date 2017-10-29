from paver.easy import error, dry, BuildFailure

import subprocess
import shlex
import sys

try:
    _shlex_quote = shlex.quote
except AttributeError:
    # Backport from Python 3.x. This suite is accordingly under the PSF
    # License rather than the BSD license used for the rest of the code.
    import re
    _find_unsafe = re.compile(r'[^\w@%+=:,./-]').search

    def _shlex_quote(s):
        """Return a shell-escaped version of the string *s*."""
        if not s:
            return "''"
        if _find_unsafe(s) is None:
            return s

        # use single quotes, and put single quotes into double quotes
        # the string $'b is then quoted as '$'"'"'b'
        return "'" + s.replace("'", "'\"'\"'") + "'"


def sh(command, capture=False, ignore_error=False, cwd=None, env=None):
    """Runs an external command. If capture is True, the output of the
    command will be captured and returned as a string.  If the command
    has a non-zero return code raise a BuildFailure. You can pass
    ignore_error=True to allow non-zero return codes to be allowed to
    pass silently, silently into the night.  If you pass cwd='some/path'
    paver will chdir to 'some/path' before exectuting the command.

    If the dry_run option is True, the command will not
    actually be run.
    
    env is a dictionary of environment variables. Refer to subprocess.Popen's
    documentation for further information on this."""
    if isinstance(command, (list, tuple)):
        command = ' '.join([_shlex_quote(c) for c in command])

    def runpipe():
        kwargs = {'shell': True, 'cwd': cwd, 'env': env}
        if capture:
            kwargs['stderr'] = subprocess.STDOUT
            kwargs['stdout'] = subprocess.PIPE
        p = subprocess.Popen(command, **kwargs)
        p_stdout = p.communicate()[0]
        if p_stdout is not None:
            p_stdout = p_stdout.decode(sys.getdefaultencoding(), 'ignore')
        if p.returncode and not ignore_error:
            if capture and p_stdout is not None:
                error(p_stdout)
            raise BuildFailure("Subprocess return code: %d" % p.returncode)

        if capture:
            return p_stdout

    return dry(command, runpipe)
