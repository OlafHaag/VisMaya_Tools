import bpy

def read(filename):
    obj = bpy.context.object
    with open(filename, "r") as file
        obj['shape_preset_data'] = 