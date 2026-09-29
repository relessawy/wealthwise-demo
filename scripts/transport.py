"""Select publishable Git files; never upload ignored local credentials or caches."""
import pathlib
import subprocess


def source_paths(root, include_build=False):
    root = pathlib.Path(root)
    names = subprocess.check_output(
        ['git', 'ls-files', '--cached', '--others', '--exclude-standard', '-z'], cwd=root
    ).decode().split('\0')
    paths = {root / n for n in names if n}
    if include_build:
        for module in ('ww-frontend', 'financial-advisor', 'investment-advisor', 'advisor-history'):
            paths.update((root / module / 'target' / 'quarkus-app').rglob('*'))
    for path in sorted(paths):
        relative = path.relative_to(root)
        if path.is_symlink() or not path.is_file():
            continue
        if any(part in relative.parts for part in ('.git', '.private', '.cache', 'node_modules', '__pycache__')):
            continue
        if 'target' in relative.parts and not include_build:
            continue
        yield path
