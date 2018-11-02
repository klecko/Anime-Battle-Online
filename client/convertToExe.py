from cx_Freeze import setup, Executable
import sys

base = None
if (sys.platform == "win32"):
    base = "Win32GUI"

setup( name = "Juego", version = "0.1", description = "Juego by KleSoft", executables = [Executable("multiplayergame_clientv2.py", base=base)]) #no se abre cmd
#setup( name = "Juego", version = "0.1", description = "Juego by KleSoft", executables = [Executable("multiplayergame_clientv2.py")]) #si se abre cmd
