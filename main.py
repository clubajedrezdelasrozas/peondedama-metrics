# main.py  ───── servidor Flask que llama a metrics2.generate_chart()
from flask import Flask, send_file
import metrics2          # importa tu script tal cual

app = Flask(__name__)

@app.route("/")
def run_metrics():
    # metrics2 genera chart.png en el cwd
    metrics2.main()      # asegúrate de que tu código va en una función main()
    return send_file("chart.png", mimetype="image/png")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)