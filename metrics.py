import os, sys, requests, pandas as pd, matplotlib.pyplot as plt
ZONE = os.getenv("MAKE_ZONE", "eu2")                # tu zona
BASE = f"https://{ZONE}.make.com/api/v2"            # ← añade /api/


ZONE        = os.getenv("MAKE_ZONE", "eu2")
TEAM_ID     = os.getenv("MAKE_TEAM_ID", "1557908")
SCENARIO_ID = os.getenv("SCENARIO_ID", "5164268")
TOKEN       = "2be818c3-dff7-44f5-bb52-3a2a57574085"
BASE = f"https://{ZONE}.make.com/api/v2"


PAGE = 50                   # máximo aceptado por la API
offset = 0
all_logs = []
headers = {"Authorization": f"Token {TOKEN}"}

while True:
    url = (
        f"{BASE}/scenarios/{SCENARIO_ID}/logs"
        f"?teamId={TEAM_ID}&pg[limit]={PAGE}&pg[offset]={offset}"
    )
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()

    page_logs = resp.json()["scenarioLogs"]
    if not page_logs:
        break

    all_logs.extend(page_logs)
    offset += PAGE          # siguiente página

if not TOKEN or not SCENARIO_ID:
    sys.exit("Faltan MAKE_TOKEN o SCENARIO_ID")





resp = requests.get(url, headers=headers)
resp.raise_for_status()                       # lanza error si no es 2xx

logs = resp.json()["scenarioLogs"]   

df = pd.DataFrame([{
        "start": x["startedAt"],
        "status": x["status"],
        "duration": x["duration"]/1000
    } for x in data])

df["day"] = pd.to_datetime(df["start"]).dt.date
daily = df.groupby("day").agg(runs=("status","count"),
                              errors=("status",lambda s: (s!="success").sum()),
                              latency=("duration","mean"))

plt.figure()
daily["runs"].plot(label="Ejecuciones")
daily["errors"].plot(label="Errores")
plt.legend()
plt.title("Peondedama – Métricas diarias")
plt.ylabel("Nº")
buf = io.BytesIO()
plt.savefig(buf, format="png")
buf.seek(0)
open("/tmp/chart.png","wb").write(buf.read())
print("saved /tmp/chart.png")
