
import sys
from pypsi import utils
import threading


class BasePypsiThread(threading.Thread):

    def __init__(self, stdin=None, stdout=None, stderr=None, **kwargs):
        super(BasePypsiThread, self).__init__(**kwargs)
        self.stdin, self.stdout, self.stderr = stdin, stdout, stderr

    def setup_io(self):
        if self.stdin and isinstance(sys.stdin, utils,ThreadLocalProxy):
            sys.stdin._add_proxy(self.stdin)

        if self.stdout and isinstance(sys.stdout, utils,ThreadLocalProxy):
            sys.stdout._add_proxy(self.stdout)

        if self.stderr and isinstance(sys.stderr, utils,ThreadLocalProxy):
            sys.stderr._add_proxy(self.stderr)

    def cleanup(self):
        if isinstance(sys.stdin, utils,ThreadLocalProxy):
            if sys.stdin.fileno() != 0:
                utils.close_input_pipe(sys.stdin._get())
            sys.stdin._remove_proxy()
        if isinstance(sys.stdout, utils,ThreadLocalProxy):
            if sys.stdout.fileno() != 1:
                utils.close_output_pipe(sys.stdout._get())
            sys.stdout._remove_proxy()
        if isinstance(sys.stderr, utils,ThreadLocalProxy):
            if sys.stderr.fileno() != 2:
                utils.close_output_pipe(sys.stderr._get())
            sys.stderr._remove_proxy()

