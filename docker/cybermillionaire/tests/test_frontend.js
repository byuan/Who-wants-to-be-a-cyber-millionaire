const fs = require("node:fs");
const vm = require("node:vm");
const assert = require("node:assert/strict");
const path = require("node:path");
const source = fs.readFileSync(path.join(__dirname, "../static/js/millionaire.js"), "utf8");
const context = {
    document: {cookie: "csrftoken=test-token; other=value"},
    window: {addEventListener() {}},
    $: () => ({ready() {}})
};
vm.createContext(context);
vm.runInContext(source, context);
assert.equal(context.escapeHtml('<img src=x onerror="alert(1)">'), '&lt;img src=x onerror=&quot;alert(1)&quot;&gt;');
assert.equal(context.escapeHtml("Tom & Jerry's"), "Tom &amp; Jerry&#39;s");
assert.equal(context.csrfToken(), "test-token");
context.document.cookie = "";
assert.equal(context.csrfToken(), "");
console.log("Frontend escaping and CSRF checks passed");
