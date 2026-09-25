// ---------------------------------------------------------------------------
// Test cases for javascript-security.yaml
//
//   semgrep --test --config rules/
//
// Annotations go on the line immediately above the code. A "ruleid" comment
// marks a line that MUST be flagged; an "ok" comment marks a line that must
// NOT be flagged. Both directions matter — the false-positive tests are what
// keep a rule deployable.
// ---------------------------------------------------------------------------
const cp = require("child_process");
const crypto = require("crypto");
const jwt = require("jsonwebtoken");

// ---------------------------------------------------------------------------
// js-mongo-query-missing-tenant-scope
// ---------------------------------------------------------------------------
async function listInvoicesBroken(db) {
  // ruleid: js-mongo-query-missing-tenant-scope
  return db.collection("invoices").find({ status: "open" });
}

async function getInvoiceBroken(db, id) {
  // ruleid: js-mongo-query-missing-tenant-scope
  return db.collection("invoices").findOne({ _id: id });
}

async function listInvoicesScoped(db, tenantId) {
  // ok: js-mongo-query-missing-tenant-scope
  return db.collection("invoices").find({ tenantId, status: "open" });
}

async function getInvoiceScoped(db, tenantId, id) {
  // ok: js-mongo-query-missing-tenant-scope
  return db.collection("invoices").findOne({ _id: id, tenantId: tenantId });
}

// ---------------------------------------------------------------------------
// js-jwt-decoded-without-verification
// ---------------------------------------------------------------------------
function currentUserBroken(req) {
  // ruleid: js-jwt-decoded-without-verification
  const claims = jwt.decode(req.headers.authorization);
  return claims.sub;
}

function currentUser(req, publicKey) {
  // ok: js-jwt-decoded-without-verification
  const claims = jwt.verify(req.headers.authorization, publicKey, {
    algorithms: ["RS256"],
    audience: "api",
  });
  return claims.sub;
}

// ---------------------------------------------------------------------------
// js-tls-verification-disabled
// ---------------------------------------------------------------------------
function agentBroken(https) {
  // ruleid: js-tls-verification-disabled
  return new https.Agent({ rejectUnauthorized: false });
}

function agent(https, ca) {
  // ok: js-tls-verification-disabled
  return new https.Agent({ ca });
}

// ---------------------------------------------------------------------------
// js-command-injection-via-interpolation
// ---------------------------------------------------------------------------
function archiveBroken(directory) {
  // ruleid: js-command-injection-via-interpolation
  cp.execSync(`tar -czf backup.tgz ${directory}`);
}

function convertBroken(filename) {
  // ruleid: js-command-injection-via-interpolation
  cp.exec("convert " + filename + " out.png");
}

function archive(directory) {
  // ok: js-command-injection-via-interpolation
  cp.execFileSync("tar", ["-czf", "backup.tgz", directory]);
}

// ---------------------------------------------------------------------------
// js-timing-unsafe-secret-comparison
// ---------------------------------------------------------------------------
function checkWebhookBroken(expectedSignature, providedSignature) {
  // ruleid: js-timing-unsafe-secret-comparison
  return expectedSignature === providedSignature;
}

function checkWebhook(expected, provided) {
  const a = Buffer.from(expected, "hex");
  const b = Buffer.from(provided, "hex");
  // ok: js-timing-unsafe-secret-comparison
  return a.length === b.length && crypto.timingSafeEqual(a, b);
}

function isSameUser(currentUserId, requestedUserId) {
  // ok: js-timing-unsafe-secret-comparison
  return currentUserId === requestedUserId;
}
