
from flask import Blueprint, jsonify, request
from app.database.connection import db
from uuid import uuid4
from datetime import datetime

import logging

logger = logging.getLogger(__name__)

publicaciones_bp = Blueprint(
    "publicaciones",
    __name__,
    url_prefix="/api/publicaciones"
)


@publicaciones_bp.route("/", methods=["GET"])
def listar_publicaciones():
    try:
        publicaciones = list(
            db.publicaciones.find(
                {},
                {
                    "_id": 1,
                    "usuario_id": 1,
                    "contenido": 1,
                    "categoria": 1,
                    "tipo": 1,
                    "fecha_publicacion": 1
                }
            ).limit(100)
        )

        return jsonify({
            "total": len(publicaciones),
            "publicaciones": publicaciones
        }), 200

    except Exception as error:
        return jsonify({"error": str(error)}), 500


@publicaciones_bp.route("/<string:publicacion_id>", methods=["GET"])
def obtener_publicacion(publicacion_id):
    try:
        publicacion = db.publicaciones.find_one(
            {"_id": publicacion_id}
        )

        if not publicacion:
            return jsonify({"error": "Publicación no encontrada"}), 404

        return jsonify(publicacion), 200

    except Exception as error:
        return jsonify({"error": str(error)}), 500



@publicaciones_bp.route("/", methods=["POST"])
def crear_publicacion():
    try:
        datos = request.get_json(silent=True)

        if not isinstance(datos, dict):
            logger.warning("Intento de crear publicación con JSON inválido")
            return jsonify({
                "error": "Debes enviar un JSON válido"
            }), 400

        campos = [
            "usuario_id", "contenido",
            "fecha_publicacion", "categoria", "tipo"
        ]

        faltantes = [
            campo for campo in campos
            if not datos.get(campo)
        ]

        if faltantes:
            logger.warning(
                "Creación de publicación rechazada. Campos faltantes: %s",
                faltantes
            )
            return jsonify({
                "error": "Faltan campos obligatorios",
                "campos": faltantes
            }), 400

        try:
            fecha_publicacion = datetime.fromisoformat(
                datos["fecha_publicacion"].replace("Z", "+00:00")
            )
        except (ValueError, AttributeError):
            logger.warning("Fecha de publicación con formato inválido")
            return jsonify({
                "error": "fecha_publicacion debe tener formato ISO 8601"
            }), 400

        usuario = db.usuarios.find_one({
            "_id": datos["usuario_id"]
        })

        if not usuario:
            logger.warning(
                "Publicación rechazada. Usuario inexistente: %s",
                datos["usuario_id"]
            )
            return jsonify({
                "error": "El usuario asociado no existe"
            }), 404

        hashtags = datos.get("hashtags", [])

        if not isinstance(hashtags, list):
            logger.warning("Hashtags debe ser una lista")
            return jsonify({
                "error": "hashtags debe ser una lista"
            }), 400

        nueva_publicacion = {
            "_id": f"pub_{uuid4().hex[:12]}",
            "usuario_id": datos["usuario_id"],
            "contenido": datos["contenido"],
            "fecha_publicacion": fecha_publicacion,
            "categoria": datos["categoria"],
            "hashtags": hashtags,
            "tipo": datos["tipo"]
        }

        db.publicaciones.insert_one(nueva_publicacion)

        logger.info(
            "Publicación creada: %s",
            nueva_publicacion["_id"]
        )

        return jsonify({
            "mensaje": "Publicación creada correctamente",
            "publicacion": nueva_publicacion
        }), 201

    except Exception:
        logger.exception("Error al crear publicación")
        return jsonify({
            "error": "Error interno del servidor"
        }), 500




@publicaciones_bp.route("/<string:publicacion_id>", methods=["PUT"])
def actualizar_publicacion(publicacion_id):
    try:
        datos = request.get_json(silent=True)

        if not isinstance(datos, dict) or not datos:
            return jsonify({"error": "Debes enviar un JSON válido"}), 400

        campos_permitidos = [
            "usuario_id", "contenido", "fecha_publicacion",
            "categoria", "hashtags", "tipo"
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

        publicacion = db.publicaciones.find_one(
            {"_id": publicacion_id}
        )

        if not publicacion:
            return jsonify({"error": "Publicación no encontrada"}), 404

        if "usuario_id" in datos:
            usuario = db.usuarios.find_one({
                "_id": datos["usuario_id"]
            })

            if not usuario:
                return jsonify({
                    "error": "El usuario asociado no existe"
                }), 404

        if "fecha_publicacion" in datos:
            try:
                datos["fecha_publicacion"] = datetime.fromisoformat(
                    datos["fecha_publicacion"].replace("Z", "+00:00")
                )
            except (ValueError, AttributeError, TypeError):
                return jsonify({
                    "error": "fecha_publicacion debe tener formato ISO 8601"
                }), 400

        if "hashtags" in datos and not isinstance(datos["hashtags"], list):
            return jsonify({
                "error": "hashtags debe ser una lista"
            }), 400

        resultado = db.publicaciones.update_one(
            {"_id": publicacion_id},
            {"$set": datos}
        )

        logger.info("Publicación actualizada: %s", publicacion_id)

        publicacion_actualizada = db.publicaciones.find_one(
            {"_id": publicacion_id}
        )

        return jsonify({
            "mensaje": "Publicación actualizada correctamente",
            "publicacion": publicacion_actualizada,
            "modificados": resultado.modified_count
        }), 200

    except Exception:
        logger.exception("Error al actualizar publicación: %s", publicacion_id)
        return jsonify({"error": "Error interno del servidor"}), 500


@publicaciones_bp.route("/<string:publicacion_id>", methods=["DELETE"])
def eliminar_publicacion(publicacion_id):
    try:
        publicacion = db.publicaciones.find_one(
            {"_id": publicacion_id}
        )

        if not publicacion:
            return jsonify({"error": "Publicación no encontrada"}), 404

        referencias = {
            "reacciones": db.reacciones.count_documents(
                {"publicacion_id": publicacion_id}
            ),
            "comentarios": db.comentarios.count_documents(
                {"publicacion_id": publicacion_id}
            ),
            "campanas": db.campanas.count_documents(
                {"publicaciones_asociadas": publicacion_id}
            )
        }

        if any(referencias.values()):
            return jsonify({
                "error": "No se puede eliminar la publicación porque tiene registros asociados",
                "referencias": referencias
            }), 409

        db.publicaciones.delete_one({"_id": publicacion_id})

        return jsonify({
            "mensaje": "Publicación eliminada correctamente",
            "publicacion_id": publicacion_id
        }), 200

    except Exception as error:
        return jsonify({"error": str(error)}), 500
