import bpy
import bmesh

def remove_overlapping_faces(obj, threshold=0.001):
    if obj.type != 'MESH':
        print("Выбранный объект не является мешем!")
        return
    
    mesh = obj.data
    bm = bmesh.new()
    bm.from_mesh(mesh)
    
    faces_to_remove = set()
    
    # Вычисляем центры всех полигонов
    face_centers = {face: face.calc_center_median() for face in bm.faces}
    
    for face1, center1 in face_centers.items():
        for face2, center2 in face_centers.items():
            if face1 != face2 and (center1 - center2).length < threshold:
                faces_to_remove.add(face1)
                faces_to_remove.add(face2)
    
    # Удаляем найденные пересекающиеся полигоны
    if faces_to_remove:
        print(f"Удаление {len(faces_to_remove)} пересекающихся полигонов")
        bmesh.ops.delete(bm, geom=list(faces_to_remove), context='FACES')
        
        # Обновляем меш
        bm.to_mesh(mesh)
    
    bm.free()

# Пример использования
obj = bpy.context.active_object
remove_overlapping_faces(obj)
