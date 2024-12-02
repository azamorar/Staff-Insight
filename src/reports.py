import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import threading
import os
import sys
import psycopg2
import pandas as pd
import json


if getattr(sys, 'frozen', False):
    # Ejecución en modo congelado (pyinstaller)
    import pyi_splash # type: ignore
    pyi_splash.update_text("Cargando...")
    
# Datos de conexión a PostgreSQL
host = "confidential"            # Dirección del servidor de PostgreSQL
port = "5432"                # Puerto (por defecto es 5432)
database = "confidential"   # Nombre de la base de datos
user = "confidential"          # Usuario de la base de datos
carpeta_Meplan = os.path.join(os.path.expanduser("~"), "AppData", "Local", "MePlan")
archivo_config = os.path.join(carpeta_Meplan, "reports_config.json")

def load_config():
    informes_basicos = [
            {
                "nombre": "PDP vs PDA",
                "query": "SELECT * FROM meplan.pdpvspda",
                "archivo": "PDPvsPDA.csv"
            },
            {
                "nombre": "Singulares (SCS)",
                "query": "SELECT * FROM meplan.txtfusionscs_2a",
                "archivo": "Singulares(SCS).csv"
            },
            {
                "nombre": "Directivos (SCD)",
                "query": "SELECT * FROM meplan.txtfusionscd",
                "archivo": "Directivos(SCD).csv"
            },
            {
                "nombre": "Directivos Especiales (PIND)",
                "query": "SELECT * FROM meplan.txtfusionpind",
                "archivo": "DirectivosEspeciales(PIND).csv"
            },
            {
                "nombre": "Acuerdo Salidas",
                "query": "SELECT * FROM meplan.calcpvs19consolidado",
                "archivo": "AcuerdoSalidas.csv"
            },
            {
                "nombre": "AVS20",
                "query": "SELECT * FROM meplan.calcpvs19consolidado WHERE id_plan = 'AVS20'",
                "archivo": "AVS20.csv"
            },
            {
                "nombre": "Penher",
                "query": "SELECT * FROM meplan.calcpenher",
                "archivo": "Penher.csv"
            },
            {
                "nombre": "Flujos",
                "query": "SELECT * FROM meplan.calcflujos",
                "archivo": "Flujos.csv"
            },
            {
                "nombre": "Energia",
                "query": "SELECT * FROM meplan.calcenergiaconsolidado",
                "archivo": "Energia.csv"
            },
            {
                "nombre": "Salud",
                "query": "SELECT * FROM meplan.calcsalud",
                "archivo": "Salud.csv"
            },
            {
                "nombre": "Premios",
                "query": "SELECT * FROM meplan.calcpremiosact",
                "archivo": "Premios.csv"
            },
            {
                "nombre": "Rentas (Anualizado)",
                "query": "SELECT * FROM meplan.calcrentagroupedbyyear",
                "archivo": "Rentas(Anualizado).csv"
            }
        ]
    with open(archivo_config, "w") as f:
        json.dump(informes_basicos, f, indent=4)
       
def execute_query(query, nombre_archivo, status_var):
    def run_query():
        try:
            # Conexión a la base de datos
            with psycopg2.connect(
                host=host,
                port=port,
                database=database,
                user=user,
                password=password
            ) as conn:
                print("Conexión exitosa a la base de datos.")
                
                # Actualiza el literal de estado
                status_var.set("Descarga en curso...")
                
                # Ejecuta la consulta y carga los datos en un DataFrame de pandas
                df = pd.read_sql(query, conn)

                # Exporta el DataFrame a un archivo CSV
                carpeta_descargas = os.path.join(os.path.expanduser("~"), "Downloads")
                nombre_archivo_completo = os.path.join(carpeta_descargas, nombre_archivo)
                df.to_csv(nombre_archivo_completo, index=False)
                
                # Muestra un mensaje de confirmación en un pop-up
                status_var.set("¡Listo!")
                messagebox.showinfo("Exportación exitosa", f"Datos exportados exitosamente a {nombre_archivo_completo}")
        
        except Exception as e:
            status_var.set("Error de descarga")
            messagebox.showerror("Error", f"Error al conectar o extraer los datos: {e}")
            print("Error al conectar o extraer los datos:", e)
        
        finally:
            print("Conexión a la base de datos cerrada.")

    # Inicia un nuevo hilo para ejecutar la consulta
    threading.Thread(target=run_query).start()

