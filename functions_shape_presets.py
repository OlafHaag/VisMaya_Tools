import os
import bpy
from bpy.props import *
from ast import literal_eval
from math import *


def show_active_preset(self, context):
    """
    Always shows name and category for highlighted preset in list.
    """
    obj = bpy.context.object
    if obj.shape_preset_index >= 0:
        obj.new_preset_name = obj.shape_preset_list[obj.shape_preset_index].name
        # refresh the category_name StringProperty
        if obj.category_name != obj['shape_preset_data'][obj.new_preset_name]['_category']:
            obj.category_name = obj['shape_preset_data'][obj.new_preset_name]['_category']


def category_items(self, context):
    """
    Updates entries of EnumProperty
    """
    obj = bpy.context.object
    categories = [(cat, cat, '') for cat in obj['shape_preset_data']['_categories_list'].keys() if
                  cat not in ['various', '_old_cat']]
    categories.sort(reverse=True)
    if 'various' in obj['shape_preset_data']['_categories_list'].keys():
        categories.insert(0, ('various', 'various', ''))
    return categories


def set_category(self, context):
    """
    Set a category for highlighted preset.
    """
    obj = bpy.context.object
    category = obj.category_name
    # get the preset name that will have its category changed
    preset_name = obj.new_preset_name
    # set the default category if category name is empty
    if category == '':
        obj.category_name = '<empty>'
        category = obj.category_name
        update_category_list(category)
    # change its category
    if category != obj['shape_preset_data'][preset_name]['_category']:
        obj['shape_preset_data'][preset_name]['_category'] = category
        update_category_list(category)
    
    # let's check if user has a <various> category or not => happens when not all presets are displayed AND displayed presets are from different categories
    # number of presets displayed in list
    nb_presets = len([preset for preset in obj.shape_preset_list.keys()])
    # total number of presets minus special ones : 'as _categories_list' and '_various'
    tot_presets = len([preset for preset in obj['shape_preset_data'].keys()]) - 2
    # check the number of different categories displayed in list - 'set' function removes doubles
    categories = list(set([obj['shape_preset_data'][preset]['_category'] for preset in obj.shape_preset_list.keys()]))
    
    # when to display the various category :
    if nb_presets < tot_presets and len(categories) > 1:
        for preset in obj.shape_preset_list.keys():
            obj['shape_preset_data'][preset]['_various'] = True
            obj['shape_preset_data']['_various'][preset] = preset
        obj['shape_preset_data']['_categories_list']['various'] = 'various'
        obj.preset_category = 'various'
    
    # when to display chosen category
    elif nb_presets < tot_presets and len(categories) == 1 and obj.preset_category != category:
        obj.preset_category = category
    
    # when to display the <All> category
    elif nb_presets == tot_presets:
        obj.preset_category = 'All'


def categorize():
    """
    Set a category for checked presets.
    """
    obj = bpy.context.object
    category = obj.category_name
    # get all presets that will have their categories changed
    presets = [preset for preset in obj.shape_preset_list.keys() if obj.shape_preset_list[preset].select_preset]
    # change the categories
    for preset in presets:
        obj['shape_preset_data'][preset]['_category'] = category
    # update_category_list(category)
    # show the category
    
    obj.preset_category = category


def update_category_list(category):
    """
    Updates the _categories_list in shape_preset_data dict.
    Created category is added to dict. If category already exists, it is simply replaced.
    If a category is not used anymore, then it is popped from dict.
    """
    obj = bpy.context.object
    # update the _categories_list data
    obj['shape_preset_data']['_categories_list'][category] = category
    
    # now we will clean the _categories_list data of unused categories. 
    # First we need a temporary list to gather the categories to keep
    used_categories = [obj['shape_preset_data'][preset]['_category'] for preset in obj['shape_preset_data'].keys() if
                       preset not in ['_categories_list', '_various']]
    
    # Now we build a list with old registered categories
    current_categories = [cat for cat in obj['shape_preset_data']['_categories_list'].keys() if cat != '_old_cat']
    
    # And compare the 2 lists to remove the corresponding key in _categories_list
    for cat in current_categories:
        if cat not in used_categories and cat != 'All':  # 'All' category must always be available
            obj['shape_preset_data']['_categories_list'].pop(cat)


