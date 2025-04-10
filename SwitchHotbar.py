import bge

# Получаем текущий контроллер и объект-владельца
controller = bge.logic.getCurrentController()
owner = controller.owner

# Список игровых свойств, которые мы переключаем
properties = ["slot1", "slot2", "slot3", "slot4", "slot5", "slot6", "slot7", "slot8", "slot9"]
block_properties = ["slot1_block", "slot2_block", "slot3_block", "slot4_block", "slot5_block", "slot6_block", "slot7_block", "slot8_block", "slot9_block"]

# Сопоставляем клавиши с индексами свойств
key_mapping = {
    bge.events.ONEKEY: 0,
    bge.events.TWOKEY: 1,
    bge.events.THREEKEY: 2,
    bge.events.FOURKEY: 3,
    bge.events.FIVEKEY: 4,
    bge.events.SIXKEY: 5,
    bge.events.SEVENKEY: 6,
    bge.events.EIGHTKEY: 7,
    bge.events.NINEKEY: 8
}

# Маппинг блоков
block_mapping = {
    1: "Glass",
    2: "Stone",
    3: "Brick",
    4: "Wool",
    5: "Turf",
    6: "Obsidian",
    7: "Board",
    8: "Concrete",
    9: "Clay"
}

# Получаем состояние клавиатуры
keyboard = bge.logic.keyboard

# Получаем текущую сцену и объект Camera
scene = bge.logic.getCurrentScene()
camera = scene.objects.get("Camera")  # Убедитесь, что объект называется "Camera"

# Проверяем нажатие клавиш и переключаем соответствующее свойство
for key, index in key_mapping.items():
    if keyboard.events[key] == bge.logic.KX_INPUT_JUST_ACTIVATED:
        # Сначала отключаем все свойства
        for prop in properties:
            owner[prop] = False
        # Включаем только одно свойство
        owner[properties[index]] = True

        # Получаем значение блока
        slot_block_value = owner[block_properties[index]]
        block_name = block_mapping.get(slot_block_value, "Unknown")

        # Устанавливаем значение в свойство Block объекта Camera
        if camera:  # Если объект Camera найден
            camera["Block"] = block_name
