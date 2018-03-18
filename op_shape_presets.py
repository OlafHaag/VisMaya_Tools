# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import bpy
from bpy.props import StringProperty
from . import functions_shape_presets as func
from bpy_extras.io_utils import (ExportHelper, ImportHelper)

class OBJECT_OT_SavePreset(bpy.types.Operator):
    bl_idname = 'save.preset'
    bl_label = 'Save'
    bl_description = 'Save actual shape keys values in a preset.'
    
    def execute(self, context):
        func.save_shape_preset()     
        return{'FINISHED'}
     
           
class OBJET_OT_DeletePreset(bpy.types.Operator):
    bl_idname = 'delete.preset'
    bl_label = 'Delete Preset'
    bl_description = 'Delete selected preset.'

    @classmethod
    def poll(cls, context):
        return (context.active_object and
                len(context.object.shape_preset_list) > 0)
   
    def execute(self, context):
        func.delete_shape_preset()
        return{'FINISHED'}

class OBJECT_OT_RawApply(bpy.types.Operator):
    bl_idname = 'raw.apply_button'
    bl_label = 'Apply Raw'
    bl_description = 'Apply highlighted preset values to shape keys. Unused shape keys are set to 0.'
 
    @classmethod
    def poll(cls, context):
        return (context.active_object and
                len(context.object.shape_preset_list) > 0)
                
    def execute(self, context):
        func.apply_shape_preset('S_RAW')
        return{'FINISHED'}

class OBJECT_OT_SetSingleCategory(bpy.types.Operator):
    bl_idname = 'category.for_hl'
    bl_label = ''
    bl_description = 'Set category to highlighted preset'
    
    @classmethod
    def poll(cls, context):
        obj = bpy.context.object
        return (context.active_object and
                len(context.object.shape_preset_list) > 0)
                
    def execute(self, context):
        func.set_category()
        return{'FINISHED'}       
        
class OBJECT_OT_SetMultiCategory(bpy.types.Operator):
    bl_idname = 'category.for_checked'
    bl_label = ''
    bl_description = 'Set category to checked presets'
    
    @classmethod
    def poll(cls, context):
        obj = bpy.context.object
        presets = [preset for preset in obj.shape_preset_list.keys() if obj.shape_preset_list[preset].select_preset]
        return (context.active_object and
                len(context.object.shape_preset_list) > 0 and
                len(presets) > 0)
                
    def execute(self, context):
        func.categorize()
        return{'FINISHED'}
        
        
class OBJECT_OT_MultiRawApply(bpy.types.Operator):
    bl_idname = 'multiraw.apply_button'
    bl_label = 'Multi Raw'
    bl_description = 'Apply checked presets values to shape keys. Unused shape keys are set to 0.'
 
    @classmethod
    def poll(cls, context):
        return (context.active_object and
                len(context.object.shape_preset_list) > 0)
                
    def execute(self, context):
        func.apply_shape_preset('M_RAW')
        return{'FINISHED'}

class OBJECT_OT_GentleApply(bpy.types.Operator):
    bl_idname = 'gentle.apply_button'
    bl_label = 'Apply Gentle'
    bl_description = 'Apply highlighted preset values only to registered shape keys.'

    @classmethod
    def poll(cls, context):
        return (context.active_object and
                len(context.object.shape_preset_list) > 0)
    
    def execute(self, context):
        func.apply_shape_preset('S_GENTLE')
        return{'FINISHED'}

class OBJECT_OT_MultiGentleApply(bpy.types.Operator):
    bl_idname = 'multigentle.apply_button'
    bl_label = 'Multi Gentle'
    bl_description = 'Apply checked presets values only to registered shape keys.'

    @classmethod
    def poll(cls, context):
        return (context.active_object and
                len(context.object.shape_preset_list) > 0)
    
    def execute(self, context):
        func.apply_shape_preset('M_GENTLE')
        return{'FINISHED'}        

class OBJECT_OT_InsertKeyframes(bpy.types.Operator):
    bl_idname = 'insert.keyframes'
    bl_label = 'Insert Keyframes'
    bl_description = 'Insert keyframes for all shape keys of selected presets.'

    @classmethod
    def poll(cls, context):
        return (context.active_object and
                len(context.object.shape_preset_list) > 0)
                
    def execute(self, context):
        func.insert_keyframes()
        return{'FINISHED'}

class OBJECT_OT_ResetShapeKeys(bpy.types.Operator):
    bl_idname = 'reset.shapekeys_button'
    bl_label = 'Reset'
    bl_description = 'All shape keys values are set to 0.'
    
    def execute(self, context):
        QT = func.ShapeKeysQuickTools()
        QT.reset_shape_keys()
        return{'FINISHED'}
        
