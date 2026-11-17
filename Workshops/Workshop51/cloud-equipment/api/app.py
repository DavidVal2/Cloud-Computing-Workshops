import os
from datetime import date, datetime

import boto3
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, jsonify, request

app = Flask(__name__)


def db_connect():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "db"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "equipment"),
        user=os.getenv("DB_USER", "equipment"),
        password=os.getenv("DB_PASSWORD", "equipment-local-password"),
        cursor_factory=RealDictCursor,
    )


def rows(query, params=(), one=False):
    with db_connect() as connection, connection.cursor() as cursor:
        cursor.execute(query, params)
        if cursor.description is None:
            return None if one else []
        result = cursor.fetchone() if one else cursor.fetchall()
        return dict(result) if one and result else ([dict(row) for row in result] if result else None if one else [])


def json_error(message, status):
    return jsonify({"error": message}), status


@app.get("/health")
def health():
    try:
        rows("SELECT 1", one=True)
    except psycopg2.Error:
        return jsonify({"status": "error", "service": "equipment-api"}), 503
    return jsonify({"status": "ok", "service": "equipment-api"})


@app.get("/empleados")
def list_employees():
    return jsonify(rows("SELECT id, name AS nombre, email AS correo, department AS departamento FROM employees ORDER BY id"))


@app.post("/empleados")
def create_employee():
    data = request.get_json(silent=True) or {}
    if not data.get("nombre") or not data.get("correo"):
        return json_error("nombre y correo son obligatorios", 400)
    try:
        employee = rows(
            "INSERT INTO employees(name,email,department) VALUES (%s,%s,%s) RETURNING id,name AS nombre,email AS correo,department AS departamento",
            (data["nombre"], data["correo"], data.get("departamento")), one=True)
    except psycopg2.errors.UniqueViolation:
        return json_error("el correo ya está registrado", 409)
    return jsonify(employee), 201


@app.get("/empleados/<int:employee_id>")
def get_employee(employee_id):
    employee = rows("SELECT id,name AS nombre,email AS correo,department AS departamento FROM employees WHERE id=%s", (employee_id,), one=True)
    return (jsonify(employee), 200) if employee else json_error("empleado no encontrado", 404)


@app.get("/equipos")
def list_equipment():
    return jsonify(rows("""SELECT id,internal_code AS codigo_interno,type AS tipo,brand AS marca,model AS modelo,
        serial_number AS numero_serie,status AS estado,acquisition_date AS fecha_adquisicion,employee_id AS empleado_id
        FROM equipment ORDER BY id"""))


@app.post("/equipos")
def create_equipment():
    data = request.get_json(silent=True) or {}
    required = ("codigo_interno", "tipo", "estado")
    if any(not data.get(field) for field in required):
        return json_error("codigo_interno, tipo y estado son obligatorios", 400)
    try:
        item = rows("""INSERT INTO equipment(internal_code,type,brand,model,serial_number,status,acquisition_date)
            VALUES (%s,%s,%s,%s,%s,%s,%s) RETURNING id,internal_code AS codigo_interno,type AS tipo,brand AS marca,
            model AS modelo,serial_number AS numero_serie,status AS estado,acquisition_date AS fecha_adquisicion,employee_id AS empleado_id""",
            (data["codigo_interno"], data["tipo"], data.get("marca"), data.get("modelo"), data.get("numero_serie"), data["estado"], data.get("fecha_adquisicion")), one=True)
    except psycopg2.errors.UniqueViolation:
        return json_error("codigo interno o número de serie ya registrado", 409)
    return jsonify(item), 201


@app.get("/equipos/<int:equipment_id>")
def get_equipment(equipment_id):
    item = rows("""SELECT id,internal_code AS codigo_interno,type AS tipo,brand AS marca,model AS modelo,
        serial_number AS numero_serie,status AS estado,acquisition_date AS fecha_adquisicion,employee_id AS empleado_id
        FROM equipment WHERE id=%s""", (equipment_id,), one=True)
    if not item:
        return json_error("equipo no encontrado", 404)
    return jsonify(item)


@app.put("/equipos/<int:equipment_id>")
def update_equipment(equipment_id):
    data = request.get_json(silent=True) or {}
    columns = {"codigo_interno": "internal_code", "tipo": "type", "marca": "brand", "modelo": "model",
               "numero_serie": "serial_number", "estado": "status", "fecha_adquisicion": "acquisition_date"}
    updates = [(columns[key], value) for key, value in data.items() if key in columns]
    if not updates:
        return json_error("no hay campos válidos para actualizar", 400)
    assignments = ", ".join(f"{column}=%s" for column, _ in updates)
    params = [value for _, value in updates] + [equipment_id]
    item = rows(f"""UPDATE equipment SET {assignments} WHERE id=%s RETURNING id,internal_code AS codigo_interno,
        type AS tipo,brand AS marca,model AS modelo,serial_number AS numero_serie,status AS estado,
        acquisition_date AS fecha_adquisicion,employee_id AS empleado_id""", params, one=True)
    return (jsonify(item), 200) if item else json_error("equipo no encontrado", 404)


