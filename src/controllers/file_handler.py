# src/controllers/file_handler.py
# -*- coding: utf-8 -*-
import os
import json
import logging
from typing import Optional

import pdfplumber

try:
    import chardet
except Exception:
    chardet = None

LOG = logging.getLogger(__name__)


def _decode_bytes(raw: bytes) -> str:
    """Intenta detectar BOM / encoding y decodificar a str."""
    if not raw:
        return ""

    # BOM checks
    if raw.startswith(b'\xff\xfe'):
        try:
            return raw.decode('utf-16')
        except Exception:
            pass
    if raw.startswith(b'\xfe\xff'):
        try:
            return raw.decode('utf-16-be')
        except Exception:
            pass
    if raw.startswith(b'\xef\xbb\xbf'):
        try:
            return raw.decode('utf-8-sig')
        except Exception:
            pass

    # Si chardet está disponible, lo usamos para detectar la codificación
    if chardet:
        try:
            info = chardet.detect(raw)
            encoding = info.get("encoding")
            confidence = info.get("confidence", 0)
            if encoding:
                try:
                    return raw.decode(encoding)
                except Exception:
                    LOG.debug("chardet sugirió %s (conf=%s) pero decode falló", encoding, confidence)
        except Exception as e:
            LOG.debug("chardet error: %s", e)

    # Intentos finales
    try:
        return raw.decode('utf-8')
    except Exception:
        try:
            return raw.decode('utf-8', errors='replace')
        except Exception:
            return raw.decode('latin-1', errors='replace')


class FileHandler:
    """
    Clase compatibilidad: proporciona extract_text(file_path) que usan los demás módulos.
    Extrae texto de PDFs, JSONs y archivos de texto intentando detectar la codificación.
    """

    @staticmethod
    def extract_text(file_path: str) -> str:
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()

        try:
            if ext == ".pdf":
                text_parts = []
                with pdfplumber.open(file_path) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text_parts.append(page_text)
                return "\n\n".join(text_parts).strip()

            if ext == ".json":
                with open(file_path, "rb") as f:
                    raw = f.read()
                text = _decode_bytes(raw)
                try:
                    obj = json.loads(text)
                    return json.dumps(obj, ensure_ascii=False, indent=2)
                except Exception:
                    return text

            if ext in {".txt", ".md", ".csv", ".log", ".xml", ".html"}:
                with open(file_path, "rb") as f:
                    raw = f.read()
                return _decode_bytes(raw).strip()

            # Si extensión desconocida, intentamos detectar si es PDF por signature
            with open(file_path, "rb") as f:
                head = f.read(16384)
            if head.startswith(b'%PDF'):
                text_parts = []
                with pdfplumber.open(file_path) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text_parts.append(page_text)
                return "\n\n".join(text_parts).strip()

            # Intento genérico de lectura (primeros bytes decodificados)
            return _decode_bytes(head).strip()

        except Exception as e:
            LOG.exception("Error al leer archivo: %s", e)
            # Lanzamos RuntimeError con mensaje legible para que el controlador lo capture y devuelva al usuario
            raise RuntimeError(f"Error al leer archivo: {e}")