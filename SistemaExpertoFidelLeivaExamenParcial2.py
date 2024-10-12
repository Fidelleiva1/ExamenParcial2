import mysql.connector
import tkinter as tk
from tkinter import ttk, messagebox

# Conexión a MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="sistema_peliculas"
)
cursor = conn.cursor()

# Función para obtener valores únicos de una columna
def obtener_valores_unicos(columna):
    query = f"SELECT DISTINCT {columna} FROM peliculas"
    cursor.execute(query)
    return [row[0] for row in cursor.fetchall()]

# Función para recomendar una película (Primera interfaz)
def recomendar_pelicula():
    genero = combo_genero.get()
    duracion = combo_duracion.get()
    estilo = combo_estilo.get()
    popularidad_minima = combo_popularidad.get()
    año = combo_año.get()

    if not genero or not duracion or not estilo or not popularidad_minima or not año:
        messagebox.showwarning("Advertencia", "Por favor, selecciona todas las preferencias.")
        return

    duracion_minima, duracion_maxima = (0, 100) if duracion == "Corta" else (100, 500)

    query = '''
    SELECT titulo, genero, duracion, estilo, popularidad, año
    FROM peliculas
    WHERE genero = %s AND  duracion BETWEEN %s AND %s AND estilo LIKE %s AND popularidad >= %s año = %s
    ORDER BY popularidad DESC LIMIT 1
    '''
    cursor.execute(query, (genero, duracion_minima, duracion_maxima, f"%{estilo}%", popularidad_minima, año))
    pelicula = cursor.fetchone()

    if pelicula:
        resultado.set(f"Te recomendamos ver: {pelicula[0]}\n"
                      f"Género: {pelicula[1]}, Duración: {pelicula[2]} min\n"
                      f"Estilo: {pelicula[3]}, Popularidad: {pelicula[4]}/10", f"Estilo: {año[5]})
    else:
        resultado.set("No se encontró una película que coincida con tus preferencias.")

# Función para abrir la segunda interfaz (para calcular probabilidad)
def abrir_segunda_interfaz():
    def calcular_probabilidad(genero, duracion, estilo):
        probabilidad_genero = {
            "Comedia": 0.25, "Drama": 0.20, "Accion": 0.15, "Romantica": 0.10,
            "Ciencia Ficcion": 0.10, "Documental": 0.10, "Terror": 0.10
        }
        probabilidad_atributos = {
            "Duracion": {
                "Corta": {"Comedia": 0.2, "Drama": 0.1, "Accion": 0.1, "Romantica": 0.2, "Documental": 0.1, "Terror": 0.3, "Ciencia Ficcion": 0.1},
                "Media": {"Comedia": 0.6, "Drama": 0.4, "Accion": 0.4, "Romantica": 0.6, "Documental": 0.3, "Terror": 0.5, "Ciencia Ficcion": 0.3},
                "Larga": {"Comedia": 0.2, "Drama": 0.5, "Accion": 0.5, "Romantica": 0.2, "Documental": 0.6, "Terror": 0.2, "Ciencia Ficcion": 0.6}
            },
            "Estilo": {
                "Moderno": {"Comedia": 0.5, "Drama": 0.5, "Accion": 0.8, "Romantica": 0.5, "Documental": 0.8, "Terror": 0.7, "Ciencia Ficcion": 0.6},
                "Clasica": {"Comedia": 0.5, "Drama": 0.5, "Accion": 0.2, "Romantica": 0.5, "Documental": 0.2, "Terror": 0.3, "Ciencia Ficcion": 0.4}
            }
        }
        prob_genero = probabilidad_genero.get(genero, 0)
        prob_duracion = probabilidad_atributos["Duracion"].get(duracion, {}).get(genero, 0)
        prob_estilo = probabilidad_atributos["Estilo"].get(estilo, {}).get(genero, 0)
        return prob_genero * prob_duracion * prob_estilo

    def recomendar_con_probabilidad():
        genero = combo_genero.get()
        duracion = combo_duracion.get()
        estilo = combo_estilo.get()

        if not genero or not duracion or not estilo:
            messagebox.showwarning("Advertencia", "Por favor, selecciona todas las preferencias.")
            return

        probabilidad = calcular_probabilidad(genero, duracion, estilo)

        query = '''
        SELECT titulo, genero, duracion, estilo, popularidad
        FROM peliculas
        WHERE genero = %s AND estilo LIKE %s
        ORDER BY popularidad DESC LIMIT 1
        '''
        cursor.execute(query, (genero, f"%{estilo}%"))
        pelicula = cursor.fetchone()

        if pelicula:
            resultado_prob.set(f"Te recomendamos ver: {pelicula[0]}\n"
                               f"Género: {pelicula[1]}, Duración: {pelicula[2]} min\n"
                               f"Estilo: {pelicula[3]}, Popularidad: {pelicula[4]}/10\n"
                               f"Probabilidad de éxito: {probabilidad:.2f}")
        else:
            resultado_prob.set("No se encontró una película que coincida con tus preferencias.")

    ventana_secundaria = tk.Toplevel()
    ventana_secundaria.title("Recomendador con Probabilidad")

    tk.Label(ventana_secundaria, text="Género").grid(row=0, column=0, padx=10, pady=10)
    combo_genero = ttk.Combobox(ventana_secundaria, values=obtener_valores_unicos("genero"))
    combo_genero.grid(row=0, column=1)

    tk.Label(ventana_secundaria, text="Duración").grid(row=1, column=0, padx=10, pady=10)
    combo_duracion = ttk.Combobox(ventana_secundaria, values=["Corta", "Media", "Larga"])
    combo_duracion.grid(row=1, column=1)

    tk.Label(ventana_secundaria, text="Estilo").grid(row=2, column=0, padx=10, pady=10)
    combo_estilo = ttk.Combobox(ventana_secundaria, values=obtener_valores_unicos("estilo"))
    combo_estilo.grid(row=2, column=1)

    btn_recomendar_prob = tk.Button(ventana_secundaria, text="Recomendar Película", command=recomendar_con_probabilidad)
    btn_recomendar_prob.grid(row=3, column=0, columnspan=2, pady=20)

    resultado_prob = tk.StringVar()
    label_resultado_prob = tk.Label(ventana_secundaria, textvariable=resultado_prob, wraplength=300, justify="left")
    label_resultado_prob.grid(row=4, column=0, columnspan=2)

# Función para agregar una nueva película
def agregar_pelicula():
    titulo = entry_titulo.get()
    genero = entry_genero.get()
    duracion = entry_duracion.get()
    estilo = entry_estilo.get()
    popularidad = entry_popularidad.get()

    if not titulo or not genero or not duracion or not estilo or not popularidad:
        messagebox.showwarning("Advertencia", "Por favor, completa todos los campos.")
        return

    try:
        duracion = int(duracion)
        popularidad = int(popularidad)
    except ValueError:
        messagebox.showerror("Error", "Duración y Popularidad deben ser números enteros.")
        return

    query = '''
    INSERT INTO peliculas (titulo, genero, duracion, estilo, popularidad)
    VALUES (%s, %s, %s, %s, %s)
    '''
    cursor.execute(query, (titulo, genero, duracion, estilo, popularidad))
    conn.commit()

    messagebox.showinfo("Éxito", "Película agregada exitosamente.")
    limpiar_campos()

def limpiar_campos():
    entry_titulo.delete(0, tk.END)
    entry_genero.set('')
    entry_duracion.delete(0, tk.END)
    entry_estilo.delete(0, tk.END)
    entry_popularidad.delete(0, tk.END)

# Función para abrir interfaz de agregar película
def abrir_interfaz_agregar():
    ventana_agregar = tk.Toplevel()
    ventana_agregar.title("Agregar Película")

    tk.Label(ventana_agregar, text="Título").grid(row=0, column=0, padx=10, pady=10)
    global entry_titulo
    entry_titulo = tk.Entry(ventana_agregar)
    entry_titulo.grid(row=0, column=1)

    tk.Label(ventana_agregar, text="Género").grid(row=1, column=0, padx=10, pady=10)
    global entry_genero
    entry_genero = ttk.Combobox(ventana_agregar, values=obtener_valores_unicos("genero"))
    entry_genero.grid(row=1, column=1)

    tk.Label(ventana_agregar, text="Duración").grid(row=2, column=0, padx=10, pady=10)
    global entry_duracion
    entry_duracion = tk.Entry(ventana_agregar)
    entry_duracion.grid(row=2, column=1)

    tk.Label(ventana_agregar, text="Estilo").grid(row=3, column=0, padx=10, pady=10)
    global entry_estilo
    entry_estilo = tk.Entry(ventana_agregar)
    entry_estilo.grid(row=3, column=1)

    tk.Label(ventana_agregar, text="Popularidad").grid(row=4, column=0, padx=10, pady=10)
    global entry_popularidad
    entry_popularidad = tk.Entry(ventana_agregar)
    entry_popularidad.grid(row=4, column=1)

    btn_guardar = tk.Button(ventana_agregar, text="Agregar Película", command=agregar_pelicula)
    btn_guardar.grid(row=5, column=0, columnspan=2, pady=20)

# Ventana principal
ventana_principal = tk.Tk()
ventana_principal.title("Recomendador de Películas")

tk.Label(ventana_principal, text="Género").grid(row=0, column=0, padx=10, pady=10)
combo_genero = ttk.Combobox(ventana_principal, values=obtener_valores_unicos("genero"))
combo_genero.grid(row=0, column=1)

tk.Label(ventana_principal, text="Duración").grid(row=1, column=0, padx=10, pady=10)
combo_duracion = ttk.Combobox(ventana_principal, values=["Corta", "Media", "Larga"])
combo_duracion.grid(row=1, column=1)

tk.Label(ventana_principal, text="Estilo").grid(row=2, column=0, padx=10, pady=10)
combo_estilo = ttk.Combobox(ventana_principal, values=obtener_valores_unicos("estilo"))
combo_estilo.grid(row=2, column=1)

tk.Label(ventana_principal, text="Popularidad Mínima").grid(row=3, column=0, padx=10, pady=10)
combo_popularidad = ttk.Combobox(ventana_principal, values=[str(i) for i in range(1, 11)])
combo_popularidad.grid(row=3, column=1)

btn_recomendar = tk.Button(ventana_principal, text="Recomendar Película", command=recomendar_pelicula)
btn_recomendar.grid(row=4, column=0, columnspan=2, pady=20)

resultado = tk.StringVar()
label_resultado = tk.Label(ventana_principal, textvariable=resultado, wraplength=300, justify="left")
label_resultado.grid(row=5, column=0, columnspan=2)

btn_abrir_segunda = tk.Button(ventana_principal, text="Abrir Recomendador con Probabilidad", command=abrir_segunda_interfaz)
btn_abrir_segunda.grid(row=6, column=0, columnspan=2, pady=10)

btn_abrir_agregar = tk.Button(ventana_principal, text="Agregar Nueva Película", command=abrir_interfaz_agregar)
btn_abrir_agregar.grid(row=7, column=0, columnspan=2, pady=10)

ventana_principal.mainloop()