@app.post("/equipos/<int:equipment_id>/asignar")
def assign_equipment(equipment_id):
    data = request.get_json(silent=True) or {}
    employee_id = data.get("empleado_id")
    if not employee_id:
        return json_error("empleado_id es obligatorio", 400)
    with db_connect() as connection, connection.cursor() as cursor:
        cursor.execute("SELECT id FROM employees WHERE id=%s", (employee_id,))
        if not cursor.fetchone():
            return json_error("empleado no encontrado", 404)
        cursor.execute("SELECT status FROM equipment WHERE id=%s FOR UPDATE", (equipment_id,))
        item = cursor.fetchone()
        if not item:
            return json_error("equipo no encontrado", 404)
        if item["status"] != "DISPONIBLE":
            return json_error("el equipo no está disponible", 409)
        cursor.execute("UPDATE equipment SET employee_id=%s,status='ASIGNADO' WHERE id=%s", (employee_id, equipment_id))
        cursor.execute("INSERT INTO equipment_events(equipment_id,event,detail) SELECT %s,'Asignación',name FROM employees WHERE id=%s", (equipment_id, employee_id))
    return jsonify({"equipo_id": equipment_id, "empleado_id": employee_id, "estado": "ASIGNADO"}), 200


@app.post("/equipos/<int:equipment_id>/mantenimientos")
def create_maintenance(equipment_id):
    data = request.get_json(silent=True) or {}
    if not data.get("tipo"):
        return json_error("tipo es obligatorio", 400)
    if not rows("SELECT id FROM equipment WHERE id=%s", (equipment_id,), one=True):
        return json_error("equipo no encontrado", 404)
    maintenance = rows("""INSERT INTO maintenance(equipment_id,type,description,cost) VALUES (%s,%s,%s,%s)
        RETURNING id,equipment_id,maintenance_date AS fecha,type AS tipo,description AS descripcion,cost AS costo""",
        (equipment_id, data["tipo"], data.get("descripcion"), data.get("costo")), one=True)
    if maintenance["costo"] is not None:
        maintenance["costo"] = float(maintenance["costo"])
    rows("INSERT INTO equipment_events(equipment_id,event,detail) VALUES (%s,'Mantenimiento',%s)",
         (equipment_id, data["tipo"]), one=True)
    return jsonify(maintenance), 201


@app.get("/equipos/<int:equipment_id>/historial")
def equipment_history(equipment_id):
    item = rows("SELECT internal_code FROM equipment WHERE id=%s", (equipment_id,), one=True)
    if not item:
        return json_error("equipo no encontrado", 404)
    history = rows("SELECT occurred_at AS fecha,event AS evento,detail AS detalle FROM equipment_events WHERE equipment_id=%s ORDER BY occurred_at,id", (equipment_id,))
    for event in history:
        event["fecha"] = event["fecha"].isoformat()
    return jsonify({"equipo": item["internal_code"], "historial": history})


@app.post("/equipos/<int:equipment_id>/documentos")
def upload_document(equipment_id):
    item = rows("SELECT internal_code FROM equipment WHERE id=%s", (equipment_id,), one=True)
    if not item:
        return json_error("equipo no encontrado", 404)
    file = request.files.get("file")
    bucket = os.getenv("S3_BUCKET")
    if not file or not file.filename:
        return json_error("se requiere un archivo en el campo file", 400)
    if not bucket:
        return json_error("S3_BUCKET no está configurado", 503)
    key = f"equipos/{item['internal_code']}/{os.path.basename(file.filename)}"
    try:
        boto3.client("s3", region_name=os.getenv("AWS_REGION")).upload_fileobj(file, bucket, key)
    except Exception:
        app.logger.exception("falló la carga a S3")
        return json_error("no se pudo guardar el documento en S3", 502)
    document = rows("""INSERT INTO documents(equipment_id,file_name,s3_key) VALUES (%s,%s,%s)
        RETURNING id,equipment_id,file_name,s3_key,created_at""", (equipment_id, file.filename, key), one=True)
    document["created_at"] = document["created_at"].isoformat()
    return jsonify(document), 201


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
