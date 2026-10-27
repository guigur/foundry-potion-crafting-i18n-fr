#!/usr/bin/env python3
"""Synchronize GitHub release URLs with the module version before packaging."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = 'https://github.com/guigur/foundry-potion-crafting-i18n-fr'
path = ROOT / 'module.json'
manifest = json.loads(path.read_text(encoding='utf-8'))
version = manifest['version']
if not re.fullmatch(r'\d+\.\d+\.\d+', version):
    raise SystemExit('Use a stable version in MAJOR.MINOR.PATCH format.')
manifest.update({
    'url': REPOSITORY,
    'manifest': f'{REPOSITORY}/releases/latest/download/module.json',
    'download': f'{REPOSITORY}/releases/download/v{version}/foundry-custom-i18n-fr.zip',
    'bugs': f'{REPOSITORY}/issues',
})
path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(f'Prepared release v{version}')
