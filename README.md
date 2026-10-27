# Potion Crafting and Gathering en français

Personal French translation for **Potion Crafting & Gathering 0.8.2**, using **Babele 2.8.x** on **Foundry VTT 14** with dnd5e.

## Installer dans Foundry

Après publication de la première [release](https://github.com/guigur/foundry-potion-crafting-i18n-fr/releases), ouvrez **Add-on Modules → Install Module** et collez cette adresse dans **Manifest URL** :

```text
https://github.com/guigur/foundry-potion-crafting-i18n-fr/releases/latest/download/module.json
```

Cliquez sur **Install**, puis activez la traduction, Babele et Potion Crafting & Gathering dans votre monde. Réglez la langue de Foundry sur **Français**. Les futures versions publiées s'installent avec **Update / Mettre à jour**.

Le [guide complet en français](GUIDE-INSTALLATION-FR.html), disponible dans les fichiers de chaque release, explique les étapes dans l'interface et l'installation manuelle du ZIP. Le nom du module et de son dossier reste `foundry-custom-i18n`, indépendamment du nom du dépôt GitHub, afin de conserver son identité lors des mises à jour.

- `dist/foundry-custom-i18n-fr.zip`: complete translation module, including the source module's import setting, prompt, and success message.
- `dist/pcg-translations-local-fr.zip`: compendium JSON files for a private Babele directory; excludes the JavaScript UI adapters.
- `compendium/fr`: seven compendium overlays and one compendium-folder overlay, with self-contained mappings.
- `legacy-recipes/fr`: twelve translated legacy recipe-book JSON files, for importers that support that old format.
- `translations/fr.json`: editable English-to-French text catalog.
- `coverage.json`: source version, source commit, coverage counts and validation limits.

Coverage: 178 Items, 56 embedded effects, 14 JournalEntries with 126 pages (including 108 recipe pages), 15 RollTables with 106 results, and three internal folders. Credits, URLs, bibliography and machine identifiers are retained. Source descriptions are translated as supplied, including differences between an item and its recipe. Dracula's Essence has a truncated source description; its cutoff is explicitly marked.

The original modules remain installed and enabled. The translation does not alter their disk data. Existing English world documents are separate copies and need selective reimport if French copies are wanted. Mastercrafted and Gatherer are separate modules: their own UI strings are outside this package's scope.

## Development

The build input is a decoded snapshot of the upstream LevelDB records, keyed by their original database keys. Pass a directory containing the seven `potion-crafting-and-gathering-{pack}.json` files and the original `assets/recipes/*.json` files:

```sh
python tools/build_translations.py /path/to/source-snapshot
python tools/validate_translations.py /path/to/source-snapshot
node tests/register.test.mjs
python tools/prepare_release.py
python tools/package.py
python tools/check_package.py
```

The data audit checks complete document/embedded-document coverage, mapped text paths, protected HTML and Foundry references, numeric rule values, and preservation of non-text fields in the legacy files. The JavaScript tests check registration and the exact-match adapters without a Foundry server. These checks do **not** replace a live Foundry/Babele integration check; this release has not been verified in a running Foundry 14 world. The manifest intentionally omits `compatibility.verified`.

## Publishing updates

The **Check and publish release** workflow validates changes and publishes a new GitHub Release after a push to `main` when the version does not already have a release. It can also be run from **Actions → Check and publish release → Run workflow** on `main`. Pull requests run the checks without publishing.

For an update, increase `version` in `module.json`, update `RELEASE-NOTES.md`, and push the changes. The workflow synchronizes the version-specific ZIP URL and uploads both ZIPs, the standalone `module.json`, and the HTML guide. Existing releases are left intact; changes without a version increase do not replace their assets. The stable installation URL above becomes available after the first workflow successfully publishes a release. No personal access token is needed by the workflow; it uses GitHub's repository token with release write permission.

The `dist/` directory is generated, not committed. Checks on GitHub use the already generated translations and do not require the upstream LevelDB snapshot. See [source and credit details](SOURCES.md).

For the first upload through GitHub's website, see [the French publishing instructions](PUBLISHING.md).
