import re
import PyPDF2
import os

def leer_pdf(ruta_pdf):
    """
    La funcion recibe la ruta del pdf y devuelve el texto almacenado en dicho pdf
    """
    with open(ruta_pdf, 'rb') as archivo_pdf:
        lector_pdf = PyPDF2.PdfReader(archivo_pdf)        
        # Por el momento considerar 1 sola pagina
        pagina = lector_pdf.pages[0]
        texto = pagina.extract_text()
    return texto

def listar_pdfs(ruta_archivos):
    """
    La funcion recibe la ruta de los archivos y devuelve una lista de todos los archivos que son pdf
    """
    archivos_pdf = []
    for archivo in os.listdir(ruta_archivos):
        if archivo.lower().endswith('.pdf'):
            archivos_pdf.append(archivo)
    return archivos_pdf

def obtener_datos_general(texto):
    """
    La funcion recibe el texto y devuelve los datos requeridos
    """
    persona = obtener_persona(texto)
    importe = obtener_importe(texto)
    fecha = obtener_fecha_emision(texto)
    num_bol = obtener_numero_boleta(texto)
    return {
        'NumBol': num_bol,
        'ImporteTotal': importe,
        'FechaDeEmision': fecha,
        'Persona': persona
    }

def obtener_importe(texto):
    """
    Se le da el texto y busca el texto luego de la palabra "ImporteTotal:"
    """
    importe_pattern = r"Importe\s*Total\s*:\s*(S\/\s*\d+(\.\d{2})?)"
    match = re.search(importe_pattern, texto)
    if match:
        return match.group(1)
    return None

def obtener_fecha_emision(texto):
    """
    Se le da el texto y busca el texto luego de la palabra "FechadeEmisión:"
    """
    fecha_pattern = r"Fecha\s*de\s*Emisión\s*:\s*(\d{2}/\d{2}/\d{4})"
    match = re.search(fecha_pattern, texto)
    if match:
        return match.group(1)
    return None

def obtener_persona(texto):
    """
    Se le da el texto y busca el texto luego de la palabra "Señor(es):"
    """
    persona_pattern = r"Señor\(es\)\s*:\s*([A-ZÑÁÉÍÓÚ\s.,-]+)(?=\n)"
    
    match = re.search(persona_pattern, texto)
    if match:
        nombres = match.group(1).strip()
        nombres = nombres.replace("\n", " ")
        return nombres
    return None

def obtener_numero_boleta(texto):
    """
    Se le da el texto y busca el texto luego del RUC
    """
    ruc_pattern = r"RUC:\s*\d{11}\s*\n([^\n]+)"
    match = re.search(ruc_pattern, texto)
    if match:
        return match.group(1).strip()
    return None


def obtener_dni(texto):
    dni_pattern = r"DNI\s*:\s*(\d{8})"
    dni_match = re.search(dni_pattern, texto)
    dni = dni_match.group(1) if dni_match else None
    return dni

def obtener_datos_especifico(texto):
    """
    Los datos generales:
    "Num. Bolela", "FechaDeEmision", "DNI", "Persona", 
    Los datos particulares:
    "Cantidad", "UM", "Codigo", "Descripción", "Precio"
    """
    num_bol = obtener_numero_boleta(texto)
    texto = texto.replace("\n", "")

    especificaciones_pattern = r"Cantidad\s*(.*?)Otros\s+Cargos\s*:"
    especificaciones_match = re.search(especificaciones_pattern, texto, re.DOTALL)
    
    productos = []
    
    #Para valores:(\d+\.\d{2})([A-Z]+)\s+([A-Z0-9]+)(POLO|CASACA|COSTO|POLERA)([\s\S]+)(\/\s*S\s*\d+(\.\d+))\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)
    #Para envio: (\d+\.\d{2})([A-Z]+)\s+(COSTO\sDE\sENVIO)(\/?\s*S?\s*\d+(\.\d+))\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)
    
    producto_pattern = r"(\d+\.\d{2})\s*([A-Z]+)\s+([\sA-Z0-9]+)(POLO|CASACA|COSTO|POLERA)\s*([^\d]*?)\s*(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(0\.00)?"
    envio_pattern = r"(\d+\.\d{2})\s*([A-Z]+)\s+((COSTO|SERVICIO|GASTOS)\sDE\s(ENVIO|ENVÍO|ENVIO.))\s*(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(0\.00)?"
    x=0
    if especificaciones_match:
        
        matches = re.finditer(producto_pattern, texto)
        
        for match in matches:
            cantidad = match.group(1)
            unidad_medida = match.group(2)
            codigo = match.group(3) if match.group(3) else ""
            descripcion = match.group(4) +" "+ match.group(5)
            valor_unitario = match.group(6)
            descuento = match.group(7)
            importe_venta = match.group(8)
            icbper = match.group(9)
            x=x+1
            productos.append({
                    'NumBol': num_bol,
                    'Cantidad': cantidad,
                    'UM': unidad_medida,
                    'Codigo': codigo,
                    'Descripcion': descripcion,
                    'Precio': importe_venta
                })
            
        
        matches = re.finditer(envio_pattern, texto)
        for match in matches:
            if(x>0):
                cantidad = match.group(1)
                unidad_medida = match.group(2)
                codigo = ""
                descripcion = match.group(3)
                valor_unitario = match.group(6)
                descuento = match.group(7)
                importe_venta = match.group(8)
                icbper = match.group(9)
            
                productos.append({
                        'NumBol': num_bol,
                        'Cantidad': cantidad,
                        'UM': unidad_medida,
                        'Codigo': codigo,
                        'Descripcion': descripcion,
                        'Precio': importe_venta
                    })
                
    else:
        if x==0:
            productos.append({
                        'NumBol': num_bol,
                        'Cantidad': 0,
                        'UM': "",
                        'Codigo': "",
                        'Descripcion': "",
                        'Precio': 0
                    })
        
    return productos