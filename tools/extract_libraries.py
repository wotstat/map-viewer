"""Read-only extraction from the selected client; libraries are never shipped."""
import os
import sys
import zipfile

target = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'as3', 'libs')
if not os.path.isdir(target):
    os.makedirs(target)
for package in ('gui-part1.pkg', 'gui-part2.pkg'):
    with zipfile.ZipFile(os.path.join(sys.argv[1], 'res', 'packages', package)) as archive:
        for name in archive.namelist():
            if name.endswith('.swc'):
                with open(os.path.join(target, name.rsplit('/', 1)[-1]), 'wb') as output:
                    output.write(archive.read(name))
                print(name)