def show_category(self, context):
    """
    Updates the list of presets according to selected category
    """
    obj = bpy.context.object
    cat = obj.preset_category
    
    old_cat = obj['shape_preset_data']['_categories_list']['_old_cat']
    
    remove_various()
    
    if cat != old_cat:
        obj.shape_preset_list.clear()
        name = obj.new_preset_name
        obj.shape_preset_index = -1
        
        if cat == 'All':
            presets = [preset for preset in obj['shape_preset_data'].keys() if
                       preset not in ['_categories_list', '_various']]
        elif cat == 'various':
            presets = [preset for preset in obj['shape_preset_data'].keys() if
                       preset not in ['_categories_list', '_various'] and obj['shape_preset_data'][preset][
                           '_various'] == True]
        else:
            presets = [preset for preset in obj['shape_preset_data'].keys() if
                       preset not in ['_categories_list', '_various'] and obj['shape_preset_data'][preset][
                           '_category'] == cat]
        
        for preset in presets:
            obj.shape_preset_list.add().name = preset
            # if preset != 'All_to_0': test without it as the preset still has the attributes
            obj.shape_preset_list[preset].influence = obj['shape_preset_data'][preset]['_infl']
            obj.shape_preset_list[preset].select_preset = obj['shape_preset_data'][preset]['_box']
        # keep highlighting on the current preset if preset is in category           
        if name in presets:
            obj.shape_preset_index = obj.shape_preset_list.keys().index(name)
        else:
            obj.shape_preset_index = 0
        
        obj['shape_preset_data']['_categories_list']['_old_cat'] = cat
        if obj.preset_category != cat:
            obj.preset_category = cat


def remove_various():
    """
    Removes the temp category 'various'
    """
    obj = bpy.context.object
    cat = obj.preset_category
    if cat != 'various' and 'various' in obj['shape_preset_data']['_categories_list'].keys():
        # unmark presets that were in temp various category
        for preset in obj['shape_preset_data']['_various'].keys():
            obj['shape_preset_data'][preset]['_various'] = False
        # and clear the dictionnary
        obj['shape_preset_data']['_various'] = {}
        # and delete the 'various' category in the categories list
        obj['shape_preset_data']['_categories_list'].pop('various')


def update_select_all(self, context):
    """
    Updates "Select all presets" checkbox when all presets are selected/deselected manually.
    """
    obj = bpy.context.object
    presets = [preset for preset in obj.shape_preset_list.keys() if preset != 'All_to_0']
    len_presets = len(presets)
    i = 0
    for preset in presets:
        if obj.shape_preset_list[preset].select_preset:
            i += 1
        else:
            i -= 1
    
    if i == len_presets and not obj.select_all_presets:
        obj.select_all_presets = True
    elif i == -len_presets and obj.select_all_presets:
        obj.select_all_presets = False
    
    # update data dict for registering checkbox state
    name = self.name
    obj['shape_preset_data'][name]['_box'] = obj.shape_preset_list[name].select_preset


def name_increment(name, names_list):
    """
    Generate a new preset name. If the name already exists, it is automatically incremented.
    """
    i = 0
    while name in names_list:
        i += 1
        if name[-3:].isdigit() and name[-4] == '.':
            name = '{}{:03d}'.format(name[:len(name) - 3], i)
        else:
            name += '.001'
    return name


