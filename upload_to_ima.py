"""
upload_to_ima.py — Upload backup markdown files to IMA Knowledge Base
Follows the 5-step upload flow: preflight → check_dupes → create_media → COS upload → add_knowledge
"""
import subprocess
import json
import os
import urllib.request
import time
import glob

# Config
KB_ID = "dDbUCbXJuKtduuYCnoE5WHeZYUpazLos1cA_HzkoUg4="
BASE_URL = "https://ima.qq.com/openapi/wiki/v1"
CLIENT_ID_FILE = os.path.expanduser("~/.config/ima/client_id")
API_KEY_FILE = os.path.expanduser("~/.config/ima/api_key")
BACKUP_DIR = "D:/hermes-tools/kb-backup"
IMA_SKILL_DIR = "D:/maozhua/ima-mcp/ima-skills/ima-skill"
PREFLIGHT_SCRIPT = os.path.join(IMA_SKILL_DIR, "knowledge-base/scripts/preflight-check.cjs")
COS_UPLOAD_SCRIPT = os.path.join(IMA_SKILL_DIR, "knowledge-base/scripts/cos-upload.cjs")

# Read credentials
with open(CLIENT_ID_FILE) as f:
    CLIENT_ID = f.read().strip()
with open(API_KEY_FILE) as f:
    API_KEY = f.read().strip()


def ima_api(endpoint, body):
    """Call IMA OpenAPI endpoint."""
    url = f"{BASE_URL}/{endpoint}"
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("ima-openapi-clientid", CLIENT_ID)
    req.add_header("ima-openapi-apikey", API_KEY)
    req.add_header("ima-openapi-ctx", "skill_version=1.1.7")
    
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body_text = e.read().decode("utf-8", errors="replace")
        return {"code": e.code, "msg": body_text}
    except Exception as e:
        return {"code": -1, "msg": str(e)}


def run_node(script, *args):
    """Run a Node.js script."""
    cmd = ["node", script] + list(args)
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    return result


def upload_file(filepath):
    """Upload a single file to IMA KB following the 5-step flow."""
    filename = os.path.basename(filepath)
    print(f"\n{'='*60}")
    print(f"📤 Uploading: {filename}")
    
    # Step 1: Preflight check
    print("  Step 1/5: Preflight check...")
    result = run_node(PREFLIGHT_SCRIPT, "--file", filepath)
    if result.returncode != 0:
        preflight = {}
        try:
            preflight = json.loads(result.stdout or "{}")
        except:
            pass
        reason = preflight.get("reason", result.stderr or "Unknown error")
        print(f"  ❌ Preflight failed: {reason}")
        return False
    
    preflight = json.loads(result.stdout)
    if not preflight.get("pass"):
        print(f"  ❌ Preflight rejected: {preflight.get('reason', 'Unknown')}")
        return False
    
    file_name = preflight["file_name"]
    file_size = preflight["file_size"]
    media_type = preflight["media_type"]
    content_type = preflight["content_type"]
    file_ext = preflight["file_ext"]
    print(f"  ✅ Preflight OK: {file_name} ({file_size/1024:.1f}KB, type={media_type})")
    
    # Step 2: Check duplicate names
    print("  Step 2/5: Checking for duplicates...")
    check_resp = ima_api("check_repeated_names", {
        "params": [{"name": file_name, "media_type": media_type}],
        "knowledge_base_id": KB_ID,
    })
    if check_resp.get("code", -1) == 0:
        data_list = check_resp.get("data", {}).get("params", [])
        for item in data_list:
            if item.get("is_repeated"):
                # Append timestamp to avoid conflict
                ts = time.strftime("%Y%m%d%H%M%S")
                base, ext = os.path.splitext(file_name)
                file_name = f"{base}_{ts}{ext}"
                print(f"  ⚠️ Duplicate found — renaming to {file_name}")
    else:
        print(f"  ⚠️ Duplicate check returned code={check_resp.get('code')}, proceeding anyway")
    
    # Step 3: Create media
    print("  Step 3/5: Creating media record...")
    create_resp = ima_api("create_media", {
        "file_name": file_name,
        "file_size": file_size,
        "content_type": content_type,
        "knowledge_base_id": KB_ID,
        "file_ext": file_ext,
    })
    
    if create_resp.get("code", -1) != 0:
        print(f"  ❌ create_media failed: {create_resp.get('msg', 'Unknown')}")
        return False
    
    media_id = create_resp.get("data", {}).get("media_id", "")
    cos_info = create_resp.get("data", {}).get("cos_credential", {})
    
    if not media_id or not cos_info:
        print(f"  ❌ Missing media_id or COS credentials in response")
        print(f"  Response: {json.dumps(create_resp, ensure_ascii=False)[:500]}")
        return False
    
    print(f"  ✅ Media created: media_id={media_id[:30]}...")
    
    # Step 4: COS upload
    print("  Step 4/5: Uploading to COS...")
    cos_args = [
        "--file", filepath,
        "--secret-id", cos_info.get("secret_id", ""),
        "--secret-key", cos_info.get("secret_key", ""),
        "--token", cos_info.get("token", ""),
        "--bucket", cos_info.get("bucket_name", ""),
        "--region", cos_info.get("region", ""),
        "--cos-key", cos_info.get("cos_key", ""),
        "--content-type", content_type,
        "--start-time", str(cos_info.get("start_time", "")),
        "--expired-time", str(cos_info.get("expired_time", "")),
        "--timeout", "300000",
    ]
    cos_result = run_node(COS_UPLOAD_SCRIPT, *cos_args)
    
    if cos_result.returncode != 0:
        print(f"  ❌ COS upload failed (exit={cos_result.returncode})")
        print(f"  stderr: {cos_result.stderr[:200]}")
        return False
    
    print(f"  ✅ COS upload successful")
    
    # Step 5: Add knowledge
    print("  Step 5/5: Adding to knowledge base...")
    add_resp = ima_api("add_knowledge", {
        "media_type": media_type,
        "media_id": media_id,
        "title": file_name,
        "knowledge_base_id": KB_ID,
        "file_info": {
            "cos_key": cos_info.get("cos_key", ""),
            "file_size": file_size,
            "file_name": file_name,
        }
    })
    
    if add_resp.get("code", -1) == 0:
        print(f"  ✅ Added to knowledge base successfully!")
        return True
    else:
        print(f"  ❌ add_knowledge failed: {add_resp.get('msg', 'Unknown')}")
        return False


def main():
    # Find all backup files from this run
    pattern = os.path.join(BACKUP_DIR, "local-kb-*-20260527-0203.md")
    files = sorted(glob.glob(pattern))
    
    if not files:
        print("❌ No backup files found matching pattern")
        print(f"   Searched: {pattern}")
        return
    
    print(f"📚 Found {len(files)} files to upload:")
    for f in files:
        size_kb = os.path.getsize(f) / 1024
        print(f"   {os.path.basename(f)} ({size_kb:.1f} KB)")
    
    results = []
    for f in files:
        success = upload_file(f)
        results.append((os.path.basename(f), success))
    
    # Summary
    print(f"\n{'='*60}")
    print(f"📊 Upload Summary")
    succeeded = sum(1 for _, s in results if s)
    failed = sum(1 for _, s in results if not s)
    print(f"   ✅ {succeeded} succeeded, ❌ {failed} failed")
    for name, ok in results:
        status = "✅" if ok else "❌"
        print(f"   {status} {name}")


if __name__ == "__main__":
    main()
