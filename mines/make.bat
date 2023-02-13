pip install pyinstaller

pyinstaller.exe mines.py --windowed --noconsole

mkdir dist\mines\img
copy img\* dist\mines\img
copy lib\libmines.dll dist\mines\libmines.dll
