# Publier le module sur GitHub

Les fichiers sont configurés pour le dépôt public [guigur/foundry-potion-crafting-i18n-fr](https://github.com/guigur/foundry-potion-crafting-i18n-fr).

## Premier envoi depuis le site GitHub

1. Décompressez `github-repository-upload.zip` sur votre ordinateur.
2. Ouvrez le dépôt GitHub et cliquez sur **uploading an existing file**, ou sur **Add file → Upload files**.
3. Déposez tous les fichiers et dossiers décompressés à la racine du dépôt, y compris `.github` et `.gitignore`. Sous Linux, utilisez **Ctrl+H** dans votre explorateur si les fichiers commençant par un point sont masqués.
4. Vérifiez que `module.json`, `README.md` et les dossiers `compendium`, `scripts`, `languages` et `.github` apparaissent directement à la racine. Ne déposez pas le ZIP lui-même et n'ajoutez pas de dossier parent.
5. Validez avec **Commit changes** sur la branche `main`.
6. Ouvrez **Actions → Check and publish release**. Le workflow vérifie les fichiers et publie automatiquement la release `v1.0.0` avec ses archives et son manifeste.

Si le lancement automatique n'a pas eu lieu, ouvrez ce workflow dans **Actions**, cliquez sur **Run workflow**, sélectionnez `main`, puis confirmez. Si GitHub Actions est désactivé dans ce dépôt, activez-le d'abord dans les paramètres du dépôt.

Quand le workflow est vert, ouvrez **Releases** et vérifiez que la release contient `module.json` et `foundry-custom-i18n-fr.zip`.

## Installer dans Foundry

Dans **Add-on Modules → Install Module → Manifest URL**, collez :

```text
https://github.com/guigur/foundry-potion-crafting-i18n-fr/releases/latest/download/module.json
```

Cette adresse fonctionne après la publication de la première release. Activez ensuite le module de traduction, Babele et Potion Crafting & Gathering dans votre monde, et choisissez Français comme langue.

## Versions suivantes

Modifiez les traductions, augmentez `version` dans `module.json`, adaptez `RELEASE-NOTES.md`, puis envoyez ces changements sur `main`. Le workflow publie la nouvelle version et Foundry peut la récupérer avec **Update**. Une version déjà publiée n'est pas remplacée.
