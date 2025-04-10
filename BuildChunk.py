import bge
import bpy
import bmesh
import json
import time
from mathutils import Vector

cont = bge.logic.getCurrentController()
sensor = cont.sensors["Keyboard"]

if sensor.positive and sensor.status == bge.logic.KX_INPUT_JUST_ACTIVATED:

    start_time = time.time()

    file_path = bpy.path.relpath("//chunk_data.json")
    with open(bpy.path.abspath(file_path), 'r') as f:
        data = json.load(f)

    block_types = data['block_types']
    chunks = data['chunks']

    material_name = "TextureAtlas"
    if material_name in bpy.data.materials:
        mat = bpy.data.materials[material_name]
    else:
        mat = bpy.data.materials.new(name=material_name)

    def get_block_object(block_name):
        if block_name in bpy.data.objects:
            return bpy.data.objects[block_name]
        else:
            print(f"Объект {block_name} не найден в сцене!")
            return None

    for chunk_name, chunk_data in chunks.items():
        if chunk_name.startswith("#"):
            print(f"Чанк {chunk_name} пропущен (закомментирован).")
            continue

        position = Vector(chunk_data['position'])
        blocks_data = chunk_data['blocks']
        blocks_length = len(blocks_data)

        # Вычисляем mesh_offset на основе position
        mesh_offset = Vector((
            -7.5 - position.x,
            -7.5 - position.y,
             7.5 - position.z
        ))

        mesh_data = bpy.data.meshes.new(name=f"Chunk_{chunk_name}")
        obj = bpy.data.objects.new(chunk_name, mesh_data)
        bpy.context.scene.collection.objects.link(obj)

        bm_target = bmesh.new()
        uv_layer_target = bm_target.loops.layers.uv.new("UVMap")

        chunk_size = 16
        total_blocks = chunk_size * chunk_size * chunk_size

        for z in reversed(range(chunk_size)):
            for y in range(chunk_size):
                for x in range(chunk_size):
                    block_index = z * chunk_size * chunk_size + y * chunk_size + x
                    data_index = block_index * 2
                    if data_index + 1 >= blocks_length:
                        continue

                    create_block = blocks_data[data_index] == '1'
                    if create_block:
                        block_id = blocks_data[data_index + 1]
                        block_name = block_types.get(block_id)
                        if block_name:
                            block_object = get_block_object(block_name)
                            if block_object and block_object.type == 'MESH':
                                bm_source = bmesh.new()
                                bm_source.from_mesh(block_object.data)

                                uv_layer_source = bm_source.loops.layers.uv.active or bm_source.loops.layers.uv.verify()

                                z_offset = (chunk_size - 1 - z)
                                block_offset = position + Vector((x, y, -z_offset)) + mesh_offset

                                vert_map = {}
                                for v in bm_source.verts:
                                    new_vert = bm_target.verts.new(v.co + block_offset)
                                    vert_map[v] = new_vert

                                for f in bm_source.faces:
                                    try:
                                        new_face = bm_target.faces.new([vert_map[v] for v in f.verts])
                                        for loop_source, loop_target in zip(f.loops, new_face.loops):
                                            loop_target[uv_layer_target].uv = loop_source[uv_layer_source].uv
                                    except:
                                        pass

                                bm_source.free()

        bm_target.to_mesh(mesh_data)
        bm_target.free()
        obj.data = mesh_data

        if len(obj.data.materials) == 0:
            obj.data.materials.append(mat)
        else:
            obj.data.materials[0] = mat

        obj.location = position

        print(f"Чанк {chunk_name} с позицией {chunk_data['position']} сгенерирован и материал применен.")

    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Генерация всех чанков завершена за {execution_time:.2f} секунд.")