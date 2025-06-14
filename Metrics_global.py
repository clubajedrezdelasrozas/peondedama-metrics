"""Peondedama · Dashboard multi-escenario (Make API v2)
----------------------------------------------------
1. Obtiene la lista de escenarios de TU equipo.
2. Para cada escenario:
   • Descarga los EXECUTION_END más recientes
   • Calcula runs, errores y latencia media por día
   • Genera un PNG   →  chart_<scenarioId>.png
3. Produce un pie.png con el % de runs por escenario
"""

import os, sys, requests, pandas as pd, matplotlib.pyplot as plt, io

# ─────────────── Parámetros de entorno ─────────────
ZONE = os.getenv("MAKE_ZONE", "eu2")
TEAM = os.getenv("MAKE_TEAM_ID", "1557908")
TOKEN = "2be818c3-dff7-44f5-bb52-3a2a57574085"
if not TEAM or not TOKEN:
    sys.exit("💥 Falta MAKE_TEAM_ID o MAKE_TOKEN")

BASE = f"https://{ZONE}.make.com/api/v2"
HEAD = {"Authorization": f"Token {TOKEN}"}
PAGE = 50        # límite API
DAYS_BACK = 30   # cuánto histórico quieres

# ─────────────── Helpers ─────────────
def list_scenarios() -> list[tuple[str, str]]:
    url = f"{BASE}/scenarios?teamId={TEAM}&cols[]=id&cols[]=name"
    resp = requests.get(url, headers=HEAD).json()["scenarios"]
    return [(str(x["id"]), x["name"]) for x in resp]

def fetch_logs(sc_id: str) -> list[dict]:
    logs, offset = [], 0
    while True:
        url = (f"{BASE}/scenarios/{sc_id}/logs"
               f"?teamId={TEAM}&pg[limit]={PAGE}&pg[offset]={offset}")
        page = requests.get(url, headers=HEAD).json()["scenarioLogs"]
        if not page:
            break
        logs.extend(page)
        offset += PAGE
    end_logs = [x for x in logs
                if x.get("eventType") == "EXECUTION_END" and "status" in x]
    return end_logs

def daily_df(end_logs: list[dict]) -> pd.DataFrame:
    # Convertimos cada timestamp a fecha (yyyy-mm-dd)
    days = [pd.to_datetime(x["timestamp"]).date() for x in end_logs]

    df = pd.DataFrame({
        "day":      days,
        "status":   [x["status"]    for x in end_logs],   # 1 OK, 2 Error
        "duration": [x["duration"]/1000 for x in end_logs]   # ms → s
    })

    return df.groupby("day").agg(
        runs    = ("status", "count"),
        errors  = ("status", lambda s: (s != 1).sum()),
        latency = ("duration", "mean")
    ).tail(DAYS_BACK)

# ─────────────── Main ─────────────
totals = {}       # escenario → nº de runs (para la tarta)

for sc_id, sc_name in list_scenarios():
    end_logs = fetch_logs(sc_id)
    if not end_logs:
        print(f"⚠️  Sin logs para {sc_name}")
        continue

    daily = daily_df(end_logs)
    totals[sc_name] = daily["runs"].sum()

    # ▸ Gráfico individual
    plt.figure()
    daily["runs"].plot(label="Ejecuciones", linewidth=2)
    daily["errors"].plot(label="Errores", linewidth=1)
    plt.title(f"{sc_name} – Métricas diarias")
    plt.ylabel("Nº")
    plt.legend()
    out = f"chart_{sc_id}.png"
    plt.savefig(out, bbox_inches="tight")
    print("✅", out)

# ─────────────── Pie chart global ─────────────
if totals:
    labels, sizes = zip(*totals.items())
    plt.figure()
    plt.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=140)
    plt.title("Distribución de ejecuciones por escenario")
    plt.savefig("pie.png", bbox_inches="tight")
    print("✅ pie.png")
else:
    print("⚠️  No se generó ningún gráfico (sin datos)")