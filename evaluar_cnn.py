import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import numpy as np
import os

BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dataset')

if not os.path.exists(BASE_DIR):
    raise FileNotFoundError(f"❌ Error: No se encontró la carpeta '{BASE_DIR}'.\n"
                            f"Asegúrate de crear la carpeta 'dataset' en el directorio del proyecto con tus imágenes.")

print("\n--- 1. PROBANDO EL DATASET ---")
datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=20,
    horizontal_flip=True,
    brightness_range=[0.5, 1.5],
    zoom_range=0.3,
    width_shift_range=0.2,
    height_shift_range=0.2,
    fill_mode='nearest'
)

# Cargamos el dataset desde las carpetas locales
train_generator = datagen.flow_from_directory(
    BASE_DIR,
    target_size=(224, 224), 
    batch_size=32, 
    class_mode='binary'
)

print("\nClases detectadas:", train_generator.class_indices)

# Extraemos un solo lote (batch) para verificar dimensiones
imagenes, etiquetas = next(train_generator)
print(f"Formato de las imágenes (Batch, Alto, Ancho, Canales): {imagenes.shape}")
print(f"Formato de las etiquetas: {etiquetas.shape}")

# Verificación estricta
assert imagenes.shape[1:] == (224, 224, 3), "❌ Error: La resolución o los canales no coinciden."
print("✅ El dataset funciona perfectamente y entrega el formato correcto.")

print("\n--- 2. CONSTRUYENDO LA CNN ---")
input_tensor = layers.Input(shape=(224, 224, 3), name="cam_input", dtype=tf.float32)

# Ajuste de escala: El generador entrega [0, 1], MobileNetV2 espera [-1, 1].
x = layers.Rescaling(scale=2.0, offset=-1.0)(input_tensor)

# MobileNetV2
base_model = tf.keras.applications.MobileNetV2(
    input_shape=(224, 224, 3),
    include_top=False,
    weights='imagenet'
)
base_model.trainable = False

x = base_model(x, training=False)
x = layers.GlobalAveragePooling2D()(x)
x = layers.Dense(128, activation='relu')(x)
x = layers.Dropout(0.5)(x)

# Salida Binaria [1, 1]
output_tensor = layers.Dense(1, activation='sigmoid', name="confidence_score")(x)

model = models.Model(inputs=input_tensor, outputs=output_tensor)
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

# Mostrar la tabla de la arquitectura
model.summary()
print("\n✅ La arquitectura CNN compiló correctamente. ¡Listo para entrenar!")
