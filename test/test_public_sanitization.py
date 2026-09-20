import importlib.util
from pathlib import Path
import struct
import sys
import unittest
import zstandard

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from public_sanitization import sanitize_dynamics_config, sanitize_text

spec = importlib.util.spec_from_file_location('privacy', Path(__file__).resolve().parents[1] / 'scripts/verify-public-privacy.py')
privacy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(privacy)


class PublicSanitizationTest(unittest.TestCase):
    def fixture(self):
        # Synthetic account data exercises the encoded-content privacy boundary.
        paths = [(b'/' + b'Users/' + b'example-user/Movies/' + name) for name in (b'cache', b'proxy', b'gallery', b'media')]
        decoded = b'\x00'.join(paths) + b'\x00native-parameters-preserved'
        compressed = zstandard.ZstdCompressor().compress(decoded)
        prefix = bytearray(44)
        struct.pack_into('>I', prefix, 31, len(compressed) + 9)
        struct.pack_into('>I', prefix, 39, len(compressed) + 1)
        return bytes(prefix) + compressed, decoded

    def test_compressed_paths_are_rejected_then_removed_without_changing_field_lengths(self):
        fixture, before = self.fixture()
        with self.assertRaisesRegex(ValueError, 'Machine-specific'):
            privacy.inspect_file('native/fixtures/example.bin', fixture)
        sanitized = sanitize_dynamics_config(fixture)
        privacy.inspect_file('native/fixtures/example.bin', sanitized)
        after = zstandard.ZstdDecompressor().decompress(sanitized[44:])
        self.assertEqual(len(before), len(after))
        self.assertEqual([len(x) for x in before.split(b'\x00')], [len(x) for x in after.split(b'\x00')])
        self.assertEqual(before.split(b'\x00')[-1], after.split(b'\x00')[-1])
        self.assertEqual(struct.unpack_from('>I', sanitized, 31)[0], len(sanitized) - 35)
        self.assertEqual(struct.unpack_from('>I', sanitized, 39)[0], len(sanitized) - 43)
        self.assertEqual(sanitize_dynamics_config(sanitized), sanitized)

    def test_export_sanitization_is_stable_and_preserves_distinct_fixture_paths(self):
        value = '/tmp/' + 'probe_20260920/a.json /tmp/' + 'probe_20260920/b.json'
        sanitized = sanitize_text(value)
        self.assertNotEqual(sanitized.split()[0], sanitized.split()[1])
        self.assertEqual(sanitize_text(sanitized), sanitized)
        privacy.inspect_bytes(sanitized.encode(), 'example.py')


if __name__ == '__main__':
    unittest.main()
