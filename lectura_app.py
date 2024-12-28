import tkinter as tk
from tkinter import filedialog, messagebox, colorchooser, simpledialog
import pyttsx3
import threading
import openai
import speech_recognition as sr
import random
import fitz  # PyMuPDF
from tooltip import Tooltip

# Configura tu clave de API de OpenAI
openai.api_key = 'TU_CLAVE_API_REAL'

class LeeFacil:
    def __init__(self, root):
        self.root = root
        self.root.title("LEE FÁCIL - IA para Lectura Accesible")
        self.root.geometry("1000x700")
        self.root.configure(bg="#f0f0f0")

        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)  # Velocidad de lectura
        self.engine.setProperty('volume', 1)  # Volumen de lectura

        # Listar todas las voces disponibles
        self.voices = self.engine.getProperty('voices')
        self.engine.setProperty('voice', self.voices[0].id)  # Usa la voz por defecto

        self.fuente_actual = "Arial"
        self.tamano_fuente = 16

        self.crear_widgets_principales()

    def crear_widgets_principales(self):
        self.text_area = tk.Text(self.root, wrap="word", font=(self.fuente_actual, self.tamano_fuente), bg="white", fg="black")
        self.text_area.pack(expand=True, fill="both", padx=10, pady=10)

        toolbar = tk.Frame(self.root, bg="#d9d9d9")
        toolbar.pack(side="top", fill="x")

        botones = [
            ("Cargar Archivo", self.cargar_archivo, "Cargar un archivo de texto o PDF"),
            ("Pegar Texto", self.pegar_texto, "Pegar texto desde el portapapeles"),
            ("Guardar Texto", self.guardar_texto, "Guardar el texto en un archivo"),
            ("Iniciar Lectura", self.iniciar_lectura, "Iniciar la lectura en voz alta del texto"),
            ("Detener Lectura", self.detener_lectura, "Detener la lectura en voz alta"),
            ("Cambiar Fuente", self.cambiar_fuente, "Cambiar la fuente del texto"),
            ("Cambiar Color", self.cambiar_color, "Cambiar el color del texto"),
            ("Velocidad Lectura", self.cambiar_velocidad, "Cambiar la velocidad de lectura"),
            ("Preguntar Texto", self.preguntar_texto, "Hacer preguntas sobre el texto"),
            ("Generar Preguntas", self.generar_preguntas, "Generar preguntas de comprensión sobre el texto"),
            ("Simplificar Texto", self.simplificar_texto, "Simplificar el texto utilizando la API de OpenAI"),
            ("🎙 Transcribir Audio", self.transcribir_audio, "Transcribir audio a texto utilizando Google Speech Recognition")
        ]

        # Asignar colores pastel a cada botón y agregar tooltips
        for texto, comando, tooltip_text in botones:
            color = self.generar_color_pastel()
            btn = tk.Button(toolbar, text=texto, command=comando, bg=color)
            btn.pack(side="left", padx=5, pady=5)
            Tooltip(btn, tooltip_text)

    def generar_color_pastel(self):
        r = random.randint(200, 255)
        g = random.randint(200, 255)
        b = random.randint(200, 255)
        return f'#{r:02x}{g:02x}{b:02x}'

    def cargar_archivo(self):
        archivo = filedialog.askopenfilename(filetypes=[("Archivos de texto", "*.txt"), ("Archivos PDF", "*.pdf")])
        if archivo:
            try:
                if archivo.endswith('.txt'):
                    with open(archivo, "r", encoding="utf-8") as f:
                        contenido = f.read()
                elif archivo.endswith('.pdf'):
                    contenido = self.extraer_texto_pdf(archivo)
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(tk.END, contenido)
            except Exception as e:
                messagebox.showerror("Error al cargar archivo", f"Error: {e}")

    def extraer_texto_pdf(self, archivo):
        doc = fitz.open(archivo)
        texto = ""
        for pagina in doc:
            texto += pagina.get_text()
        return texto

    def pegar_texto(self):
        try:
            texto_portapapeles = self.root.clipboard_get()
            self.text_area.insert(tk.END, texto_portapapeles)
        except Exception as e:
            messagebox.showerror("Error al pegar texto", f"Error: {e}")

    def guardar_texto(self):
        archivo = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Archivos de texto", "*.txt")])
        if archivo:
            try:
                with open(archivo, "w", encoding="utf-8") as f:
                    f.write(self.text_area.get(1.0, tk.END).strip())
                messagebox.showinfo("Guardar Texto", "Archivo guardado exitosamente.")
            except Exception as e:
                messagebox.showerror("Error al guardar archivo", f"Error: {e}")

    def iniciar_lectura(self):
        texto = self.text_area.get(1.0, tk.END).strip()
        if texto:
            self.lectura_activa = True
            texto = texto.replace(" y ", " i ")  # Corrige pronunciación
            threading.Thread(target=self.leer_texto, args=(texto,), daemon=True).start()

    def leer_texto(self, texto):
        try:
            self.engine.say(texto)
            self.engine.runAndWait()
        except Exception as e:
            messagebox.showerror("Error de Lectura", f"Error: {e}")

    def detener_lectura(self):
        self.lectura_activa = False
        self.engine.stop()

    def cambiar_fuente(self):
        def aplicar_cambio():
            self.fuente_actual = fuente_var.get()
            self.tamano_fuente = tamano_var.get()
            self.text_area.config(font=(self.fuente_actual, self.tamano_fuente))
            fuente_dialogo.destroy()

        fuente_dialogo = tk.Toplevel(self.root)
        fuente_dialogo.title("Cambiar Fuente")

        tk.Label(fuente_dialogo, text="Familia:").pack(pady=5)
        fuente_var = tk.StringVar(value=self.fuente_actual)
        tk.Entry(fuente_dialogo, textvariable=fuente_var).pack(pady=5)

        tk.Label(fuente_dialogo, text="Tamaño:").pack(pady=5)
        tamano_var = tk.IntVar(value=self.tamano_fuente)
        tk.Entry(fuente_dialogo, textvariable=tamano_var).pack(pady=5)

        tk.Button(fuente_dialogo, text="Aplicar", command=aplicar_cambio).pack(pady=10)

    def cambiar_color(self):
        color = colorchooser.askcolor()[1]
        if color:
            self.text_area.config(fg=color)

    def cambiar_velocidad(self):
        velocidad = simpledialog.askinteger("Velocidad de Lectura", "Ingrese la velocidad de lectura (50-300):", minvalue=50, maxvalue=300)
        if velocidad:
            self.engine.setProperty('rate', velocidad)
            messagebox.showinfo("Velocidad de Lectura", f"Velocidad de lectura ajustada a {velocidad}.")

    def preguntar_texto(self):
        pregunta = simpledialog.askstring("Pregunta", "¿Qué quieres saber del texto?")
        if pregunta:
            respuesta = self.buscar_respuesta(pregunta)
            messagebox.showinfo("Respuesta", respuesta)

    def buscar_respuesta(self, pregunta):
        texto = self.text_area.get(1.0, tk.END).strip()
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Eres un asistente útil."},
                    {"role": "user", "content": f"Texto: {texto}\n\nPregunta: {pregunta}"}
                ]
            )
            return response.choices[0].message['content'].strip()
        except Exception as e:
            return f"Error: {e}"

    def generar_preguntas(self):
        texto = self.text_area.get(1.0, tk.END).strip()
        if texto:
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "Eres un asistente útil."},
                        {"role": "user", "content": f"Genera preguntas de comprensión para el siguiente texto:\n\n{texto}"}
                    ]
                )
                preguntas = response.choices[0].message['content'].strip()
                messagebox.showinfo("Preguntas Generadas", preguntas)
            except Exception as e:
                messagebox.showerror("Error al generar preguntas", f"Error: {e}")

    def simplificar_texto(self):
        texto_original = self.text_area.get(1.0, tk.END).strip()
        texto_simplificado = self.simplificar_texto_func(texto_original)
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(tk.END, texto_simplificado)

    def simplificar_texto_func(self, texto):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Eres un asistente útil."},
                    {"role": "user", "content": f"Simplifica el siguiente texto:\n\n{texto}"}
                ]
            )
            texto_simplificado = response.choices[0].message['content'].strip()
            return texto_simplificado
        except Exception as e:
            return f"Error: {e}"

    def transcribir_audio(self):
        archivo_audio = filedialog.askopenfilename(filetypes=[("Archivos de audio", "*.wav *.mp3")])
        if archivo_audio:
            recognizer = sr.Recognizer()
            with sr.AudioFile(archivo_audio) as source:
                audio = recognizer.record(source)
                try:
                    transcripcion = recognizer.recognize_google(audio, language="es-ES")
                    self.text_area.delete(1.0, tk.END)
                    self.text_area.insert(tk.END, transcripcion)
                except sr.UnknownValueError:
                    self.text_area.insert(tk.END, "No se pudo entender el audio.")
                except sr.RequestError:
                    self.text_area.insert(tk.END, "Error al conectar con el servicio de transcripción.")

if __name__ == "__main__":
    root = tk.Tk()
    app = LeeFacil(root)
    root.mainloop()