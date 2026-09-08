import os
import py_compile
import sys
import zipfile
version = sys.argv[1]
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
stage = os.path.join(root, '.build')
with open(os.path.join(stage, 'meta.xml'), 'wb') as output:
    output.write('<root><id>wotstat.local-maps</id><version>%s</version><name>Local Maps RU</name><description>Local map viewer for MT RU 1.45</description></root>' % version)
for directory, unused, files in os.walk(stage):
    for name in files:
        if name.endswith('.py'):
            filename = os.path.join(directory, name)
            with open(filename, 'rb') as source:
                data = source.read().replace('{{VERSION}}', version)
            with open(filename, 'wb') as target:
                target.write(data)
            relative = os.path.relpath(filename, stage).replace('\\', '/')
            py_compile.compile(filename, dfile=relative, doraise=True)
artifact = os.path.join(root, 'dist', 'wotstat.local-maps_%s.mtmod' % version)
with zipfile.ZipFile(artifact, 'w', zipfile.ZIP_STORED) as archive:
    for directory, unused, files in os.walk(stage):
        for name in files:
            if not name.endswith('.py'):
                path = os.path.join(directory, name)
                archive.write(path, os.path.relpath(path, stage).replace('\\', '/'))
print(artifact)
