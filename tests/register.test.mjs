import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import vm from "node:vm";

const script = readFileSync(new URL("../scripts/register.js", import.meta.url), "utf8");
const translations = JSON.parse(readFileSync(new URL("../languages/fr.json", import.meta.url), "utf8")).PCGFR;
const prompt = "Do you want to import all tables, journals and recipes?";
const success = "potion-crafting-and-gathering | Recipe Books Imported. The Potion Crafting & Gathering module needs to stay enabled as the items are stored in it's compendium packs.";

function environment(lang = "fr", active = true) {
  const hooks = new Map(), calls = [], setting = { name: "Import Content on startup" };
  const context = vm.createContext({
    Hooks: { once: (name, fn) => hooks.set(name, fn) },
    game: {
      i18n: { lang, localize: (key) => translations[key.split(".")[1]] },
      modules: new Map([["potion-crafting-and-gathering", { active, title: "Potion Crafting & Gathering" }]]),
      settings: { settings: new Map([["potion-crafting-and-gathering.booksImported", setting]]) }
    },
    Dialog: { confirm(data, options) { calls.push({ type: "dialog", data, options, receiver: this }); return "dialog result"; } },
    ui: { notifications: { success(message, options) { calls.push({ type: "success", message, options, receiver: this }); return 42; } } }
  });
  const originalConfirm = context.Dialog.confirm, originalSuccess = context.ui.notifications.success;
  new vm.Script(script).runInContext(context);
  return { context, hooks, calls, setting, originalConfirm, originalSuccess };
}

test("registers the French source at Babele initialization", () => {
  const env = environment(); let registration;
  env.hooks.get("babele.init")({ register: (value) => { registration = value; } });
  assert.deepEqual(JSON.parse(JSON.stringify(registration)), {
    module: "foundry-custom-i18n", lang: "fr", dir: "compendium/fr"
  });
});

test("French adapters preserve callbacks, options, return values, and receiver", () => {
  const env = environment(); env.hooks.get("setup")();
  const yes = () => {}, options = { width: 600 };
  const original = { content: prompt, title: "Potion Crafting & Gathering", yes, defaultYes: true };
  assert.equal(env.context.Dialog.confirm(original, options), "dialog result");
  const call = env.calls[0];
  assert.equal(call.data.content, translations.ImportPrompt);
  assert.equal(call.data.title, translations.ImportTitle);
  assert.equal(call.data.yes, yes);
  assert.equal(call.data.defaultYes, true);
  assert.equal(call.options, options);
  assert.equal(call.receiver, env.context.Dialog);
  assert.equal(original.content, prompt);
  assert.equal(env.setting.name, "PCGFR.ImportSetting");
  const notificationOptions = { permanent: true };
  assert.equal(env.context.ui.notifications.success(success, notificationOptions), 42);
  assert.equal(env.calls[1].message, `potion-crafting-and-gathering | ${translations.ImportSuccess}`);
  assert.equal(env.calls[1].options, notificationOptions);
  assert.equal(env.calls[1].receiver, env.context.ui.notifications);
});

test("unrelated dialogs and notifications pass through unchanged", () => {
  const env = environment(); env.hooks.get("setup")();
  for (const data of [{ title: "Other module", content: prompt },
    { title: "Potion Crafting & Gathering", content: "Different content" }]) {
    env.context.Dialog.confirm(data);
    assert.equal(env.calls.at(-1).data, data);
  }
  env.context.ui.notifications.success("Other notification");
  assert.equal(env.calls.at(-1).message, "Other notification");
});

test("English worlds and inactive source modules install no UI adapters", () => {
  for (const [lang, active] of [["en", true], ["fr", false]]) {
    const env = environment(lang, active); env.hooks.get("setup")();
    assert.equal(env.context.Dialog.confirm, env.originalConfirm);
    assert.equal(env.context.ui.notifications.success, env.originalSuccess);
    assert.equal(env.setting.name, "Import Content on startup");
  }
});

test("adapters check the language again when invoked", () => {
  const env = environment(); env.hooks.get("setup")(); env.context.game.i18n.lang = "en";
  const data = { content: prompt, title: "Potion Crafting & Gathering" };
  env.context.Dialog.confirm(data);
  env.context.ui.notifications.success(success);
  assert.equal(env.calls[0].data, data);
  assert.equal(env.calls[1].message, success);
});
