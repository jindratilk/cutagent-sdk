"""Remove machine-specific evidence from the reviewed standalone projection."""
import hashlib
import re
import struct


def sanitize_text(text):
    def evidence(match):
        path = match.group()
        suffix = path.rsplit('.', 1)[-1] if '.' in path.rsplit('/', 1)[-1] else 'json'
        suffix = suffix if re.fullmatch(r'[a-zA-Z0-9]{1,8}', suffix) else 'json'
        identity = hashlib.sha256(path.encode()).hexdigest()[:12]
        return '/tmp/cutagent-public-fixtures/evidence-' + identity + '.' + suffix

    text = re.sub(r'/tmp/[^\s\"\x27<>]*202\d[^\s\"\x27<>]*', evidence, text)
    text = re.sub(r'CUTAGENT_[A-Z0-9_]*20\d{6}_\d{6}', 'CUTAGENT_PUBLIC_FIXTURE', text)
    text = text.replace('/Users/' + 'guest/Projects/CUTAGENT_PUBLIC_FIXTURE', '/Users/<user>/Projects/<project>')
    text = re.sub(r'CutAgent MC [^\"\n]*20\d{6}-\d{6}', 'CutAgent multicam fixture', text)
    return text


def sanitize_dynamics_config(data):
    """Keep serialized field lengths while replacing donor-machine paths."""
    import zstandard
    offset = data.find(bytes.fromhex('28b52ffd'))
    if offset != 44 or struct.unpack_from('>I', data, 31)[0] != len(data) - 35 or struct.unpack_from('>I', data, 39)[0] != len(data) - 43:
        raise ValueError('Unexpected dynamics fixture envelope; review before export')
    decoded = zstandard.ZstdDecompressor().decompress(data[offset:], max_output_size=16_000_000)
    pattern = rb'/Users/[\x20-\x7e]+'
    paths = list(re.finditer(pattern, decoded))
    if not paths:
        return data
    if len(paths) != 4:
        raise ValueError('Unexpected dynamics fixture path count')
    sanitized = bytearray(decoded)
    for index, match in enumerate(paths):
        replacement = ('/tmp/public-fixture-' + str(index)).encode()
        if len(replacement) > len(match.group()):
            raise ValueError('Fixture path is too short for an anonymous replacement')
        sanitized[match.start():match.end()] = replacement.ljust(len(match.group()), b'_')
    compressed = zstandard.ZstdCompressor(level=3).compress(bytes(sanitized))
    prefix = bytearray(data[:offset])
    struct.pack_into('>I', prefix, 31, len(compressed) + 9)
    struct.pack_into('>I', prefix, 39, len(compressed) + 1)
    return bytes(prefix) + compressed


def sanitize_export(path, data):
    if path.endswith(('dynamics_cfg_off.bin', 'dynamics_cfg_on.bin')):
        return sanitize_dynamics_config(data)
    if path.endswith(('.py', '.json', '.md', '.js', '.mjs', '.ts', '.lua', '.xml', '.setting')):
        return sanitize_text(data.decode('utf-8')).encode('utf-8')
    return data
