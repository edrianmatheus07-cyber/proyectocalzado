"""
Detector de Calzado — Interfaz profesional para imágenes estáticas
"""

import os
from tkinter import filedialog
import customtkinter as ctk
from PIL import Image

from validar_modelo import evaluar_foto

# ── Design system ─────────────────────────────────────────────────────────
class T:
    """Tokens de diseño (paleta y tipografía)."""

    # Fondos pasteles
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
    ACCENT_SOFT = "#EDE9FE"
    GLOW = "#7C3AED"
    TEXT_ON_ACCENT = "#FFFFFF"

    # Texto — alto contraste
    TEXT = "#1E1B4B"              # títulos principales
    TEXT_HEADING = "#312E81"       # subtítulos / secciones
    TEXT_BODY = "#4338CA"          # párrafos y cuerpo
    TEXT_LABEL = "#5B21B6"         # etiquetas
    TEXT_MUTED = "#6D28D9"         # texto secundario
    TEXT_DIM = "#64748B"           # hints y placeholders
    TEXT_ACCENT = "#7C3AED"        # badges, enlaces
    TIPS_TEXT = "#4C1D95"          # consejos en tarjeta

    # Semánticos
    SUCCESS = "#047857"
    SUCCESS_BG = "#D1FAE5"
    SUCCESS_BORDER = "#6EE7B7"
    DANGER = "#BE185D"
    DANGER_BG = "#FCE7F3"
    DANGER_BORDER = "#F9A8D4"
    DANGER_HOVER = "#EC4899"
    WARNING = "#B45309"
    WARNING_BG = "#FEF3C7"

    # UI
    RADIUS_SM = 8
    RADIUS_MD = 14
    RADIUS_LG = 20
    RADIUS_XL = 24

    FONT_DISPLAY = ("Segoe UI", 24, "bold")
    FONT_H1 = ("Segoe UI", 19, "bold")
    FONT_H2 = ("Segoe UI", 15, "bold")
    FONT_BODY = ("Segoe UI", 13)
    FONT_CAPTION = ("Segoe UI", 11)
    FONT_MICRO = ("Segoe UI", 10)
    FONT_METRIC = ("Segoe UI", 32, "bold")


ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")


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


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("ShoeVision AI — Clasificador de Calzados")
        self.geometry("1180x740")
        self.minsize(1020, 660)
        self.configure(fg_color=T.BG)

        self.ruta = ""
        self.ctk_image = None

        # Configuración de grid principal
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_main()

    def _build_sidebar(self):
        side = ctk.CTkFrame(
            self, width=248, corner_radius=0,
            fg_color=T.SURFACE_2, border_width=0,
        )
        side.grid(row=0, column=0, sticky="nsew")
        side.grid_propagate(False)

        # Logo
        brand = ctk.CTkFrame(side, fg_color="transparent")
        brand.pack(fill="x", padx=22, pady=(28, 8))

        logo_box = ctk.CTkFrame(brand, width=44, height=44, corner_radius=12, fg_color=T.GLOW)
        logo_box.pack(side="left")
        logo_box.pack_propagate(False)
        ctk.CTkLabel(logo_box, text="SV", font=("Segoe UI", 16, "bold"), text_color=T.TEXT_ON_ACCENT).place(
            relx=0.5, rely=0.5, anchor="center"
        )

        titles = ctk.CTkFrame(brand, fg_color="transparent")
        titles.pack(side="left", padx=(12, 0))
        ctk.CTkLabel(titles, text="ShoeVision", font=T.FONT_H2, text_color=T.TEXT).pack(anchor="w")
        ctk.CTkLabel(titles, text="AI Analyzer", font=T.FONT_MICRO, text_color=T.TEXT_MUTED).pack(anchor="w")

        ctk.CTkFrame(side, height=1, fg_color=T.BORDER).pack(fill="x", padx=20, pady=20)

        ctk.CTkLabel(
            side, text="ACCIONES DE ARCHIVO", font=T.FONT_MICRO,
            text_color=T.TEXT_LABEL,
        ).pack(anchor="w", padx=24)

        # Botón Examinar
        self.btn_examinar = ctk.CTkButton(
            side, text="   Cargar imagen",
            font=T.FONT_BODY, height=46, anchor="w",
            fg_color=T.GLOW, hover_color=T.ACCENT_HOVER,
            text_color=T.TEXT_ON_ACCENT, corner_radius=T.RADIUS_MD,
            command=self.seleccionar_archivo,
        )
        self.btn_examinar.pack(fill="x", padx=20, pady=(14, 8))

        # Botón Evaluar
        self.btn_analizar = ctk.CTkButton(
            side, text="   Evaluar imagen",
            font=T.FONT_BODY, height=46, anchor="w",
            fg_color=T.SURFACE, hover_color=T.SURFACE_3,
            text_color=T.TEXT_HEADING, corner_radius=T.RADIUS_MD,
            border_width=1, border_color=T.BORDER,
            command=self.evaluar,
        )
        self.btn_analizar.pack(fill="x", padx=20, pady=4)

        ctk.CTkFrame(side, height=1, fg_color=T.BORDER).pack(fill="x", padx=20, pady=24)

        # Info del modelo
        info = _card(side, fg_color=T.SURFACE, border_color=T.BORDER_LIGHT, corner_radius=T.RADIUS_MD)
        info.pack(fill="x", padx=20, pady=4)

        ctk.CTkLabel(info, text="MODELO", font=T.FONT_MICRO, text_color=T.TEXT_LABEL).pack(
            anchor="w", padx=14, pady=(12, 0)
        )
        ctk.CTkLabel(
            info, text="MobileNetV2 + ONNX",
            font=T.FONT_CAPTION, text_color=T.TEXT_HEADING,
        ).pack(anchor="w", padx=14)
        ctk.CTkLabel(
            info, text="Evaluación por Archivo",
            font=T.FONT_MICRO, text_color=T.TEXT_MUTED).pack(anchor="w", padx=14, pady=(2, 12))

        # Footer discreto
        ctk.CTkLabel(
            side, text="v1.1  ·  IUJO 2026",
            font=T.FONT_MICRO, text_color=T.TEXT_DIM,
        ).pack(side="bottom", pady=20)

    def _build_main(self):
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.grid(row=0, column=1, sticky="nsew")
        main.grid_columnconfigure(0, weight=1)
        main.grid_rowconfigure(1, weight=1)

        # Top bar
        topbar = ctk.CTkFrame(main, fg_color="transparent", height=72)
        topbar.grid(row=0, column=0, sticky="ew", padx=28, pady=(24, 0))
        topbar.grid_columnconfigure(0, weight=1)

        left_tb = ctk.CTkFrame(topbar, fg_color="transparent")
        left_tb.grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(left_tb, text="Panel de análisis", font=T.FONT_DISPLAY, text_color=T.TEXT).pack(anchor="w")
        ctk.CTkLabel(
            left_tb, text="Clasificación de imágenes estáticas de calzado",
            font=T.FONT_CAPTION, text_color=T.TEXT_BODY,
        ).pack(anchor="w", pady=(2, 0))

        right_tb = ctk.CTkFrame(topbar, fg_color="transparent")
        right_tb.grid(row=0, column=1, sticky="e")
        self.badge_estado = _pill(right_tb, "● Sistema listo", bg=T.SUCCESS_BG, fg=T.SUCCESS)
        self.badge_estado.pack(side="right")

        # Contenido principal: visor + métricas
        content = ctk.CTkFrame(main, fg_color="transparent")
        content.grid(row=1, column=0, sticky="nsew", padx=28, pady=(20, 0))
        content.grid_columnconfigure(0, weight=3)
        content.grid_columnconfigure(1, weight=1)
        content.grid_rowconfigure(0, weight=1)

        # Visor (Izquierda)
        preview_col = ctk.CTkFrame(content, fg_color="transparent")
        preview_col.grid(row=0, column=0, sticky="nsew", padx=(0, 14))

        prev_header = ctk.CTkFrame(preview_col, fg_color="transparent")
        prev_header.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(prev_header, text="Visor de Imagen", font=T.FONT_H2, text_color=T.TEXT_HEADING).pack(side="left")

        self.preview_outer = _card(preview_col, fg_color=T.PREVIEW_BG, border_color=T.BORDER, corner_radius=T.RADIUS_XL)
        self.preview_outer.pack(fill="both", expand=True)
        self.preview_outer.pack_propagate(False)

        # Placeholder vacío
        self.empty_state = ctk.CTkFrame(self.preview_outer, fg_color="transparent")
        self.empty_state.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(self.empty_state, text="◎", font=("Segoe UI", 48), text_color=T.ACCENT_HOVER).pack()
        ctk.CTkLabel(self.empty_state, text="Sin imagen seleccionada", font=T.FONT_H1, text_color=T.TEXT_HEADING).pack(pady=(8, 4))
        ctk.CTkLabel(self.empty_state, text="Sube un archivo desde la barra lateral para comenzar", font=T.FONT_BODY, text_color=T.TEXT_BODY).pack()

        self.thumb_label = ctk.CTkLabel(self.preview_outer, text="", fg_color="transparent")
        self.thumb_label.pack(expand=True, fill="both", padx=4, pady=4)

        # Banner inferior para logs/rutas
        self.banner = _card(preview_col, fg_color=T.SURFACE_2, border_color=T.BORDER, corner_radius=T.RADIUS_MD)
        self.banner.pack(fill="x", pady=(12, 0))
        self.lbl_banner = ctk.CTkLabel(
            self.banner, text="Esperando archivo...", font=T.FONT_BODY, text_color=T.TEXT_BODY,
            wraplength=620, justify="left"
        )
        self.lbl_banner.pack(anchor="w", padx=16, pady=12)

        # Panel Métricas (Derecha)
        metrics_col = ctk.CTkFrame(content, fg_color="transparent")
        metrics_col.grid(row=0, column=1, sticky="nsew")

        ctk.CTkLabel(metrics_col, text="Resultados", font=T.FONT_H2, text_color=T.TEXT_HEADING).pack(anchor="w", pady=(0, 10))

        # Tarjeta Confianza
        self.card_conf = _card(metrics_col, fg_color=T.SURFACE, border_color=T.BORDER)
        self.card_conf.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(self.card_conf, text="NIVEL DE CERTEZA", font=T.FONT_MICRO, text_color=T.TEXT_LABEL).pack(anchor="w", padx=18, pady=(16, 0))
        self.lbl_conf_grande = ctk.CTkLabel(self.card_conf, text="—", font=T.FONT_METRIC, text_color=T.TEXT)
        self.lbl_conf_grande.pack(anchor="w", padx=18)

        self.progress_bar = ctk.CTkProgressBar(self.card_conf, height=8, corner_radius=4, fg_color=T.SURFACE_2, progress_color=T.GLOW)
        self.progress_bar.set(0)
        self.progress_bar.pack(fill="x", padx=18, pady=(4, 18))

        # Tarjeta Clasificación final
        self.card_class = _card(metrics_col, fg_color=T.SURFACE, border_color=T.BORDER)
        self.card_class.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(self.card_class, text="CLASIFICACIÓN", font=T.FONT_MICRO, text_color=T.TEXT_LABEL).pack(anchor="w", padx=18, pady=(14, 0))
        self.lbl_resultado_final = ctk.CTkLabel(self.card_class, text="—", font=T.FONT_H1, text_color=T.TEXT, wraplength=220, justify="left")
        self.lbl_resultado_final.pack(anchor="w", padx=18, pady=(4, 16))

        # Espacio inferior del Layout
        ctk.CTkFrame(main, fg_color="transparent", height=40).grid(row=2, column=0, sticky="ew")

    def _mostrar_empty(self, visible: bool):
        if visible:
            self.empty_state.lift()
        else:
            self.empty_state.lower()

    def seleccionar_archivo(self):
        ruta = filedialog.askopenfilename(
            title="Seleccionar imagen",
            filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.bmp *.gif")],
        )
        if not ruta:
            return
        
        self.ruta = ruta
        
        # Resetear campos y estados visuales
        self.lbl_resultado_final.configure(text="—", text_color=T.TEXT)
        self.lbl_conf_grande.configure(text="—", text_color=T.TEXT)
        self.progress_bar.set(0)
        self.preview_outer.configure(border_color=T.BORDER)
        self.badge_estado.configure(text="● Imagen cargada", fg_color=T.SURFACE_3, text_color=T.TEXT_ACCENT)

        # Mostrar preview adaptativo
        img = Image.open(ruta)
        img.thumbnail((740, 400))
        self.ctk_image = ctk.CTkImage(light_image=img, dark_image=img, size=img.size)
        self.thumb_label.configure(image=self.ctk_image, text="")
        self._mostrar_empty(False)
        
        self.lbl_banner.configure(text=f"Archivo: {os.path.basename(ruta)}. Listo para evaluar.")

    def evaluar(self):
        if not self.ruta:
            self.lbl_banner.configure(text="Selecciona una imagen primero.", text_color=T.DANGER)
            return

        es_calzado, confianza = evaluar_foto(self.ruta)
        
        if es_calzado is None:
            self.lbl_banner.configure(text="Error al procesar la imagen.", text_color=T.DANGER)
            return

        if es_calzado:
            texto_resultado = "Es un calzado"
            color = T.SUCCESS
            borde = T.SUCCESS_BORDER
            bg_badge = T.SUCCESS_BG
            texto_estado = "● Identificado"
        else:
            texto_resultado = "No es un calzado"
            color = T.DANGER
            borde = T.DANGER_BORDER
            bg_badge = T.DANGER_BG
            texto_estado = "● No coincide"

        # Actualizar componentes visuales de las métricas
        self.lbl_resultado_final.configure(text=texto_resultado, text_color=color)
        self.lbl_conf_grande.configure(text=f"{confianza:.1f}%", text_color=color)
        self.progress_bar.configure(progress_color=color)
        self.progress_bar.set(confianza / 100.0)
        self.preview_outer.configure(border_color=borde)
        
        self.badge_estado.configure(text=texto_estado, fg_color=bg_badge, text_color=color)
        self.lbl_banner.configure(text=f"Análisis completado: {texto_resultado} ({confianza:.1f}% de certeza).")


if __name__ == "__main__":
    App().mainloop()
if __name__ == "__main__":
    App().mainloop()
