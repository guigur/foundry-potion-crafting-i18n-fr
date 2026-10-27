#!/usr/bin/env python3
"""Create installation ZIPs and the standalone release manifest offline."""
import shutil
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'
DIST.mkdir(exist_ok=True)
shutil.copyfile(ROOT / 'module.json', DIST / 'module.json')
with ZipFile(DIST / 'foundry-custom-i18n-fr.zip', 'w', ZIP_DEFLATED) as archive:
    for name in ['module.json', 'scripts', 'languages', 'compendium', 'legacy-recipes',
                 'translations', 'tools', 'tests',
                 'GUIDE-INSTALLATION-FR.html', 'README.md', 'SOURCES.md', 'coverage.json']:
        target = ROOT / name
        files = sorted(target.rglob('*')) if target.is_dir() else [target]
        for file in files:
            if file.is_file() and '__pycache__' not in file.parts and file.suffix != '.pyc':
                archive.write(file, 'foundry-custom-i18n/' + file.relative_to(ROOT).as_posix())
with ZipFile(DIST / 'pcg-translations-local-fr.zip', 'w', ZIP_DEFLATED) as archive:
    for file in sorted((ROOT / 'compendium/fr').glob('*.json')):
        archive.write(file, 'pcg-translations/fr/' + file.name)
    archive.write(ROOT / 'GUIDE-INSTALLATION-FR.html', 'GUIDE-INSTALLATION-FR.html')
for file in sorted(DIST.glob('*.zip')):
    print(f'{file.name}: {file.stat().st_size:,} bytes')
