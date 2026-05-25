from tkinter import filedialog

import customtkinter as ctk
from PIL import Image

from validar_modelo import evaluar_foto

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")  # Puedes cambiar a "dark-blue" o "green" si lo prefieres


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Clasificador de Calzados")
        self.geometry("600x520")
        self.resizable(False, False)

        self.ruta = ""
        self.ctk_image = None
        self.thumb_label = None
        self._build_ui()

    def _build_ui(self):
        # ── file row ──
        row1 = ctk.CTkFrame(self)
        row1.pack(fill="x", padx=15, pady=(15, 0))

        ctk.CTkLabel(row1, text="Imagen:", font=("Segoe UI", 13)).pack(
            side="left", padx=(0, 8)
        )
        self.ruta_entry = ctk.CTkEntry(
            row1, placeholder_text="Selecciona una imagen..."
        )
        self.ruta_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        ctk.CTkButton(row1, text="Examinar", command=self.seleccionar_archivo).pack(
            side="right"
        )

        # ── image preview ──
        self.preview_frame = ctk.CTkFrame(self)
        self.preview_frame.pack(fill="both", expand=True, padx=15, pady=12)

        self.thumb_label = ctk.CTkLabel(
            self.preview_frame,
            text="Sin imagen seleccionada",
            font=("Segoe UI", 12),
        )
        self.thumb_label.pack(expand=True)

        # ── evaluate button ──
        ctk.CTkButton(
            self, text="Evaluar", command=self.evaluar, height=38, font=("Segoe UI", 13)
        ).pack(padx=15, pady=(0, 10), fill="x")

        # ── result area ──
        self.result_label = ctk.CTkLabel(
            self,
            text="",
            font=("Segoe UI", 16, "bold"),
        )
        self.result_label.pack(pady=(0, 15))

    def seleccionar_archivo(self):
        ruta = filedialog.askopenfilename(
            title="Seleccionar imagen",
            filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.bmp *.gif")],)
        if not ruta:
            return
        self.ruta = ruta
        self.ruta_entry.delete(0, "end")
        self.ruta_entry.insert(0, ruta)
        self._mostrar_preview(ruta)
        self.result_label.configure(text="")

    def _mostrar_preview(self, ruta):
        img = Image.open(ruta)
        img.thumbnail((500, 300))
        self.ctk_image = ctk.CTkImage(light_image=img, dark_image=img, size=img.size)
        self.thumb_label.configure(image=self.ctk_image, text="")

    def evaluar(self):
        if not self.ruta:
            self.result_label.configure(text="Selecciona una imagen primero.")
            return

        es_calzado, confianza = evaluar_foto(self.ruta)
        if es_calzado is None:
            self.result_label.configure(text="Error al procesar la imagen.")
            return

        if es_calzado:
            texto = f"ES UN CALZADO  —  {confianza:.1f}% de certeza"
            color = "#2ecc71"
        else:
            texto = f"NO ES UN CALZADO  —  {confianza:.1f}% de certeza"
            color = "#e74c3c"

        self.result_label.configure(text=texto, text_color=color)


if __name__ == "__main__":
    App().mainloop()
