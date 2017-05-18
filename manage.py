#!/usr/bin/python
import os
import sys

# BEGIN activacte virtualenv
from project.settings import PROJECT_DIR, normpath

try:
    activate_path = normpath(PROJECT_DIR, 'env/bin/activate_this.py')
    with open(activate_path) as f:
        code = compile(f.read(), "somefile.py", 'exec')
        exec(code, dict(__file__=activate_path))  # noqa
except IOError:
    print("E: virtualenv must be installed to PROJECT_DIR/env")
# END activacte virtualenv

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
