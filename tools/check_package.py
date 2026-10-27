#!/usr/bin/env python3
"""Check release archive integrity, URLs, shipped paths and translation counts."""
import json
from pathlib import Path, PurePosixPath
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
manifest = json.loads((ROOT / 'module.json').read_text(encoding='utf-8'))
release_manifest = json.loads((ROOT / 'dist/module.json').read_text(encoding='utf-8'))
assert release_manifest == manifest, 'Release manifest differs from source manifest'
base = 'https://github.com/guigur/foundry-potion-crafting-i18n-fr'
assert manifest['manifest'] == f'{base}/releases/latest/download/module.json'
assert manifest['download'] == f'{base}/releases/download/v{manifest["version"]}/foundry-custom-i18n-fr.zip'

with ZipFile(ROOT / 'dist/foundry-custom-i18n-fr.zip') as archive:
    assert archive.testzip() is None, 'Corrupt release ZIP'
    prefix = manifest['id'] + '/'
    names = set(archive.namelist())
    assert all(n.startswith(prefix) and '..' not in PurePosixPath(n).parts for n in names)
    assert json.loads(archive.read(prefix + 'module.json')) == release_manifest
    for name in manifest['esmodules'] + [lang['path'] for lang in manifest['languages']]:
        assert prefix + name in names, f'Missing manifest path: {name}'
    pack_files = [n for n in names if n.startswith(prefix + 'compendium/fr/') and n.endswith('.json')]
    assert len(pack_files) == 8, 'Expected seven packs and one folder overlay'
    counts = {'documents': 0, 'pages': 0, 'effects': 0, 'results': 0}
    for name in pack_files:
        data = json.loads(archive.read(name))
        assert isinstance(data['entries'], dict), name
        if name.endswith('._packs-folders.json'):
            continue
        counts['documents'] += len(data['entries'])
        for entry in data['entries'].values():
            assert isinstance(entry['name'], str) and entry['name'], name
            assert set(entry) <= set(data['mapping']), name
            for field in ('pages', 'effects', 'results'):
                nested = entry.get(field, {})
                counts[field] += len(nested)
                for child in nested.values():
                    assert set(child) <= set(data['mapping'][field]['mapping']), name
    assert counts == {'documents': 207, 'pages': 126, 'effects': 56, 'results': 106}, counts
    for name in names:
        if name.endswith('.json'):
            json.loads(archive.read(name))
with ZipFile(ROOT / 'dist/pcg-translations-local-fr.zip') as archive:
    assert archive.testzip() is None
    assert len([n for n in archive.namelist() if n.startswith('pcg-translations/fr/')]) == 8
print('PASS: release URLs, manifests, ZIP integrity, file paths and full translation counts')