def preset_influence(self, context):
    """
    Set the preset influence.
    """
    obj = bpy.context.object
    temp_dict = {}
    # update data dict for registering current influence value - used for categories implementation
    name = self.name
    obj['shape_preset_data'][name]['_infl'] = obj.shape_preset_list[name].influence
    presets = [preset for preset in obj['shape_preset_data'].keys() if preset not in ['_categories_list', '_various']]
    for preset in presets:
        for shape, value in obj['shape_preset_data'][preset].items():
            if shape in obj.data.shape_keys.key_blocks.keys():
                if shape not in temp_dict.keys():
                    temp_dict[shape] = value * obj['shape_preset_data'][preset]['_infl']
                elif temp_dict[shape] < value * obj['shape_preset_data'][preset]['_infl']:
                    temp_dict[shape] = value * obj['shape_preset_data'][preset]['_infl']
                obj.data.shape_keys.key_blocks[shape].value = temp_dict[shape]


def save_shape_preset():
    """
    Save the current shape key values in a preset dict.
    Only visible shape keys with value > 0 are saved.
    """
    obj = bpy.context.object
    level = obj.group_level_value
    try:
        obj['shape_preset_data']
    except:
        obj['shape_preset_data'] = {}
        obj['shape_preset_data']['_various'] = {}
        obj['shape_preset_data']['_categories_list'] = {'All': 'All', '_old_cat': 'All', '<empty>': '<empty>'}
    
    shape_values = {}
    
    # get only visible and used shape keys for new preset
    shape_keys_list = [shape for shape in obj.data.shape_keys.key_blocks.keys() if
                       obj.data.shape_keys.key_blocks[shape].mute == False and
                       obj.data.shape_keys.key_blocks[shape].value != 0]
    
    if len(shape_keys_list) != 0:
        if obj.shapekeys_group_mode:
            group_ref = []
            for elt in shape_keys_list:
                if elt[:level] not in group_ref:
                    group_ref.append(elt[:level])
            shape_keys_list = [shape for shape in obj.data.shape_keys.key_blocks.keys() if
                               shape[:level] in group_ref]
        
        for shape in shape_keys_list:
            shape_values[shape] = obj.data.shape_keys.key_blocks[shape].value
        
        preset_name = name_increment('Preset', obj.shape_preset_list.keys())
        obj.shape_preset_list.add().name = preset_name
    
    # if all shape keys are equal to 0, register all shape keys values at 0 in shape_values dict
    else:
        for index, shape in enumerate(obj.data.shape_keys.key_blocks.keys()):
            if index > 0:
                shape_values[shape] = 0
        preset_name = 'All_to_0'
        
        # remove already existing All_to_0 preset
        if 'All_to_0' in obj.shape_preset_list.keys():
            obj.shape_preset_list.remove(obj.shape_preset_list.keys().index('All_to_0'))
            obj['shape_preset_data'].pop('All_to_0')
            if obj.shape_preset_index > len(obj.shape_preset_list) - 1:
                obj.shape_preset_index = len(obj.shape_preset_list) - 1
        obj.shape_preset_list.add().name = preset_name
    
    shape_values['_category'] = '<empty>'
    shape_values['_infl'] = 1
    shape_values['_box'] = False
    shape_values['_various'] = False
    shapes_dict = dict(shape_values)
    obj['shape_preset_data'][preset_name] = shapes_dict
    obj.shape_preset_index = len(obj.shape_preset_list) - 1
    obj.active_shape_key_index = 0
    obj.new_preset_name = obj.shape_preset_list[obj.shape_preset_index].name


