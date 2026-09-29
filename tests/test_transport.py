import pathlib
import sys
import subprocess
import tempfile
import unittest
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'scripts'))
from transport import source_paths


class TransportBoundary(unittest.TestCase):
    def test_ignored_credentials_and_external_symlinks_never_transfer(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            subprocess.run(['git', 'init', '-q', str(root)], check=True)
            (root / '.gitignore').write_text('*.local.*\n.private/\n')
            (root / 'app.java').write_text('public source')
            (root / 'credentials.local.json').write_text('must not transfer')
            (root / '.private').mkdir()
            (root / '.private' / 'password').write_text('must not transfer')
            (root / 'external').symlink_to('/etc/hosts')
            names = {p.name for p in source_paths(root)}
            self.assertIn('app.java', names)
            self.assertNotIn('credentials.local.json', names)
            self.assertNotIn('password', names)
            self.assertNotIn('external', names)
