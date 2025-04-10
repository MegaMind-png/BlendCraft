import bge
import bpy
import mathutils
import bmesh

def cast_ray_from_camera():
    camera = bpy.context.scene.camera
    if not camera:
        return
    
    camera_location = camera.location
    local_direction = mathutils.Vector((0, 0, -1))  # Направление луча
    world_direction = camera.rotation_euler.to_matrix() @ local_direction  # Преобразуем в мировые координаты

    # Выполняем лучевой кастинг
    result = bpy.context.scene.ray_cast(bpy.context.view_layer.depsgraph, camera_location, world_direction)

    if result[0]:
        hit_location = result[1]  # Точка пересечения
        hit_normal = result[2]    # Нормаль пересекаемого полигона
        print(f"Пересечение с полигоном: {hit_location}")
        print(f"Нормаль пересекаемого полигона: {hit_normal}")
        
        # Получаем объект, на котором произошло пересечение
        hit_object = result[4]
        
        if hit_object and hit_object.type == 'MESH':
            # Преобразуем точку пересечения в локальные координаты объекта
            local_hit_location = hit_object.matrix_world.inverted() @ hit_location
            print(f"Локальная точка пересечения: {local_hit_location}")
            
            # Смещаем точку вдоль нормали, чтобы избежать пересечения
            offset = 0.1  # Смещение по нормали
            snapped_location = snap_to_grid(local_hit_location + hit_normal * offset)
            print(f"Смещённая точка (локальная): {snapped_location}")
            
            # Преобразуем локальную точку обратно в мировые координаты
            world_location = hit_object.matrix_world @ snapped_location
            print(f"Мировая точка (мировые координаты): {world_location}")
            
            # Создаем куб как часть этого объекта
            add_cube_to_mesh(hit_object, world_location)

def snap_to_grid(location):
    # Округляем до ближайшего целого для точности сетки
    return mathutils.Vector((round(location.x), round(location.y), round(location.z)))

def add_cube_to_mesh(obj, location):
    # Создаем бмэш для объекта
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    
    # Создаем UV-слой, если его нет
    uv_layer = bm.loops.layers.uv.verify()

    # Размер куба
    size = 1.0
    half_size = size / 2.0
    
    # Создаем вершины для куба в указанной позиции
    vertices = [
        # Нижняя грань (против часовой стрелки)
        bm.verts.new((location.x - half_size, location.y - half_size, location.z - half_size)),
        bm.verts.new((location.x - half_size, location.y + half_size, location.z - half_size)),
        bm.verts.new((location.x + half_size, location.y + half_size, location.z - half_size)),
        bm.verts.new((location.x + half_size, location.y - half_size, location.z - half_size)),
        
        # Верхняя грань (по часовой стрелке)
        bm.verts.new((location.x - half_size, location.y - half_size, location.z + half_size)),
        bm.verts.new((location.x + half_size, location.y - half_size, location.z + half_size)),
        bm.verts.new((location.x + half_size, location.y + half_size, location.z + half_size)),
        bm.verts.new((location.x - half_size, location.y + half_size, location.z + half_size)),
    ]
    
    # Создаем грани для куба с учетом порядка обхода вершин
    faces = [
        bm.faces.new([vertices[0], vertices[1], vertices[2], vertices[3]]),  # Нижняя грань
        bm.faces.new([vertices[4], vertices[5], vertices[6], vertices[7]]),  # Верхняя грань
        bm.faces.new([vertices[0], vertices[4], vertices[7], vertices[1]]),  # Левая грань
        bm.faces.new([vertices[3], vertices[2], vertices[6], vertices[5]]),  # Правая грань
        bm.faces.new([vertices[1], vertices[7], vertices[6], vertices[2]]),  # Задняя грань
        bm.faces.new([vertices[0], vertices[3], vertices[5], vertices[4]]),  # Передняя грань
    ]
    
    # Настройка UV-координат для каждой грани с точными значениями
    precise_uv_coords = [
        (0.15625, 0.687516),     # Координата 0
        (0.15625, 0.718745),     # Координата 1
        (0.140635, 0.718745),    # Координата 2
        (0.140635, 0.687516)     # Координата 3
    ]
    
    # Применяем точные UV-координаты для каждой грани
    for face in faces:
        for i, loop in enumerate(face.loops):
            loop[uv_layer].uv = precise_uv_coords[i]
    
    # Применяем изменения и обновляем объект
    bm.to_mesh(obj.data)
    bm.free()
    print(f"Куб с точными UV добавлен в объект {obj.name} в точке {location}")

def main():
    cont = bge.logic.getCurrentController()
    mouse = cont.sensors["RMB"]

    if mouse.positive and mouse.status == bge.logic.KX_INPUT_JUST_ACTIVATED:
        cast_ray_from_camera()

main()



6/6

