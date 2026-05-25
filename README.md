# DO YOU TENSORFLOW? — Calzando la IA 👟🤖
## IUJO — Feria de Haceres Período I-2026
### Unidad Curricular: INO-544 (Investigación de Operaciones)

---

## 👥 Integrantes y Roles
* **Integrante 1:** [Nombre Completo] - [Cédula] - *Rol: Ingeniero de Datos (Dataset y Preprocesamiento)*
* **Integrante 2:** [Nombre Completo] - [Cédula] - *Rol: Arquitecto de IA (Modelado y Entrenamiento)*
* **Integrante 3:** [Nombre Completo] - [Cédula] - *Rol: Ingeniero de Despliegue (Exportación ONNX y Pruebas)*

---

## 🎯 1. Clase/Tema Seleccionado
* **Tema asignado:** Calzado (Zapatos / Calzado Deportivo / Calzado Formal)
* **Descripción del Objeto:** El modelo está diseñado para reconocer e identificar calzado a través de sus características visuales clave, tales como la silueta de la suela, la presencia de cordones/trenzas, la curvatura del talón, la textura de la capellada (cuero, lona, malla sintética) y la puntera del zapato.

---

## 📊 2. Gestión del Dataset (Ingeniería de Datos)
* **Cantidad de imágenes originales recopiladas:** [Número exacto, mín. 200]
* **Estrategia de Data Augmentation aplicada:**
    * *Rotación:* [Rango de grados, ej. -15 a 15 grados para simular diferentes ángulos de pisada]
    * *Zoom:* [Porcentaje, ej. 10% para simular tomas cercanas y lejanas]
    * *Cambios de Brillo:* [Rango, ej. 0.8 a 1.2 para evaluar el calzado bajo luz natural o de tienda]
    * *Otras transformaciones:* [Ej. Volteo horizontal (Horizontal Flip) para alternar el perfil izquierdo y derecho del zapato]
* **Total de imágenes generadas para el entrenamiento:** [Número total después de la aumentación]
* **Resolución y formato estandarizado:** 224x224 píxeles, JPG, canales RGB (Formato Tensor: `[1, 224, 224, 3]`).

---

## 🧠 3. Arquitectura del Modelo y Entrenamiento
* **Framework utilizado:** [TensorFlow/Keras o PyTorch]
* **Descripción de la Red (CNN):** [Explicar brevemente cuántas capas convolucionales, de pooling y densas se utilizaron para extraer patrones del calzado como texturas y contornos].
* **Hiperparámetros óptimos seleccionados:**
    * *Función de pérdida (Loss):* [Ej. Binary Crossentropy si es Zapato/No Zapato, o Categorical Crossentropy si son varios tipos]
    * *Optimizador:* [Ej. Adam / SGD]
    * *Tasa de Aprendizaje (Learning Rate):* [Ej. 0.001]
    * *Épocas (Epochs):* [Número]
    * *Tamaño de lote (Batch Size):* [Número]

### 💡 Justificación Crítica (Control de Autoría)
*Explique detalladamente por qué el equipo eligió esa Tasa de Aprendizaje (Learning Rate) específica y el impacto que tuvo en las gráficas de pérdida durante el laboratorio:*
> [Escribir aquí la respuesta analítica del equipo. Expliquen cómo afectó el Learning Rate al reconocimiento de las formas del calzado y eviten respuestas genéricas generadas por IA].

---

## 📈 4. Métricas de Rendimiento (Testing - 20%)
* **Precisión final (Accuracy) en la data de test:** [Ej. 91.5%]
* **Pérdida final (Loss) en la data de test:** [Ej. 0.18]

*(Inserte aquí abajo la captura de pantalla de la gráfica de entrenamiento Accuracy/Loss de su modelo)*
![Gráfica de Entrenamiento](src/grafica_rendimiento.png)

---

## ⚙️ 5. Especificación de Exportación ONNX
El modelo se ha homologado bajo los estándares requeridos por la interfaz centralizada:
* **Nombre del archivo:** `model/nombre_equipo.onnx`
* **Tensor de Entrada (Input Shape):** `[1, 224, 224, 3]` (Tipo: `float32`)
* **Tensor de Salida (Output Shape):** `[1, 1]` (Tipo: `float32`)
* **Función de activación final:** Sigmoide (Rango de salida de 0.0 a 1.0 para conversión a porcentaje de confianza).

---

## 🚀 6. Instrucciones de Ejecución Local
Para replicar el preprocesamiento, entrenamiento y prueba del modelo de calzado:

1. Clonar el repositorio:
```bash
   git clone [https://github.com/](https://github.com/)[usuario]/[repositorio].git
