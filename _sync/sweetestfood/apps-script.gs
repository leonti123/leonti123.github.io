// Google Apps Script: the SweetestFood VK mini app sends the admin's VK token here.
// The script reads the group's VK market itself (so nobody can post fake prices),
// saves it to the site repo, and the push starts the GitHub Actions rebuild.
// Script properties: GH_TOKEN (fine-grained token: repo leonti123.github.io, Contents read/write)
const GID = 241272766;
const REPO = "leonti123/leonti123.github.io";
const PATH = "_sync/sweetestfood/data/market.json";

const reply = body => ContentService.createTextOutput(JSON.stringify(body)).setMimeType(ContentService.MimeType.JSON);

function vk(method, params) {
  const res = UrlFetchApp.fetch("https://api.vk.com/method/" + method, {
    method: "post", muteHttpExceptions: true, payload: Object.assign({ v: "5.199" }, params),
  });
  return JSON.parse(res.getContentText());
}

function gh(method, url, payload) {
  const opt = {
    method, muteHttpExceptions: true,
    headers: { Authorization: "Bearer " + PropertiesService.getScriptProperties().getProperty("GH_TOKEN"), Accept: "application/vnd.github+json" },
  };
  if (payload) { opt.contentType = "application/json"; opt.payload = JSON.stringify(payload); }
  const res = UrlFetchApp.fetch("https://api.github.com/repos/" + REPO + url, opt);
  return { code: res.getResponseCode(), body: JSON.parse(res.getContentText() || "{}") };
}

function doPost(e) {
  let body;
  try { body = JSON.parse(e.postData.contents); } catch (err) { return reply({ ok: false, error: "bad_json" }); }
  const token = String(body.token || "");
  if (!/^[\w.\-]{20,400}$/.test(token)) return reply({ ok: false, error: "bad_token" });

  // One update at a time is plenty: the button is pressed by hand
  const cache = CacheService.getScriptCache();
  if (cache.get("busy")) return reply({ ok: false, error: "busy" });
  cache.put("busy", "1", 20);

  const market = vk("market.get", { access_token: token, owner_id: -GID, count: 200, extended: 1 });
  if (market.error) {
    // Log only the code and text: the request contains the token
    console.log(`VK error ${market.error.error_code}: ${market.error.error_msg}`);
    return reply({ ok: false, error: "vk", code: market.error.error_code, msg: market.error.error_msg });
  }
  const items = (market.response && market.response.items) || [];
  if (!items.length || items.some(it => it.owner_id !== -GID)) return reply({ ok: false, error: "empty" });

  const content = Utilities.base64Encode(Utilities.newBlob(JSON.stringify(market)).getBytes());
  for (let attempt = 0; attempt < 3; attempt++) {
    const cur = gh("get", "/contents/" + PATH + "?ref=main");
    if (cur.code !== 200) { console.log("GitHub get " + cur.code); return reply({ ok: false, error: "github", code: cur.code }); }
    const put = gh("put", "/contents/" + PATH, {
      message: "sweetestfood: menu from VK (button in the mini app)", content, sha: cur.body.sha, branch: "main",
    });
    if (put.code === 200 || put.code === 201) return reply({ ok: true, count: items.length, sha: put.body.commit.sha });
    if (put.code !== 409) { console.log("GitHub put " + put.code); return reply({ ok: false, error: "github", code: put.code }); }
    Utilities.sleep(1500); // the sync bot committed in between: take the new sha and retry
  }
  return reply({ ok: false, error: "github", code: 409 });
}

function doGet() { return reply({ ok: true, service: "sweetestfood menu update" }); }

// Run by hand to check the GitHub token: logs whether it can push to the repo
function checkGitHub() {
  const r = gh("get", "");
  console.log("GitHub " + r.code + " push=" + (r.body.permissions && r.body.permissions.push));
}
