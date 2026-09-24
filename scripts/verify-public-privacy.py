"""Check tracked source or a release tarball, including encoded native fixtures."""
import ast
import base64
import json
from pathlib import Path
import re
import subprocess
import sys
import tarfile
import zlib
import zstandard

PATTERNS = [
    re.compile(r'/(?:Users|home)/[A-Za-z0-9_.-]+'),
    re.compile(r'/var/folders/[A-Za-z0-9_/.-]+'),
    re.compile(r'/tmp/[^\s\"\x27<>]*202\d[^\s\"\x27<>]*'),
    re.compile(r'CUTAGENT_[A-Z0-9_]*20\d{6}_\d{6}'),
]


def inspect_bytes(data, name, depth=0):
    if depth > 4:
        raise ValueError('Fixture compression nesting exceeds the reviewed limit')
    for encoding in ('utf-8', 'utf-16-le', 'utf-16-be'):
        text = data.decode(encoding, errors='ignore')
        if any(pattern.search(text) for pattern in PATTERNS):
            raise ValueError('Machine-specific information in ' + name)
    if '/fixtures/' not in name:
        return
    for magic in (bytes.fromhex('28b52ffd'), bytes.fromhex('789c'), bytes.fromhex('78da')):
        for match in re.finditer(re.escape(magic), data):
            try:
                if magic[0] == 40:
                    decoded = zstandard.ZstdDecompressor().decompress(data[match.start():], max_output_size=16_000_000)
                else:
                    decoder = zlib.decompressobj()
                    decoded = decoder.decompress(data[match.start():], 16_000_001)
                    if not decoder.eof:
                        continue
            except (zstandard.ZstdError, zlib.error):
                continue
            if len(decoded) > 16_000_000:
                raise ValueError('Fixture exceeds the reviewed decoded size limit')
            inspect_bytes(decoded, name, depth + 1)


def inspect_file(name, data):
    source_name = name.removeprefix('package/')
    if source_name in {'PUBLICATION_CHECKS.md', 'docs/PUBLICATION.md',
                       'docs/FREE_21_1_ACCEPTANCE_2026-09-08.json',
                       'docs/STUDIO_PUBLIC_SOURCE_ACCEPTANCE_2026-09-08.json'}:
        raise ValueError('Internal publication document in ' + name)
    if source_name.startswith(('skills/', 'agent-knowledge/')) or Path(source_name).name in {'CUTAGENT.md', 'SKILL.md'}:
        raise ValueError('Private agent instructions in ' + name)
    inspect_bytes(data, name)
    if '/fixtures/' not in name:
        return
    if name.endswith('.json'):
        def walk(value):
            if isinstance(value, dict):
                for key, item in value.items():
                    if isinstance(item, str) and key.endswith(('_b64', '_hex')):
                        decoded = base64.b64decode(item, validate=True) if key.endswith('_b64') else bytes.fromhex(item)
                        inspect_bytes(decoded, name)
                    else:
                        walk(item)
            elif isinstance(value, list):
                for item in value:
                    walk(item)
        walk(json.loads(data))
    elif name.endswith('.py'):
        for node in ast.walk(ast.parse(data)):
            if isinstance(node, ast.Constant) and isinstance(node.value, str) and re.fullmatch(r'[0-9A-Fa-f]{40,}', node.value):
                inspect_bytes(bytes.fromhex(node.value), name)


def main():
    root = Path(__file__).resolve().parents[1]
    if len(sys.argv) == 2:
        with tarfile.open(sys.argv[1], 'r:gz') as archive:
            for member in archive.getmembers():
                if member.isfile():
                    inspect_file(member.name, archive.extractfile(member).read())
    else:
        paths = subprocess.check_output(['git', 'ls-files', '-z', '--cached', '--others', '--exclude-standard'], cwd=root).decode().split('\0')
        for name in sorted(set(paths) - {''}):
            path = root / name
            if path.is_file():
                inspect_file(name, path.read_bytes())
    print('Public privacy checks passed, including compressed and encoded fixtures.')


if __name__ == '__main__':
    main()
