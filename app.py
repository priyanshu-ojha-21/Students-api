from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)
DB_NAME = "students.db"


def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def create_table():
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER,
            course TEXT
        )
    """)
    conn.commit()
    conn.close()


@app.route("/students", methods=["POST"])
def add_student():
    data = request.get_json() or {}


    name = data.get("name")
    age = data.get("age")
    course = data.get("course")

    if not name:
        return jsonify({"error": "Name is required"}), 400

    conn = get_db_connection()
    conn.execute(
        "INSERT INTO students (name, age, course) VALUES (?, ?, ?)",
        (name, age, course)
    )
    conn.commit()
    conn.close()

    return jsonify({"message": "Student added successfully"}), 201


@app.route("/students", methods=["GET"])
def get_students():
    conn = get_db_connection()
    students = conn.execute("SELECT * FROM students").fetchall()
    conn.close()

    result = []
    for s in students:
        result.append({
            "id": s["id"],
            "name": s["name"],
            "age": s["age"],
            "course": s["course"]
        })

    return jsonify(result), 200


@app.route("/students/<int:id>", methods=["GET"])
def get_student(id):
    conn = get_db_connection()
    student = conn.execute(
        "SELECT * FROM students WHERE id = ?", (id,)
    ).fetchone()
    conn.close()

    if student is None:
        return jsonify({"error": "Student not found"}), 404

    return jsonify({
        "id": student["id"],
        "name": student["name"],
        "age": student["age"],
        "course": student["course"]
    }), 200


@app.route("/students/<int:id>", methods=["DELETE"])
def delete_student(id):
    conn = get_db_connection()
    cur = conn.execute(
        "DELETE FROM students WHERE id = ?", (id,)
    )
    conn.commit()
    conn.close()

    if cur.rowcount == 0:
        return jsonify({"error": "Student not found"}), 404

    return jsonify({"message": "Student deleted"}), 200


if __name__ == "__main__":
    create_table()
    app.run(debug=True)