def apply_shape_preset(type):
    """
    Apply the selected preset to shape keys.
    If some registered shape names don't match the current shape keys for some reason, 
    the shapes are removed from preset data.
    
    If Raw Apply selected, the preset values are applied to corresponding shape keys.
    Other shape key values are set to zero.
    
    If Gentle Apply selected, the preset values are applied with no changes to other shape keys.
    """
    obj = bpy.context.object
    
    try:
        presets = obj['shape_preset_data']
    except:
        delete_shape_preset()
    if type[0] == 'S':
        selected_preset = [obj.shape_preset_list[obj.shape_preset_index].name]
        apply_values(selected_preset)
        if type == 'S_RAW':
            values_to_zero(selected_preset)
        del selected_preset
    else:
        checked_presets = [preset for preset in obj.shape_preset_list.keys() if
                           obj.shape_preset_list[preset].select_preset]
        apply_values(checked_presets)
        if type == 'M_RAW':
            values_to_zero(checked_presets)
        del checked_presets


def apply_values(selection):
    obj = bpy.context.object
    presets = obj['shape_preset_data']
    values = {}
    # compare and collect all values to get the highest value for each shape
    for preset in selection:
        for key, value in presets[preset].items():
            if key not in values.keys() or value > values[key]:
                values[key] = value
    # apply values            
    for shape in values.keys():
        if shape in obj.data.shape_keys.key_blocks.keys():
            obj.data.shape_keys.key_blocks[shape].value = values[shape]
            obj.data.shape_keys.key_blocks[shape].mute = False
    # update used presets   
    for preset in selection:
        for shape in presets[preset].keys():
            # if shape doesn't exist anymore, remove it from preset     
            if shape not in obj.data.shape_keys.key_blocks.keys():
                del presets[preset][shape]
        # set preset influence to 1
        obj.shape_preset_list[preset].influence = 1.0
    del values


def values_to_zero(selection):
    obj = bpy.context.object
    presets = obj['shape_preset_data']
    shapes = []
    # collect all shapes that will be used together
    for preset in selection:
        for shape in presets[preset].keys():
            if shape not in shapes:
                shapes.append(shape)
    # unused shapes will be set to zero
    for preset in selection:
        for shape in obj.data.shape_keys.key_blocks.keys():
            if shape not in shapes:
                obj.data.shape_keys.key_blocks[shape].value = 0
    # other / unchecked preset influences are set to zero
    for preset in obj.shape_preset_list.keys():
        if preset not in selection:
            obj.shape_preset_list[preset].influence = 0.0


def delete_shape_preset():
    """
    Selected preset is removed from preset data dict so as the associate UI_List entry
    """
    obj = bpy.context.object
    selected_preset = obj.shape_preset_list[obj.shape_preset_index].name
    # remove the preset in UI_list
    obj.shape_preset_list.remove(obj.shape_preset_index)
    try:
        obj['shape_preset_data'].pop(selected_preset)
    except:
        pass
    if obj.shape_preset_index > len(obj.shape_preset_list) - 1:
        obj.shape_preset_index = len(obj.shape_preset_list) - 1
    # if there's no preset anymore, set the name preset field to ''
    if len(obj.shape_preset_list.keys()) == 0:
        obj.new_preset_name = ''
        obj['shape_preset_data']['_categories_list'] = {}
        obj['shape_preset_data']['_categories_list'] = {'All': 'All', '_old_cat': 'All'}
        obj.preset_category = 'All'
        obj.category_name = 'All'


def rename_shape_preset(self, context):
    """
    Rename selected preset.
    This function is used as update function for the StringProperty operator.
    """
    obj = bpy.context.object
    if len(obj.shape_preset_list.keys()) > 0 and obj.new_preset_name != obj.shape_preset_list[
        obj.shape_preset_index].name:
        if obj.new_preset_name != '':
            name = name_increment(obj.new_preset_name, obj.shape_preset_list.keys())
            for key in obj['shape_preset_data'].keys():
                if key == obj.shape_preset_list[obj.shape_preset_index].name:
                    obj['shape_preset_data'][name] = obj['shape_preset_data'][key]
                    obj['shape_preset_data'].pop(key)
            obj.shape_preset_list[obj.shape_preset_index].name = name
        obj.new_preset_name = obj.shape_preset_list[obj.shape_preset_index].name


