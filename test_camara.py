import cv2

def probar_camara():
    # 0 suele ser la cámara integrada, 1 o 2 podrían ser cámaras USB
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    if not cap.isOpened():
        print("Error: No se pudo acceder a la cámara.")
        return

    print("Cámara abierta. Si no ves la ventana, busca un icono de Python en la barra de tareas. Presiona 'q' para salir.")

    while True:
        # Capturar frame por frame
        ret, frame = cap.read()

        if not ret:
            print("Error: No se puede recibir video (¿cámara desconectada?).")
            break

        # Mostrar el resultado
        cv2.imshow('Prueba de Camara', frame)
        
        # Forzar que la ventana esté al frente
        cv2.setWindowProperty('Prueba de Camara', cv2.WND_PROP_TOPMOST, 1)

        # Detener con la tecla 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Liberar recursos
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    probar_camara()