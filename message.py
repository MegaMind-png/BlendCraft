import bge
from collections import OrderedDict
import json
import os
import bmesh
import bpy
from mathutils import Vector

class Component(bge.types.KX_PythonComponent):
    # Put your arguments here of the format ("key", default_value).
    # These values are exposed to the UI.
    args = OrderedDict([
    ])

    def start(self, args):
        # Put your initialization code here, args stores the values from the UI.
        # self.object is the owner object of this component.
        # self.object.scene is the main scene.
        
        path = os.path.dirname(os.path.realpath(__file__))
        
        self.chunk_data = {}
        
        with open(path + '\\chunk_data.json') as f:
            self.chunk_data = json.load(f)

        self.load_chunks()
    
    def load_chunks(self):
        i = 0
        #print(i)
        for chunk_name in self.chunk_data["chunks"]:
            if chunk_name[0] == "#":
                continue
            
            chunk = self.chunk_data["chunks"][chunk_name]
            chunk_position = Vector((chunk["position"][0], chunk["position"][1], chunk["position"][2]))
            mesh_offset = Vector((
            -7.5 - chunk_position.x,
            -7.5 - chunk_position.y,
             7.5 - chunk_position.z
            ))

            mesh_data = bpy.data.meshes.new(name="Chunk_Mesh")
            obj = bpy.data.objects.new("Chunk" + str(i), mesh_data)
            bpy.context.scene.collection.objects.link(obj)
            bm_target = bmesh.new()
            uv_layer_target = bm_target.loops.layers.uv.new("UVMap")  # Create UV layer for target mesh
            chunk_size = 16

            blocks_length = len(chunk["blocks"]) // 2

            for block_index in range(blocks_length):
                block = chunk["blocks"][block_index * 2 + 1]
                block_show = chunk["blocks"][block_index * 2]
                x = (block_index % chunk_size) + chunk_position.x
                y = ((block_index // chunk_size) % chunk_size) + chunk_position.y
                z = (block_index // (chunk_size * chunk_size)) + chunk_position.z

                block_type = self.chunk_data["block_types"][block]
                
                if block_show == "0":
                    continue

                block_object = bpy.data.objects[block_type]

                bm_source = bmesh.new()
                bm_source.from_mesh(block_object.data)

                # Get or verify active UV layer from the source (creates one if it doesn't exist)
                uv_layer_source = bm_source.loops.layers.uv.active or bm_source.loops.layers.uv.verify()

                z_offset = (chunk_size - 1 - z)
                block_offset = chunk_position + Vector((x, y, -z_offset)) + mesh_offset

                vert_map = {}
                for v in bm_source.verts:
                    new_vert = bm_target.verts.new(v.co + block_offset)
                    vert_map[v] = new_vert

                for f in bm_source.faces:
                    try:
                        new_face = bm_target.faces.new([vert_map[v] for v in f.verts])
                        for loop_source, loop_target in zip(f.loops, new_face.loops):
                            loop_target[uv_layer_target].uv = loop_source[uv_layer_source].uv
                        new_face.material_index = f.material_index
                    except Exception:
                        # Ignore faces that already exist
                        pass  
                    # End for f in bm_source.faces
                bm_source.free()

            bm_target.to_mesh(mesh_data)
            bm_target.free()

            material_name = "TextureAtlas"
            if material_name in bpy.data.materials:
                mat = bpy.data.materials[material_name]
            else:
                mat = bpy.data.materials.new(name=material_name)
            if len(obj.data.materials) == 0:
                obj.data.materials.append(mat)
            else:
                obj.data.materials[0] = mat

            obj.data = mesh_data

    def update(self):
        # Put your code executed every logic step here.
        # self.object is the owner object of this component.
        # self.object.scene is the main scene.
        pass
