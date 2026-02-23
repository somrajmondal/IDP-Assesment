import os

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS

from app.api import admin, documents, folders, process, templates
from app.db.database import Base, engine

Base.metadata.create_all(bind=engine)


def create_app() -> Flask:
    app = Flask(__name__)

    CORS(
        app,
        origins=["http://localhost:3000", "http://localhost:5173"],
        supports_credentials=True,
    )

    os.makedirs("uploads", exist_ok=True)
    os.makedirs("processed", exist_ok=True)

    app.register_blueprint(folders.bp, url_prefix="/api/folders")
    app.register_blueprint(documents.bp, url_prefix="/api/documents")
    app.register_blueprint(templates.bp, url_prefix="/api/templates")
    app.register_blueprint(admin.bp, url_prefix="/api/admin")
    app.register_blueprint(process.bp, url_prefix="/api/process")

    @app.get("/")
    def root():
        return jsonify({"message": "Document Digitization Platform API", "version": "1.0.0"})

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"})

    @app.get("/uploads/<path:filename>")
    def uploaded_file(filename: str):
        return send_from_directory("uploads", filename)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
