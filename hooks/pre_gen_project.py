import sys
import re

PY_VER_RE = re.compile(r"^\d+\.\d+$")

python_version = "{{ cookiecutter.python_version }}"

if not PY_VER_RE.match(python_version):
    raise ValueError(
        f"python_version must be like '3.12', got: {python_version}"
    )

# Warn if current interpreter's major.minor differs
cur_ver = f"{sys.version_info.major}.{sys.version_info.minor}"
if cur_ver != python_version:
    sys.stderr.write(
        f"[cookiecutter] WARNING: Your current Python is {cur_ver}, "
        f"but cookiecutter.python_version is {python_version}.\n"
        "We'll still generate the project; the post-gen hook can create a venv.\n"
    )
