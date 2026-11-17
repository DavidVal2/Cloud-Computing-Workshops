import os
import socket
from datetime import datetime, timezone

from flask import Flask

app = Flask(__name__)


@app.get("/")
def home():
    return {
        "message": "Hola desde EC2",
        "hostname_contenedor": socket.gethostname(),
        "hostname_ec2": os.getenv("EC2_HOSTNAME", "configurar-EC2_HOSTNAME-en-el-host"),
        "hora_utc": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