def select_all_presets(self, context):
    """
    Select all presets for keyframe insertion purpose.
    """
    obj = bpy.context.object
    presets = [preset for preset in obj.shape_preset_list.keys() if preset != 'All_to_0']
    len_presets = len(presets)
    checked_presets = [preset for preset in obj.shape_preset_list.keys() if
                       preset != 'All_to_0' and obj.shape_preset_list[preset].select_preset == True]
    
    # comparison between len_presets and checked_presets is used to avoid the select_all_presets function to be called when select_all_button state is updated.
    if len(checked_presets) != len_presets and obj.select_all_presets:
        for idx, elt in enumerate(obj.shape_preset_list.keys()):
            if obj.shape_preset_list[idx].name != 'All_to_0':
                obj.shape_preset_list[idx].select_preset = True
    elif len(checked_presets) != 0 and not obj.select_all_presets:
        for idx, elt in enumerate(obj.shape_preset_list):
            obj.shape_preset_list[idx].select_preset = False


def insert_keyframes():
    """
    Insert keyframes on shape keys used by selected preset.
    """
    obj = bpy.context.object
    shape_keys = obj.data.shape_keys.key_blocks.keys()
    active_preset = obj.shape_preset_list[obj.shape_preset_index].name
    
    selected = [preset for preset in obj.shape_preset_list.keys() if obj.shape_preset_list[preset].select_preset]
    
    if selected != []:
        for preset in selected:
            for key in obj['shape_preset_data'][preset].keys():
                if key in shape_keys:
                    obj.data.shape_keys.key_blocks[key].keyframe_insert('value')
    else:
        for key in obj['shape_preset_data'][active_preset].keys():
            if key in shape_keys:
                obj.data.shape_keys.key_blocks[key].keyframe_insert('value')
    
    # refresh dopesheet & graph editor
    bpy.context.scene.frame_current += 0


#
#    Shape Keys Quick Tools
#


class ShapeKeysQuickTools:
    
    def __init__(self):
        self.obj = bpy.context.object
        self.shape_keys_list = self.obj.data.shape_keys.key_blocks.keys()
    
    def reset_shape_keys(self):
        """
        Set all shape key values to 0.
        """
        for shape in self.shape_keys_list:
            self.obj.data.shape_keys.key_blocks[shape].value = 0
        # refresh Shape Keys Panel
        self.obj.active_shape_key_index += 0
        
        for preset in self.obj.shape_preset_list.keys():
            self.obj.shape_preset_list[preset].influence = 0.0
    
    def mute_shape_keys(self):
        """
        Mute all shape keys.
        """
        for shape in self.shape_keys_list:
            if self.obj.data.shape_keys.key_blocks[shape] == self.obj.data.shape_keys.key_blocks[0]:
                self.obj.data.shape_keys.key_blocks[shape].mute = False
            else:
                self.obj.data.shape_keys.key_blocks[shape].mute = True
        self.obj.active_shape_key_index += 0
    
    def unmute_shape_keys(self):
        """
        Unmute all shape keys.
        """
        for shape in self.shape_keys_list:
            self.obj.data.shape_keys.key_blocks[shape].mute = False
        self.obj.active_shape_key_index += 0


#
#    Import Export Presets
#

def readable_str_dict(dict):
    str_dict = str(dict)
    ndict = ''
    # i will set the number of spaces for indentation
    i = 0
    # j will determine when insert a new line between keys
    j = 0
    specials = ['{', '}', ',']
    for char in str_dict:
        if char not in specials:
            ndict += char
        elif char == ',':
            ndict += char + '\n' + (i - 1) * ' '
        elif char == '{':
            ndict += '\n' + i * ' ' + char + '\n'
            i += 4
            ndict += i * ' '
        elif char == '}':
            i -= 4
            ndict += '\n' + i * ' ' + char
    return ndict


