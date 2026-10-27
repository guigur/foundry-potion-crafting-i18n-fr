#!/usr/bin/env python3
"""Build Babele overlays from decoded upstream LevelDB records (no Foundry writes).

Usage: python tools/build_translations.py /path/to/extracted-source
The directory must contain potion-crafting-and-gathering-{pack}.json objects
keyed by LevelDB record key, and assets/recipes/*.json for legacy recipe books.
"""
import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = 'potion-crafting-and-gathering'
TOKEN = re.compile(r'(<[^>]*>|@(?:UUID|Compendium)\[[^\]]*\]|\[\[[\s\S]*?\]\]|[{}])')
LABELS = {
    'ingredients': 'Fabrication de potions — Ingrédients',
    'alchemy': 'Fabrication de potions — Alchimie',
    'herbalism': 'Fabrication de potions — Herboristerie',
    'poisons': 'Fabrication de potions — Poisons',
    'journal': 'Fabrication de potions — Guide et récolte',
    'recipes': 'Fabrication de potions — Livres de recettes',
    'tables': 'Fabrication de potions — Tables de récolte',
}


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def human(path, value):
    if not isinstance(value, str) or not value.strip():
        return False
    return (path == 'name' or path in {
        'description', 'text.content', 'system.description.value',
        'system.description.chat', 'system.description.unidentified',
        'system.chatFlavor', 'flags.magicitems.destroyFlavorText',
        'flags.gatherer.require', 'flags.magicitems.spells.0.name',
    } or path.startswith('flags.mastercrafted.') and path.split('.')[-1] in {
        'name', 'description', 'require',
    })


def leaves(value, path=''):
    if isinstance(value, dict):
        for key, child in value.items():
            yield from leaves(child, f'{path}.{key}'.lstrip('.'))
    elif isinstance(value, list):
        for i, child in enumerate(value):
            yield from leaves(child, f'{path}.{i}')
    else:
        yield path, value


class Translator:
    def __init__(self):
        self.catalog = json.loads((ROOT / 'translations/fr.json').read_text(encoding='utf-8'))
        self.count = 0

    def text(self, value):
        chunks = TOKEN.split(value)
        for i in range(0, len(chunks), 2):
            chunk = chunks[i]
            key = chunk.strip()
            if not key or not re.search('[A-Za-z]', key):
                continue
            if key not in self.catalog:
                raise ValueError(f'Missing French translation: {key!r}')
            start = len(chunk) - len(chunk.lstrip())
            end = len(chunk.rstrip())
            chunks[i] = chunk[:start] + self.catalog[key] + chunk[end:]
        self.count += 1
        return ''.join(chunks)

    def document(self, row):
        payload, mapping = {}, {}
        aliases = {'name': 'name', 'description': 'description',
                   'system.description.value': 'description', 'text.content': 'text'}
        for path, value in leaves(row):
            if human(path, value):
                key = aliases.get(path, path.replace('.', '_'))
                assert key not in mapping, path
                mapping[key] = path
                payload[key] = self.text(value)
        return payload, mapping

    def legacy(self, value, key=''):
        if isinstance(value, dict):
            return {k: self.legacy(v, k) for k, v in value.items()}
        if isinstance(value, list):
            return [self.legacy(v) for v in value]
        if key in {'name', 'description', 'tools'} and isinstance(value, str) and value:
            return self.text(value)
        return value


def build(source):
    translator = Translator()
    coverage = {}
    for suffix, label in LABELS.items():
        data = json.loads((source / f'{PACKAGE}-{suffix}.json').read_text(encoding='utf-8'))
        kind = 'journal' if suffix in {'journal', 'recipes'} else 'tables' if suffix == 'tables' else 'items'
        child, document_type = {'journal': ('pages', 'JournalEntryPage'),
                                'tables': ('results', 'TableResult'),
                                'items': ('effects', 'ActiveEffect')}[kind]
        mapping, child_mapping, entries, folders = {}, {}, {}, {}
        children = 0
        for record_key, row in data.items():
            if record_key.startswith('!folders!'):
                folders[row['name']] = translator.text(row['name'])
            if not record_key.startswith(f'!{kind}!'):
                continue
            payload, fields = translator.document(row)
            mapping.update(fields)
            embedded = {}
            for child_id in row.get(child, []):
                child_row = data[f'!{kind}.{child}!{row["_id"]}.{child_id}']
                child_payload, child_fields = translator.document(child_row)
                child_mapping.update(child_fields)
                embedded[child_id] = child_payload
                children += 1
            if embedded:
                payload[child] = embedded
            entries[row['_id']] = payload
        if child_mapping:
            mapping[child] = {'path': child, 'converter': 'document',
                              'documentType': document_type, 'cardinality': 'many',
                              'mapping': child_mapping}
        output = {'label': label, 'mapping': mapping, 'entries': entries}
        if folders:
            output['folders'] = folders
        dump(ROOT / 'compendium/fr' / f'{PACKAGE}.{PACKAGE}-{suffix}.json', output)
        coverage[suffix] = {'documents': len(entries), child: children, 'folders': len(folders)}
    dump(ROOT / 'compendium/fr' / f'{PACKAGE}._packs-folders.json', {
        'entries': {'Potion Crafting & Gathering': 'Fabrication de potions et récolte'}
    })
    legacy = sorted((source / 'assets/recipes').glob('*.json'))
    assert len(legacy) == 12, 'Expected twelve upstream legacy recipe files'
    for path in legacy:
        dump(ROOT / 'legacy-recipes/fr' / path.name,
             translator.legacy(json.loads(path.read_text(encoding='utf-8'))))
    dump(ROOT / 'coverage.json', {
        'source': PACKAGE, 'sourceVersion': '0.8.2',
        'sourceCommit': '98847c5f676297a112f8e51948faadfcc3c5cb0f',
        'language': 'fr', 'packs': coverage,
        'catalogSegments': len(translator.catalog),
        'translatedFieldOccurrences': translator.count, 'legacyRecipeFiles': len(legacy),
        'runtimeValidation': 'Pending verification in a running Foundry VTT 14 world',
        'notes': ["Dracula's Essence description is truncated in the upstream source; the cutoff is marked in French.",
                  'Source credits, URLs, identifiers, source-book citations, and mechanical enum values remain unchanged.'],
    })
    print(json.dumps(coverage, ensure_ascii=False, indent=2))
    print(f'{translator.count} text fields; {len(translator.catalog)} catalog segments; {len(legacy)} legacy books')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    build(parser.parse_args().source)
