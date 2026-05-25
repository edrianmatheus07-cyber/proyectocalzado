import numpy as np
from PIL import Image
import onnxruntime as ort
import os

# Nombre exacto de tu modelo exportado
RUTA_MODELO = "modelo_calzados_v1a.onnx"

def preprocesar_imagen(ruta_imagen):
    """Prepara una sola foto para que el modelo la entienda"""
    if not os.path.exists(ruta_imagen):
        print(f"❌ Error: No se encontró la imagen '{ruta_imagen}'")
        return None
        
    # 1. Abrir imagen y manejar fondos transparentes (PNG)
    img = Image.open(ruta_imagen)
    
    if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
        fondo_blanco = Image.new('RGB', img.size, (255, 255, 255))
        fondo_blanco.paste(img, mask=img.convert('RGBA').split()[3])
        img = fondo_blanco
    else:
        img = img.convert('RGB')
    
    # 2. Forzar resolución exacta 224x224
    img = img.resize((224, 224))
    
    # 3. Convertir a números y aplicar la normalización (rescale=1./255)
    img_array = np.array(img, dtype=np.float32) / 255.0
    
    # 4. Agregar la dimensión del Batch: [1, 224, 224, 3]
    img_array = np.expand_dims(img_array, axis=0) 
    
    return img_array

def evaluar_foto(ruta_imagen):
    print(f"\nAnalizando: '{ruta_imagen}'...")
    
    # Preprocesamos la foto
    input_data = preprocesar_imagen(ruta_imagen)
    if input_data is None:
        return None, None
    
    # Iniciamos el motor de ONNX
    sesion = ort.InferenceSession(RUTA_MODELO)
    input_name = sesion.get_inputs()[0].name
    output_name = sesion.get_outputs()[0].name
    
    # Hacemos la predicción
    resultado = sesion.run([output_name], {input_name: input_data})
    score = resultado[0][0][0] # Extraemos el número final
    
    # ==========================================
    # LÓGICA DE DECISIÓN
    # ==========================================
    # Keras asignó 0 a Calzados y 1 a No_Calzados por orden alfabético.
    
    print("-" * 50)
    if score < 0.5: 
        # Si está más cerca de 0
        confianza = (1.0 - score) * 100
        es_calzado = True
        print(f"✅ ¡ES UN CALZADO!")
        print(f"📊 Nivel de certeza: {confianza:.2f}%")
    else:
        # Si está más cerca de 1
        confianza = score * 100
        es_calzado = False
        print(f"❌ NO ES UN CALZADO")
        print(f"📊 Nivel de certeza: {confianza:.2f}%")
    print("-" * 50)
    
    return es_calzado, confianza

# ==========================================
# ZONA DE PRUEBAS
# ==========================================
if __name__ == "__main__":
    if not os.path.exists(RUTA_MODELO):
        print(f"⚠️ No se encontró '{RUTA_MODELO}'. Ejecuta el entrenamiento primero.")
    else:
        # Pon el nombre de las fotos que quieras probar aquí abajo:
        evaluar_foto("1. Nike Air Force 1_roto.jpg") 
        evaluar_foto("2. montana12.jpg") 
        

        