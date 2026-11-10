// Google Apps Script: the SweetestFood VK mini app sends the group's goods here,
// the script saves them to the site repo, and the push starts the GitHub Actions rebuild.
// The mini app's VK token only works from inside VK (from Google VK answers error 5),
// so the app reads the goods itself and the script trusts them only when the VK launch
// signature is valid and the user is allowed.
// Script properties:
//   GH_TOKEN       fine-grained token: repo leonti123.github.io, Contents read/write
//   VK_APP_SECRET  «Защищённый ключ» of VK app 54888593 (signs the launch params)
//   ALLOWED_USERS  optional extra VK user ids, comma-separated
const GID = 241272766;
const APP_ID = "54888593";
const USERS = ["8398959", "538251826"]; // Ольга (SweetestFood), Леонтий
const REPO = "leonti123/leonti123.github.io";
const PATH = "_sync/sweetestfood/data/market.json";

const reply = body => ContentService.createTextOutput(JSON.stringify(body)).setMimeType(ContentService.MimeType.JSON);
const fail = (error, extra) => { console.log("refused: " + error); return reply(Object.assign({ ok: false, error }, extra || {})); };

function gh(method, url, payload) {
  const opt = {
    method, muteHttpExceptions: true,
    headers: { Authorization: "Bearer " + PropertiesService.getScriptProperties().getProperty("GH_TOKEN"), Accept: "application/vnd.github+json" },
  };
  if (payload) { opt.contentType = "application/json"; opt.payload = JSON.stringify(payload); }
  const res = UrlFetchApp.fetch("https://api.github.com/repos/" + REPO + url, opt);
  return { code: res.getResponseCode(), body: JSON.parse(res.getContentText() || "{}") };
}

// VK launch params check: vk_* params sorted by name, HMAC-SHA256 with the app secret, base64url without "="
function launchUser(query) {
  const secret = PropertiesService.getScriptProperties().getProperty("VK_APP_SECRET");
  if (!secret) return null;
  const params = {};
  String(query || "").replace(/^\?/, "").split("&").forEach(pair => {
    const i = pair.indexOf("=");
    if (i > 0) params[decodeURIComponent(pair.slice(0, i))] = decodeURIComponent(pair.slice(i + 1).replace(/\+/g, " "));
  });
  const keys = Object.keys(params).filter(k => k.indexOf("vk_") === 0).sort();
  const signed = keys.map(k => k + "=" + encodeURIComponent(params[k])).join("&");
  const sign = Utilities.base64EncodeWebSafe(Utilities.computeHmacSha256Signature(signed, secret)).replace(/=+$/, "");
  if (!params.sign || sign !== params.sign) return null;
  if (params.vk_app_id !== APP_ID) return null;
  if (Date.now() / 1000 - Number(params.vk_ts || 0) > 2 * 86400) return null; // launch older than 2 days
  return params.vk_user_id;
}

function doPost(e) {
  let body;
  try { body = JSON.parse(e.postData.contents); } catch (err) { return fail("bad_json"); }

  const user = launchUser(body.launch);
  if (!user) return fail("bad_sign");
  const extra = (PropertiesService.getScriptProperties().getProperty("ALLOWED_USERS") || "").split(",").map(s => s.trim());
  if (USERS.indexOf(user) < 0 && extra.indexOf(user) < 0) return fail("not_allowed", { user });

  // One update at a time is plenty: the button is pressed by hand
  const cache = CacheService.getScriptCache();
  if (cache.get("busy")) return fail("busy");
  cache.put("busy", "1", 20);

  const market = body.market;
  const items = market && market.response && market.response.items;
  if (!Array.isArray(items) || !items.length || items.length > 200) return fail("empty");
  const okItem = it => it && it.owner_id === -GID && typeof it.id === "number" && typeof it.title === "string" && it.price && /^\d+$/.test(String(it.price.amount));
  if (!items.every(okItem)) return fail("bad_items");
  console.log("market items " + items.length + " from user " + user);

  const content = Utilities.base64Encode(Utilities.newBlob(JSON.stringify({ response: { count: items.length, items } })).getBytes());
  for (let attempt = 0; attempt < 3; attempt++) {
    const cur = gh("get", "/contents/" + PATH + "?ref=main");
    if (cur.code !== 200) return fail("github", { code: cur.code });
    const put = gh("put", "/contents/" + PATH, {
      message: "sweetestfood: menu from VK (button in the mini app)", content, sha: cur.body.sha, branch: "main",
    });
    if (put.code === 200 || put.code === 201) return reply({ ok: true, count: items.length, sha: put.body.commit.sha });
    if (put.code !== 409) return fail("github", { code: put.code });
    Utilities.sleep(1500); // the sync bot committed in between: take the new sha and retry
  }
  return fail("github", { code: 409 });
}

function doGet() { return reply({ ok: true, service: "sweetestfood menu update" }); }

// Run by hand to check the GitHub token: logs whether it can push to the repo
function checkGitHub() {
  const r = gh("get", "");
  console.log("GitHub " + r.code + " push=" + (r.body.permissions && r.body.permissions.push));
}
