import cv2

def probar_camara():
    # Buscaremos en los primeros 5 índices disponibles
    cap = None
    for i in range(5):
        print(f"Probando cámara en índice {i}...")
        cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
        if cap.isOpened():
            print(f"¡Éxito! Cámara encontrada en el índice {i}")
            break
        cap.release()

    if cap is None or not cap.isOpened():
        print("Error: No se detectó ninguna cámara (Iriun, integrada o USB).")
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