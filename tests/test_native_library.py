import os
import struct
import sys
import unittest
import zlib

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'res', 'scripts', 'client', 'gui', 'mods'))
from wotstat_local_maps.native_library import codeLibrary


def tag(kind, data=b''):
    if len(data) < 63:
        return struct.pack('<H', kind << 6 | len(data)) + data
    return struct.pack('<HI', kind << 6 | 63, len(data)) + data


def movie(body, compressed=True):
    return (b'CWS' if compressed else b'FWS') + b'\x11' + struct.pack('<I', len(body) + 8) + (zlib.compress(body) if compressed else body)


class NativeLibraryTest(unittest.TestCase):
    def test_keeps_bytecode_without_instantiating_document_or_assets(self):
        header = b'\x08\x00\x00\x18\x01\x00'
        attributes = tag(69, b'\x08\x00\x00\x00')
        bytecode = tag(82, b'\x00' * 120)
        body = header + attributes + tag(76, b'\x01\x00\x00\x00LobbyApplication\x00') + tag(87, b'asset') + bytecode + tag(1) + tag(0)
        for compressed in (False, True):
            result = codeLibrary(movie(body, compressed))
            self.assertEqual(result[:4], b'CWS\x11')
            decoded = zlib.decompress(result[8:])
            self.assertEqual(decoded, header + attributes + bytecode + tag(1) + tag(0))
            self.assertEqual(struct.unpack('<I', result[4:8])[0], len(decoded) + 8)

    def test_rejects_truncated_or_invalid_resources(self):
        header = b'\x08\x00\x00\x18\x01\x00'
        for data in (b'', b'ZWS' + b'\x00' * 10, movie(header + struct.pack('<H', 82 << 6 | 62)), movie(header + struct.pack('<H', 82 << 6 | 63)), movie(header + tag(82, b'abc') + tag(0))[:-2]):
            with self.assertRaises(ValueError):
                codeLibrary(data)

    def test_rejects_resource_without_code(self):
        with self.assertRaises(ValueError):
            codeLibrary(movie(b'\x08\x00\x00\x18\x01\x00' + tag(0)))
