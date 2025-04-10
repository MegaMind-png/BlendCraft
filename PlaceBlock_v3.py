import bge
import bpy
import mathutils
import bmesh
import time

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

    result = bpy.context.scene.ray_cast(bpy.context.view_layer.depsgraph, camera_location, world_direction)

    if result[0]:
        hit_location = result[1]
        hit_normal = result[2]
        hit_object = result[4]

        if hit_object and hit_object.type == 'MESH':
            # Создаем bmesh для объекта
            bm = bmesh.new()
            bm.from_mesh(hit_object.data)
            
            # Находим ближайший полигон
            closest_face = None
            min_dist = float('inf')
            for face in bm.faces:
                center = face.calc_center_median()
                distance = (hit_location - center).length
                
                if distance < min_dist:
                    min_dist = distance
                    closest_face = face

            if closest_face:
                median = closest_face.calc_center_median()
                normal = closest_face.normal
                
                # Смещение и ориентация
                offset = 0.5
                dot_product = normal.dot(hit_normal)

                if dot_product > 0:
                    median += normal * offset
                else:
                    median -= normal * offset
                
                rotation = normal.to_track_quat('Z', 'Y').to_matrix().to_4x4()
                
                # Находим исходный объект для копирования
                source_object = bpy.data.objects.get('Board')
                if source_object and source_object.type == 'MESH':
                    # Создаем bmesh для источника
                    bm_source = bmesh.new()
                    bm_source.from_mesh(source_object.data)
                    
                    # Создаем bmesh для целевого объекта
                    bm_target = bmesh.new()
                    bm_target.from_mesh(hit_object.data)
                    
                    # Создаем UV-слой
                    uv_layer_target = bm_target.loops.layers.uv.verify()
                    uv_layer_source = bm_source.loops.layers.uv.active or bm_source.loops.layers.uv.verify()

                    # Матрицы преобразования
                    matrix_source = source_object.matrix_world
                    matrix_target_inv = hit_object.matrix_world.inverted()

                    # Словарь для соответствия вершин
                    vert_map = {}

                    # Копирование вершин
                    for v in bm_source.verts:
                        world_coord = matrix_source @ v.co
                        local_coord = matrix_target_inv @ world_coord + median
                        new_vert = bm_target.verts.new(local_coord)
                        vert_map[v] = new_vert

                    # Копирование граней
                    for f in bm_source.faces:
                        try:
                            new_face = bm_target.faces.new([vert_map[v] for v in f.verts])
                            
                            # Копирование UV-координат
                            for loop_source, loop_target in zip(f.loops, new_face.loops):
                                loop_target[uv_layer_target].uv = loop_source[uv_layer_source].uv
                        except:
                            pass

                    # Применяем изменения
                    bm_target.to_mesh(hit_object.data)
                    
                    # Освобождаем память
                    bm_source.free()
                    bm_target.free()

            # Освобождаем память
            bm.free()

    print(f"Время выполнения лучевого кастинга: {time.time() - start_time:.6f} секунд")

def main():
    """
    Основная функция
    """
    start_time = time.time()

    cont = bge.logic.getCurrentController()
    mouse = cont.sensors["RMB"]

    if mouse.positive and mouse.status == bge.logic.KX_INPUT_JUST_ACTIVATED:
        cast_ray_from_camera()

    print(f"Время выполнения всего скрипта: {time.time() - start_time:.6f} секунд")

main()