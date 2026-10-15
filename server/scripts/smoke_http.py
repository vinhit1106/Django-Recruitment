"""Minimal HTTP smoke test for the local API.

Usage: python scripts/smoke_http.py
Environment: API_BASE_URL (default http://127.0.0.1:8000), SMOKE_PASSWORD.
Tokens are held in memory and are never printed.
"""
import json
import os
import time
import urllib.error
import urllib.request

BASE = os.getenv("API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
PASSWORD = os.getenv("SMOKE_PASSWORD") or os.getenv("DEMO_PASSWORD")
if not PASSWORD or len(PASSWORD) < 8:
    raise SystemExit("SMOKE_PASSWORD or DEMO_PASSWORD (8+ chars) is required.")


def call(path, method="GET", payload=None, token=None, expected=200):
    data = json.dumps(payload).encode() if payload is not None else None
    headers = {"Accept": "application/json"}
    if payload is not None:
        headers["Content-Type"] = "application/json"
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(BASE + path, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            status = response.status
            body = response.read()
    except urllib.error.HTTPError as error:
        status = error.code
        body = error.read()
    except urllib.error.URLError as error:
        raise SystemExit(f"HTTP smoke blocked: {error.reason}") from error
    if status != expected:
        raise SystemExit(f"{method} {path}: expected {expected}, got {status}")
    try:
        return json.loads(body.decode()) if body else {}
    except json.JSONDecodeError:
        return {}


health = call("/api/v1/health/")
if health.get("status") != "ok" or health.get("database") != "ok":
    raise SystemExit("Health endpoint did not report an available database.")

schema_request = urllib.request.Request(BASE + "/api/schema/?format=json", headers={"Accept": "application/json"})
with urllib.request.urlopen(schema_request, timeout=10) as response:
    schema = json.load(response)
operation = schema["paths"]["/api/v1/auth/register/"]["post"]
components = schema["components"]["schemas"]

def resolve(value):
    while "$ref" in value or "allOf" in value:
        if "$ref" in value:
            value = components[value["$ref"].split("/")[-1]]
        elif "allOf" in value:
            value = value["allOf"][0]
    return value

request_schema = resolve(operation["requestBody"]["content"]["application/json"]["schema"])
if set(request_schema["required"]) != {"email", "password"}:
    raise SystemExit("Registration required fields do not match the verified contract.")
role_schema = resolve(request_schema["properties"]["role"])
if set(role_schema["enum"]) != {"CANDIDATE", "EMPLOYER"}:
    raise SystemExit("Registration role enum does not match the verified contract.")

suffix = str(time.time_ns())
email = f"smoke.{suffix}@example.com"
registered = call("/api/v1/auth/register/", "POST", {"email": email, "password": PASSWORD, "first_name": "Smoke", "last_name": "Test"}, expected=201)
response_schema = resolve(operation["responses"]["201"]["content"]["application/json"]["schema"])
if set(registered) != set(response_schema["properties"]) or registered["user"]["role"] != "CANDIDATE":
    raise SystemExit("Registration response does not match OpenAPI.")
call("/api/v1/candidate/profile/", token=registered["access"])
duplicate = call("/api/v1/auth/register/", "POST", {"email": email.upper(), "password": PASSWORD}, expected=400)
if "email" not in duplicate.get("error", {}).get("details", {}):
    raise SystemExit("Duplicate email did not return field validation.")
call("/api/v1/auth/register/", "POST", {"email": f"smoke.admin.{suffix}@example.com", "password": PASSWORD, "role": "ADMIN"}, expected=400)
call("/api/v1/auth/register/", "POST", {"email": f"smoke.weak.{suffix}@example.com", "password": "password"}, expected=400)
employer = call("/api/v1/auth/register/", "POST", {"email": f"smoke.employer.{suffix}@example.com", "password": PASSWORD, "role": "EMPLOYER"}, expected=201)
if employer["user"]["role"] != "EMPLOYER":
    raise SystemExit("Employer registration returned the wrong role.")
login = call("/api/v1/auth/login/", "POST", {"email": email, "password": PASSWORD})
access = login.get("access")
refresh = login.get("refresh")
if not access or not refresh:
    raise SystemExit("Registration did not return JWT pair.")
me = call("/api/v1/auth/me/", token=access)
if me.get("email") != email:
    raise SystemExit("Authenticated profile did not match the registered user.")
jobs = call("/api/v1/jobs/")
if not isinstance(jobs.get("results"), list):
    raise SystemExit("Public job response is not paginated.")
rotated = call("/api/v1/auth/refresh/", "POST", {"refresh": refresh})
if not rotated.get("access") or not rotated.get("refresh"):
    raise SystemExit("Refresh rotation did not return a JWT pair.")
call("/api/v1/auth/logout/", "POST", {"refresh": rotated["refresh"]}, token=rotated["access"], expected=204)
print("HTTP smoke passed: health/database, live OpenAPI registration contract, candidate/employer registration, candidate profile, duplicate/admin/weak password rejection, login, me, jobs pagination, refresh rotation, logout.")
