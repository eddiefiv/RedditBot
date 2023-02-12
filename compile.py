import sys

from cx_Freeze import setup, Executable

build_exe_options = {'packages': ['os']}

base = None

if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name="Reddit Bot",
    version="1.1",
    description="Reddit Bot",
    options={"build_exe": build_exe_options},
    executables=[Executable("main.py", base=base)]
)