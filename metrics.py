# metrics.py
import requests, pandas as pd, matplotlib.pyplot as plt, io, os, datetime as dt

TOKEN = os.environ["MAKE_TOKEN"]
SCENARIO_ID = "123456"

headers = {"Authorization": f"Token {TOKEN}"}
url = f"https://api.make.com/v2/scenarios/{SCENARIO_ID}/executions?limit=1000"
data = requests.get(url, headers=headers).json()["data"]

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
