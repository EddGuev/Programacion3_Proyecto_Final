"""
Procesador de archivos TXT, PDF, JSON, XML
"""
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Tuple


class FileProcessor:
    """Procesador de múltiples formatos de archivo"""

    @staticmethod
    def load_file(file_path: str) -> Tuple[bool, str, str]:
        """
        Cargar archivo y extraer contenido

        Returns:
            (success, message, content)
        """
        try:
            path = Path(file_path)

            if not path.exists():
                return False, "El archivo no existe", ""

            extension = path.suffix.lower()

            if extension == '.txt':
                return FileProcessor._load_txt(path)
            elif extension == '.pdf':
                return FileProcessor._load_pdf(path)
            elif extension == '.json':
                return FileProcessor._load_json(path)
            elif extension == '.xml':
                return FileProcessor._load_xml(path)
            else:
                return False, f"Formato no soportado: {extension}", ""

        except Exception as e:
            return False, f"Error al cargar archivo: {str(e)}", ""

    @staticmethod
    def _load_txt(path: Path) -> Tuple[bool, str, str]:
        """Cargar archivo TXT"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            return True, f"✅ Archivo TXT cargado: {path.name}", content
        except UnicodeDecodeError:
            with open(path, 'r', encoding='latin-1') as f:
                content = f.read()
            return True, f"✅ Archivo TXT cargado: {path.name}", content

    @staticmethod
    def _load_pdf(path: Path) -> Tuple[bool, str, str]:
        """Cargar archivo PDF con pdfplumber"""
        try:
            import pdfplumber

            text_content = []
            with pdfplumber.open(path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        text_content.append(text)

            content = "\n\n".join(text_content)

            if not content.strip():
                return False, "El PDF no contiene texto extraíble", ""

            return True, f"✅ PDF cargado: {path.name} ({len(pdf.pages)} páginas)", content

        except ImportError:
            return False, "pdfplumber no está instalado. Instala con: pip install pdfplumber", ""
        except Exception as e:
            return False, f"Error al leer PDF: {str(e)}", ""

    @staticmethod
    def _load_json(path: Path) -> Tuple[bool, str, str]:
        """Cargar archivo JSON"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Convertir JSON a texto legible
            content = json.dumps(data, indent=2, ensure_ascii=False)
            return True, f"✅ JSON cargado: {path.name}", content

        except json.JSONDecodeError as e:
            return False, f"JSON inválido: {str(e)}", ""
        except Exception as e:
            return False, f"Error al leer JSON: {str(e)}", ""

    @staticmethod
    def _load_xml(path: Path) -> Tuple[bool, str, str]:
        """Cargar archivo XML"""
        try:
            tree = ET.parse(path)
            root = tree.getroot()

            # Convertir XML a texto legible
            content = FileProcessor._xml_to_text(root)
            return True, f"✅ XML cargado: {path.name}", content

        except ET.ParseError as e:
            return False, f"XML inválido: {str(e)}", ""
        except Exception as e:
            return False, f"Error al leer XML: {str(e)}", ""

    @staticmethod
    def _xml_to_text(element, level=0) -> str:
        """Convertir elemento XML a texto"""
        indent = "  " * level
        text = f"{indent}<{element.tag}>"

        if element.text and element.text.strip():
            text += f" {element.text.strip()}"

        text += "\n"

        for child in element:
            text += FileProcessor._xml_to_text(child, level + 1)

        if element.tail and element.tail.strip():
            text += f"{indent}{element.tail.strip()}\n"

        return text
