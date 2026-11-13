
import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB", "contentflow")

client = MongoClient(
    MONGO_URI,
    serverSelectionTimeoutMS=10000
)

db = client[MONGO_DB]

def test_connection():
    try:
        client.admin.command("ping")
        print("MongoDB Atlas conectado correctamente")
        return True
    except Exception as error:
        print(f"Error de conexión: {error}")
        return False



def diagnosticar_base_datos():
    print("\n--- DIAGNOSTICO MONGODB ---")
    print("Base configurada:", db.name)
    print("Bases disponibles:", client.list_database_names())
    print("Colecciones:", db.list_collection_names())

    for coleccion in db.list_collection_names():
        print(
            f"{coleccion}: "
            f"{db[coleccion].count_documents({})} documentos"
        )
