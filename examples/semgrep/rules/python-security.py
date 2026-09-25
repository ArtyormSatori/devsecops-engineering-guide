# ---------------------------------------------------------------------------
# Test cases for python-security.yaml
#
#   semgrep --test --config rules/
#
# Annotations go on the line immediately above the code. A "ruleid" comment
# marks a line that MUST be flagged (guarding against false negatives); an
# "ok" comment marks a line that must NOT be flagged (guarding against false
# positives). Semgrep also understands "todoruleid" and "todook" for known
# gaps you have not fixed yet.
#
# Every rule needs both kinds. A rule with only positive tests drifts into
# flagging everything, and nobody notices until the team turns it off.
# ---------------------------------------------------------------------------
import hashlib
import json
import os
import pickle
import ssl
import subprocess

import jwt
import requests
import yaml


# ---------------------------------------------------------------------------
# orm-query-missing-tenant-scope
# ---------------------------------------------------------------------------
def list_invoices_broken(db):
    # ruleid: orm-query-missing-tenant-scope
    return db.session.query(Invoice).all()


def get_invoice_broken(db, invoice_id):
    # ruleid: orm-query-missing-tenant-scope
    return db.session.query(Invoice).filter(Invoice.id == invoice_id).all()


def list_invoices_django_broken():
    # ruleid: orm-query-missing-tenant-scope
    return Invoice.objects.filter(status="open").all()


def list_invoices_scoped(db, tenant_id):
    # ok: orm-query-missing-tenant-scope
    return db.session.query(Invoice).filter(Invoice.tenant_id == tenant_id).all()


def get_invoice_scoped(db, tenant_id, invoice_id):
    # ok: orm-query-missing-tenant-scope
    return (
        db.session.query(Invoice)
        .filter(Invoice.tenant_id == tenant_id, Invoice.id == invoice_id)
        .first()
    )


# ---------------------------------------------------------------------------
# jwt-signature-not-verified
# ---------------------------------------------------------------------------
def identity_from_token_broken(token):
    # ruleid: jwt-signature-not-verified
    return jwt.decode(token, options={"verify_signature": False})


def identity_from_token_also_broken(token, key):
    # ruleid: jwt-signature-not-verified
    return jwt.decode(token, key, algorithms=["HS256", "none"])


def identity_from_token(token, key):
    # ok: jwt-signature-not-verified
    return jwt.decode(token, key, algorithms=["RS256"], audience="api")


# ---------------------------------------------------------------------------
# tls-verification-disabled
# ---------------------------------------------------------------------------
def fetch_broken(url):
    # ruleid: tls-verification-disabled
    return requests.get(url, timeout=10, verify=False)


def unverified_context_broken():
    # ruleid: tls-verification-disabled
    return ssl._create_unverified_context()


def fetch(url):
    # ok: tls-verification-disabled
    return requests.get(url, timeout=10)


def fetch_internal(url):
    # ok: tls-verification-disabled
    return requests.get(url, timeout=10, verify="/etc/ssl/certs/internal-ca.pem")


# ---------------------------------------------------------------------------
# subprocess-shell-true-with-interpolation
# ---------------------------------------------------------------------------
def archive_broken(directory):
    # ruleid: subprocess-shell-true-with-interpolation
    subprocess.run(f"tar -czf backup.tgz {directory}", shell=True, check=True)


def ping_broken(host):
    # ruleid: subprocess-shell-true-with-interpolation
    os.system("ping -c 1 " + host)


def archive(directory):
    # ok: subprocess-shell-true-with-interpolation
    subprocess.run(["tar", "-czf", "backup.tgz", directory], check=True)


def list_root():
    # ok: subprocess-shell-true-with-interpolation
    subprocess.run("ls -la /", shell=True, check=True)


# ---------------------------------------------------------------------------
# secret-passed-as-cli-argument
# ---------------------------------------------------------------------------
def dump_database_broken(password):
    # ruleid: secret-passed-as-cli-argument
    subprocess.run(["mysqldump", "--password", password, "appdb"], check=True)


def push_image_broken(token):
    # ruleid: secret-passed-as-cli-argument
    subprocess.run(["registry-cli", "login", "--token", token], check=True)


def dump_database(password):
    # ok: secret-passed-as-cli-argument
    subprocess.run(
        ["mysqldump", "appdb"],
        env={**os.environ, "MYSQL_PWD": password},
        check=True,
    )


# ---------------------------------------------------------------------------
# unsafe-deserialisation
# ---------------------------------------------------------------------------
def load_config_broken(raw):
    # ruleid: unsafe-deserialisation
    return yaml.load(raw)


def load_cache_broken(blob):
    # ruleid: unsafe-deserialisation
    return pickle.loads(blob)


def load_config(raw):
    # ok: unsafe-deserialisation
    return yaml.safe_load(raw)


def load_cache(blob):
    # ok: unsafe-deserialisation
    return json.loads(blob)


def content_digest(blob):
    # ok: unsafe-deserialisation
    return hashlib.sha256(blob).hexdigest()
