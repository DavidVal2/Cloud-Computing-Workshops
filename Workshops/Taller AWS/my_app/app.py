from flask import Flask, jsonify

app = Flask(__name__)

@app.get("/health")
def health():
    return jsonify({
        "status": "ok",
        "service": "equipment-api"
    })

@app.get("/equipos")
def equipos():
    return jsonify([
  {
    "name": "Laptop Mini Mac",
    "id": 1,
    "category": "Laptop",
    "price": "5000000"
  },
  {
    "name": "Smartphone Ultra 5G",
    "id": 2,
    "category": "Smartphone",
    "price": "3500000"
  },
  {
    "name": "Monitor Gamer 27 4K",
    "id": 3,
    "category": "Monitor",
    "price": "1800000"
  },
  {
    "name": "Teclado Mecánico RGB",
    "id": 4,
    "category": "Periféricos",
    "price": "350000"
  },
  {
    "name": "Mouse Inalámbrico Pro",
    "id": 5,
    "category": "Periféricos",
    "price": "220000"
  },
  {
    "name": "Audífonos Noise Cancelling",
    "id": 6,
    "category": "Audio",
    "price": "950000"
  },
  {
    "name": "Tablet Pro 11 Pulgadas",
    "id": 7,
    "category": "Tablet",
    "price": "2800000"
  },
  {
    "name": "Disco Duro SSD 1TB NVMe",
    "id": 8,
    "category": "Almacenamiento",
    "price": "450000"
  },
  {
    "name": "Silla Gamer Ergonómica",
    "id": 9,
    "category": "Mobiliario",
    "price": "850000"
  },
  {
    "name": "Cámara Web Full HD 1080p",
    "id": 10,
    "category": "Accesorios",
    "price": "180000"
  }
])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)