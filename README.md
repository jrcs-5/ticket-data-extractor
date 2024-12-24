# Extractor de Datos de Boletas

Aplicación en Python para extraer datos específicos de boletas en formato PDF usando expresiones regulares y mostrarlos en una interfaz gráfica. Permite realizar búsquedas y exportar la información a Excel.

## Requisitos

- Python 3.x
- Librerías necesarias: `PyPDF2`, `tkinter`, `pandas`, entre otras.

## Configuración

1. Modifica `logic.py` para adaptarlo a los diferentes formatos de boletas.
2. Utiliza expresiones regulares para extraer los datos predeterminados.
   - Recomendación: Usa [regex101](https://regex101.com/) para probar las expresiones regulares.

## Funcionamiento

1. Al ejecutar el archivo, selecciona la carpeta con las boletas en PDF.
2. Realiza búsquedas generales o específicas (por nombre de archivo, fecha de emisión, importe, etc.).
3. Exporta la información extraída a un archivo Excel si es necesario.

## Instalación

1. Clona el repositorio:
   ```bash
   git clone <URL del repositorio>
