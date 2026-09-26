import urllib.request
import json
import os

api_key = "rnd_vsNd9zqRTgLh8Jd13NDyPJQsiDNW"
service_id = "srv-daro718jo6nc738p9a1g"

url = f"https://api.render.com/v1/services/{service_id}"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

payload = {
    "serviceDetails": {
        "envSpecificDetails": {
            "buildCommand": "pip install -r requirements.txt",
            "startCommand": "uvicorn backend.main:app --host 0.0.0.0 --port 10000"
        }
    }
}

req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers, method='PATCH')
try:
    with urllib.request.urlopen(req) as resp:
        res_data = json.loads(resp.read().decode())
        print("Updated Service Start Command:", res_data['serviceDetails']['envSpecificDetails']['startCommand'])
except Exception as e:
    print("Error updating service:", e)

# Trigger new deploy
deploy_url = f"https://api.render.com/v1/services/{service_id}/deploys"
req_deploy = urllib.request.Request(deploy_url, data=json.dumps({}).encode('utf-8'), headers=headers, method='POST')
try:
    with urllib.request.urlopen(req_deploy) as resp:
        res_deploy = json.loads(resp.read().decode())
        print("Triggered New Deploy ID:", res_deploy.get("id"))
except Exception as e:
    print("Error triggering deploy:", e)
