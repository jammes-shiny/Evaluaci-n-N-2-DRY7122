# sample_app.py
from flask import Flask

app = Flask(__name__)

@app.route("/")
def main():
    return "<h1>Muestra de aplicacion web en Python - Evaluacion CI/CD</h1>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050)
