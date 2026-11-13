
from flask import Blueprint, jsonify, request
from app.database.connection import db
from uuid import uuid4
from datetime import datetime

import logging

logger = logging.getLogger(__name__)

usuarios_bp = Blueprint("usuarios", __name__, url_prefix="/api/usuarios")


@usuarios_bp.route("/", methods=["GET"])
def listar_usuarios():
    try:
        usuarios = list(
            db.usuarios.find(
                {},
                {"_id": 1, "nombre": 1, "correo": 1, "pais": 1}
            ).limit(100)
        )
        
        return jsonify({
            "total": len(usuarios),
            "usuarios": usuarios
        }), 200

    except Exception as error:
        return jsonify({"error": str(error)}), 500


@usuarios_bp.route("/<string:usuario_id>", methods=["GET"])
def obtener_usuario(usuario_id):
    try:
        usuario = db.usuarios.find_one({"_id": usuario_id})

        if not usuario:
            return jsonify({"error": "Usuario no encontrado"}), 404

        return jsonify(usuario), 200

    except Exception as error:
        return jsonify({"error": str(error)}), 500



@usuarios_bp.route("/", methods=["POST"])
def crear_usuario():
    try:
        datos = request.get_json(silent=True)

        if not isinstance(datos, dict):
            return jsonify({"error": "Debes enviar un JSON válido"}), 400

        campos = [
            "nombre", "correo", "pais",
            "genero", "fecha_registro", "dispositivo"
        ]

        faltantes = [
            campo for campo in campos
            if not datos.get(campo)
        ]

        if faltantes:
            return jsonify({
                "error": "Faltan campos obligatorios",
                "campos": faltantes
            }), 400

        # Validar y convertir fecha ISO 8601 a datetime
        try:
            fecha_registro = datetime.fromisoformat(
                datos["fecha_registro"].replace("Z", "+00:00")
            )
        except (ValueError, AttributeError, TypeError):
            return jsonify({
                "error": "fecha_registro debe tener formato ISO 8601"
            }), 400

        if db.usuarios.find_one({"correo": datos["correo"]}):
            return jsonify({
                "error": "Ya existe un usuario con ese correo"
            }), 409

        nuevo_usuario = {
            "_id": f"user_{uuid4().hex[:12]}",
            **{campo: datos[campo] for campo in campos}
        }

        # Sobrescribir el texto con un objeto datetime
        nuevo_usuario["fecha_registro"] = fecha_registro

        db.usuarios.insert_one(nuevo_usuario)

        logger.info("Usuario creado: %s", nuevo_usuario["_id"])

        return jsonify({
            "mensaje": "Usuario creado correctamente",
            "usuario": nuevo_usuario
        }), 201

    except Exception:
        logger.exception("Error al crear usuario")
        return jsonify({
            "error": "Error interno del servidor"
        }), 500





@usuarios_bp.route("/<string:usuario_id>", methods=["PUT"])
def actualizar_usuario(usuario_id):
    try:
        datos = request.get_json(silent=True)

        if not isinstance(datos, dict) or not datos:
            return jsonify({"error": "Debes enviar un JSON válido"}), 400

        campos_permitidos = [
            "nombre", "correo", "pais",
            "genero", "fecha_registro", "dispositivo"
        ]

        if "_id" in datos:
            return jsonify({"error": "No se permite modificar el ID"}), 400

        campos_invalidos = [
            campo for campo in datos
            if campo not in campos_permitidos
        ]

        if campos_invalidos:
            return jsonify({
                "error": "Campos no permitidos",
                "campos": campos_invalidos
            }), 400

        usuario = db.usuarios.find_one({"_id": usuario_id})

        if not usuario:
            return jsonify({"error": "Usuario no encontrado"}), 404

        if "correo" in datos:
            existente = db.usuarios.find_one({
                "correo": datos["correo"],
                "_id": {"$ne": usuario_id}
            })

            if existente:
                return jsonify({
                    "error": "El correo ya está registrado"
                }), 409

        if "fecha_registro" in datos:
            try:
                datos["fecha_registro"] = datetime.fromisoformat(
                    datos["fecha_registro"].replace("Z", "+00:00")
                )
            except (ValueError, AttributeError, TypeError):
                return jsonify({
                    "error": "fecha_registro debe tener formato ISO 8601"
                }), 400

        resultado = db.usuarios.update_one(
            {"_id": usuario_id},
            {"$set": datos}
        )

        logger.info("Usuario actualizado: %s", usuario_id)

        usuario_actualizado = db.usuarios.find_one(
            {"_id": usuario_id}
        )

        return jsonify({
            "mensaje": "Usuario actualizado correctamente",
            "usuario": usuario_actualizado,
            "modificados": resultado.modified_count
        }), 200

    except Exception:
        logger.exception("Error al actualizar usuario: %s", usuario_id)
        return jsonify({"error": "Error interno del servidor"}), 500


@usuarios_bp.route("/<string:usuario_id>", methods=["DELETE"])
def eliminar_usuario(usuario_id):
    try:
        usuario = db.usuarios.find_one({"_id": usuario_id})

        if not usuario:
            return jsonify({"error": "Usuario no encontrado"}), 404

        referencias = {
            "publicaciones": db.publicaciones.count_documents(
                {"usuario_id": usuario_id}
            ),
            "reacciones": db.reacciones.count_documents(
                {"usuario_id": usuario_id}
            ),
            "comentarios": db.comentarios.count_documents(
                {"usuario_id": usuario_id}
            )
        }

        if any(referencias.values()):
            return jsonify({
                "error": "No se puede eliminar el usuario porque tiene registros asociados",
                "referencias": referencias
            }), 409

        db.usuarios.delete_one({"_id": usuario_id})

        return jsonify({
            "mensaje": "Usuario eliminado correctamente",
            "usuario_id": usuario_id
        }), 200

    except Exception as error:
        return jsonify({"error": str(error)}), 500