def export_presets(filepath):
    """
    Export the shape key presets in a .txt file.
    """
    obj = bpy.context.object
    presets = readable_str_dict(obj['shape_preset_data'].to_dict())
    with open(filepath, 'w') as file:
        file.write(presets)


def import_presets(filename):
    """
    Import shape key presets from a .txt file. 
    The string is converted to dict data with ast.literal_eval()
    """
    obj = bpy.context.object
    # delete properties
    obj['shape_preset_index'] = 0
    obj['new_preset_name'] = ''
    obj['shape_preset_list'] = []
    # get the presets in the .txt file
    with open(filename, 'r') as file:
        obj['shape_preset_data'] = literal_eval(file.read())
    
    try:
        obj['shape_preset_data'].pop('_various')
    except:
        pass
    
    presets = [preset for preset in obj['shape_preset_data'].keys() if preset != '_categories_list']
    
    for preset in presets:
        obj['shape_preset_data'][preset]['_various'] = 0
    
    presets.sort()
    # new list of elements for UI_List
    for elt in presets:
        obj.shape_preset_list.add().name = elt
    obj.new_preset_name = obj.shape_preset_list[obj.shape_preset_index].name


#
#   Preset Management
#


def clean_presets():
    """
    Check all presets. If a saved shape key doesn't exist anymore, it is removed.
    If the preset gets empty, it is removed too.
    """
    obj = bpy.context.object
    shape_key_list = obj.data.shape_keys.key_blocks.keys()
    # clean all presets - delete shape key values if the concerned shape key is not found
    for preset in obj['shape_preset_data'].keys():
        if preset not in ['_categories_list', '_various']:
            for shape, value in obj['shape_preset_data'][preset].items():
                if shape not in shape_key_list and shape not in ['_various', '_category', '_box', '_infl']:
                    obj['shape_preset_data'][preset].pop(shape)
    
    # delete empty presets - if a preset has lost all its values, it is removed from data
    for preset, data in obj['shape_preset_data'].to_dict().items():
        if len(data) == 4:
            obj['shape_preset_data'].pop(preset)
            for index, name in enumerate(obj.shape_preset_list.keys()):
                if obj['shape_preset_list'][index]['name'] == preset:
                    obj.shape_preset_list.remove(index)
                    break
    if len(obj.shape_preset_list) == 0:
        obj['new_preset_name'] = ''
        obj['shape_preset_index'] = -1


def sort_presets():
    """
    Sort presets in the UI_List
    """
    obj = bpy.context.object
    presets = [preset for preset in obj.shape_preset_list.keys() if preset != "All_to_0"]
    presets.sort()
    if "All_to_0" in obj.shape_preset_list.keys():
        presets.insert(0, "All_to_0")
    
    for idx, preset in enumerate(presets):
        obj.shape_preset_index = obj.shape_preset_list.keys().index(preset)
        start_position = obj.shape_preset_index
        final_position = idx
        
        while final_position != start_position:
            if start_position < final_position:
                obj.shape_preset_list.move(start_position, start_position + 1)
                start_position += 1
            elif start_position > final_position:
                obj.shape_preset_list.move(start_position, start_position - 1)
                start_position -= 1
    
    obj.new_preset_name = obj.shape_preset_list[obj.shape_preset_index].name


def invert_selection():
    """
    Invert checked presets in the UI_List
    """
    obj = bpy.context.object
    # create a list with values for inverted selection
    sample = []
    for preset in obj.shape_preset_list.keys():
        if preset != 'All_to_0' and obj.shape_preset_list[preset].select_preset:
            sample.append(0)
        else:
            sample.append(1)
            # uncheck all presets before inversion
    for preset in obj.shape_preset_list.keys():
        if preset != 'All_to_0':
            obj.shape_preset_list[preset].select_preset = False
    # apply inverted selection with the sample list     
    for idx, preset in enumerate(obj.shape_preset_list.keys()):
        if preset != 'All_to_0':
            if sample[idx] == 0:
                obj.shape_preset_list[preset].select_preset = False
            else:
                obj.shape_preset_list[preset].select_preset = True
    # get rid of sample        
    del sample


