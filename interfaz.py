import pandas as pd
import tkinter as tk
from tkinter import filedialog, Menu, ttk
from logic import *
import openpyxl

def visualizar_datos_de_boletas(datos_pdf, cabeceras, titulo):
    def ordenar_por_columna(col):
        nonlocal df
        df = df.sort_values(by=col, ascending=not tabla.heading(col, "text").startswith("▲"))
        for heading in tabla["columns"]:
            tabla.heading(heading, text=heading.replace("▲ ", "").replace("▼ ", ""))
        tabla.heading(col, text=("▲ " if df[col].is_monotonic_increasing else "▼ ") + col)
        actualizar_tabla(df)
        
    # Insertar los datos en la tabla
    def actualizar_tabla(df_actual):
        for row in tabla.get_children():
            tabla.delete(row)
        for index, row in df_actual.iterrows():
            tabla.insert("", "end", values=list(row))
            
    # Función para filtrar datos según la búsqueda
    def filtrar_tabla(event=None):
        query = entry_buscar.get().lower()  
        filtered_df = df[df.apply(lambda row: row.astype(str).str.contains(query, case=False, na=False).any(), axis=1)]
        actualizar_tabla(filtered_df)
        
    # Función para el menú contextual
    def copiar_valor(event):
        col = tabla.identify_column(event.x)
        row = tabla.identify_row(event.y)
        if row and col:
            col_index = int(col.replace("#", "")) - 1
            selected_item = tabla.item(row)
            cell_value = selected_item['values'][col_index]
            if cell_value is not None:
                root.clipboard_clear()
                root.clipboard_append(cell_value)
                root.update()
                print(f"Valor copiado: {cell_value}")
    def show_context_menu(event):
        nonlocal last_click_event
        last_click_event = event
        menu.post(event.x_root, event.y_root)
    
    df = pd.DataFrame(datos_pdf)
    root = tk.Tk()
    root.title("Visualización de Datos de la Boleta")
    root.geometry("1200x600")
    frame_tabla = ttk.Frame(root)
    frame_tabla.pack(fill="both", expand=True)

    # Crear un buscador
    label_buscar = ttk.Label(root, text="Buscador global:")
    label_buscar.pack(pady=5)
    entry_buscar = ttk.Entry(root)
    entry_buscar.pack(pady=5)
    
    vcmd = (root.register(lambda s: len(s) <= 20), '%P')
    entry_buscar.config(validate='key', validatecommand=vcmd)
    entry_buscar.bind("<KeyRelease>", filtrar_tabla)
    tabla = ttk.Treeview(frame_tabla, columns=list(df.columns), show='headings')
    for col in df.columns:
        tabla.heading(col, text=col, command=lambda c=col: ordenar_por_columna(c))
        tabla.column(col, anchor='center')

    last_click_event = None
    menu = Menu(root, tearoff=0)
    menu.add_command(label="Copiar", command=lambda: copiar_valor(last_click_event))
    tabla.bind("<Button-3>", show_context_menu)
    
    # Barra de desplazamiento vertical
    scrollbar_y = ttk.Scrollbar(frame_tabla, orient="vertical", command=tabla.yview)
    tabla.configure(yscroll=scrollbar_y.set)
    scrollbar_y.pack(side="right", fill="y")
    
    # Barra de desplazamiento horizontal
    scrollbar_x = ttk.Scrollbar(frame_tabla, orient="horizontal", command=tabla.xview)
    tabla.configure(xscroll=scrollbar_x.set)
    scrollbar_x.pack(side="bottom", fill="x")
    tabla.pack(side="left", fill="both", expand=True)
    actualizar_tabla(df)
    boton_exportar = ttk.Button(root, text="Exportar a excel datos", command=lambda: exportar_a_excel_boleta(cabeceras, datos_pdf, titulo))
    boton_exportar.pack(pady=10)
    
    
    root.mainloop()


def interfaz_inicial(dir_inicial):
    """
    Interfaz inicial donde se selecciona la ubicacion de las
    boletas a buscar
    """
    root = tk.Tk()
    root.title("Buscador de boletas Stealth")
    frame = ttk.Frame(root)
    frame.pack(pady=10)
    
    label_ruta = ttk.Label(frame, text="Ruta de la carpeta:")
    label_ruta.grid(row=0, column=0, padx=5, pady=5)
    entry_ruta = ttk.Entry(frame, width=90)
    entry_ruta.insert(0, dir_inicial)
    entry_ruta.grid(row=0, column=1, padx=5, pady=5)
    boton_seleccionar_carpeta = ttk.Button(frame, text="Seleccionar Carpeta", command=lambda: seleccionar_ruta(entry_ruta, dir_inicial))
    boton_seleccionar_carpeta.grid(row=0, column=2, padx=5, pady=5)
    boton_visualizar_boletas_general = ttk.Button(root, text="Visualizar las boletas general", command=lambda: cargar_datos_boleta_general(entry_ruta.get()))
    boton_visualizar_boletas_general.pack(pady=10)
    boton_visualizar_boletas_especifico = ttk.Button(root, text="Visualizar las boletas especificación", command=lambda: cargar_datos_boleta_especifico(entry_ruta.get()))
    boton_visualizar_boletas_especifico.pack(pady=10)
    root.mainloop()


def cargar_datos_boleta_general(ruta):
    cabeceras = ["NombreArchivo", "NumBol", "ImporteTotal", "FechaDeEmision", "Persona"]
    titulo = "Datos General"
    lista_rutas_pdf = listar_pdfs(ruta)
    datos_pdf = []
    for nombre_pdf in lista_rutas_pdf:
        ruta_pdf = os.path.join(ruta, nombre_pdf)
        texto = leer_pdf(ruta_pdf)
        datos = obtener_datos_general(texto)
        datos['NombreArchivo'] = nombre_pdf
        datos_pdf.append(datos)
    visualizar_datos_de_boletas(datos_pdf, cabeceras, titulo)


def cargar_datos_boleta_especifico(ruta):
    cabeceras = ["Num. Bolela", "Cantidad", "UM", "Codigo", "Descripcion", "Precio" ]
    titulo = "Datos Especificación"
    lista_rutas_pdf = listar_pdfs(ruta)
    datos_pdf = []
    for nombre_pdf in lista_rutas_pdf:
        ruta_pdf = os.path.join(ruta, nombre_pdf)
        texto = leer_pdf(ruta_pdf)
        productos = obtener_datos_especifico(texto)
        for producto in productos:
            datos_pdf.append(producto)

    visualizar_datos_de_boletas(datos_pdf, cabeceras, titulo)
    

def exportar_a_excel_boleta(cabeceras, datos_pdf, titulo):
    ruta_excel = filedialog.asksaveasfilename(
        defaultextension = ".xlsx", 
        filetypes = [("Excel files", "*.xlsx")], 
        initialfile = "Boletas Stealth"
    )
    if not ruta_excel:
        return
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = titulo
    
    ws.append(cabeceras)
    for dato in datos_pdf:
        fila = [dato.get(col, "") for col in cabeceras]
        ws.append(fila)

    wb.save(ruta_excel)
    print(f"Datos exportados a: {ruta_excel}")


def seleccionar_ruta(entrada_ruta, dir_inicial):
    ruta_seleccionada = filedialog.askdirectory(initialdir=dir_inicial)
    if ruta_seleccionada:
        entrada_ruta.delete(0, tk.END)
        entrada_ruta.insert(0, ruta_seleccionada)