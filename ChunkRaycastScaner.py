import bge

def update():
    scene = bge.logic.getCurrentScene()
    objects = scene.objects
    owner = bge.logic.getCurrentController().owner  # Объект, испускающий лучи
    radius = 50.0  # Радиус сканирования

    for obj in objects:
        if (obj == owner or not hasattr(obj, 'meshes') or len(obj.meshes) == 0 
            or not obj.visible):
            continue  # Пропускаем сам объект, объекты без меша и скрытые объекты

        distance = owner.getDistanceTo(obj)
        if distance > radius:
            continue  # Пропускаем объекты за пределами радиуса

        # По умолчанию луч зелёный
        color = [0, 1, 0]

        # Проверяем, что на пути нет других объектов
        hit, pos, normal = owner.rayCast(obj.worldPosition, owner.worldPosition)
        if hit and hit != obj and hasattr(hit, 'meshes') and len(hit.meshes) > 0 and hit.visible:
            color = [1, 0, 0]  # Если есть препятствие, красный цвет

        bge.render.drawLine(owner.worldPosition, obj.worldPosition, color)

def main():
    update()

main()
