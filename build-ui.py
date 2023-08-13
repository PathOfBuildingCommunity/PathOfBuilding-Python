"""
Creates .py script from .ui files in the /src/ui/ folder
"""

import os
import sys
from pathlib import Path
from subprocess import Popen, PIPE

import PySide6


def get_uic_exe():
    pyside_dir = Path(PySide6.__file__).resolve().parent
    print(sys.platform)
    # Don't know if this is overkill but just something that could be
    # utilized if running on different machines. (L28 too)
    #
    # Could use some further tweaking if that usecase above is correct.
    if sys.platform != "win32":
        exe = pyside_dir / "Qt" / "libexec" / "uic"
    else:
        exe = pyside_dir / "uic.exe"
    print(exe)
    return exe


def get_rcc_exe():
    pyside_dir = Path(PySide6.__file__).resolve().parent
    if sys.platform != "win32":
        exe = pyside_dir / "Qt" / "libexec" / "rcc"
    else:
        exe = pyside_dir / "rcc.exe"
    return exe


def generate_py_from_ui():
    exe = get_uic_exe()
    for path in Path("./Assets/ui_files/").glob("*.ui"):
        Path("src", "ui").mkdir(exist_ok=True)
        outpath = Path("src", "ui", path.name).with_suffix(".py")
        ui_time = os.path.getmtime(path)
        if os.path.isfile(outpath) and ui_time == os.path.getmtime(outpath):
            print(f"skipping {outpath}, exists and no change.")
            pass
        else:
            print(path, ">>", outpath)

            cmd = [os.fspath(exe), "-g", "python", str(path), "-o", str(outpath)]
            proc = Popen(cmd, stderr=PIPE)
            out, err = proc.communicate()
            if err:
                msg = err.decode("utf-8")
                command = " ".join(cmd)
                print(f"Error: {msg}\nwhile executing '{command}'")
            else:
                os.utime(outpath, (ui_time, ui_time))


def generate_qrc():
    exe = get_rcc_exe()
    path = "./Assets/PoB.qrc"
    outpath = Path("src", "PoB_rc").with_suffix(".py")
    ui_time = os.path.getmtime(path)
    if os.path.isfile(outpath) and ui_time == os.path.getmtime(outpath):
        print(f"skipping {outpath}, exists and no change.")
        pass
    else:
        print(path, ">>", outpath)

        cmd = [os.fspath(exe), "-g", "python", str(path), "-o", str(outpath)]
        proc = Popen(cmd, stderr=PIPE)
        out, err = proc.communicate()
        if err:
            msg = err.decode("utf-8")
            command = " ".join(cmd)
            print(f"Error: {msg}\nwhile executing '{command}'")
        else:
            os.utime(outpath, (ui_time, ui_time))


generate_py_from_ui()
generate_qrc()