def delete_all_presets():
    """
    Delete all presets without condition.
    """
    obj = bpy.context.object
    obj.preset_category = 'All'
    obj.category_name = 'All'
    obj['shape_preset_index'] = -1
    obj['shape_preset_data'] = {}
    obj['new_preset_name'] = ''
    obj['shape_preset_list'] = []
    obj['shape_preset_data']['_various'] = {}
    obj['shape_preset_data']['_categories_list'] = {}
    obj['shape_preset_data']['_categories_list'] = {'All': 'All', '_old_cat': 'All'}


def sort_shape_keys():
    """
    Sort all shape keys. But "Basis" -or whatever the name of first basic shape is- stays on top."
    """
    obj = bpy.context.object
    sk_list = obj.data.shape_keys.key_blocks.keys()
    temp_shapekeys_list = [shape for shape in sk_list if sk_list.index(shape) > 0]
    temp_shapekeys_list.sort()
    temp_shapekeys_list.insert(0, obj.data.shape_keys.key_blocks[0].name)
    
    for shape in temp_shapekeys_list:
        # the shape keys list must be redifined each time an item is sorted
        sk_list = obj.data.shape_keys.key_blocks.keys()
        # set active shape key to the current of temp_shapekeys_list
        obj.active_shape_key_index = sk_list.index(shape)
        # start position
        start_position = sk_list.index(shape)
        # position to reach
        final_position = temp_shapekeys_list.index(shape)
        
        while final_position != start_position:
            if start_position < final_position:
                sort_down()
                start_position += 1
            elif start_position > final_position:
                sort_up()
                start_position -= 1


def sort_down():
    bpy.ops.object.shape_key_move(type='DOWN')


def sort_up():
    bpy.ops.object.shape_key_move(type='UP')


def take_snapshot():
    obj = bpy.context.object
    scn = bpy.context.scene
    
    x_res = scn.render.resolution_x
    y_res = scn.render.resolution_y
    name = obj.new_preset_name
    filepath = 'C:/Users/Oliver/Desktop/Blender/' + name + '.png'
    
    # select only visible objects
    objects_to_hide = [object for object in scn.objects.keys() if
                       not bpy.data.objects[object].hide and object != obj.name]
    
    # hide visible objects 
    for object in objects_to_hide:
        bpy.data.objects[object].hide = True
    
    # set render resolution
    scn.render.resolution_x = 200
    scn.render.resolution_y = 200

    # get the original value of influence
    influence = obj.shape_preset_list[obj.shape_preset_index].influence

    # set the influence to 1 for accurate preset snapshot
    obj.shape_preset_list[obj.shape_preset_index].influence = 1.0
    
    obj.select = False
    bpy.ops.render.opengl()
    bpy.data.images['Render Result'].save_render(filepath=filepath)
    obj.select = True

    # set back the influence at its original value
    obj.shape_preset_list[obj.shape_preset_index].influence = influence
    
    # set render resolution to previous settings
    scn.render.resolution_x = x_res
    scn.render.resolution_y = y_res
    
    # restore visible objects
    for object in objects_to_hide:
        bpy.data.objects[object].hide = False


def update_presets():
    obj = bpy.context.object
    obj['shape_preset_data']['_categories_list'] = {'All': 'All', '_old_cat': 'All', '<empty>': '<empty>'}
    obj['shape_preset_data']['_various'] = {}
    for preset in obj.shape_preset_list.keys():
        obj['shape_preset_data'][preset]['_category'] = '<empty>'
        obj['shape_preset_data'][preset]['_infl'] = 1.0
        obj['shape_preset_data'][preset]['_box'] = False
        obj['shape_preset_data'][preset]['_various'] = False
        


















