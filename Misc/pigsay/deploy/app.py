#!/usr/bin/env python

from importlib import reload
from os import environ
from pathlib import Path
from subprocess import check_output
from tempfile import NamedTemporaryFile, TemporaryDirectory
from uuid import uuid4

import jwt
import pigsay
import uvicorn
from litestar import Litestar, get, post
from litestar.datastructures import UploadFile
from litestar.params import Body
from litestar.static_files import create_static_files_router

JWT_KEY = environ.pop("JWT_KEY").encode()
PIG_KEY = environ.pop("PIG_KEY").encode()
converter = pigsay.PigConverter(PIG_KEY)


@get("/api/ping")
async def ping() -> dict[str, str]:
    """
    Ping? Pong!
    """
    return {"code": 20000, "msg": "pong"}


@post("/api/encrypt")
async def encrypt(data: dict) -> dict[str, str]:
    """
    Encrypt some text to pigsay text.
    """
    try:
        ret = converter.encrypt_string(str(data["text"]))
        return {"code": 20000, "msg": "encrypt success", "data": ret}
    except Exception as e:
        return {"code": 50000, "msg": f"encrypt error: {e}"}


@post("/api/decrypt")
async def decrypt(data: dict) -> dict[str, str]:
    """
    Decrypt some pigsay text.
    """
    try:
        ret = converter.decrypt_string(str(data["text"]))
        return {"code": 20000, "msg": "decrypt success", "data": ret}
    except Exception as e:
        return {"code": 50000, "msg": f"decrypt error: {e}"}


def check_file_type(filename: str):
    allows = [".zip", ".rar", ".7z", ".tar.gz"]
    return any([filename.endswith(allow) for allow in allows])


def uncompress_file(filepath: str, handler: callable):
    file = Path(filepath)
    suffix = "".join(file.suffixes)
    with TemporaryDirectory(uuid4().hex) as tmp_dir:
        tmp_dir = Path(tmp_dir)
        try:
            args = (filepath, str(tmp_dir.absolute()))
            match suffix:
                case ".zip":
                    unzip_file(*args)
                case ".rar":
                    unrar_file(*args)
                case ".7z":
                    un7z_file(*args)
                case ".tar.gz":
                    untar_file(*args)
                case _:
                    raise Exception(f"Unsupported file type: {suffix}")
            return {
                "code": 20000,
                "msg": "success",
                "data": {
                    item.name: handler(item.read_text())
                    for item in tmp_dir.glob("*.txt")
                },
            }
        except Exception as e:
            return {"code": 50000, "msg": f"Uncompress file error: {e}"}


def unzip_file(filepath: str, extract_to_filepath: str):
    import zipfile

    with zipfile.ZipFile(filepath) as zf:
        zf.extractall(extract_to_filepath)


def unrar_file(filepath: str, extract_to_filepath: str):
    import rarfile

    with rarfile.RarFile(filepath) as rf:
        rf.extractall(extract_to_filepath)


def un7z_file(filepath: str, extract_to_filepath: str):
    import py7zr

    with py7zr.SevenZipFile(filepath) as sf:
        sf.extractall(extract_to_filepath)


def untar_file(filepath: str, extract_to_filepath: str):
    import tarfile

    with tarfile.open(filepath, "r:gz") as tf:
        tf.extractall(extract_to_filepath)


@post("/api/file/encrypt", request_max_body_size=1024 * 1024)
async def encrypt_file(
    data: UploadFile = Body(media_type="multipart/form-data"),
) -> dict[str, str]:
    """
    We can encrypt some txt file in a compressed file
    """
    filename = data.filename
    if not check_file_type(filename):
        return {"code": 40000, "msg": "Invalid file type"}
    content = await data.read()
    try:
        with NamedTemporaryFile(mode="wb", suffix=filename) as tmp:
            tmp.write(content)
            tmp.seek(0)
            return uncompress_file(tmp.name, converter.encrypt_string)
    except Exception as e:
        return {"code": 50000, "msg": f"Encrypt file error: {e}"}


@post("/api/file/decrypt", request_max_body_size=1024 * 1024)
async def decrypt_file(
    data: UploadFile = Body(media_type="multipart/form-data"),
) -> dict[str, str]:
    """
    We can decrypt some txt file in a compressed file
    """
    filename = data.filename
    if not check_file_type(filename):
        return {"code": 40000, "msg": "Invalid file type"}
    content = await data.read()
    try:
        with NamedTemporaryFile(mode="wb", suffix=filename) as tmp:
            tmp.write(content)
            tmp.seek(0)
            return uncompress_file(tmp.name, converter.decrypt_string)
    except Exception as e:
        return {"code": 50000, "msg": f"Encrypt file error: {e}"}


@post(f"/api/admin/upgrade/{uuid4().hex}")
async def upgrade(headers: dict) -> dict[str, str]:
    """
    Only admin can do!
    """
    token = headers.get("r3-token")
    if not token:
        return {"code": 40300, "msg": "Authentication Failed"}
    try:
        if jwt.decode(token, JWT_KEY, algorithms=["HS256"]).get("role") != "admin":
            return {"code": 40300, "msg": "Permission Denied"}
    except Exception:
        return {"code": 40300, "msg": "Authentication Error"}

    try:
        ret = (
            check_output(
                ["/app/upgrade.sh"],
                env=None,
                universal_newlines=True,
                timeout=60,
                user="r3ctf",
            )
            .strip()
            .replace("\n", ", ")
        )

        reload(pigsay)

        global converter
        converter = pigsay.PigConverter(PIG_KEY)

        return {"code": 20000, "msg": "Upgrade successfully", "data": ret}
    except Exception as e:
        return {"code": 50000, "msg": "Upgrade failed", "data": str(e)}


app = Litestar(
    route_handlers=[
        ping,
        encrypt,
        decrypt,
        encrypt_file,
        decrypt_file,
        upgrade,
        create_static_files_router(path="/static", directories=["static"]),
        create_static_files_router(path="/", directories=["public"], html_mode=True),
    ],
)

uvicorn.run(app, host="0.0.0.0", port=8000)
