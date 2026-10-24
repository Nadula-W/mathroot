const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const ts = require("typescript");

// Compile only our small TS modules in memory using the project's existing compiler.
// No new test dependency or build output is needed.
for (const extension of [".ts", ".tsx"]) {
  require.extensions[extension] = (module, filename) => {
    const result = ts.transpileModule(fs.readFileSync(filename, "utf8"), {
      compilerOptions: { module: ts.ModuleKind.CommonJS, jsx: ts.JsxEmit.ReactJSX, target: ts.ScriptTarget.ES2020 },
      fileName: filename,
    });
    module._compile(result.outputText, filename);
  };
}
const { en } = require("../lib/i18n/en.ts");
const { si } = require("../lib/i18n/si.ts");
const { translate, translatedContent, translatedError, hasMissingTranslation, savedLanguage, topicLabel, inputValidationMessage } = require("../lib/i18n/core.ts");

test("English and Sinhala dictionaries cover the same messages and interpolation fields", () => {
  assert.deepEqual(Object.keys(en).sort(), Object.keys(si).sort());
  for (const [key, value] of Object.entries(en)) {
    assert.ok(si[key].trim(), key);
    assert.deepEqual((value.match(/\{\w+\}/g) || []).sort(), (si[key].match(/\{\w+\}/g) || []).sort(), key);
  }
  assert.equal(translate("en", "Question {number} of {total}", { number: 2, total: 5 }), "Question 2 of 5");
  assert.match(translate("si", "Question {number} of {total}", { number: 2, total: 5 }), /5.*2/);
});

test("every literal t() interface key has both translations", () => {
  function visitFile(filename) {
    const source = ts.createSourceFile(filename, fs.readFileSync(filename, "utf8"), ts.ScriptTarget.Latest, true, ts.ScriptKind.TSX);
    function visit(node) {
      if (ts.isCallExpression(node) && ts.isIdentifier(node.expression) && node.expression.text === "t" && node.arguments[0] && ts.isStringLiteral(node.arguments[0])) {
        assert.ok(en[node.arguments[0].text], `${filename}: ${node.arguments[0].text}`);
      }
      ts.forEachChild(node, visit);
    }
    visit(source);
  }
  function walk(directory) {
    for (const entry of fs.readdirSync(directory, { withFileTypes: true })) {
      const filename = path.join(directory, entry.name);
      if (entry.isDirectory()) walk(filename);
      else if (filename.endsWith(".tsx")) visitFile(filename);
    }
  }
  walk(path.join(__dirname, "../app"));
});

test("language changes alter display only and report unavailable translations", () => {
  const question = {
    question_id: "question-1", statement: "Expand and simplify: 3(x + 4)", correct_option_id: "option-2",
    options: [{ id: "option-1", text: "3x + 4" }, { id: "option-2", text: "3x + 12" }],
    translations: { si: { statement: "ප්‍රසාරණය කර සුළු කරන්න: 3(x + 4)" } },
    translation_warnings: ["explanation"],
  };
  const original = JSON.stringify(question);
  assert.equal(translatedContent("en", question, "statement"), question.statement);
  assert.match(translatedContent("si", question, "statement"), /3\(x \+ 4\)$/);
  assert.equal(translatedContent("en", question, "statement"), question.statement);
  assert.equal(JSON.stringify(question), original);
  assert.equal(hasMissingTranslation("en", question), false);
  assert.equal(hasMissingTranslation("si", question, ["statement"]), false);
  assert.equal(hasMissingTranslation("si", question), true);
  assert.equal(translatedContent("si", { statement: "Historical English" }, "statement"), "Historical English");
  assert.equal(savedLanguage("si"), "si");
  assert.equal(savedLanguage("invalid"), "en");
  assert.equal(savedLanguage(null), "en");
  assert.notEqual(topicLabel("si", "binomial"), "binomial");
});

test("known errors translate while unknown service details remain visible", () => {
  assert.equal(translatedError("si", "Incorrect class join code."), si["Incorrect class join code."]);
  assert.equal(translatedError("si", "Input should be greater than or equal to 1"), translate("si", "Input should be greater than or equal to {count}", { count: 1 }));
  assert.match(translatedError("si", "Topics not ready: equations"), new RegExp(topicLabel("si", "equations")));
  assert.match(translatedError("si", "Unexpected upstream detail"), /Unexpected upstream detail/);
  assert.notEqual(translatedError("si", "Unexpected upstream detail"), "Unexpected upstream detail");
});

test("native form validation messages cover required, email and length in both languages", () => {
  assert.equal(inputValidationMessage("si", { valueMissing: true }), si["Field required"]);
  assert.equal(inputValidationMessage("en", { valueMissing: true }), "Field required");
  assert.equal(inputValidationMessage("si", { typeMismatch: true }), si["Enter a valid email address."]);
  assert.match(inputValidationMessage("si", { tooShort: true }, 8), /8/);
  assert.match(inputValidationMessage("si", { tooLong: true }, -1, 100), /100/);
  assert.equal(inputValidationMessage("en", {}), "Invalid input");
});

test("server rendering defaults to English without browser storage or document access", () => {
  const React = require("react");
  const { renderToString } = require("react-dom/server");
  const { LanguageProvider } = require("../lib/i18n/LanguageProvider.tsx");
  const LanguageSelector = require("../app/components/LanguageSelector.tsx").default;
  const html = renderToString(React.createElement(LanguageProvider, null, React.createElement(LanguageSelector)));
  assert.match(html, /value="en" selected=""/);
  assert.match(html, /English/);
  assert.match(html, /value="si"/);
});
