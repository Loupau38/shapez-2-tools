import os
command = "pyinstaller --onefile --console"
for dirEntry in os.scandir("."):
    if dirEntry.is_file() and dirEntry.name.endswith((".png",".ttf")):
        command += ' --add-data "'
        command += dirEntry.path
        command += ';."'
for dirEntry in os.scandir(os.path.expandvars("%LOCALAPPDATA%\\Programs\\Python\\Python313\\Lib\\site-packages\\shapez2\\gameFiles")):
    command += ' --add-data "'
    command += dirEntry.path
    command += ';./shapez2/gameFiles"'
command += ' "./OL tracker.py"'
print("-----")
print()
print(command)
print()
print("-----")