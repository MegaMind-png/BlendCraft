import bpy
import bge
import mathutils
import bmesh
import time  # Для замера времени

# Флаг для управления выводом, будет изменяться через игровое свойство
DEBUG_MODE = False

# Максимальная длина луча
MAX_RAY_DISTANCE = 10  # Измени при необходимости

# Функция для обновления флага DEBUG_MODE в зависимости от игрового свойства
def update_debug_mode():
    global DEBUG_MODE
    source_object = bpy.data.objects.get("ScriptHandler")  # Замените "ScriptHandler" на имя вашего объекта
    if source_object and source_object.game:
        prop_index = source_object.game.properties.find("Debug")
        if prop_index != -1:
            prop = source_object.game.properties[prop_index]
            DEBUG_MODE = prop.value
        else:
            DEBUG_MODE = False
    else:
        DEBUG_MODE = False

# Функция для вывода сообщений в консоль, если DEBUG_MODE включен
def debug_print(message):
    if DEBUG_MODE:
        print(message)

# Функция для кастинга луча из камеры
def cast_ray_from_camera():
    start_time = time.time()
    camera = bpy.context.scene.camera
    if not camera:
        return

    camera_location = camera.location
    local_direction = mathutils.Vector((0, 0, -1))
    world_direction = camera.rotation_euler.to_matrix() @ local_direction
    world_direction.normalize()
    
    # Расчёт точки конца луча с учётом максимальной длины
    end_location = camera_location + world_direction * MAX_RAY_DISTANCE

    # Кастинг с ограничением расстояния
    result = bpy.context.scene.ray_cast(
        bpy.context.view_layer.depsgraph,
        camera_location,
        end_location - camera_location
    )

    if result[0]:
        hit_location = result[1]
        hit_distance = (hit_location - camera_location).length

        if hit_distance <= MAX_RAY_DISTANCE:
            hit_normal = result[2]
            debug_print(f"Пересечение с полигоном: {hit_location}")
            debug_print(f"Нормаль пересекаемого полигона: {hit_normal}")

            hit_object = result[4]

            if hit_object and hit_object.type == 'MESH':
                local_hit_location = hit_object.matrix_world.inverted() @ hit_location
                debug_print(f"Локальная точка пересечения: {local_hit_location}")

                hit_face_index = result[3]
                remove_connected_polygons_and_vertices_from_mesh(hit_object, hit_face_index)
        else:
            debug_print(f"Луч попал, но точка дальше лимита: {hit_distance:.2f} > {MAX_RAY_DISTANCE}")

    if DEBUG_MODE:
        debug_print(f"Время выполнения кастинга луча: {time.time() - start_time:.6f} секунд")

# Функция для удаления полигонов и вершин из объекта
def remove_connected_polygons_and_vertices_from_mesh(obj, face_index):
    start_time = time.time()  # Засекаем время начала функции
    # Создаём бмэш для объекта
    bm = bmesh.new()
    bm.from_mesh(obj.data)

    # Обновляем таблицу индексов для вершин и полигонов
    bm.faces.ensure_lookup_table()

    # Получаем полигон, который нужно удалить
    face_to_remove = bm.faces[face_index]
    
    # Создаём список для хранения всех удаляемых полигонов
    polygons_to_remove = set()
    vertices_to_remove = set()

    # Начинаем с исходного полигона
    polygons_to_remove.add(face_to_remove)

    # Используем очередь для поиска всех связанных полигонов
    queue = [face_to_remove]

    while queue:
        current_face = queue.pop()
        for edge in current_face.edges:
            for adjacent_face in edge.link_faces:
                if adjacent_face not in polygons_to_remove:
                    polygons_to_remove.add(adjacent_face)
                    queue.append(adjacent_face)

    # Собираем все вершины, которые принадлежат удаляемым полигонам
    for poly in polygons_to_remove:
        for vertex in poly.verts:
            vertices_to_remove.add(vertex)

    # Удаляем все найденные полигоны
    for poly in polygons_to_remove:
        bm.faces.remove(poly)

    # Удаляем вершины, связанные с этими полигонами
    for vertex in vertices_to_remove:
        bm.verts.remove(vertex)

    # Применяем изменения и обновляем объект
    bm.to_mesh(obj.data)
    bm.free()

    if DEBUG_MODE:
        debug_print(f"Время выполнения удаления: {time.time() - start_time:.6f} секунд")
    debug_print(f"Удалены {len(polygons_to_remove)} полигонов и {len(vertices_to_remove)} вершин из объекта {obj.name}")

def main():
    update_debug_mode()

    cont = bge.logic.getCurrentController()
    mouse = cont.sensors["LMB"]

    if mouse.positive and mouse.status == bge.logic.KX_INPUT_JUST_ACTIVATED:
        cast_ray_from_camera()

main()
