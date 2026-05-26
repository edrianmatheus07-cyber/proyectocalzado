"""
Detector de Calzado — Interfaz profesional
Detección en vivo con ventana de análisis configurable (3–5 s).
"""

import os
import time

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    cv2 = None
    CV2_AVAILABLE = False

from tkinter import filedialog
import customtkinter as ctk
from PIL import Image, ImageDraw

from validar_modelo import VentanaAnalisis, evaluar_foto, evaluar_frame

# ── Detección ─────────────────────────────────────────────────────────────
SEGUNDOS_ANALISIS = 4.0
INTERVALO_VIDEO_MS = 33
INTERVALO_INFERENCIA_MS = 180

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

    # Texto — alto contraste (cada nivel con color distinto)
    TEXT = "#1E1B4B"              # títulos principales
    TEXT_HEADING = "#312E81"       # subtítulos / secciones
    TEXT_BODY = "#4338CA"          # párrafos y cuerpo
    TEXT_LABEL = "#5B21B6"         # etiquetas (MÉTRICAS, MODELO…)
    TEXT_MUTED = "#6D28D9"         # texto secundario
    TEXT_DIM = "#64748B"           # hints y placeholders (gris legible)
    TEXT_ACCENT = "#7C3AED"        # timer, badges, enlaces
    TIPS_TEXT = "#4C1D95"          # consejos en tarjeta

    # Semánticos — fondos pastel + texto oscuro legible
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

    FONT_DISPLAY = ("Segoe UI", 26, "bold")
    FONT_H1 = ("Segoe UI", 20, "bold")
    FONT_H2 = ("Segoe UI", 15, "bold")
    FONT_BODY = ("Segoe UI", 13)
    FONT_CAPTION = ("Segoe UI", 11)
    FONT_MICRO = ("Segoe UI", 10)
    FONT_METRIC = ("Segoe UI", 32, "bold")
    FONT_METRIC_SM = ("Segoe UI", 18, "bold")


ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")


def abrir_camara():
    if not CV2_AVAILABLE:
        return None, "OpenCV no está instalado. Ejecuta: pip install opencv-python"

    backends = []
    if os.name == "nt":
        backends.extend([cv2.CAP_DSHOW, cv2.CAP_MSMF])
    backends.append(0)

    for backend in backends:
        for indice in range(6):
            cap = cv2.VideoCapture(indice, backend) if backend else cv2.VideoCapture(indice)
            if not cap.isOpened():
                cap.release()
                continue
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            ok = any(cap.read()[0] for _ in range(8))
            if ok:
                print(f"✅ Cámara — índice {indice}, backend {backend}")
                return cap, None
            cap.release()

    return None, (
        "No se detectó ninguna cámara.\n"
        "Conecta tu webcam o activa Iriun Webcam."
    )


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


def _frame_con_esquinas(img: Image.Image, color=(167, 139, 250)) -> Image.Image:
    """Dibuja un marco de escaneo sutil sobre el frame."""
    w, h = img.size
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    L, t = int(w * 0.06), int(h * 0.08)
    r, b = w - L, h - t
    esp, g = 28, 3
    rgba = (*color, 200)
    for x1, y1, x2, y2 in [
        (L, t, L + esp, t), (L, t, L, t + esp),
        (r - esp, t, r, t), (r, t, r, t + esp),
        (L, b - esp, L, b), (L, b - esp, L + esp, b),
        (r - esp, b, r, b), (r - esp, b, r, b - esp),
    ]:
        draw.line([(x1, y1), (x2, y2)], fill=rgba, width=g)
    base = img.convert("RGBA")
    # Viñeta suave (tono lavanda, acorde al tema pastel)
    vig = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    vd = ImageDraw.Draw(vig)
    for i in range(10):
        alpha = int(8 + i * 2)
        m = i * 3
        vd.rectangle([m, m, w - m, h - m], outline=(196, 181, 253, alpha))
    out = Image.alpha_composite(base, vig)
    out = Image.alpha_composite(out, overlay)
    return out.convert("RGB")


