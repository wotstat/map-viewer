"""Inspect original SWF symbol names without modifying resources."""
import struct
import sys
import zipfile
import zlib
for package in ('gui-part1.pkg', 'gui-part2.pkg'):
    archive = zipfile.ZipFile('E:/Games/Tanki/res/packages/' + package)
    for filename in sys.argv[1:]:
        name = 'gui/flash/' + filename
        if name not in archive.namelist():
            continue
        data = archive.read(name)
        body = zlib.decompress(data[8:]) if data[:3] == 'CWS' else data[8:]
        pos = (5 + 4 * (ord(body[0]) >> 3) + 7) // 8 + 4
        print(filename)
        while pos + 2 <= len(body):
            tag = struct.unpack_from('<H', body, pos)[0]
            pos += 2
            size = tag & 63
            if size == 63:
                size = struct.unpack_from('<I', body, pos)[0]
                pos += 4
            if tag >> 6 in (57, 71):
                print('IMPORT', body[pos:pos + size].split('\0', 1)[0])
            if tag >> 6 in (56, 76):
                section = body[pos:pos + size]
                count = struct.unpack_from('<H', section)[0]
                offset = 2
                for unused in range(count):
                    symbolID = struct.unpack_from('<H', section, offset)[0]
                    end = section.index('\0', offset + 2)
                    symbol = section[offset + 2:end]
                    if any(x in symbol.lower() for x in ('minimap', 'training', 'ingame', 'drop')) or symbolID == 0:
                        print(symbolID, symbol)
                    offset = end + 1
            pos += size
