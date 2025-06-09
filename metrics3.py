#!/usr/bin/env python3
"""
Peondedama – Extracción de métricas diarias de Make
---------------------------------------------------
• Descarga los logs de un escenario (API v2)
• Calcula ejecuciones, errores y latencia media por día
• Genera un gráfico PNG (chart.png)

Requiere variables de entorno:
    MAKE_ZONE       eu1 | eu2 | us1           (p.ej. "eu2")
    MAKE_TEAM_ID    1557908                   (nº de tu organización/equipo)
    SCENARIO_ID     5164268                  (nº del escenario)
    MAKE_TOKEN      <token con scope scenarios:logs:read>
"""
def main():
    import os, sys, io, requests, pandas as pd, matplotlib.pyplot as plt

    # ------------------------------------------------------------------ Config
    ZONE        = os.getenv("MAKE_ZONE", "eu2")
    TEAM_ID     = os.getenv("MAKE_TEAM_ID", "1557908")
    SCENARIO_ID = os.getenv("SCENARIO_ID", "5164268")
    TOKEN       = "2be818c3-dff7-44f5-bb52-3a2a57574085"

    for var, name in [(TEAM_ID, "MAKE_TEAM_ID"),
                    (SCENARIO_ID, "SCENARIO_ID"),
                    (TOKEN, "MAKE_TOKEN")]:
        if not var:
            sys.exit(f"💥 Falta la variable de entorno {name}")

    BASE  = f"https://{ZONE}.make.com/api/v2"
    HEAD  = {"Authorization": f"Token {TOKEN}"}

    PAGE_LIMIT = 50   # máximo que permite la API
    # ------------------------------------------------------------------ Descarga
    all_logs, offset = [], 0
    while True:
        url = (f"{BASE}/scenarios/{SCENARIO_ID}/logs"
            f"?teamId={TEAM_ID}&pg[limit]={PAGE_LIMIT}&pg[offset]={offset}")
        resp = requests.get(url, headers=HEAD)
        resp.raise_for_status()

        page = resp.json()["scenarioLogs"]
        if not page:
            break

        all_logs.extend(page)
        offset += PAGE_LIMIT

    if not all_logs:
        sys.exit("⚠️  No se encontraron logs para este escenario.")

    # ----------------------------------------------------------------- Filtrado
    end_logs = [x for x in all_logs
                if x.get("eventType") == "EXECUTION_END" and "status" in x]

    if not end_logs:
        sys.exit("⚠️  No hay eventos EXECUTION_END en el rango consultado.")
    if not end_logs:
        sys.exit("⚠️  No hay eventos EXECUTION_END en el rango consultado.")

    # --- Métricas ----------------------------
    days      = [pd.to_datetime(x["timestamp"]).date() for x in end_logs]
    statuses  = [x["status"] for x in end_logs]           # 1 OK, 2 Error
    durations = [x["duration"]/1000 for x in end_logs]    # ms → s

    df = pd.DataFrame({"day": days, "status": statuses, "duration": durations})

    daily = df.groupby("day").agg(
        runs    = ("status", "count"),
        errors  = ("status", lambda s: (s != 1).sum()),
        latency = ("duration", "mean")
    )

    # --- Gráfico -----------------------------
    import matplotlib.pyplot as plt
    plt.figure()
    daily["runs"].plot(label="Ejecuciones")
    daily["errors"].plot(label="Errores")
    plt.title("Peondedama – Métricas diarias (Make)")
    plt.ylabel("Nº")
    plt.legend()

    outfile = "chart.png"
    plt.savefig(outfile, bbox_inches="tight")
    print(f"✅ saved {outfile}")
