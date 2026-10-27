/* Babele owns the compendium overlay. These small UI adapters cover the three
 * upstream strings that are hard-coded rather than passed through game.i18n.
 * Exact matching deliberately leaves other modules' dialogs/messages alone.
 */
const SOURCE_ID = "potion-crafting-and-gathering";
const IMPORT_PROMPT = "Do you want to import all tables, journals and recipes?";
const IMPORT_SUCCESS = `${SOURCE_ID} | Recipe Books Imported. The Potion Crafting & Gathering module needs to stay enabled as the items are stored in it's compendium packs.`;

Hooks.once("babele.init", (babele) => {
  babele.register({
    module: "foundry-custom-i18n",
    lang: "fr",
    dir: "compendium/fr"
  });
});

Hooks.once("setup", () => {
  const french = () => game.i18n.lang === "fr" && game.modules.get(SOURCE_ID)?.active;
  if (!french()) return;

  const setting = game.settings.settings.get(`${SOURCE_ID}.booksImported`);
  if (setting) {
    setting.name = "PCGFR.ImportSetting";
    setting.hint = "PCGFR.ImportHint";
  }

  // The source module calls this legacy API itself, including on Foundry 14.
  if (typeof globalThis.Dialog?.confirm === "function") {
    const confirm = globalThis.Dialog.confirm;
    globalThis.Dialog.confirm = function (data, ...args) {
      if (french() && data?.content === IMPORT_PROMPT
          && data?.title === game.modules.get(SOURCE_ID)?.title) {
        data = { ...data, title: game.i18n.localize("PCGFR.ImportTitle"),
          content: game.i18n.localize("PCGFR.ImportPrompt") };
      }
      return confirm.call(this, data, ...args);
    };
  }

  if (typeof ui.notifications?.success === "function") {
    const success = ui.notifications.success;
    ui.notifications.success = function (message, ...args) {
      if (french() && message === IMPORT_SUCCESS) {
        message = `${SOURCE_ID} | ${game.i18n.localize("PCGFR.ImportSuccess")}`;
      }
      return success.call(this, message, ...args);
    };
  }
});
