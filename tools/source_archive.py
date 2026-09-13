"""Package project sources and documentation."""
import os
import sys
import zipfile

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
version = sys.argv[1]
destination = os.path.join(root, 'dist')
if not os.path.isdir(destination):
    os.makedirs(destination)
artifact = os.path.join(destination, 'wotstat.map-viewer_%s_source.zip' % version)
folders = ('res', 'as3/src', 'as3/libs', 'tools', 'tests', 'docs', '.vscode', '.github')
files = ['README.md', '.gitignore', 'build.ps1', 'as3/asconfig.json']
for folder in folders:
    for directory, unused, names in os.walk(os.path.join(root, folder)):
        for name in names:
            if name.endswith(('.pyc', '.pyo')):
                continue
            files.append(os.path.relpath(os.path.join(directory, name), root))
with zipfile.ZipFile(artifact, 'w', zipfile.ZIP_DEFLATED) as archive:
    for relative in sorted(files):
        archive.write(os.path.join(root, relative), relative.replace('\\', '/'))
print(artifact)
