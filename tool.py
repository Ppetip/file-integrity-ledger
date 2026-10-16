"""Create bounded SHA-256 directory manifests and compare snapshots to identify additions, deletions and modifications."""
import hashlib
from pathlib import Path

def snapshot(root, max_bytes=100_000_000):
    root = Path(root).resolve(strict=True)
    if not root.is_dir():
        raise ValueError('root must be a directory')
    result = {}
    total = 0
    for path in sorted(root.rglob('*')):
        if path.is_symlink():
            raise ValueError('symlinks are not accepted')
        if path.is_file():
            if not path.resolve().is_relative_to(root):
                raise ValueError('path escaped root')
            digest = hashlib.sha256()
            with path.open('rb') as stream:
                for block in iter(lambda:stream.read(65536), b''):
                    total += len(block)
                    if total > max_bytes:
                        raise ValueError('snapshot byte budget exceeded')
                    digest.update(block)
            result[path.relative_to(root).as_posix()] = digest.hexdigest()
    return result

def analyze(data):
    before, after = data['before'], data['after']
    return [dict(kind='added' if p not in before else 'removed' if p not in after else 'modified',path=p)
            for p in sorted(before.keys() | after.keys()) if before.get(p) != after.get(p)]


def main():
    import argparse, json, sys
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', help='path to JSON input, or - for stdin')
    args = parser.parse_args()
    try:
        if args.input == '-':
            data = json.load(sys.stdin)
        else:
            with open(args.input, encoding='utf-8') as stream:
                data = json.load(stream)
        result = analyze(data)
        print(json.dumps(result, indent=2, allow_nan=False))
        return 0
    except (ValueError, KeyError, TypeError, OSError, OverflowError) as error:
        print('Invalid input: '+str(error), file=sys.stderr)
        return 2

if __name__ == '__main__':
    raise SystemExit(main())