def load_reports():
    
    if not os.path.exists(carpeta_Meplan):
        os.makedirs(carpeta_Meplan)
    
    if not os.path.exists(archivo_config):
        load_config()
        
    with open(archivo_config, "r") as f:
        return json.load(f)

# Función para ejecutar la consulta del informe seleccionado
def execute_selected():
    selected_informe = informe_combobox.get()
    if selected_informe == "":  # No se ha seleccionado ningún informe
        messagebox.showerror("Error", "Por favor, selecciona un informe.")
        return
    for informe in informes:
        if informe['nombre'] == selected_informe:
            execute_query(informe['query'], informe['archivo'], status_var)
            break

# Función para mostrar la información del informe seleccionado
def show_info():
    selected_informe = informe_combobox.get()
    for informe in informes:
        if informe['nombre'] == selected_informe:
            info = f"Nombre: {informe['nombre']}\n\nQuery: {informe['query']}\n\nArchivo de salida: {informe['archivo']}"
            messagebox.showinfo("Información del Informe", info)
            return
    messagebox.showinfo("Información del Informe", "No se ha seleccionado ningún informe")

def validate_query(query):
    # Verificar que la consulta comience con "SELECT"
    if not query.strip().upper().startswith("SELECT"):
        messagebox.showerror("Error de validación", f"La consulta debe comenzar con la palabra SELECT.")
        return False
    # Verificar que la consulta no contenga palabras clave peligrosas
    dangerous_keywords = ["DELETE", "DROP", "INSERT", "UPDATE", "ALTER"]
    for keyword in dangerous_keywords:
        if keyword in query.upper():
            messagebox.showerror("Error de validación", f"La consulta contiene la palabra {keyword} que no es válida.")
            return False
    return True

# Función para agregar una nueva entrada al archivo reports_config.json
def add_new_entry():
    def save_entry():
        nombre = nombre_var.get()
        if nombre == "":
            messagebox.showerror("Error de validación", "El nombre no puede estar vacío.")
            return
        query = query_var.get()
        if query == "":
            messagebox.showerror("Error de validación", "La consulta no puede estar vacía.")
            return
        if not validate_query(query):
            return
        new_entry = {
            "nombre": nombre,
            "query": query,
            "archivo": nombre + ".csv"
        }
        informes.append(new_entry)
        with open(archivo_config, "w") as f:
            json.dump(informes, f, indent=4)
        informe_combobox['values'] = [informe['nombre'] for informe in informes]
        add_entry_window.destroy()
        informe_combobox.set("")
        messagebox.showinfo("Entrada añadida", "La nueva entrada ha sido añadida exitosamente.")

    add_entry_window = tk.Toplevel(root)
    add_entry_window.geometry("420x150")
    add_entry_window.title("Añadir nueva entrada")

    tk.Label(add_entry_window, text="Nombre:").grid(row=0, column=0, padx=10, pady=5)
    nombre_var = tk.StringVar()
    tk.Entry(add_entry_window, width=50,  textvariable=nombre_var).grid(row=0, column=1, padx=10, pady=5)

    tk.Label(add_entry_window, text="Query:").grid(row=1, column=0, padx=10, pady=5)
    query_var = tk.StringVar()
    tk.Entry(add_entry_window,width=50, textvariable=query_var).grid(row=1, column=1, padx=10, pady=5)

    tk.Label(add_entry_window, text="Las tablas deben tener el prefijo 'meplan.' , por ejemplo: meplan.tabla1").grid(row=3, column=0, columnspan=2, pady=10)
    tk.Button(add_entry_window, text="Guardar", command=save_entry).grid(row=4, column=0, columnspan=2, pady=10)

