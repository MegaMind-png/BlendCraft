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
        hit_location, hit_normal, hit_index, hit_object = result[1], result[2], result[3], result[4]
        
        if hit_object and hit_object.type == 'MESH':
            mesh = hit_object.data
            if hit_index >= 0:
                face = mesh.polygons[hit_index]
                median = face.center.copy()
                normal = face.normal.copy()
                
                # Смещение
                offset = 0.5 if normal.dot(hit_normal) > 0 else -0.5
                median += normal * offset
                
                # Ориентация
                rotation = normal.to_track_quat('Z', 'Y').to_matrix().to_4x4()
                
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
                    
                    matrix_source = source_object.matrix_world
                    matrix_target_inv = hit_object.matrix_world.inverted()
                    
                    bm_source.verts.ensure_lookup_table()
                    vert_map = {}
                    
                    for v in bm_source.verts:
                        world_coord = matrix_source @ v.co
                        local_coord = matrix_target_inv @ world_coord + median
                        vert_map[v] = bm_target.verts.new(local_coord)
                    
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