class OBJECT_OT_SortShapeKeys(bpy.types.Operator):
    bl_idname = 'sort.shapekeys_button'
    bl_label = 'Sort'
    bl_description = 'All shape keys are sorted except the first one.'
    
    @classmethod
    def poll(cls, context):
        return (context.active_object and
                context.mode != 'EDIT_MESH')
    
    def execute(self, context):
        func.sort_shape_keys()
        return{'FINISHED'}

class OBJECT_OT_MuteAll(bpy.types.Operator):
    bl_idname = 'mute.all_button'
    bl_label = 'Mute'
    bl_description = 'All shape keys are muted except the first one.'
       
    def execute(self, context):
        QT = func.ShapeKeysQuickTools()
        QT.mute_shape_keys()
        return{'FINISHED'}
    
class OBJECT_OT_UnmuteAll(bpy.types.Operator):
    bl_idname = 'unmute.all_button'
    bl_label = 'Unmute'
    bl_description = 'All shape keys are unmuted.'
    
    def execute(self, context):
        QT = func.ShapeKeysQuickTools()
        QT.unmute_shape_keys()
        return{'FINISHED'}

#
#   Import Export Classes
#

class OBJECT_OT_Import(bpy.types.Operator, ImportHelper):
    bl_idname = 'import.preset'
    bl_label = 'Import'
    bl_description = 'Import presets'
    
    filename_ext = '.txt'

    def execute(self, context):
        func.import_presets(self.filepath)
        return{'FINISHED'}
        
        
class OBJECT_OT_Export(bpy.types.Operator, ExportHelper):
    bl_idname = 'export.preset'
    bl_label = 'Export'
    bl_description = 'Export all presets'
    
    @classmethod
    def poll(cls, context):
        return (context.active_object and
                len(context.object.shape_preset_list) > 0)
    
    filename_ext = ".txt"
    
    def execute(self, context):
        func.export_presets(self.filepath)
        return{'FINISHED'}
        
     
class OBJECT_OT_SortPresets(bpy.types.Operator):
    bl_idname = 'sort.presets'
    bl_label = 'Sort'
    bl_description = 'Sort all presets'
    
    def execute(self, context):
        func.sort_presets()
        return{'FINISHED'}   

        
class OBJECT_OT_InvertSelection(bpy.types.Operator):
    bl_idname = 'invert.selection'
    bl_label = 'Invert'
    bl_description = 'Invert selected presets'
    
    def execute(self, context):
        func.invert_selection()
        return{'FINISHED'}         

        
class OBJECT_OT_CleanPresets(bpy.types.Operator):
    bl_idname = 'clean.presets'
    bl_label = 'Clean'
    bl_description = 'Delete empty presets only'
    
    def execute(self, context):
        func.clean_presets()
        return{'FINISHED'}  

class OBJECT_OT_DeleteAllPresets(bpy.types.Operator):
    bl_idname = 'delete.all_presets'
    bl_label = 'Delete all'
    bl_description = 'Delete all presets of active object'
    
    def execute(self, context):
        func.delete_all_presets()
        return{'FINISHED'}   

class OBJECT_OT_UpdatePresets(bpy.types.Operator):
    bl_idname = 'update.presets'
    bl_label = 'Update'
    bl_description = 'Make all presets compatible with 0.6 update - sets all presets to "All" category'
    
    def execute(self, context):
        func.update_presets()
        return{'FINISHED'}         
 
 
class OBJECT_OT_PresetItemMoveUp(bpy.types.Operator):
    bl_idname = 'preset.move_up'
    bl_label = 'Move up'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}
    
    @classmethod
    def poll(cls, context):
        return (context.active_object and
                context.active_object.type == 'MESH' and
                len(context.object.shape_preset_list) > 0 and
                bpy.context.object.shape_preset_index > 0)

    def draw(self, context):
        layout = self.layout
        
    def execute(self, context):
        index = bpy.context.object.shape_preset_index
        context.object.shape_preset_list.move(index, index-1)
        context.object.shape_preset_index -= 1

        return {'FINISHED'}
    
class OBJECT_OT_PresetItemMoveDown(bpy.types.Operator):
    bl_idname = 'preset.move_down'
    bl_label = 'Move Down'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}
    
    @classmethod
    def poll(cls, context):
        return (context.active_object and
                context.active_object.type == 'MESH' and
                len(context.object.shape_preset_list) > 0 and
                bpy.context.object.shape_preset_index != len(context.object.shape_preset_list)-1)

    def draw(self, context):
        layout = self.layout
        
    def execute(self, context):
        index = bpy.context.object.shape_preset_index
        context.object.shape_preset_list.move(index, index+1)
        context.object.shape_preset_index += 1

        return {'FINISHED'}

class OBJECT_OT_TakeSnapshot(bpy.types.Operator):
    bl_idname = 'take.snapshot'
    bl_label = 'Take Snapshot'
    bl_description = 'Take snapshot of 3D view'
    
    def execute(self, context):
        func.take_snapshot()
        return{'FINISHED'} 

