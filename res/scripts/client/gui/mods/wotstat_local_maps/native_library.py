"""Read native class definitions without running the lobby document timeline."""
import struct
import zlib


def codeLibrary(movie):
    if len(movie) < 9 or movie[:3] not in (b'CWS', b'FWS'):
        raise ValueError('Unsupported native SWF header')
    try:
        body = zlib.decompress(movie[8:]) if movie[:3] == b'CWS' else movie[8:]
    except zlib.error:
        raise ValueError('Invalid native SWF compression')
    if len(body) + 8 != struct.unpack('<I', movie[4:8])[0] or not body:
        raise ValueError('Invalid native SWF length')
    # RECT uses five bits for Nbits, then four signed coordinates. The frame
    # rate and count follow its final byte boundary.
    nbits = bytearray(body[:1])[0] >> 3
    offset = (5 + 4 * nbits + 7) // 8 + 4
    if offset > len(body):
        raise ValueError('Truncated native SWF frame header')
    parts = [body[:offset]]
    hasCode = ended = False
    while offset + 2 <= len(body):
        start = offset
        record = struct.unpack('<H', body[offset:offset + 2])[0]
        offset += 2
        size = record & 63
        kind = record >> 6
        if size == 63:
            if offset + 4 > len(body):
                raise ValueError('Truncated native SWF tag header')
            size = struct.unpack('<I', body[offset:offset + 4])[0]
            offset += 4
        if offset + size > len(body):
            raise ValueError('Truncated native SWF tag')
        if kind in (69, 82):  # FileAttributes and DoABC; no SymbolClass root.
            parts.append(body[start:offset + size])
            hasCode = hasCode or kind == 82
        offset += size
        if kind == 0:
            ended = True
            break
    if not hasCode or not ended:
        raise ValueError('Native SWF contains no complete class library')
    parts.append(struct.pack('<HH', 64, 0))  # Empty frame and End.
    result = b''.join(parts)
    return b'CWS' + movie[3:4] + struct.pack('<I', len(result) + 8) + zlib.compress(result)
