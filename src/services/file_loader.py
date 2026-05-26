# src/services/file_loader.py
"""
Servicio para cargar diferentes tipos de archivos.
Soporta: TXT, PDF, JSON, XML
"""
import json
import xml.etree.ElementTree as ET
from typing import Optional


def cargar_archivo(ruta: str) -> str:
    """
    Carga un archivo y retorna su contenido como texto.
    Soporta: .txt, .pdf, .json, .xml
    """
    ruta = ruta.strip()
    extension = ruta.lower().split('.')[-1]
    
    if extension == 'txt':
        return _cargar_txt(ruta)
    elif extension == 'pdf':
        return _cargar_pdf(ruta)
    elif extension == 'json':
        return _cargar_json(ruta)
    elif extension == 'xml':
        return _cargar_xml(ruta)
    else:
        raise ValueError(f"Formato de archivo no soportado: .{extension}")


def _cargar_txt(ruta: str) -> str:
    """Carga archivo de texto plano."""
    with open(ruta, 'r', encoding='utf-8', errors='ignore') as f:
        return f.read()


def _cargar_pdf(ruta: str) -> str:
    """Carga archivo PDF usando pdfplumber."""
    try:
        import pdfplumber
    except ImportError:
        return "ERROR: pdfplumber no esta instalado. Ejecuta: pip install pdfplumber"
    
    texto = []
    with pdfplumber.open(ruta) as pdf:
        for pagina in pdf.pages:
            contenido = pagina.extract_text()
            if contenido:
                texto.append(contenido)
    
    return '\n\n'.join(texto)


def _cargar_json(ruta: str) -> str:
    """Carga archivo JSON y lo convierte a texto legible."""
    with open(ruta, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Convertir a texto formateado
    return json.dumps(data, indent=2, ensure_ascii=False)


def _cargar_xml(ruta: str) -> str:
    """Carga archivo XML y lo convierte a texto legible."""
    tree = ET.parse(ruta)
    root = tree.getroot()
    
    # Convertir XML a texto recursivamente
    return _xml_to_text(root)


def _xml_to_text(element, nivel=0) -> str:
    """Convierte un elemento XML a texto legible recursivamente."""
    indent = "  " * nivel
    texto = [f"{indent}<{element.tag}>"]
    
    # Agregar atributos
    if element.attrib:
        for key, value in element.attrib.items():
            texto.append(f"{indent}  @{key}: {value}")
    
    # Agregar texto del elemento
    if element.text and element.text.strip():
        texto.append(f"{indent}  {element.text.strip()}")
    
    # Procesar hijos recursivamente
    for child in element:
        texto.append(_xml_to_text(child, nivel + 1))
    
    texto.append(f"{indent}</{element.tag}>")
    return '\n'.join(texto)