# Función para editar una entrada existente en el archivo reports_config.json
def edit_entry():
    selected_informe = informe_combobox.get()
    if selected_informe == "":
        messagebox.showerror("Error", "Por favor, selecciona un informe para editar.")
        return

    for informe in informes:
        if informe['nombre'] == selected_informe:
            def save_edit():
                nombre = nombre_var.get()
                if nombre == "":
                    messagebox.showerror("Error de validación", "El nombre no puede estar vacío.")
                    return
                query = query_var.get()
                if query == "":
                    messagebox.showerror("Error de validación", "La consulta no puede estar vacía.")
                    return
                if not validate_query(query):
                    return
                informe['nombre'] = nombre
                informe['query'] = query
                informe['archivo'] = nombre + ".csv"
                with open(archivo_config, "w") as f:
                    json.dump(informes, f, indent=4)
                informe_combobox['values'] = [informe['nombre'] for informe in informes]
                edit_entry_window.destroy()
                informe_combobox.set("")
                messagebox.showinfo("Entrada editada", "La entrada ha sido editada exitosamente.")

            edit_entry_window = tk.Toplevel(root)
            edit_entry_window.geometry("420x150")
            edit_entry_window.title("Editar entrada")

            tk.Label(edit_entry_window, text="Nombre:").grid(row=0, column=0, padx=10, pady=5)
            nombre_var = tk.StringVar(value=informe['nombre'])
            tk.Entry(edit_entry_window, width=50, textvariable=nombre_var).grid(row=0, column=1, padx=10, pady=5)

            tk.Label(edit_entry_window, text="Query:").grid(row=1, column=0, padx=10, pady=5)
            query_var = tk.StringVar(value=informe['query'])
            tk.Entry(edit_entry_window, width=50, textvariable=query_var).grid(row=1, column=1, padx=10, pady=5)

            tk.Label(edit_entry_window, text="Las tablas deben tener el prefijo 'meplan.' , por ejemplo: meplan.tabla1").grid(row=3, column=0, columnspan=2, pady=10)
            tk.Button(edit_entry_window, text="Guardar", command=save_edit).grid(row=4, column=0, columnspan=2, pady=10)
            break

# Función para eliminar una entrada del archivo reports_config.json
def delete_entry():
    selected_informe = informe_combobox.get()
    if selected_informe == "":
        messagebox.showerror("Error", "Por favor, selecciona un informe para eliminar.")
        return

    for informe in informes:
        if informe['nombre'] == selected_informe:
            if messagebox.askyesno("Confirmar eliminación", f"¿Estás seguro de que deseas eliminar el informe '{selected_informe}'?"):
                informes.remove(informe)
                with open(archivo_config, "w") as f:
                    json.dump(informes, f, indent=4)
                informe_combobox['values'] = [informe['nombre'] for informe in informes]
                informe_combobox.set("")
                messagebox.showinfo("Informe eliminado", "El informe ha sido eliminado exitosamente.")
            break

def login():
    global password
    password = password_var.get()
    try:
        # Intentar conectar a la base de datos con la contraseña proporcionada
        with psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
        ) as conn:
            print("Conexión exitosa a la base de datos.")
            login_window.destroy()
            main_window()
    except Exception as e:
        messagebox.showerror("Error de inicio de sesión", f"Error al conectar a la base de datos: {e}")

