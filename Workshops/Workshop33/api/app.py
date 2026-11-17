import os
import psycopg
from psycopg.rows import dict_row
from flask import Flask, jsonify, request

app = Flask(__name__)
INSTANCE = os.getenv("INSTANCE", "api-local")

def get_connection():
    return psycopg.connect(
        host=os.getenv("DB_HOST"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

def product_to_dict(product):
    product["price"] = float(product["price"])
    return product

@app.get("/products")
def get_products():
    with get_connection() as connection:
        with connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute("SELECT id, name, price FROM products ORDER BY id")
            products = [product_to_dict(product) for product in cursor.fetchall()]

    return jsonify({"served_by": INSTANCE, "products": products})

@app.get("/products/<int:product_id>")
def get_product(product_id):
    with get_connection() as connection:
        with connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                "SELECT id, name, price FROM products WHERE id = %s",
                (product_id,)
            )
            product = cursor.fetchone()

    if product is None:
        return jsonify({"message": "Producto no encontrado"}), 404

    return jsonify({"served_by": INSTANCE, "product": product_to_dict(product)})

@app.post("/products")
def create_product():
    data = request.get_json()

    with get_connection() as connection:
        with connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                "INSERT INTO products (name, price) VALUES (%s, %s) RETURNING id, name, price",
                (data["name"], data["price"])
            )
            product = cursor.fetchone()

    return jsonify({"served_by": INSTANCE, "product": product_to_dict(product)}), 201

@app.put("/products/<int:product_id>")
def update_product(product_id):
    data = request.get_json()

    with get_connection() as connection:
        with connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                "UPDATE products SET name = %s, price = %s WHERE id = %s RETURNING id, name, price",
                (data["name"], data["price"], product_id)
            )
            product = cursor.fetchone()

    if product is None:
        return jsonify({"message": "Producto no encontrado"}), 404

    return jsonify({"served_by": INSTANCE, "product": product_to_dict(product)})

@app.delete("/products/<int:product_id>")
def delete_product(product_id):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM products WHERE id = %s", (product_id,))

    return jsonify({"served_by": INSTANCE, "message": "Producto eliminado"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
