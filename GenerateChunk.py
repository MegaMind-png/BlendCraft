import bpy
import bmesh

def get_block_at_position(grid, x, y, z):
    """ Проверяет, есть ли блок в указанной позиции """
    return grid.get((x, y, z), 0)

def create_face(bm, verts):
    """Создаёт грань по переданным вершинам"""
    face_verts = [bm.verts.new(v) for v in verts]
    bm.faces.new(face_verts)

def generate_block(bm, grid, x, y, z, size=1):
    """Создаёт грани блока, если соседний блок отсутствует"""
    half_size = size / 2
    px, py, pz = x * size, y * size, z * size
    
    verts = {
        'bottom': [(px - half_size, py - half_size, pz - half_size),
                   (px + half_size, py - half_size, pz - half_size),
                   (px + half_size, py + half_size, pz - half_size),
                   (px - half_size, py + half_size, pz - half_size)],
        'top': [(px - half_size, py - half_size, pz + half_size),
                (px + half_size, py - half_size, pz + half_size),
                (px + half_size, py + half_size, pz + half_size),
                (px - half_size, py + half_size, pz + half_size)],
        'left': [(px - half_size, py - half_size, pz - half_size),
                 (px - half_size, py - half_size, pz + half_size),
                 (px - half_size, py + half_size, pz + half_size),
                 (px - half_size, py + half_size, pz - half_size)],
        'right': [(px + half_size, py - half_size, pz - half_size),
                  (px + half_size, py - half_size, pz + half_size),
                  (px + half_size, py + half_size, pz + half_size),
                  (px + half_size, py + half_size, pz - half_size)],
        'front': [(px - half_size, py - half_size, pz - half_size),
                  (px + half_size, py - half_size, pz - half_size),
                  (px + half_size, py - half_size, pz + half_size),
                  (px - half_size, py - half_size, pz + half_size)],
        'back': [(px - half_size, py + half_size, pz - half_size),
                 (px + half_size, py + half_size, pz - half_size),
                 (px + half_size, py + half_size, pz + half_size),
                 (px - half_size, py + half_size, pz + half_size)]
    }
    
    if get_block_at_position(grid, x + 1, y, z) == 0:
        create_face(bm, verts['right'])
    if get_block_at_position(grid, x - 1, y, z) == 0:
        create_face(bm, verts['left'])
    if get_block_at_position(grid, x, y + 1, z) == 0:
        create_face(bm, verts['back'])
    if get_block_at_position(grid, x, y - 1, z) == 0:
        create_face(bm, verts['front'])
    if get_block_at_position(grid, x, y, z + 1) == 0:
        create_face(bm, verts['top'])
    if get_block_at_position(grid, x, y, z - 1) == 0:
        create_face(bm, verts['bottom'])

def create_voxel_mesh(grid, size=1):
    """Создаёт воксельную сетку"""
    mesh = bpy.data.meshes.new(name="VoxelMesh")
    obj = bpy.data.objects.new("VoxelObject", mesh)
    bpy.context.collection.objects.link(obj)
    
    bm = bmesh.new()
    
    for (x, y, z), value in grid.items():
        if value != 0:
            generate_block(bm, grid, x, y, z, size)
    
    bm.to_mesh(mesh)
    bm.free()

def create_voxel_grid(dim_x=5, dim_y=5, dim_z=5):
    """Создаёт тестовую воксельную сетку"""
    grid = {}
    for x in range(dim_x):
        for y in range(dim_y):
            for z in range(dim_z):
                grid[(x, y, z)] = 1  # Заполняем все блоки
    return grid

# Создаём воксельную сетку размером 5x5x5
voxel_grid = create_voxel_grid(5, 5, 5)
create_voxel_mesh(voxel_grid)