def main_window():
    global root, informe_combobox, status_var, informes
    
    # Create the main application window
    root = tk.Tk()
    root.title("Descarga de Informes MePlan")
    root.geometry("600x350")

    # Crear el título en negrita
    tk.Label(root, text="Selecciona el informe que deseas descargar:", font=("Helvetica", 16, "bold")).pack(pady=5)

    button_frame = tk.Frame(root)
    button_frame.pack(pady=10)

    # Crear los literales de estado y los botones
    informes = load_reports()

    # Crear el combobox para seleccionar el informe
    informe_var = tk.StringVar()

    combo_frame = tk.Frame(button_frame)
    combo_frame.pack(pady=10)

    informe_combobox = ttk.Combobox(combo_frame, textvariable=informe_var, width=50)
    informe_combobox['values'] = [informe['nombre'] for informe in informes]
    informe_combobox.pack(side=tk.LEFT)

    # Crear el botón para mostrar la información del informe seleccionado
    info_button = tk.Button(combo_frame, text="Detalles", command=show_info)
    info_button.pack(side=tk.LEFT, padx=5)

    # Crear el literal de estado
    status_var = tk.StringVar()
    status_var.set("")
    status_label = tk.Label(button_frame, textvariable=status_var, relief=tk.FLAT, bd=0, width=20)
    status_label.pack(pady=10)

    # Crear el botón para ejecutar la descarga del informe seleccionado
    tk.Button(button_frame, text="Descargar Informe", width=30, command=execute_selected, bg='#FDFD96').pack(pady=20)

    report_frame = tk.Frame(root)
    report_frame.pack(pady=10)

    # Crear el botón para añadir una nueva entrada al archivo reports_config.json
    tk.Button(report_frame, text="Crear Informe", width=20, command=add_new_entry).grid(row=0, column=0, padx=10, pady=5)
    tk.Button(report_frame, text="Editar Informe", width=20, command=edit_entry).grid(row=0, column=1, padx=10, pady=5)
    tk.Button(report_frame, text="Eliminar Informe", width=20, command=delete_entry).grid(row=0, column=2, padx=10, pady=5)

    if getattr(sys, 'frozen', False):
        # Ejecución en modo congelado (pyinstaller)
        import pyi_splash # type: ignore
        pyi_splash.close() # type: ignore

    # Start the main event loop
    root.mainloop()

# Crear la ventana de inicio de sesión
login_window = tk.Tk()
login_window.title("Inicio de Sesión")
login_window.geometry("350x250")  # Doble de grande

tk.Label(login_window, text="Me-Plan", font=("Helvetica", 16, "bold")).pack(pady=5)


# Crear un frame para organizar las etiquetas y entradas
login_frame = tk.Frame(login_window)
login_frame.pack(pady=20)

tk.Label(login_frame, text="Host:").grid(row=0, column=0, padx=10, pady=5)
tk.Entry(login_frame, textvariable=tk.StringVar(value=host), state='readonly', width=25).grid(row=0, column=1, padx=10, pady=5)

tk.Label(login_frame, text="Base de Datos:").grid(row=1, column=0, padx=10, pady=5)
tk.Entry(login_frame, textvariable=tk.StringVar(value=database), state='readonly', width=25).grid(row=1, column=1, padx=10, pady=5)

tk.Label(login_frame, text="Usuario:").grid(row=2, column=0, padx=10, pady=5)
tk.Entry(login_frame, textvariable=tk.StringVar(value=user), state='readonly', width=25).grid(row=2, column=1, padx=10, pady=5)

tk.Label(login_frame, text="Contraseña:").grid(row=3, column=0, padx=10, pady=5)
password_var = tk.StringVar()
tk.Entry(login_frame, textvariable=password_var, show="*", width=25).grid(row=3, column=1, padx=10, pady=5)

tk.Button(login_frame, text="Iniciar Sesión", command=login).grid(row=4, column=0, columnspan=2, pady=20)

if getattr(sys, 'frozen', False):
    # Ejecución en modo congelado (pyinstaller)
    pyi_splash.close() # type: ignore

# Start the login event loop
login_window.mainloop()
