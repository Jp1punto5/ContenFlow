
from app import create_app
from app.database.connection import test_connection, diagnosticar_base_datos

app = create_app()

if __name__ == "__main__":
    if test_connection():
        diagnosticar_base_datos()
        app.run(host="127.0.0.1", port=5000, debug=True)
