import bpy

def write(filepath):
    obj = bpy.context.object
    presets = str(obj['shape_preset_data'].to_dict())
    with open(filepath, 'w') as file:
        file.write(presets)
