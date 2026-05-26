"""
ShoeVision AI — Módulo de Captura y Prueba de Cámara en Tiempo Real (Auto-Start)
"""

import sys
import customtkinter as ctk
import cv2
from PIL import Image, ImageTk

# ── Design System ─────────────────────────────────────────────────────────
class T:
    """Tokens de diseño (paleta, tipografía y bordes)."""
    BG = "#FAF5FF"
    SURFACE = "#FFFFFF"
    SURFACE_2 = "#F5F3FF"
    SURFACE_3 = "#EDE9FE"
    BORDER = "#E9D5FF"
    BORDER_LIGHT = "#DDD6FE"
    PREVIEW_BG = "#F3E8FF"

    # Marca (lavanda / malva)
    ACCENT = "#C4B5FD"
    ACCENT_HOVER = "#A78BFA"
    GLOW = "#7C3AED"
    TEXT_ON_ACCENT = "#FFFFFF"

    # Texto alto contraste
    TEXT = "#1E1B4B"
    TEXT_HEADING = "#312E81"
    TEXT_BODY = "#4338CA"
    TEXT_LABEL = "#5B21B6"
    TEXT_MUTED = "#6D28D9"
    TEXT_DIM = "#64748B"

    # Semánticos
    SUCCESS = "#047857"
    SUCCESS_BG = "#D1FAE5"
    DANGER = "#BE185D"
    DANGER_BG = "#FCE7F3"

    RADIUS_MD = 14
    RADIUS_LG = 20
    RADIUS_XL = 24

    FONT_DISPLAY = ("Segoe UI", 24, "bold")
    FONT_H1 = ("Segoe UI", 19, "bold")
    FONT_H2 = ("Segoe UI", 15, "bold")
    FONT_BODY = ("Segoe UI", 13)
    FONT_CAPTION = ("Segoe UI", 11)
    FONT_MICRO = ("Segoe UI", 10)


ctk.set_appearance_mode("Light")


def _card(parent, **kw) -> ctk.CTkFrame:
    defaults = dict(
        fg_color=T.SURFACE,
        corner_radius=T.RADIUS_LG,
        border_width=1,
        border_color=T.BORDER,
    )
    defaults.update(kw)
    return ctk.CTkFrame(parent, **defaults)


def _pill(parent, text, bg=T.SURFACE_2, fg=T.TEXT_BODY) -> ctk.CTkLabel:
    return ctk.CTkLabel(
        parent, text=text,
        font=T.FONT_MICRO, text_color=fg,
        fg_color=bg, corner_radius=20,
        padx=12, pady=4,
    )


class CamaraApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("ShoeVision AI — Control de Cámara")
        self.geometry("1100x700")
        self.minsize(980, 600)
        self.configure(fg_color=T.BG)

        # Variables de control de video heredadas de tu lógica original
        self.cap = None
        self.indice_camara = -1
        self.actualizando = False

        # Configuración de Grid Principal
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_main()
        
        # Iniciar el escaneo automático al levantar la interfaz
        self.after(200, self.probar_camara)

    def _build_sidebar(self):
        side = ctk.CTkFrame(self, width=250, corner_radius=0, fg_color=T.SURFACE_2)
        side.grid(row=0, column=0, sticky="nsew")
        side.grid_propagate(False)

        # Logo / Brand
        brand = ctk.CTkFrame(side, fg_color="transparent")
        brand.pack(fill="x", padx=22, pady=(28, 8))

        logo_box = ctk.CTkFrame(brand, width=44, height=44, corner_radius=12, fg_color=T.GLOW)
        logo_box.pack(side="left")
        logo_box.pack_propagate(False)
        ctk.CTkLabel(logo_box, text="📷", font=("Segoe UI", 16), text_color=T.TEXT_ON_ACCENT).place(relx=0.5, rely=0.5, anchor="center")

        titles = ctk.CTkFrame(brand, fg_color="transparent")
        titles.pack(side="left", padx=(12, 0))
        ctk.CTkLabel(titles, text="CamStream", font=T.FONT_H2, text_color=T.TEXT).pack(anchor="w")
        ctk.CTkLabel(titles, text="Hardware Test", font=T.FONT_MICRO, text_color=T.TEXT_MUTED).pack(anchor="w")

        ctk.CTkFrame(side, height=1, fg_color=T.BORDER).pack(fill="x", padx=20, pady=20)

        # Controles (Solo botón de salida)
        ctk.CTkLabel(side, text="CONTROLES DE VIDEO", font=T.FONT_MICRO, text_color=T.TEXT_LABEL).pack(anchor="w", padx=24)

        self.btn_salir = ctk.CTkButton(
            side, text="🚪  Detener y Salir (Q)",
            font=T.FONT_BODY, height=44, anchor="w",
            fg_color=T.SURFACE, hover_color=T.DANGER_BG,
            text_color=T.DANGER, corner_radius=T.RADIUS_MD,
            border_width=1, border_color=T.BORDER,
            command=self.cerrar_aplicacion
        )
        self.btn_salir.pack(fill="x", padx=20, pady=(14, 8))

        ctk.CTkFrame(side, height=1, fg_color=T.BORDER).pack(fill="x", padx=20, pady=24)

        # Estado del dispositivo
        self.card_info = _card(side, fg_color=T.SURFACE, border_color=T.BORDER_LIGHT, corner_radius=T.RADIUS_MD)
        self.card_info.pack(fill="x", padx=20, pady=4)

        ctk.CTkLabel(self.card_info, text="DISPOSITIVO", font=T.FONT_MICRO, text_color=T.TEXT_LABEL).pack(anchor="w", padx=14, pady=(12, 0))
        self.lbl_nombre_cam = ctk.CTkLabel(self.card_info, text="Buscando hardware...", font=T.FONT_CAPTION, text_color=T.TEXT_HEADING)
        self.lbl_nombre_cam.pack(anchor="w", padx=14, pady=(0, 12))
        
        self.lbl_detalles_cam = ctk.CTkLabel(side, text="Compatible con Iriun, Webcams USB\ny cámaras integradas.", font=T.FONT_MICRO, text_color=T.TEXT_DIM, justify="left")
        self.lbl_detalles_cam.pack(anchor="w", padx=24, pady=12)

        # Footer
        ctk.CTkLabel(side, text="v1.1  ·  IUJO 2026", font=T.FONT_MICRO, text_color=T.TEXT_DIM).pack(side="bottom", pady=20)

    def _build_main(self):
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.grid(row=0, column=1, sticky="nsew")
        main.grid_columnconfigure(0, weight=1)
        main.grid_rowconfigure(1, weight=1)

        # Topbar
        topbar = ctk.CTkFrame(main, fg_color="transparent", height=72)
        topbar.grid(row=0, column=0, sticky="ew", padx=28, pady=(24, 0))
        topbar.grid_columnconfigure(0, weight=1)

        left_tb = ctk.CTkFrame(topbar, fg_color="transparent")
        left_tb.grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(left_tb, text="Prueba de Dispositivo", font=T.FONT_DISPLAY, text_color=T.TEXT).pack(anchor="w")
        ctk.CTkLabel(left_tb, text="Verificación de latencia y encuadre en tiempo real", font=T.FONT_CAPTION, text_color=T.TEXT_BODY).pack(anchor="w", pady=(2, 0))

        right_tb = ctk.CTkFrame(topbar, fg_color="transparent")
        right_tb.grid(row=0, column=1, sticky="e")
        self.badge_estado = _pill(right_tb, "● Verificando", bg=T.SURFACE_3, fg=T.TEXT_MUTED)
        self.badge_estado.pack(side="right")

        # Contenedor del Feed de Video
        video_col = ctk.CTkFrame(main, fg_color="transparent")
        video_col.grid(row=1, column=0, sticky="nsew", padx=28, pady=(20, 24))
        video_col.grid_columnconfigure(0, weight=1)
        video_col.grid_rowconfigure(0, weight=1)

        self.preview_outer = _card(video_col, fg_color=T.PREVIEW_BG, border_color=T.BORDER, corner_radius=T.RADIUS_XL)
        self.preview_outer.grid(row=0, column=0, sticky="nsew")
        self.preview_outer.grid_propagate(False)

        # Label donde se renderizarán los fotogramas
        self.video_label = ctk.CTkLabel(self.preview_outer, text="")
        self.video_label.place(relx=0.5, rely=0.5, anchor="center")

        # Estado Vacío / Cargando
        self.empty_state = ctk.CTkFrame(self.preview_outer, fg_color="transparent")
        self.empty_state.place(relx=0.5, rely=0.5, anchor="center")
        
        self.lbl_icono_empty = ctk.CTkLabel(self.empty_state, text="🔄", font=("Segoe UI", 44))
        self.lbl_icono_empty.pack()
        self.lbl_titulo_empty = ctk.CTkLabel(self.empty_state, text="Conectando flujo de video...", font=T.FONT_H1, text_color=T.TEXT_HEADING)
        self.lbl_titulo_empty.pack(pady=(8, 4))
        self.lbl_desc_empty = ctk.CTkLabel(self.empty_state, text="Por favor, asegúrate de tener tu cámara o Iriun App encendida.", font=T.FONT_BODY, text_color=T.TEXT_BODY)
        self.lbl_desc_empty.pack()

        # Vinculación del teclado para mantener la funcionalidad de la tecla 'q'
        self.bind("<Key>", self._evaluar_tecla_q)

    def probar_camara(self):
        """Lógica original de escaneo automático sin intervención de botones."""
        self.liberar_recursos()
        self.lbl_titulo_empty.configure(text="Escaneando puertos de video...")
        self.lbl_icono_empty.configure(text="🔍")
        self.empty_state.lift()

        camara_encontrada = False
        for i in range(5):
            print(f"Probando cámara en índice {i}...")
            cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
            if cap.isOpened():
                print(f"¡Éxito! Cámara encontrada en el índice {i}")
                self.cap = cap
                self.indice_camara = i
                camara_encontrada = True
                break
            cap.release()

        if camara_encontrada:
            self.lbl_nombre_cam.configure(text=f"Índice {self.indice_camara} activo")
            self.badge_estado.configure(text="● Conectado", fg_color=T.SUCCESS_BG, text_color=T.SUCCESS)
            self.empty_state.lower()
            self.actualizando = True
            self.actualizar_stream()
        else:
            print("Error: No se detectó ninguna cámara (Iriun, integrada o USB).")
            self.lbl_nombre_cam.configure(text="No detectada")
            self.lbl_titulo_empty.configure(text="No se detectó ninguna cámara")
            self.lbl_desc_empty.configure(text="Verifica la conexión USB, drivers o la app Iriun y reinicia el módulo.")
            self.lbl_icono_empty.configure(text="❌")
            self.badge_estado.configure(text="● Desconectado", fg_color=T.DANGER_BG, text_color=T.DANGER)

    def actualizar_stream(self):
        """Captura frame por frame de manera asíncrona sin congelar la ventana."""
        if not self.actualizando or self.cap is None:
            return

        ret, frame = self.cap.read()
        if ret:
            cv2_img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img_pil = Image.fromarray(cv2_img)

            ancho_contenedor = self.preview_outer.winfo_width() - 40
            auto_contenedor = self.preview_outer.winfo_height() - 40
            
            if ancho_contenedor < 100: ancho_contenedor = 640
            if auto_contenedor < 100: auto_contenedor = 480

            img_pil.thumbnail((ancho_contenedor, auto_contenedor))
            
            img_tk = ImageTk.PhotoImage(image=img_pil)
            self.video_label.configure(image=img_tk)
            self.video_label.image = img_tk 
            
            self.after(30, self.actualizar_stream)
        else:
            print("Error: No se puede recibir video (¿cámara desconectada?).")
            self.probar_camara()

    def _evaluar_tecla_q(self, event):
        """Mantiene la funcionalidad original de cerrar el script con la tecla 'q'."""
        if event.char.lower() == 'q':
            self.cerrar_aplicacion()

    def liberar_recursos(self):
        self.actualizando = False
        if self.cap is not None:
            self.cap.release()
        self.cap = None

    def cerrar_aplicacion(self):
        self.liberar_recursos()
        cv2.destroyAllWindows()
        self.destroy()
        sys.exit(0)


if __name__ == "__main__":
    app = CamaraApp()
    app.protocol("WM_DELETE_WINDOW", app.cerrar_aplicacion)
    app.mainloop()
