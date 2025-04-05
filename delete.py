import os
import cv2
import shutil

def get_image_files(directory):
    """Obtiene la lista de imágenes en el directorio."""
    return [os.path.join(directory, f) for f in os.listdir(directory) if f.lower().endswith(('jpg', 'jpeg', 'png'))]

def delete_file(file_path, backup_dir):
    """Elimina el archivo y lo guarda en una carpeta de respaldo."""
    try:
        if os.path.isfile(file_path):
            backup_path = os.path.join(backup_dir, os.path.basename(file_path))
            shutil.move(file_path, backup_path)
            print(f"Imagen eliminada: {file_path}")
            return backup_path
    except Exception as e:
        print(f"Error al eliminar {file_path}: {e}")
    return None

def undo_delete(last_deleted, original_dir):
    """Restaura la última imagen eliminada."""
    if last_deleted:
        restored_path = os.path.join(original_dir, os.path.basename(last_deleted))
        shutil.move(last_deleted, restored_path)
        print(f"Imagen restaurada: {restored_path}")
        return restored_path
    print("No hay imagen para restaurar.")
    return None

def add_overlay(image, text, position):
    """Añade texto sobre la imagen."""
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1
    thickness = 2
    color = (255, 255, 255)
    shadow = (0, 0, 0)

    # Agregar sombra al texto para mejor visibilidad
    cv2.putText(image, text, (position[0] + 2, position[1] + 2), font, font_scale, shadow, thickness + 2, cv2.LINE_AA)
    cv2.putText(image, text, position, font, font_scale, color, thickness, cv2.LINE_AA)

def main():
    folder = "Beds"
    backup_folder = "Beds_backup"
    os.makedirs(backup_folder, exist_ok=True)

    images = get_image_files(folder)
    total_images = len(images)

    if total_images == 0:
        print("No hay imágenes en la carpeta.")
        return
    
    index = 0
    last_deleted = None

    while index < total_images:
        image_path = os.path.abspath(images[index])
        img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)

        if img is None:
            print(f"Error al abrir la imagen: {image_path}")
            index += 1
            continue

        # Redimensionar las imágenes a la pantalla
        max_width, max_height = 1280, 720
        height, width = img.shape[:2]
        if width > max_width or height > max_height:
            scale = min(max_width / width, max_height / height)
            img = cv2.resize(img, (int(width * scale), int(height * scale)))

        # Añadir contador arriba de las imágenes
        add_overlay(img, f"Imagen {index + 1} de {total_images}", (20, 40))
        # Añadir instrucciones abajo
        add_overlay(img, "1 - Siguiente | 2 - Eliminar | Z - Deshacer", (20, img.shape[0] - 20))

        cv2.imshow("Revisión de imágenes", img)
        key = cv2.waitKey(0)  # Esperar entrada de teclado

        if key == ord("1"):  # Siguiente imagen
            index += 1
        elif key == ord("2"):  # Eliminar imagen
            last_deleted = delete_file(image_path, backup_folder)
            images.pop(index)
            total_images -= 1
            if index >= total_images:
                index -= 1
        elif key == ord("z"):  # Deshacer eliminación
            restored = undo_delete(last_deleted, folder)
            if restored:
                images.insert(index, restored)
                total_images += 1
        
        cv2.destroyAllWindows()

    print("Revisión de imágenes completada.")

if __name__ == "__main__":
    main()