class AppModerna(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("ShoeVision AI — Detector de Calzado")
        self.geometry("1180x780")
        self.minsize(1020, 700)
        self.configure(fg_color=T.BG)

        self.ruta_actual = ""
        self.ctk_image = None
        self.modo = "inicio"
        self.cap = None
        self.camara_activa = False
        self.frame_actual = None
        self._ultima_inferencia = 0.0
        self.ventana_analisis = VentanaAnalisis(SEGUNDOS_ANALISIS)
        self._resultado_estable = (None, None)
        self._scan_overlay = True

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_main()
        self.protocol("WM_DELETE_WINDOW", self.cerrar_aplicacion)

    # ══════════════════════════════════════════════════════════════════════
    #  LAYOUT
    # ══════════════════════════════════════════════════════════════════════

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

        logo_box = ctk.CTkFrame(brand, width=44, height=44, corner_radius=12, fg_color=T.ACCENT)
        logo_box.pack(side="left")
        logo_box.pack_propagate(False)
        ctk.CTkLabel(logo_box, text="SV", font=("Segoe UI", 16, "bold"), text_color=T.TEXT_ON_ACCENT).place(
            relx=0.5, rely=0.5, anchor="center"
        )

        titles = ctk.CTkFrame(brand, fg_color="transparent")
        titles.pack(side="left", padx=(12, 0))
        ctk.CTkLabel(titles, text="ShoeVision", font=T.FONT_H2, text_color=T.TEXT).pack(anchor="w")
        ctk.CTkLabel(titles, text="AI Detector", font=T.FONT_MICRO, text_color=T.TEXT_MUTED).pack(anchor="w")

        ctk.CTkFrame(side, height=1, fg_color=T.BORDER).pack(fill="x", padx=20, pady=20)

        ctk.CTkLabel(
            side, text="FUENTE DE ENTRADA", font=T.FONT_MICRO,
            text_color=T.TEXT_LABEL,
        ).pack(anchor="w", padx=24)

        self.btn_camara = ctk.CTkButton(
            side, text="  Escaneo en vivo",
            font=T.FONT_BODY, height=46, anchor="w",
            fg_color=T.ACCENT_HOVER, hover_color=T.GLOW,
            text_color=T.TEXT_ON_ACCENT,
            corner_radius=T.RADIUS_MD,
            command=self.toggle_camara,
        )
        self.btn_camara.pack(fill="x", padx=20, pady=(14, 8))

        self.btn_examinar = ctk.CTkButton(
            side, text="  Cargar imagen",
            font=T.FONT_BODY, height=46, anchor="w",
            fg_color=T.SURFACE_2, hover_color=T.SURFACE_3,
            text_color=T.TEXT_HEADING, corner_radius=T.RADIUS_MD,
            border_width=1, border_color=T.BORDER,
            command=self.seleccionar_archivo,
        )
        self.btn_examinar.pack(fill="x", padx=20, pady=4)

        self.btn_analizar = ctk.CTkButton(
            side, text="  Analizar imagen",
            font=T.FONT_BODY, height=46, anchor="w",
            state="disabled",
            fg_color=T.SURFACE_3, hover_color=T.BORDER_LIGHT,
            text_color=T.TEXT_DIM, corner_radius=T.RADIUS_MD,
            command=self.evaluar_archivo,
        )
        self.btn_analizar.pack(fill="x", padx=20, pady=4)

        ctk.CTkFrame(side, height=1, fg_color=T.BORDER).pack(fill="x", padx=20, pady=24)

        # Info modelo
        info = _card(side, fg_color=T.SURFACE_2, corner_radius=T.RADIUS_MD)
        info.pack(fill="x", padx=20, pady=4)

        ctk.CTkLabel(info, text="Modelo", font=T.FONT_MICRO, text_color=T.TEXT_LABEL).pack(
            anchor="w", padx=14, pady=(12, 0)
        )
        ctk.CTkLabel(
            info, text="MobileNetV2 + ONNX",
            font=T.FONT_CAPTION, text_color=T.TEXT_HEADING,
        ).pack(anchor="w", padx=14)
        ctk.CTkLabel(
            info, text="224 × 224  ·  Binario",
            font=T.FONT_MICRO, text_color=T.TEXT_BODY,
        ).pack(anchor="w", padx=14, pady=(2, 12))

        # Tips
        tips = _card(side, fg_color=T.ACCENT_SOFT, border_color=T.ACCENT)
        tips.pack(fill="x", padx=20, pady=(16, 0))

        ctk.CTkLabel(
            tips, text="Consejo",
            font=T.FONT_MICRO, text_color=T.TEXT_ACCENT,
        ).pack(anchor="w", padx=14, pady=(12, 2))
        ctk.CTkLabel(
            tips,
            text=f"Mantén el calzado centrado.\nEl análisis toma ~{SEGUNDOS_ANALISIS:.0f}s.",
            font=T.FONT_MICRO, text_color=T.TIPS_TEXT,
            justify="left", wraplength=190,
        ).pack(anchor="w", padx=14, pady=(0, 12))

        # Footer sidebar
        ctk.CTkLabel(
            side, text="v1.0  ·  IUJO 2026",
            font=T.FONT_MICRO, text_color=T.TEXT_DIM,
        ).pack(side="bottom", pady=20)

    def _build_main(self):
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.grid(row=0, column=1, sticky="nsew", padx=(0, 0))
        main.grid_columnconfigure(0, weight=1)
        main.grid_rowconfigure(1, weight=1)

        # Top bar
        topbar = ctk.CTkFrame(main, fg_color="transparent", height=72)
        topbar.grid(row=0, column=0, sticky="ew", padx=28, pady=(24, 0))
        topbar.grid_columnconfigure(0, weight=1)

        left_tb = ctk.CTkFrame(topbar, fg_color="transparent")
        left_tb.grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(left_tb, text="Panel de detección", font=T.FONT_DISPLAY, text_color=T.TEXT).pack(
            anchor="w"
        )
        ctk.CTkLabel(
            left_tb,
            text="Clasificación inteligente de calzado en tiempo real",
            font=T.FONT_CAPTION, text_color=T.TEXT_BODY,
        ).pack(anchor="w", pady=(2, 0))

        right_tb = ctk.CTkFrame(topbar, fg_color="transparent")
        right_tb.grid(row=0, column=1, sticky="e")

        self.badge_modelo = _pill(right_tb, "ONNX Runtime", bg=T.ACCENT_SOFT, fg=T.TEXT_ACCENT)
        self.badge_modelo.pack(side="right", padx=(8, 0))
        self.badge_estado = _pill(right_tb, "● Listo", bg=T.SUCCESS_BG, fg=T.SUCCESS)
        self.badge_estado.pack(side="right")

        # Contenido: preview + métricas
        content = ctk.CTkFrame(main, fg_color="transparent")
        content.grid(row=1, column=0, sticky="nsew", padx=28, pady=(20, 0))
        content.grid_columnconfigure(0, weight=3)
        content.grid_columnconfigure(1, weight=1)
        content.grid_rowconfigure(0, weight=1)

        # ── Preview (izquierda) ──
        preview_col = ctk.CTkFrame(content, fg_color="transparent")
        preview_col.grid(row=0, column=0, sticky="nsew", padx=(0, 14))

        prev_header = ctk.CTkFrame(preview_col, fg_color="transparent")
        prev_header.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(prev_header, text="Visor", font=T.FONT_H2, text_color=T.TEXT).pack(side="left")
        self.live_badge = _pill(prev_header, "En espera", bg=T.SURFACE_2)
        self.live_badge.pack(side="right")

        self.preview_outer = _card(preview_col, fg_color=T.PREVIEW_BG, corner_radius=T.RADIUS_XL)
        self.preview_outer.pack(fill="both", expand=True)
        self.preview_outer.pack_propagate(False)

        # Placeholder vacío
        self.empty_state = ctk.CTkFrame(self.preview_outer, fg_color="transparent")
        self.empty_state.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(
            self.empty_state, text="◎",
            font=("Segoe UI", 48), text_color=T.BORDER_LIGHT,
        ).pack()
        ctk.CTkLabel(
            self.empty_state, text="Sin señal de video",
            font=T.FONT_H2, text_color=T.TEXT_MUTED,
        ).pack(pady=(8, 4))
        ctk.CTkLabel(
            self.empty_state,
            text="Inicia el escaneo en vivo o carga una imagen",
            font=T.FONT_CAPTION, text_color=T.TEXT_DIM,
        ).pack()

        self.thumb_label = ctk.CTkLabel(self.preview_outer, text="", fg_color="transparent")
        self.thumb_label.pack(expand=True, fill="both", padx=4, pady=4)

        # Barra inferior del visor
        scan_bar_card = _card(preview_col, fg_color=T.SURFACE_2, corner_radius=T.RADIUS_MD)
        scan_bar_card.pack(fill="x", pady=(12, 0))

        row_lbl = ctk.CTkFrame(scan_bar_card, fg_color="transparent")
        row_lbl.pack(fill="x", padx=16, pady=(12, 4))

        ctk.CTkLabel(
            row_lbl, text="Ventana de análisis",
            font=T.FONT_CAPTION, text_color=T.TEXT_MUTED,
        ).pack(side="left")
        self.lbl_timer = ctk.CTkLabel(
            row_lbl, text=f"0.0 / {SEGUNDOS_ANALISIS:.0f}s",
            font=T.FONT_CAPTION, text_color=T.GLOW,
        )
        self.lbl_timer.pack(side="right")

        self.barra_escaneo = ctk.CTkProgressBar(
            scan_bar_card, height=6, corner_radius=4,
            fg_color=T.SURFACE_3, progress_color=T.ACCENT_HOVER,
        )
        self.barra_escaneo.set(0)
        self.barra_escaneo.pack(fill="x", padx=16, pady=(0, 14))

        # Banner estado
        self.banner = _card(preview_col, fg_color=T.SURFACE_2, corner_radius=T.RADIUS_MD)
        self.banner.pack(fill="x", pady=(10, 0))
        self.lbl_banner = ctk.CTkLabel(
            self.banner,
            text="Selecciona una fuente de entrada para comenzar el análisis.",
            font=T.FONT_CAPTION, text_color=T.TEXT_MUTED,
            wraplength=620, justify="left",
        )
        self.lbl_banner.pack(anchor="w", padx=16, pady=12)

        # ── Panel métricas (derecha) ──
        metrics_col = ctk.CTkFrame(content, fg_color="transparent")
        metrics_col.grid(row=0, column=1, sticky="nsew")

        ctk.CTkLabel(metrics_col, text="Métricas", font=T.FONT_H2, text_color=T.TEXT).pack(
            anchor="w", pady=(0, 10)
        )

        # Tarjeta confianza grande
        self.card_conf = _card(metrics_col, fg_color=T.SURFACE_2)
        self.card_conf.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            self.card_conf, text="NIVEL DE CONFIANZA",
            font=T.FONT_MICRO, text_color=T.TEXT_DIM,
        ).pack(anchor="w", padx=18, pady=(16, 0))

        self.lbl_conf_grande = ctk.CTkLabel(
            self.card_conf, text="—",
            font=T.FONT_METRIC, text_color=T.TEXT,
        )
        self.lbl_conf_grande.pack(anchor="w", padx=18)

        self.progress_bar = ctk.CTkProgressBar(
            self.card_conf, height=8, corner_radius=4,
            fg_color=T.SURFACE_3, progress_color=T.ACCENT_HOVER,
        )
        self.progress_bar.set(0)
        self.progress_bar.pack(fill="x", padx=18, pady=(4, 18))

        # Tarjeta clasificación
        self.card_class = _card(metrics_col, fg_color=T.SURFACE_2)
        self.card_class.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            self.card_class, text="CLASIFICACIÓN",
            font=T.FONT_MICRO, text_color=T.TEXT_DIM,
        ).pack(anchor="w", padx=18, pady=(14, 0))

        self.lbl_resultado_final = ctk.CTkLabel(
            self.card_class, text="—",
            font=T.FONT_H1, text_color=T.TEXT_MUTED,
            wraplength=220, justify="left",
        )
        self.lbl_resultado_final.pack(anchor="w", padx=18, pady=(4, 4))

        self.lbl_probabilidad = ctk.CTkLabel(
            self.card_class, text="Esperando análisis",
            font=T.FONT_CAPTION, text_color=T.TEXT_DIM,
        )
        self.lbl_probabilidad.pack(anchor="w", padx=18, pady=(0, 16))

        # Mini stats
        for titulo, attr in [("Modo", "lbl_modo"), ("Muestras", "lbl_muestras"), ("Latencia", "lbl_latencia")]:
            row = _card(metrics_col, fg_color=T.SURFACE, corner_radius=T.RADIUS_SM)
            row.pack(fill="x", pady=3)
            inner = ctk.CTkFrame(row, fg_color="transparent")
            inner.pack(fill="x", padx=14, pady=10)
            ctk.CTkLabel(inner, text=titulo, font=T.FONT_MICRO, text_color=T.TEXT_DIM).pack(side="left")
            lbl = ctk.CTkLabel(inner, text="—", font=T.FONT_CAPTION, text_color=T.TEXT)
            lbl.pack(side="right")
            setattr(self, attr, lbl)

        self.lbl_modo.configure(text="Inactivo")
        self.lbl_muestras.configure(text="0")
        self.lbl_latencia.configure(text=f"~{INTERVALO_INFERENCIA_MS}ms")

        # Resultado inferior (full width)
        result_row = ctk.CTkFrame(main, fg_color="transparent")
        result_row.grid(row=2, column=0, sticky="ew", padx=28, pady=(16, 24))

        self.result_strip = _card(result_row, fg_color=T.SURFACE_2, corner_radius=T.RADIUS_MD)
        self.result_strip.pack(fill="x")

        strip_inner = ctk.CTkFrame(self.result_strip, fg_color="transparent")
        strip_inner.pack(fill="x", padx=20, pady=14)

        ctk.CTkLabel(
            strip_inner, text="Estado del sistema",
            font=T.FONT_MICRO, text_color=T.TEXT_DIM,
        ).pack(side="left")

        self.lbl_strip = ctk.CTkLabel(
            strip_inner,
            text="Listo para detectar calzado",
            font=T.FONT_BODY, text_color=T.TEXT_MUTED,
        )
        self.lbl_strip.pack(side="right")

    # ══════════════════════════════════════════════════════════════════════
    #  UI HELPERS
    # ══════════════════════════════════════════════════════════════════════

    def _set_banner(self, texto: str, bg=T.SURFACE_2, fg=T.TEXT_MUTED):
        self.banner.configure(fg_color=bg, border_color=T.BORDER)
        self.lbl_banner.configure(text=texto, text_color=fg)
        self.lbl_strip.configure(text=texto[:80], text_color=fg)

    def _set_live_badge(self, texto: str, bg=T.SURFACE_2, fg=T.TEXT_MUTED):
        self.live_badge.configure(text=texto, fg_color=bg, text_color=fg)

    def _set_badge_estado(self, texto: str, fg=T.SUCCESS):
        self.badge_estado.configure(text=texto, text_color=fg)

    def _set_borde_preview(self, color: str):
        self.preview_outer.configure(border_color=color)

    def _mostrar_empty(self, visible: bool):
        if visible:
            self.empty_state.lift()
        else:
            self.empty_state.lower()

    def resetear_resultados(self):
        self.progress_bar.set(0)
        self.barra_escaneo.set(0)
        self.lbl_timer.configure(text=f"0.0 / {SEGUNDOS_ANALISIS:.0f}s")
        self.lbl_conf_grande.configure(text="—", text_color=T.TEXT_DIM)
        self.lbl_probabilidad.configure(text="Esperando análisis", text_color=T.TEXT_DIM)
        self.lbl_resultado_final.configure(text="—", text_color=T.TEXT_MUTED)
        self.lbl_muestras.configure(text="0")
        self._set_borde_preview(T.BORDER)
        self.progress_bar.configure(progress_color=T.ACCENT_HOVER)

    def mostrar_resultado(self, es_calzado: bool, confianza: float, estable: bool = False):
        if es_calzado:
            color = T.SUCCESS
            texto = "Calzado"
            sub = "Objeto identificado como calzado"
            borde = T.SUCCESS_BORDER
            bg_banner = T.SUCCESS_BG
        else:
            color = T.DANGER
            texto = "No es calzado"
            sub = "El objeto no coincide con la clase"
            borde = T.DANGER_BORDER
            bg_banner = T.DANGER_BG

        prefijo = "Confirmado" if estable else "Analizando"
        self.lbl_resultado_final.configure(text=texto, text_color=color)
        self.lbl_probabilidad.configure(text=sub, text_color=T.TEXT_MUTED)
        self.lbl_conf_grande.configure(text=f"{confianza:.0f}%", text_color=color)
        self.lbl_conf_grande.pack_configure()
        self.progress_bar.configure(progress_color=color)
        self.progress_bar.set(confianza / 100.0)
        self._set_borde_preview(borde)

        self._set_banner(
            f"{prefijo}: {texto} — {confianza:.1f}% de confianza.",
            bg=bg_banner, fg=color,
        )
        self._set_live_badge(
            f"{'✓' if es_calzado else '✗'} {prefijo}",
            bg=T.SURFACE_3, fg=color,
        )

    # ══════════════════════════════════════════════════════════════════════
    #  CÁMARA
    # ══════════════════════════════════════════════════════════════════════

    def toggle_camara(self):
        if self.camara_activa:
            self.apagar_camara()
            return

        if not CV2_AVAILABLE:
            self._set_banner("Instala opencv-python para usar la cámara.", bg=T.DANGER_BG, fg=T.DANGER)
            return

        cap, error = abrir_camara()
        if cap is None:
            self._mostrar_empty(True)
            self.thumb_label.configure(text="")
            self._set_banner(error.splitlines()[0], bg=T.DANGER_BG, fg=T.DANGER)
            return

        self.cap = cap
        self.camara_activa = True
        self.modo = "camara"
        self.ruta_actual = ""
        self.ventana_analisis.reiniciar()
        self.resetear_resultados()
        self._mostrar_empty(False)

        self.btn_camara.configure(
            text="  Detener escaneo",
            fg_color=T.DANGER, hover_color=T.DANGER_HOVER,
            text_color=T.TEXT_ON_ACCENT,
        )
        self.btn_analizar.configure(state="disabled", text_color=T.TEXT_DIM)
        self.lbl_modo.configure(text="Cámara en vivo")
        self._set_badge_estado("● En vivo", T.DANGER)
        self._set_live_badge("● Escaneando", bg=T.ACCENT_SOFT, fg=T.GLOW)
        self._set_banner(
            f"Cámara activa. Acerca el calzado — análisis en ventanas de {SEGUNDOS_ANALISIS:.0f}s.",
            bg=T.ACCENT_SOFT, fg=T.TIPS_TEXT,
        )
        self._loop_camara()

    def _loop_camara(self):
        if not self.camara_activa or self.cap is None:
            return

        t0 = time.time()
        ret, frame = self.cap.read()
        if ret:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.frame_actual = frame_rgb
            self._mostrar_frame(frame_rgb)
            self._procesar_deteccion_en_vivo(frame_rgb)
            lat = (time.time() - t0) * 1000
            self.lbl_latencia.configure(text=f"{lat:.0f}ms")
        else:
            self._set_live_badge("Sin señal", bg=T.WARNING_BG, fg=T.WARNING)

        self.after(INTERVALO_VIDEO_MS, self._loop_camara)

    def _mostrar_frame(self, frame_rgb):
        img = Image.fromarray(frame_rgb)
        if self._scan_overlay and self.camara_activa:
            img = _frame_con_esquinas(img)
        img.thumbnail((780, 440), Image.Resampling.LANCZOS)
        self.ctk_image = ctk.CTkImage(light_image=img, dark_image=img, size=img.size)
        self.thumb_label.configure(image=self.ctk_image, text="")
        self._mostrar_empty(False)

    def _procesar_deteccion_en_vivo(self, frame_rgb):
        ahora = time.time()
        if (ahora - self._ultima_inferencia) * 1000 < INTERVALO_INFERENCIA_MS:
            return
        self._ultima_inferencia = ahora

        _, _, score = evaluar_frame(frame_rgb, verbose=False)
        if score is None:
            return

        self.ventana_analisis.agregar(score)
        self.lbl_muestras.configure(text=str(self.ventana_analisis.cantidad_muestras))

        progreso = self.ventana_analisis.progreso
        seg = self.ventana_analisis.segundos_acumulados
        self.barra_escaneo.set(progreso)
        self.lbl_timer.configure(text=f"{seg:.1f} / {SEGUNDOS_ANALISIS:.0f}s")

        prev_es, prev_conf = self.ventana_analisis.vista_previa()
        if prev_es is not None and prev_conf is not None:
            self.mostrar_resultado(prev_es, prev_conf, estable=False)

        if self.ventana_analisis.listo:
            es, conf, _ = self.ventana_analisis.resultado()
            if es is not None and conf is not None:
                self._resultado_estable = (es, conf)
                self.mostrar_resultado(es, conf, estable=True)
                self._set_badge_estado("● Confirmado", T.SUCCESS if es else T.DANGER)
            self.ventana_analisis.reiniciar()
            self.barra_escaneo.set(0)
            self.lbl_muestras.configure(text="0")

    def apagar_camara(self):
        self.camara_activa = False
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        self.frame_actual = None
        self.ventana_analisis.reiniciar()

        self.btn_camara.configure(
            text="  Escaneo en vivo",
            fg_color=T.ACCENT_HOVER, hover_color=T.GLOW,
            text_color=T.TEXT_ON_ACCENT,
        )
        if self.modo == "camara":
            self.modo = "inicio"
            self.btn_analizar.configure(state="disabled")
            self.thumb_label.configure(image="", text="")
            self._mostrar_empty(True)
        self.lbl_modo.configure(text="Inactivo")
        self._set_badge_estado("● Listo", T.SUCCESS)
        self._set_live_badge("En espera")
        self._set_banner("Selecciona una fuente de entrada para comenzar el análisis.")

    # ══════════════════════════════════════════════════════════════════════
    #  ARCHIVO
    # ══════════════════════════════════════════════════════════════════════

    def seleccionar_archivo(self):
        if self.camara_activa:
            self.apagar_camara()

        ruta = filedialog.askopenfilename(
            title="Seleccionar imagen",
            filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.bmp *.gif")],
        )
        if not ruta:
            return

        self.modo = "archivo"
        self.ruta_actual = ruta
        img = Image.open(ruta)
        img.thumbnail((780, 440), Image.Resampling.LANCZOS)
        self.ctk_image = ctk.CTkImage(light_image=img, dark_image=img, size=img.size)
        self.thumb_label.configure(image=self.ctk_image, text="")
        self._mostrar_empty(False)
        self.btn_analizar.configure(state="normal", text_color=T.TEXT)
        self.resetear_resultados()
        self.lbl_modo.configure(text="Imagen estática")
        self._set_live_badge("Imagen cargada", bg=T.SURFACE_3, fg=T.GLOW)
        self._set_banner(f"Archivo: {os.path.basename(ruta)}. Pulsa «Analizar imagen».")

    def evaluar_archivo(self):
        if not self.ruta_actual:
            self._set_banner("Selecciona una imagen primero.", bg=T.WARNING_BG, fg=T.WARNING)
            return

        self.btn_analizar.configure(state="disabled")
        self._set_live_badge("Procesando…", bg=T.ACCENT_SOFT, fg=T.GLOW)
        self._set_badge_estado("● Analizando", T.WARNING)
        self.update()

        es_calzado, confianza = evaluar_foto(self.ruta_actual, verbose=False)
        self.btn_analizar.configure(state="normal")

        if es_calzado is None:
            self._set_banner("Error al procesar la imagen.", bg=T.DANGER_BG, fg=T.DANGER)
            return

        self.mostrar_resultado(es_calzado, confianza, estable=True)
        self._set_badge_estado("● Completado", T.SUCCESS if es_calzado else T.DANGER)

    def cerrar_aplicacion(self):
        if self.camara_activa and self.cap is not None:
            self.cap.release()
        self.destroy()


if __name__ == "__main__":
    AppModerna().mainloop()
