#!/usr/bin/env python3
"""Audit overlay coverage and preservation against the extracted upstream snapshot.

This checks data and mappings independently of Foundry's running Babele engine.
Run: python tools/validate_translations.py /path/to/extracted-source
"""
import argparse
import copy
import json
import re
from pathlib import Path
from build_translations import ROOT, PACKAGE, LABELS, human, leaves


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def get(value, path):
    for key in path.split('.'):
        value = value[int(key)] if isinstance(value, list) else value[key]
    return value


def set_value(value, path, replacement):
    keys = path.split('.')
    for key in keys[:-1]:
        value = value[int(key)] if isinstance(value, list) else value[key]
    key = int(keys[-1]) if isinstance(value, list) else keys[-1]
    value[key] = replacement


PROTECTED = re.compile(r'<[^>]*>|@(?:UUID|Compendium)\[[^\]]*\]|\[\[[\s\S]*?\]\]')
NUMBERS = re.compile(r'\d+(?:d\d+)?')


def audit_document(source, payload, mapping, location):
    changed = copy.deepcopy(source)
    covered = set()
    fields = 0
    for key, value in payload.items():
        target = mapping[key]
        if isinstance(target, dict):
            path = target['path']
            assert target['converter'] == 'document', location
            documents = get(changed, path)
            assert set(value) == {row['_id'] for row in documents}, (location, path)
            for row in documents:
                result, count = audit_document(row, value[row['_id']], target['mapping'], location + '/' + row['_id'])
                row.clear(); row.update(result); fields += count
            continue
        before = get(source, target)
        assert isinstance(before, str) and isinstance(value, str), (location, target)
        assert human(target, before), (location, target, 'unexpected field')
        assert PROTECTED.findall(before) == PROTECTED.findall(value), (location, target, 'HTML or reference changed')
        assert sorted(NUMBERS.findall(before)) == sorted(NUMBERS.findall(value)), (location, target, 'numeric rules changed')
        set_value(changed, target, value)
        covered.add(target); fields += 1
    # Embedded documents are checked above with their own relative paths.
    expected = {path for path, value in leaves(source) if human(path, value)}
    assert covered == expected, (location, 'missing text paths', expected - covered)
    # All values outside the explicitly translated fields must remain identical.
    for path, value in leaves(source):
        if path in covered or path.split('.')[0] in {'effects', 'pages', 'results'}:
            continue
        assert get(changed, path) == value, (location, path, 'non-text field changed')
    return changed, fields


def validate(source):
    fields = 0
    for suffix in LABELS:
        data = load(source / f'{PACKAGE}-{suffix}.json')
        overlay = load(ROOT / 'compendium/fr' / f'{PACKAGE}.{PACKAGE}-{suffix}.json')
        kind = 'journal' if suffix in {'journal', 'recipes'} else 'tables' if suffix == 'tables' else 'items'
        child = {'journal': 'pages', 'tables': 'results', 'items': 'effects'}[kind]
        roots = [row for key, row in data.items() if key.startswith(f'!{kind}!')]
        assert set(overlay['entries']) == {row['_id'] for row in roots}, suffix
        for root in roots:
            row = copy.deepcopy(root)
            row[child] = [data[f'!{kind}.{child}!{row["_id"]}.{identity}'] for identity in row.get(child, [])]
            _, count = audit_document(row, overlay['entries'][row['_id']], overlay['mapping'], suffix + '/' + row['_id'])
            fields += count
        folders = [row['name'] for key, row in data.items() if key.startswith('!folders!')]
        assert set(overlay.get('folders', {})) == set(folders), suffix
    # Legacy books preserve every field except their human-readable text.
    for path in sorted((source / 'assets/recipes').glob('*.json')):
        original = load(path)
        french = load(ROOT / 'legacy-recipes/fr' / path.name)
        before, after = dict(leaves(original)), dict(leaves(french))
        assert before.keys() == after.keys(), path
        for key, value in before.items():
            if key.split('.')[-1] in {'name', 'description', 'tools'} and isinstance(value, str):
                assert isinstance(after[key], str), (path, key)
                assert sorted(NUMBERS.findall(value)) == sorted(NUMBERS.findall(after[key])), (path, key)
            else:
                assert value == after[key], (path, key)
    print(f'PASS: all seven packs; {fields} mapped text fields; IDs, markup, references and numeric rules preserved; twelve legacy books checked.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    validate(parser.parse_args().source)
