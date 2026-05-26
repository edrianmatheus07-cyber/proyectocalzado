import os
import time
from collections import deque

import numpy as np
import onnxruntime as ort
from PIL import Image

RUTA_MODELO = "modelo_calzados_v1a.onnx"

_sesion = None
_input_name = None
_output_name = None


def _cargar_modelo():
    global _sesion, _input_name, _output_name
    if _sesion is None:
        if not os.path.exists(RUTA_MODELO):
            raise FileNotFoundError(f"No se encontró el modelo '{RUTA_MODELO}'")
        _sesion = ort.InferenceSession(RUTA_MODELO)
        _input_name = _sesion.get_inputs()[0].name
        _output_name = _sesion.get_outputs()[0].name
    return _sesion


def _pil_a_tensor(img: Image.Image) -> np.ndarray:
    if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
        fondo = Image.new("RGB", img.size, (255, 255, 255))
        fondo.paste(img, mask=img.convert("RGBA").split()[3])
        img = fondo
    else:
        img = img.convert("RGB")

    img = img.resize((224, 224))
    tensor = np.array(img, dtype=np.float32) / 255.0
    return np.expand_dims(tensor, axis=0)


def preprocesar_imagen(ruta_imagen):
    if not os.path.exists(ruta_imagen):
        print(f"❌ Error: No se encontró la imagen '{ruta_imagen}'")
        return None
    return _pil_a_tensor(Image.open(ruta_imagen))


def preprocesar_frame(frame_rgb: np.ndarray) -> np.ndarray:
    """Preprocesa un frame BGR/RGB numpy (H, W, 3) sin escribir a disco."""
    if frame_rgb is None or frame_rgb.size == 0:
        return None
    return _pil_a_tensor(Image.fromarray(frame_rgb.astype(np.uint8)))


def interpretar_score(score: float) -> tuple[bool, float]:
    """
  score < 0.5  → calzado (clase 0 en orden alfabético de carpetas).
  score >= 0.5 → no es calzado.
    """
    if score < 0.5:
        return True, (1.0 - score) * 100.0
    return False, score * 100.0


def predecir_tensor(input_data: np.ndarray) -> float:
    sesion = _cargar_modelo()
    resultado = sesion.run([_output_name], {_input_name: input_data})
    return float(resultado[0][0][0])


def evaluar_frame(frame_rgb, verbose: bool = False) -> tuple[bool | None, float | None, float | None]:
    """
    Evalúa un frame en memoria.
    Retorna (es_calzado, confianza, score_crudo).
    """
    try:
        input_data = preprocesar_frame(frame_rgb)
        if input_data is None:
            return None, None, None
        score = predecir_tensor(input_data)
        es_calzado, confianza = interpretar_score(score)
        if verbose:
            etiqueta = "CALZADO" if es_calzado else "NO ES UN CALZADO"
            print(f"  → {etiqueta} ({confianza:.1f}%)")
        return es_calzado, confianza, score
    except FileNotFoundError as exc:
        print(exc)
        return None, None, None


def evaluar_foto(ruta_imagen, verbose: bool = True) -> tuple[bool | None, float | None]:
    if verbose:
        print(f"\nAnalizando: '{ruta_imagen}'...")

    input_data = preprocesar_imagen(ruta_imagen)
    if input_data is None:
        return None, None

    try:
        score = predecir_tensor(input_data)
    except FileNotFoundError as exc:
        print(exc)
        return None, None

    es_calzado, confianza = interpretar_score(score)
    res_texto = "CALZADO" if es_calzado else "NO ES UN CALZADO"

    if verbose:
        print("-" * 50)
        print(f"🔍 Resultado: {res_texto}")
        print(f"📊 CONFIRMADO: {confianza:.2f}%")
        print("-" * 50)

    return es_calzado, confianza


class VentanaAnalisis:
    """Acumula predicciones durante N segundos y devuelve un resultado estable."""

    def __init__(self, duracion_seg: float = 4.0):
        self.duracion_seg = duracion_seg
        self._scores: deque[tuple[float, float]] = deque()

    def reiniciar(self):
        self._scores.clear()

    def agregar(self, score: float):
        ahora = time.time()
        self._scores.append((ahora, score))
        self._podar(ahora)

    def _podar(self, ahora: float):
        limite = ahora - self.duracion_seg
        while self._scores and self._scores[0][0] < limite:
            self._scores.popleft()

    @property
    def segundos_acumulados(self) -> float:
        if len(self._scores) < 2:
            return 0.0
        return self._scores[-1][0] - self._scores[0][0]

    @property
    def progreso(self) -> float:
        if not self._scores:
            return 0.0
        return min(1.0, self.segundos_acumulados / self.duracion_seg)

    @property
    def cantidad_muestras(self) -> int:
        return len(self._scores)

    @property
    def listo(self) -> bool:
        return self.segundos_acumulados >= self.duracion_seg * 0.85 and len(self._scores) >= 3

    def resultado(self) -> tuple[bool | None, float | None, float | None]:
        if not self._scores:
            return None, None, None
        scores = [s for _, s in self._scores]
        score_medio = float(np.median(scores))
        es_calzado, confianza = interpretar_score(score_medio)
        return es_calzado, confianza, score_medio

    def vista_previa(self) -> tuple[bool | None, float | None]:
        """Resultado parcial con las muestras actuales (aunque no haya terminado el tiempo)."""
        if not self._scores:
            return None, None
        scores = [s for _, s in self._scores]
        return interpretar_score(float(np.median(scores)))


if __name__ == "__main__":
    if not os.path.exists(RUTA_MODELO):
        print(f"⚠️ No se encontró '{RUTA_MODELO}'. Ejecuta el entrenamiento primero.")
    else:
        evaluar_foto("montana12.jpg")
