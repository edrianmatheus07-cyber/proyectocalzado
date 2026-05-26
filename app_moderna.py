import os
try:
    import cv2  # <-- Nueva librería para la cámara
    CV2_AVAILABLE = True
except ImportError:
    cv2 = None
    CV2_AVAILABLE = False

from tkinter import filedialog
import customtkinter as ctk
from PIL import Image

# Importamos tu función del modelo
from validar_modelo import evaluar_foto

ctk.set_appearance_mode("Light") 
ctk.set_default_color_theme("blue") 

class AppModerna(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Detector de Calzado")
        self.geometry("950x650")
        self.resizable(False, False)
        self.configure(fg_color="#EEF2FF") # Fondo Indigo Pastel Suave

        self.ruta_actual = ""
        self.ctk_image = None
        
        # Variables para la cámara
        self.cap = None
        self.camara_activa = False
        self.frame_actual = None # Guarda la captura de la cámara en memoria
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_main_area()
        
        # Apagar la cámara correctamente si el usuario cierra la ventana
        self.protocol("WM_DELETE_WINDOW", self.cerrar_aplicacion)
        
    def _build_main_area(self):
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

        # -- Cabecera (Título y Botones) --
        header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))

        titulo = ctk.CTkLabel(header_frame, text="Detector de Calzado", 
                              font=("Segoe UI", 24, "bold"), text_color="#6366F1")
        titulo.pack(side="left")

        # El botón Analizar ahora es el principal (Teal) y empieza deshabilitado
        self.btn_analizar = ctk.CTkButton(header_frame, text="🧠 Analizar", font=("Segoe UI", 14, "bold"), 
                                          state="disabled",
                                          fg_color="#10B981", text_color="white", 
                                          text_color_disabled="white", hover_color="#059669", 
                                          height=40, width=120, command=self.evaluar)
        self.btn_analizar.pack(side="right", padx=(10, 0))

        self.btn_examinar = ctk.CTkButton(header_frame, text="📁 Archivos", font=("Segoe UI", 14, "bold"),
                                          fg_color="transparent", text_color="#6366F1", hover_color="#E0E7FF", 
                                          border_width=2, border_color="#6366F1", height=40, width=110, command=self.seleccionar_archivo)
        self.btn_examinar.pack(side="right", padx=(10, 0))
        
        # Botón Cámara con estilo basado en el color primario Índigo
        self.btn_camara = ctk.CTkButton(header_frame, text="📷 Cámara", font=("Segoe UI", 14, "bold"),
                                     fg_color="transparent", text_color="#6366F1", hover_color="#E0E7FF", 
                                     border_width=2, border_color="#6366F1",
                                     height=40, width=110, command=self.toggle_camara)
        self.btn_camara.pack(side="right")

        # -- Área de la Imagen Cargada --
        preview_container = ctk.CTkFrame(self.main_frame, fg_color="#FFFFFF", corner_radius=20, border_width=1, border_color="#E2E8F0")
        preview_container.pack(fill="both", expand=True, pady=(0, 20))
        preview_container.pack_propagate(False)

        # Se eliminó la etiqueta "VISUALIZADOR" y se ajustó el thumb_label
        self.thumb_label = ctk.CTkLabel(preview_container, text="Seleccione una fuente para comenzar", font=("Segoe UI", 13), text_color="#94A3B8")
        self.thumb_label.pack(expand=True, fill="both", padx=15, pady=(0, 15))

        # -- Panel de Resultados --
        self.result_box = ctk.CTkFrame(self.main_frame, fg_color="#E0E7FF", corner_radius=20, height=140, border_width=1, border_color="#C7D2FE")
        self.result_box.pack(fill="x")
        self.result_box.pack_propagate(False)

        text_frame = ctk.CTkFrame(self.result_box, fg_color="transparent")
        text_frame.pack(fill="x", padx=20, pady=(15, 5))
        
        ctk.CTkLabel(text_frame, text="ESTADO DE INFERENCIA", font=("Segoe UI", 11, "bold"), text_color="#94A3B8").pack(side="left")
        self.lbl_probabilidad = ctk.CTkLabel(text_frame, text="CONFIRMADO: --%", font=("Segoe UI", 14, "bold"), text_color="#64748B")
        self.lbl_probabilidad.pack(side="right")

        self.progress_bar = ctk.CTkProgressBar(self.result_box, height=18, corner_radius=9, 
                                               fg_color="#E2E8F0", progress_color="#818CF8")
        self.progress_bar.set(0)
        self.progress_bar.pack(fill="x", padx=20, pady=(10, 5))

        labels_frame = ctk.CTkFrame(self.result_box, fg_color="transparent")
        labels_frame.pack(fill="x", padx=25)
        
        ctk.CTkLabel(labels_frame, text="Clase Detectada:", font=("Segoe UI", 10, "bold"), text_color="#475569").pack(side="left")
        self.lbl_resultado_final = ctk.CTkLabel(labels_frame, text="", font=("Segoe UI", 16, "bold"), text_color="#6366F1")
        self.lbl_resultado_final.pack(side="right")
        self.lbl_resultado_final.configure(text="")

    # ── LÓGICA DE LA CÁMARA ──
    def toggle_camara(self):
        if not self.camara_activa:
            if not CV2_AVAILABLE:
                self.thumb_label.configure(text="❌ Error: OpenCV no instalado.\nEjecuta: pip install opencv-python", text_color="red")
                return
                
            # Encender cámara
            # Escaneamos del índice 0 al 4 para encontrar Iriun Webcam
            encontrada = False
            for i in range(5):
                self.cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
                if self.cap.isOpened():
                    encontrada = True
                    print(f"✅ Cámara detectada en el índice: {i}")
                    break

            if not encontrada:
                self.thumb_label.configure(
                    text="❌ Error: No se detectó ninguna cámara.\n"
                         "Asegúrate de que Iriun Webcam esté abierto en PC y Celular.", 
                    text_color="red"
                )
                return
                
            self.camara_activa = True
            self.btn_camara.configure(text="🛑 Detener", fg_color="#EF4444", hover_color="#DC2626", text_color="white")
            self.btn_analizar.configure(state="normal")
            self.actualizar_frame_camara()
        else:
            # Apagar cámara
            self.apagar_camara()

    def actualizar_frame_camara(self):
        if self.camara_activa and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                self.frame_actual = frame_rgb # Lo guardamos por si le dan al botón evaluar
                
                img = Image.fromarray(frame_rgb)
                img.thumbnail((800, 450), Image.Resampling.LANCZOS)
                
                self.ctk_image = ctk.CTkImage(light_image=img, dark_image=img, size=img.size)
                self.thumb_label.configure(image=self.ctk_image, text="")
            
            # Repetir este proceso cada 15 milisegundos para crear el efecto de video
            self.after(15, self.actualizar_frame_camara)

    def apagar_camara(self):
        self.camara_activa = False
        if self.cap:
            self.cap.release()
        self.btn_camara.configure(text="📷 Cámara", fg_color="transparent", text_color="#6366F1", hover_color="#E0E7FF", 
                                 border_width=2, border_color="#6366F1")
        self.btn_analizar.configure(state="disabled")
        self.thumb_label.configure(image="", text="Cámara apagada. Sube una foto o reactiva la cámara.")
        self.ruta_actual = ""

    # ── LÓGICA DE ARCHIVOS E INFERENCIA ──
    def seleccionar_archivo(self):
        if self.camara_activa:
            self.apagar_camara() # Apagamos la cámara si vamos a usar un archivo
            
        ruta = filedialog.askopenfilename(
            title="Seleccionar imagen",
            filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.bmp *.gif")])
        if ruta:
            self.ruta_actual = ruta
            img = Image.open(ruta)
            img.thumbnail((800, 450), Image.Resampling.LANCZOS)
            self.ctk_image = ctk.CTkImage(light_image=img, dark_image=img, size=img.size)
            self.thumb_label.configure(image=self.ctk_image, text="")
            self.btn_analizar.configure(state="normal")
            self.resetear_ui()

    def evaluar(self):
        # CASO 1: Está usando la cámara
        if self.camara_activa and self.frame_actual is not None:
            # Guardamos la captura actual en un archivo temporal para que tu modelo la lea
            ruta_temporal = "captura_temp.jpg"
            Image.fromarray(self.frame_actual).save(ruta_temporal)
            self.ruta_actual = ruta_temporal
            self.apagar_camara() # Congelamos la imagen apagando la cámara
            
        # CASO 2: No hay ni foto ni cámara
        elif not self.ruta_actual:
            self.lbl_probabilidad.configure(text="SELECCIONE IMAGEN O CÁMARA", text_color="#EF4444")
            return

        # Proceso de análisis
        self.btn_analizar.configure(state="disabled", text="Procesando...")
        self.update()

        # Llamamos al modelo
        es_calzado, confianza = evaluar_foto(self.ruta_actual)
        
        self.btn_analizar.configure(state="normal", text="🧠 Analizar")

        if es_calzado is None:
            self.lbl_probabilidad.configure(text="ERROR EN ARCHIVO", text_color="#EF4444")
            return

        # Ajustamos colores y textos para el modo binario
        color_progreso = "#34D399" if es_calzado else "#FB7185"
        texto_final = "CALZADO" if es_calzado else "NO ES UN CALZADO"
        
        self.progress_bar.configure(progress_color=color_progreso)
        self.lbl_resultado_final.configure(text=texto_final, text_color=color_progreso)
        
        target_value = confianza / 100.0
        self.animar_barra(target_value, 0.0, confianza, color_progreso)

    def resetear_ui(self):
        self.progress_bar.set(0)
        self.lbl_probabilidad.configure(text="CONFIRMADO: --%", text_color="#64748B")
        self.lbl_resultado_final.configure(text="")

    def animar_barra(self, target, current, porcentaje_final, color):
        step = 0.04
        if current < target:
            current += step
            if current > target:
                current = target
            self.progress_bar.set(current)
            self.lbl_probabilidad.configure(text=f"CONFIRMADO: {current * 100:.1f}%", text_color="#475569")
            self.after(20, self.animar_barra, target, current, porcentaje_final, color)
        else:
            self.progress_bar.set(target)
            self.lbl_probabilidad.configure(text=f"CONFIRMADO: {porcentaje_final:.1f}%", text_color=color)

    def cerrar_aplicacion(self):
        if self.camara_activa and self.cap:
            self.cap.release() # Apaga el LED de la cámara de tu laptop
        self.destroy()

if __name__ == "__main__":
    AppModerna().mainloop()