import assert from "node:assert/strict";
import test from "node:test";

async function render() {
  const workerUrl = new URL("../dist/server/index.js", import.meta.url);
  workerUrl.searchParams.set("test", `${process.pid}-${Date.now()}`);
  const { default: worker } = await import(workerUrl.href);

  return worker.fetch(
    new Request("http://localhost/", { headers: { accept: "text/html" } }),
    { ASSETS: { fetch: async () => new Response("Not found", { status: 404 }) } },
    { waitUntil() {}, passThroughOnException() {} },
  );
}

test("server-renders the Dancing Angels AI website shell", async () => {
  const response = await render();
  assert.equal(response.status, 200);
  assert.match(response.headers.get("content-type") ?? "", /^text\/html\b/i);

  const html = await response.text();
  assert.match(html, /<title>Dancing Angels AI — Make your hero dance<\/title>/i);
  assert.match(html, /Dancing Angels\s*<strong>AI<\/strong>/i);
  assert.match(html, /Choose your hero(?:&apos;|&#x27;|')s moves/);
  assert.match(html, /Preview dance/);
  assert.match(html, /Bring my hero to life/);
  assert.match(html, /Add a song/);
  assert.match(html, /Add your character/);
  assert.match(html, /Dance on beat/);
  assert.match(html, /My Heroes/);
  assert.match(html, /Play song/);
  assert.match(html, /Upload your song/);
  assert.match(html, /Step 7 complete/);
  assert.match(html, /Blueprint Grid/);
  assert.match(html, /Holographic Polymer/);
  assert.match(html, /Golden Beat/);
  assert.match(html, /I Will Be Here \(Wolfgang Gartner Remix\)/);
  assert.match(html, /Tiësto &amp; Sneaky Sound System/);
  assert.match(html, /woman-1\.png/);
  assert.match(html, /\/og\.png/);
  assert.doesNotMatch(html, /Your site is taking shape|react-loading-skeleton/);
});
