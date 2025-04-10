import bge
import bpy
import mathutils
import bmesh
import time  # Модуль для замера времени

def copy_mesh_to_object(source_object_name, target_object, hit_location, hit_normal):
    start_time = time.time()  # Начинаем замер времени
    
    # Находим исходный объект по имени
    source_object = bpy.data.objects.get(source_object_name)
    if not source_object or source_object.type != 'MESH':
        # print(f"Объект {source_object_name} не найден или не является мешем")
        return
    
    # Создаем новый bmesh для целевого объекта
    bm_target = bmesh.new()
    bm_target.from_mesh(target_object.data)

    # Создаем bmesh из исходного объекта
    bm_source = bmesh.new()
    bm_source.from_mesh(source_object.data)

    # Преобразуем вершины исходного меша в мировые координаты
    matrix_source = source_object.matrix_world
    matrix_target_inv = target_object.matrix_world.inverted()

    # Словарь для отслеживания соответствия вершин
    vert_map = {}

    # Копируем вершины, грани и UV-координаты
    for v in bm_source.verts:
        # Преобразуем координаты вершины из локальных координат источника в мировые, 
        # затем в локальные координаты целевого объекта
        world_coord = matrix_source @ v.co
        local_coord = matrix_target_inv @ world_coord
        
        # Смещаем координаты относительно точки пересечения
        local_coord += hit_location
        
        # Создаем новую вершину в целевом bmesh
        new_vert = bm_target.verts.new(local_coord)
        vert_map[v] = new_vert

    # Копируем грани
    for f in bm_source.faces:
        # Создаем новую грань с соответствующими вершинами
        try:
            new_face = bm_target.faces.new([vert_map[v] for v in f.verts])
            
            # Копируем UV-координаты, если они есть
            if bm_source.loops.layers.uv:
                uv_layer_source = bm_source.loops.layers.uv.active
                uv_layer_target = bm_target.loops.layers.uv.verify()
                
                for loop_source, loop_target in zip(f.loops, new_face.loops):
                    loop_target[uv_layer_target].uv = loop_source[uv_layer_source].uv
        except Exception as e:
            # print(f"Ошибка при создании грани: {e}")
            pass

    # Обновляем меш целевого объекта
    bm_target.to_mesh(target_object.data)
    bm_target.free()
    bm_source.free()

    # print(f"Меш из {source_object_name} скопирован в объект {target_object.name}")

    # Выводим время выполнения
    print(f"Время копирования меша: {time.time() - start_time:.6f} секунд")

def get_polygon_center_and_normal(hit_object, hit_location):
    start_time = time.time()  # Начинаем замер времени

    # Получаем bmesh целевого объекта
    bm = bmesh.new()
    bm.from_mesh(hit_object.data)

    # Находим ближайшее лицо к точке пересечения
    closest_face = None
    min_dist = float('inf')

    # Перебираем все грани объекта, чтобы найти ближайшую
    for face in bm.faces:
        # Проверяем, является ли точка пересечения в пределах грани
        center = face.calc_center_median()  # Средняя точка полигона
        distance = (hit_location - center).length
        
        if distance < min_dist:
            min_dist = distance
            closest_face = face

    if closest_face:
        normal = closest_face.normal  # Нормаль грани
        median = closest_face.calc_center_median()  # Средняя точка полигона

        # Выводим информацию о полигоне
        # print(f"Полигон найден: {closest_face}")
        # print(f"Средняя точка полигона: {median}")
        # print(f"Нормаль полигона: {normal}")
        # print(f"Количество вершин в полигоне: {len(closest_face.verts)}")
        # for vert in closest_face.verts:
        #     print(f"Вершина: {vert.co}")

        bm.free()

        # Выводим время вычислений для поиска полигона
        print(f"Время поиска полигона: {time.time() - start_time:.6f} секунд")
        
        return median, normal
    else:
        bm.free()
        # print("Полигон не найден")
        return hit_location, mathutils.Vector((0, 0, 1))  # Если не нашли, возвращаем точку и нормаль

def cast_ray_from_camera():
    start_time = time.time()  # Начинаем замер времени

    camera = bpy.context.scene.camera
    if not camera:
        # print("Камера не найдена")
        return
    
    camera_location = camera.location
    local_direction = mathutils.Vector((0, 0, -1))  # Направление луча
    world_direction = camera.rotation_euler.to_matrix() @ local_direction  # Преобразуем в мировые координаты

    # Выполняем лучевой кастинг
    result = bpy.context.scene.ray_cast(bpy.context.view_layer.depsgraph, camera_location, world_direction)

    if result[0]:
        hit_location = result[1]  # Точка пересечения
        hit_normal = result[2]    # Нормаль пересекаемого полигона
        hit_object = result[4]
        
        # print(f"Луч пересек объект: {hit_object.name}")
        # print(f"Точка пересечения: {hit_location}")
        # print(f"Нормаль пересекаемого полигона: {hit_normal}")

        if hit_object and hit_object.type == 'MESH':
            # Получаем среднюю точку полигона и нормаль
            median, normal = get_polygon_center_and_normal(hit_object, hit_location)
            
            # Смещаем точку вдоль нормали, чтобы избежать пересечения
            offset = 0.5  # Смещение вдоль нормали, чтобы куб не был погружен
            dot_product = normal.dot(hit_normal)  # Смотрим на ориентацию нормалей

            if dot_product > 0:  # Если нормали направлены в одну сторону, сдвигаем в положительную сторону
                median += normal * offset
            else:  # Если нормали направлены в противоположные стороны, сдвигаем в отрицательную
                median -= normal * offset
            
            # Ориентируем объект в зависимости от нормали
            rotation = normal.to_track_quat('Z', 'Y').to_matrix().to_4x4()
            
            # Создаем копию блока с корректной ориентацией
            copy_mesh_to_object('Board', hit_object, median, rotation)

    # Выводим время выполнения лучевого кастинга
    print(f"Время выполнения лучевого кастинга: {time.time() - start_time:.6f} секунд")

def main():
    start_time = time.time()  # Начинаем замер времени

    cont = bge.logic.getCurrentController()
    mouse = cont.sensors["RMB"]

    if mouse.positive and mouse.status == bge.logic.KX_INPUT_JUST_ACTIVATED:
        cast_ray_from_camera()

    # Выводим время выполнения всего скрипта
    print(f"Время выполнения всего скрипта: {time.time() - start_time:.6f} секунд")

main()
