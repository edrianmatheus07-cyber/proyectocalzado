# DO YOU TENSORFLOW? — Calzando la IA 👟🤖
## IUJO — Feria de Haceres Período I-2026
### Unidad Curricular: INO-544 (Investigación de Operaciones)

---

## 👥 Integrantes y Roles
* **Integrante 1:** [Edrian Matheus] - [29.661.577] - *Rol: Ingeniero de Datos (Dataset y Preprocesamiento)*
* **Integrante 2:** [José Márquez] - [Cédula] - *Rol: Ingeniero de Despliegue (Exportación ONNX y Pruebas)*
* **Integrante 3:** [Matgreyd Duran] - [31.288.154] - *Rol: Arquitecto de IA (Modelado y Entrenamiento)*
* **Integrante 4:** [Ashley Aguilar] - [28.052.136] - *Rol: Arquitecto de IA (Modelado y Entrenamiento)*

---

## 🎯 1. Clase/Tema Seleccionado
* **Tema asignado:** Calzado (Zapatos / Calzado Deportivo / Calzado Formal)
* **Descripción del Objeto:** El modelo está diseñado para reconocer e identificar calzado a través de sus características visuales clave, tales como la silueta de la suela, la presencia de cordones/trenzas, la curvatura del talón, la textura de la capellada (cuero, lona, malla sintética) y la puntera del zapato.

---

## 📊 2. Gestión del Dataset (Ingeniería de Datos)
* **Cantidad de imágenes originales recopiladas:** [Contiene aproximadamente entre 400 - 500]
* **Estrategia de Data Augmentation aplicada:**
    * *Rotación:* [Entre -20° y +20°]
    * *Zoom:* [Rango del 20% (0.2).]
    * *Cambios de Brillo:* [Rando de 0,8 a 1.2]
    * *Otras transformaciones:* [Volteo horizontal (horizontal flip) y desplazamiento (width/height shift) del 10% de movimiento lateral y vertical ppara simular distintos encuadres de cámara]
* **Total de imágenes generadas para el entrenamiento:** [2190]
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

Para el laboratorio de Transfer Learning con MobileNetV2, decidimos implementar el optimizador Adam con una tasa de aprendizaje inicial de 0.001 para lograr el equilibrio perfecto entre velocidad y estabilidad. Al trabajar con un modelo preentrenado en ImageNet, las capas convolucionales ya contaban con una base sólida para detectar bordes y texturas básicas, por lo que un valor más agresivo (como 0.01) habría destruido ese conocimiento previo con gradientes bruscos, mientras que uno más bajo habría ralentizado el proceso de forma ineficiente. Gracias a este ajuste intermedio, las nuevas capas densas finales se adaptaron con total precisión a la geometría específica de los zapatos, como las curvas del empeine y las suelas permitiendo que el modelo ignorara los fondos complejos y se enfocara en los contornos clave, lo que elevó la confianza de la inferencia por encima del 90% en ángulos variados.

Este acierto técnico se reflejó directamente en el comportamiento de las gráficas de rendimiento durante el entrenamiento. La curva de pérdida mostró un descenso exponencial suave y controlado en las primeras cuatro épocas hasta estabilizarse por completo hacia la octava, demostrando una convergencia asintótica ideal y libre de las oscilaciones erráticas que provoca un parámetro demasiado alto. De este modo, la elección de 0.001 demostró ser la estrategia óptima para balancear la velocidad de convergencia con la preservación de las características ya extraídas por MobileNetV2, logrando que el modelo generalizara la morfología del calzado de manera efectiva y sin caer en el riesgo de sobreajuste.

---

## 📈 4. Métricas de Rendimiento (Testing - 20%)
* **Precisión final (Accuracy) en la data de test:** [Ej. 91.5%]
* **Pérdida final (Loss) en la data de test:** [Ej. 0.18]

*(Inserte aquí abajo la captura de pantalla de la gráfica de entrenamiento Accuracy/Loss de su modelo)*
![Gráfica de Entrenamiento](src/grafica_rendimiento.png)

PRUEBA DE MODELO DE DETECTOR DE CALZADOS DESDE EL TERMINAL:
<img width="1429" height="251" alt="Captura de pantalla 2026-05-25 162900" src="https://github.com/user-attachments/assets/5f0d0ad5-74c8-413c-9494-b2a39bf06532" />

PRUEBA DE MODELO DE DETECTOR DESDE LA INTERFAZ ¨ES UN CALZADO¨ USANDO CUSTOMTKINTER:
<img width="948" height="673" alt="Captura de pantalla 2026-05-25 162800" src="https://github.com/user-attachments/assets/30af62d6-5275-4f04-8aee-99ed6724f2c6" />

PRUEBA DE MODELO DE DETECTOR DESDE LA INTERFAZ ¨NO ES UN CALZADO¨ USANDO CUSTOMTKINTER:
<img width="945" height="675" alt="Captura de pantalla 2026-05-25 163458" src="https://github.com/user-attachments/assets/49af5a66-9313-4b46-8723-63fa4ccfc9a9" />

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
