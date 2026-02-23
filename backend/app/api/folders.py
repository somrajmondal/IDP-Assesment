import os
import shutil
import tempfile
import uuid
import zipfile

from flask import Blueprint, jsonify, request, send_file
from pydantic import ValidationError

from app.db.database import SessionLocal
from app.models.models import DocumentFile, Folder
from app.schemas.schemas import FolderCreate, FolderOut, FolderUpdate

bp = Blueprint("folders", __name__)

UPLOAD_DIR = "uploads"
MAX_FILES_PER_FOLDER = 5
ALLOWED_EXTENSIONS = {"pdf", "jpg", "jpeg", "png", "tiff", "tif"}


def get_file_extension(filename: str) -> str:
    return filename.rsplit(".", 1)[-1].lower() if "." in filename else ""


@bp.get("/")
def list_folders():
    db = SessionLocal()
    try:
        folders = db.query(Folder).order_by(Folder.created_at.desc()).all()
        payload = [FolderOut.model_validate(item, from_attributes=True).model_dump(mode="json") for item in folders]
        return jsonify(payload)
    finally:
        db.close()


@bp.post("/")
def create_folder():
    db = SessionLocal()
    try:
        try:
            folder_in = FolderCreate.model_validate(request.get_json(silent=True) or {})
        except ValidationError as exc:
            return jsonify({"detail": exc.errors()}), 422

        db_folder = Folder(**folder_in.model_dump())
        db.add(db_folder)
        db.commit()
        db.refresh(db_folder)
        payload = FolderOut.model_validate(db_folder, from_attributes=True).model_dump(mode="json")
        return jsonify(payload), 201
    finally:
        db.close()


@bp.get("/<int:folder_id>")
def get_folder(folder_id: int):
    db = SessionLocal()
    try:
        folder = db.query(Folder).filter(Folder.id == folder_id).first()
        if not folder:
            return jsonify({"detail": "Folder not found"}), 404
        payload = FolderOut.model_validate(folder, from_attributes=True).model_dump(mode="json")
        return jsonify(payload)
    finally:
        db.close()


@bp.put("/<int:folder_id>")
def update_folder(folder_id: int):
    db = SessionLocal()
    try:
        folder = db.query(Folder).filter(Folder.id == folder_id).first()
        if not folder:
            return jsonify({"detail": "Folder not found"}), 404

        try:
            update = FolderUpdate.model_validate(request.get_json(silent=True) or {})
        except ValidationError as exc:
            return jsonify({"detail": exc.errors()}), 422

        for k, v in update.model_dump(exclude_none=True).items():
            setattr(folder, k, v)
        db.commit()
        db.refresh(folder)
        payload = FolderOut.model_validate(folder, from_attributes=True).model_dump(mode="json")
        return jsonify(payload)
    finally:
        db.close()


@bp.delete("/<int:folder_id>")
def delete_folder(folder_id: int):
    db = SessionLocal()
    try:
        folder = db.query(Folder).filter(Folder.id == folder_id).first()
        if not folder:
            return jsonify({"detail": "Folder not found"}), 404
        folder_path = os.path.join(UPLOAD_DIR, str(folder_id))
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
        db.delete(folder)
        db.commit()
        return jsonify({"message": "Folder deleted"})
    finally:
        db.close()


@bp.post("/<int:folder_id>/upload")
def upload_files(folder_id: int):
    db = SessionLocal()
    try:
        folder = db.query(Folder).filter(Folder.id == folder_id).first()
        if not folder:
            return jsonify({"detail": "Folder not found"}), 404

        files = request.files.getlist("files")
        if not files:
            return jsonify({"detail": "No files uploaded"}), 400

        existing_count = db.query(DocumentFile).filter(DocumentFile.folder_id == folder_id).count()
        if existing_count + len(files) > MAX_FILES_PER_FOLDER:
            return (
                jsonify(
                    {
                        "detail": (
                            f"Folder can hold max {MAX_FILES_PER_FOLDER} files. "
                            f"Currently has {existing_count}."
                        )
                    }
                ),
                400,
            )

        folder_path = os.path.join(UPLOAD_DIR, str(folder_id))
        os.makedirs(folder_path, exist_ok=True)

        uploaded = []
        for file in files:
            ext = get_file_extension(file.filename or "")
            if ext not in ALLOWED_EXTENSIONS:
                return jsonify({"detail": f"File type .{ext} not allowed"}), 400

            unique_name = f"{uuid.uuid4().hex}_{file.filename}"
            file_path = os.path.join(folder_path, unique_name)

            content = file.read()
            with open(file_path, "wb") as out:
                out.write(content)

            db_file = DocumentFile(
                folder_id=folder_id,
                filename=unique_name,
                original_filename=file.filename,
                file_path=file_path,
                file_type=ext,
                file_size=len(content),
                status="pending",
            )
            db.add(db_file)
            db.commit()
            db.refresh(db_file)
            uploaded.append(db_file)

        return jsonify({"uploaded": len(uploaded), "files": [f.id for f in uploaded]})
    finally:
        db.close()


@bp.get("/<int:folder_id>/download-zip")
def download_folder_zip(folder_id: int):
    db = SessionLocal()
    try:
        folder = db.query(Folder).filter(Folder.id == folder_id).first()
        if not folder:
            return jsonify({"detail": "Folder not found"}), 404

        fd, zip_path = tempfile.mkstemp(prefix=f"folder_{folder_id}_", suffix=".zip")
        os.close(fd)
        with zipfile.ZipFile(zip_path, "w") as zf:
            for doc_file in folder.files:
                if doc_file.file_path and os.path.exists(doc_file.file_path):
                    zf.write(doc_file.file_path, doc_file.original_filename)

        return send_file(zip_path, mimetype="application/zip", as_attachment=True, download_name=f"{folder.name}.zip")
    finally:
        db.close()
