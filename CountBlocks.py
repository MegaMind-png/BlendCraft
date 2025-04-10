import bge
import bpy

# Функция для подсчета полигонов в сцене
def count_polygons():
    total_polygons = 0
    view_layer = bpy.context.view_layer
    
    # Проходим по всем объектам в сцене
    for obj in bpy.context.scene.objects:
        # Проверяем, что объект является мешем (Mesh) и видим в viewport
        if obj.type == 'MESH' and obj.visible_get(view_layer=view_layer):
            # Суммируем количество полигонов (треугольников)
            total_polygons += len(obj.data.polygons)
    
    return total_polygons

# Получаем текущую сцену
scene = bge.logic.getCurrentScene()

# Ищем объект, на который прикреплен скрипт (пустышка или любой другой объект)
owner = bge.logic.getCurrentController().owner

# Создаем свойство для отображения информации (если оно не существует)
if 'block_count' not in owner:
    owner['block_count'] = 0

# Подсчитываем количество полигонов
polygon_count = count_polygons()

# Каждые 8 полигонов = 1 объект, поэтому делим на 8 и округляем вниз, добавляя 1
object_count = (polygon_count // 6) + 1

# Обновляем свойство с количеством объектов
owner['block_count'] = object_count
