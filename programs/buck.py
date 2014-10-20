#!/usr/bin/env python
from __future__ import print_function
import os
import signal
import sys
from buck_repo import BuckRepo, BuckRepoException, Command
from buck_project import BuckProject, NoBuckConfigFoundException
from tracing import Tracing
import uuid

THIS_DIR = os.path.dirname(os.path.realpath(__file__))


def main():
    try:
        java_home = os.getenv("JAVA_HOME", "")
        path = os.getenv("PATH", "")
        if java_home:
            pathsep = os.pathsep
            if sys.platform == 'cygwin':
                pathsep = ';'
            os.environ["PATH"] = os.path.join(java_home, 'bin') + pathsep + path

        tracing_dir = None
        build_id = str(uuid.uuid4())
        with Tracing("main"):
            with BuckProject.from_current_dir() as project:
                tracing_dir = os.path.join(project.get_buck_out_log_dir(), 'traces')
                bin_dir = os.path.join(os.path.dirname(THIS_DIR), 'bin')
                buck_repo = BuckRepo(bin_dir, project, Command.BUCK)
                exit_code = buck_repo.launch_buck(build_id)
                sys.exit(exit_code)
    finally:
        if tracing_dir:
            Tracing.write_to_dir(tracing_dir, build_id)

if __name__ == "__main__":
    try:
        main()
    except (BuckRepoException, NoBuckConfigFoundException) as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(1)
