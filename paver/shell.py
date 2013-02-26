import subprocess
import sys
from paver.easy import error, dry


def sh(command, capture=False, ignore_error=False, cwd=None):
    """Runs an external command. If capture is True, the output of the
    command will be captured and returned as a string.  If the command
    has a non-zero return code raise a BuildFailure. You can pass
    ignore_error=True to allow non-zero return codes to be allowed to
    pass silently, silently into the night.  If you pass cwd='some/path'
    paver will chdir to 'some/path' before exectuting the command.

    If the dry_run option is True, the command will not
    actually be run."""
    def runpipe():
        kwargs = {'shell': True, 'cwd': cwd}
        if capture:
            kwargs['stderr'] = subprocess.STDOUT
            kwargs['stdout'] = subprocess.PIPE
        p = subprocess.Popen(command, **kwargs)
        p_stdout = p.communicate()[0]
        if p_stdout is not None:
            p_stdout = p_stdout.decode(sys.getdefaultencoding())
        if p.returncode and not ignore_error:
            if capture and p_stdout is not None:
                error(p_stdout)
            raise BuildFailure("Subprocess return code: %d" % p.returncode)

        if capture:
            return p_stdout

    return dry(command, runpipe)
