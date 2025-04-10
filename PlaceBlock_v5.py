import bge
import bpy
import mathutils
import bmesh
import time

# Флаг для управления выводом времени выполнения
DEBUG_MODE = False
MAX_RAY_DISTANCE = 11  # Максимальная длина луча

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
    """
    Основная функция лучевого кастинга
    """
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
        hit_location, hit_normal, hit_index, hit_object = result[1], result[2], result[3], result[4]
        
        # Проверяем, что точка пересечения находится в пределах максимальной длины луча
        hit_distance = (hit_location - camera_location).length
        if hit_distance <= MAX_RAY_DISTANCE:
            if hit_object and hit_object.type == 'MESH':
                mesh = hit_object.data
                if hit_index >= 0:
                    face = mesh.polygons[hit_index]
                    median = face.center.copy()
                    normal = face.normal.copy()
                    
                    # Смещение
                    offset = 0.5 if normal.dot(hit_normal) > 0 else -0.5
                    median += normal * offset
                    
                    # Получаем имя объекта из игрового свойства
                    cont = bge.logic.getCurrentController()
                    own = cont.owner
                    object_name = own["Block"]  # Игровое свойство типа String

                    # Получаем объект по имени
                    source_object = bpy.data.objects.get(object_name)
                    if source_object and source_object.type == 'MESH':
                        bm_source = bmesh.new()
                        bm_source.from_mesh(source_object.data)
                        
                        bm_target = bmesh.new()
                        bm_target.from_mesh(mesh)
                        
                        uv_layer_target = bm_target.loops.layers.uv.verify()
                        uv_layer_source = bm_source.loops.layers.uv.active or bm_source.loops.layers.uv.verify()
                        
                        # Теперь мы не используем matrix_world, чтобы не зависеть от pivot
                        # Просто размещаем в hit_location
                        new_location = hit_location + normal * offset
                        
                        # Модифицируем местоположение вершин относительно hit_location
                        bm_source.verts.ensure_lookup_table()
                        vert_map = {}
                        
                        for v in bm_source.verts:
                            local_coord = v.co + median
                            new_vert = bm_target.verts.new(local_coord)
                            vert_map[v] = new_vert
                        
                        for f in bm_source.faces:
                            try:
                                new_face = bm_target.faces.new([vert_map[v] for v in f.verts])
                                for loop_source, loop_target in zip(f.loops, new_face.loops):
                                    loop_target[uv_layer_target].uv = loop_source[uv_layer_source].uv
                            except:
                                pass
                        
                        bm_target.to_mesh(mesh)
                        
                        bm_source.free()
                        bm_target.free()
        else:
            debug_print(f"Точка пересечения дальше максимального расстояния: {hit_distance:.2f} > {MAX_RAY_DISTANCE}")
    
    debug_print(f"Время выполнения лучевого кастинга: {time.time() - start_time:.6f} секунд")

def main():
    """
    Основная функция
    """
    start_time = time.time()

    # Обновляем флаг DEBUG_MODE
    update_debug_mode()

    cont = bge.logic.getCurrentController()
    mouse = cont.sensors["RMB"]

    if mouse.positive and mouse.status == bge.logic.KX_INPUT_JUST_ACTIVATED:
        cast_ray_from_camera()

    debug_print(f"Время выполнения всего скрипта: {time.time() - start_time:.6f} секунд")

main()