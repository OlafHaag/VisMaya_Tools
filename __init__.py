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


bl_info = {
    'name': 'Vismaya Tools',
    'author': 'Project Vismaya',
    'version': (1, 1),
    'blender': (2, 56, 2),
    'location': 'View3D > Toolbar',
    'description': 'Vismaya Tools',
    'category': '3D View'}

import bpy
from bpy.types import Operator, Panel
from bpy.props import (StringProperty,
                       EnumProperty,
                       FloatProperty,
                       BoolProperty)
from . import lighting
from . import Modelling
from . import bonetools
from . import parent
from . import op_shape_presets
from . import vismaya_tools
from . import Delete_Unused_nodes
from . import functions_shape_presets as func

from rna_prop_ui import PropertyPanel
from bl_ui.properties_animviz import MotionPathButtonsPanel
from math import *
from mathutils import Matrix
from bpy.props import *
import bmesh, random, math, os
from bpy.types import Header, Menu
from bpy_extras.io_utils import (ExportHelper, ImportHelper)
import getpass
from bpy.props import IntProperty, FloatProperty, FloatVectorProperty
from bpy.props import EnumProperty, PointerProperty, StringProperty, BoolProperty, CollectionProperty
from mathutils import Vector
from platform import system as currentOS
from bl_ui.properties_paint_common import UnifiedPaintPanel

opps = 0
opps1 = 0


############# Rendering #######################
class LayerSelection(bpy.types.PropertyGroup):
    active = bpy.props.BoolProperty(name="Active", description="Toggle on if the layer must be rendered", default=False)


# Container that keeps track of the settings used for this render batch
class BatchSettings(bpy.types.PropertyGroup):
    start_frame = bpy.props.IntProperty(name="Starting frame of this batch", default=0)
    end_frame = bpy.props.IntProperty(name="Ending frame of this batch", default=1)
    reso_x = bpy.props.IntProperty(name="X resolution", description="resoution of this batch", default=1920, min=1,
                                   max=10000, soft_min=1, soft_max=10000)
    reso_y = bpy.props.IntProperty(name="Y resoliution", description="resolution of this batch", default=1080, min=1,
                                   max=10000, soft_min=1, soft_max=10000)
    reso_percentage = bpy.props.IntProperty(name="percentage",
                                            description="Percentage of the resolution at which this batch is rendered",
                                            default=100, min=1, max=100, soft_min=1, soft_max=100)
    samples = IntProperty(name='Samples', description='Number of samples that is used (Cycles only)', min=1,
                          max=1000000, soft_min=1, soft_max=100000, default=100)
    camera = StringProperty(name="Camera", description="Camera to be used for rendering this patch", default="")
    filepath = bpy.props.StringProperty(subtype='FILE_PATH', default="")
    layers = bpy.props.CollectionProperty(name="layer container", type=LayerSelection)
    markedForDeletion = bpy.props.BoolProperty(name="Toggled on if this must be deleted", default=False)


# Container that records what frame ranges are to be rendered
class BatchRenderData(bpy.types.PropertyGroup):
    frame_ranges = bpy.props.CollectionProperty(name="Container for frame ranges defined for rendering",
                                                type=BatchSettings)
    active_range = bpy.props.IntProperty(name="Index for currently processed range", default=0)


class CUSTOM_OT_SelectObjectButton(bpy.types.Operator):
    bl_idname = "batch_render.select_object"
    bl_label = "Select"
    bl_description = "Select the chosen object"
    
    def invoke(self, context, event):
        updateObjectList()
        obj = bpy.context.scene.objects[int(bpy.context.scene.camera_list)]
        # for o in bpy.data.objects:
        # print(o.name)
        print(obj.name)
        bpy.context.scene.objects.active = obj
        return {'FINISHED'}


def check_camera(c):
    """Checks if a specified camera exists."""
    for obj in bpy.context.scene.objects:
        if (obj.type == 'CAMERA'):
            if (obj.name == c):
                return True
    return False


def get_cameras():
    out = []
    for obj in bpy.context.scene.objects:
        if (obj.type == 'CAMERA'):
            out.append(obj.name)
    return out


class OBJECT_OT_BatchRenderButton(bpy.types.Operator):
    """Operator that starts the rendering."""
    bl_idname = "batch_render.render"
    bl_label = "Batch Render"
    
    def execute(self, context):
        batcher = bpy.context.scene.batch_render
        sce = bpy.context.scene
        rd = sce.render
        batch_count = 0
        for it in batcher.frame_ranges:
            batch_count += 1
            print("***********")
            if (it.end_frame <= it.start_frame):
                print("Skipped batch " + str(it.start_frame) + " - " + str(
                    it.end_frame) + ": Start frame greater than end frame")
                continue
            sce.frame_start = it.start_frame
            sce.frame_end = it.end_frame
            rd.resolution_x = it.reso_x
            rd.resolution_y = it.reso_y
            rd.resolution_percentage = it.reso_percentage
            if check_camera(it.camera):
                sce.camera = bpy.data.objects[it.camera]
            else:
                print(
                    "I did not find the specified camera for this batch. The camera was " + it.camera + ". Following cameras exist in the scene:")
                print(get_cameras())
            
            if rd.engine == 'CYCLES':
                sce.cycles.samples = it.samples
            
            sce.render.filepath = it.filepath
            sce.render.filepath += ("batch_" + str(batch_count) + "_" + str(it.reso_x) + "x" + str(it.reso_y) + "_")
            
            i = 0
            while i < 20:
                bpy.context.scene.layers[i] = it.layers[i].active
                if bpy.context.scene.layers[i]:
                    print("Enabled layer " + str(i + 1))
                i += 1
            
            print("Rendering frames: " + str(it.start_frame) + " - " + str(it.end_frame))
            print("At resolution " + str(it.reso_x) + "x" + str(it.reso_y) + " (" + str(it.reso_percentage) + "%)")
            if rd.engine == 'CYCLES':
                print("With " + str(it.samples) + " samples")
            print("using camera " + bpy.context.scene.camera.name)
            print("Saving frames in " + it.filepath)
            print("Ok! I'm beginning rendering now. Wait warmly.")
            bpy.ops.render.render(animation=True)
        sum = 0
        for it in batcher.frame_ranges:
            if it.end_frame >= it.start_frame:
                sum += (it.end_frame - it.start_frame)
        print("Rendered " + str(len(batcher.frame_ranges)) + " batches containing " + str(sum) + " frames")
        return {'FINISHED'}


class OBJECT_OT_BatchRenderAddNew(bpy.types.Operator):
    """Operator that adds a new frame range to be rendered."""
    bl_idname = "batch_render.add_new"
    bl_label = "Add new set"
    
    def execute(self, context):
        batcher = bpy.context.scene.batch_render
        rd = bpy.context.scene.render
        batcher.frame_ranges.add()
        last_item = len(batcher.frame_ranges) - 1
        batcher.frame_ranges[last_item].start_frame = 1
        batcher.frame_ranges[last_item].end_frame = 2
        batcher.frame_ranges[last_item].samples = bpy.context.scene.cycles.samples
        batcher.frame_ranges[last_item].reso_x = rd.resolution_x
        batcher.frame_ranges[last_item].reso_y = rd.resolution_y
        batcher.frame_ranges[last_item].camera = bpy.context.scene.camera.name
        batcher.frame_ranges[last_item].filepath = bpy.context.scene.render.filepath
        i = 0
        while i < 20:
            batcher.frame_ranges[last_item].layers.add()
            if bpy.context.scene.layers[i]:
                batcher.frame_ranges[last_item].layers[i].active = True
            i += 1
        
        return {'FINISHED'}


class OBJECT_OT_BatchRenderRemove(bpy.types.Operator):
    """Removes items that have been marked for deletion."""
    bl_idname = "batch_render.remove"
    bl_label = "Remove selected sets"
    
    def execute(self, context):
        batcher = bpy.context.scene.batch_render
        
        done = False
        while (done == False):
            count = 0
            if (len(batcher.frame_ranges) < 1):
                break
            for it in batcher.frame_ranges:
                if (it.markedForDeletion == True):
                    batcher.frame_ranges.remove(count)
                    break
                count += 1
                if count >= (len(batcher.frame_ranges) - 1):
                    done = True
        return {'FINISHED'}


class OBJECT_PT_PresetNames(bpy.types.PropertyGroup):
    name = StringProperty(name="Preset Name", default="Unknown")
    influence = FloatProperty(min=0.0, max=1.0, default=1.0, precision=3, update=func.preset_influence,
                              description="Influence of preset.")
    select_preset = BoolProperty(description="Insert this preset in keyframes.", update=func.update_select_all)


bpy.utils.register_class(OBJECT_PT_PresetNames)


class OS_UL_ShapePresets(bpy.types.UIList):
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row()
        row.label(text=item.name, translate=False, icon='SHAPEKEY_DATA')
        if item.name != 'All_to_0':
            row.prop(item, "influence", text="", emboss=False)
            row.prop(item, "select_preset", text="")


class MENU_MT_PresetsSpecials(bpy.types.Menu):
    bl_idname = 'MENU_MT_PresetsSpecials'
    bl_label = 'Presets Special tools'
    COMPAT_ENGINES = {'BLENDER_RENDER', 'BLENDER_GAME'}
    
    def draw(self, context):
        layout = self.layout
        layout.operator('import.preset', icon='IMPORT')
        layout.operator('export.preset', icon='EXPORT')
        layout.operator('sort.presets', icon='SORTALPHA')
        layout.operator('invert.selection', icon='FILE_REFRESH')
        layout.operator('clean.presets', icon='MOD_FLUIDSIM')
        layout.operator('delete.all_presets', icon='X')
        layout.operator('update.presets', icon='RECOVER_AUTO')


########### Car Rigging ###########
def generate(origin):
    print("origin")
    ob = bpy.context.active_object
    ob.show_x_ray = True
    ob.name = "Car Rig"
    amt = ob.data
    
    bpy.ops.object.mode_set(mode='EDIT')
    #####################################Computing Average Positions#######################
    posx = (ob.data.bones['FRWheel'].head_local[0] + ob.data.bones['FLWheel'].head_local[0]) / 2
    posy = (ob.data.bones['FRWheel'].head_local[1] + ob.data.bones['FLWheel'].head_local[1]) / 2
    posz = (ob.data.bones['FRWheel'].head_local[2] + ob.data.bones['FLWheel'].head_local[2]) / 2
    
    pos2x = (ob.data.bones['BRWheel'].head_local[0] + ob.data.bones['BLWheel'].head_local[0]) / 2
    pos2y = (ob.data.bones['BRWheel'].head_local[1] + ob.data.bones['BLWheel'].head_local[1]) / 2
    pos2z = (ob.data.bones['BRWheel'].head_local[2] + ob.data.bones['BLWheel'].head_local[2]) / 2
    
    pos3x = ob.data.bones['Body'].head_local[0]
    pos3y = ob.data.bones['Body'].head_local[1]
    pos3z = ob.data.bones['Body'].head_local[2]
    
    #####################################Create Bones#################################
    axis = amt.edit_bones.new("axis")
    axis.head = (pos2x, pos2y, pos2z)
    axis.tail = (posx, posy, posz)
    axis.layers[30] = True
    axis.layers[0] = False
    
    damper_center = amt.edit_bones.new("damperCenter")
    damper_center.head = ob.data.bones['Body'].head_local
    damper_center.tail = (pos3x, pos3y - 1, pos3z)
    damper_center.layers[30] = True
    damper_center.layers[0] = False
    
    body = amt.edit_bones["Body"]
    body.parent = axis
    body.layers[31] = True
    body.layers[0] = False
    
    fr_wheel = amt.edit_bones["FRWheel"]
    fr_wheel.layers[29] = True
    fr_wheel.layers[0] = False
    fr_wheel.parent = damper_center
    
    fl_wheel = amt.edit_bones["FLWheel"]
    fl_wheel.layers[29] = True
    fl_wheel.layers[0] = False
    
    br_wheel = amt.edit_bones["BRWheel"]
    br_wheel.layers[29] = True
    br_wheel.layers[0] = False
    br_wheel.parent = damper_center
    
    bl_wheel = amt.edit_bones["BLWheel"]
    bl_wheel.layers[29] = True
    bl_wheel.layers[0] = False
    bl_wheel.parent = damper_center
    
    wheel_front = amt.edit_bones.new("wheelFront")
    wheel_front.head = (posx, posy, posz)
    wheel_front.tail = (posx, posy - 0.8, posz)
    wheel_front.parent = damper_center
    wheel_front.layers[31] = True
    wheel_front.layers[0] = False
    
    steering_wheel = amt.edit_bones.new("steeringWheel")
    steering_wheel.head = (posx, posy - 2, posz)
    steering_wheel.tail = (posx, posy - 2.5, posz)
    
    damper_front = amt.edit_bones.new("damperFront")
    damper_front.head = ob.data.bones['FRWheel'].head_local
    damper_front.tail = ob.data.bones['FLWheel'].head_local
    damper_front.layers[30] = True
    damper_front.layers[0] = False
    
    damper_back = amt.edit_bones.new("damperBack")
    damper_back.head = ob.data.bones['BRWheel'].head_local
    damper_back.tail = ob.data.bones['BLWheel'].head_local
    damper_back.layers[30] = True
    damper_back.layers[0] = False
    
    damper = amt.edit_bones.new("damper")
    damper.head = (pos3x, pos3y, pos3z + 2)
    damper.tail = (pos3x, pos3y - 1, pos3z + 2)
    damper.parent = damper_center
    
    fr_sensor = amt.edit_bones.new("FRSensor")
    fr_sensor.head = ob.data.bones['FRWheel'].head_local
    fr_sensor.tail = ob.data.bones['FRWheel'].head_local
    fr_sensor.tail[2] = fr_sensor.tail.z + 0.3
    fr_sensor.parent = damper_center
    
    fl_sensor = amt.edit_bones.new("FLSensor")
    fl_sensor.head = ob.data.bones['FLWheel'].head_local
    fl_sensor.tail = ob.data.bones['FLWheel'].head_local
    fl_sensor.tail[2] = fl_sensor.tail.z + 0.3
    fl_sensor.parent = damper_center
    
    br_sensor = amt.edit_bones.new("BRSensor")
    br_sensor.head = ob.data.bones['BRWheel'].head_local
    br_sensor.tail = ob.data.bones['BRWheel'].head_local
    br_sensor.tail[2] = br_sensor.tail.z + 0.3
    
    bl_sensor = amt.edit_bones.new("BLSensor")
    bl_sensor.head = ob.data.bones['BLWheel'].head_local
    bl_sensor.tail = ob.data.bones['BLWheel'].head_local
    bl_sensor.tail[2] = bl_sensor.tail.z + 0.3
    bl_sensor.parent = damper_center
    
    wheel_rot = amt.edit_bones.new("WheelRot")
    wheel_rot.head = ob.data.bones['FLWheel'].head_local
    wheel_rot.tail = ob.data.bones['FLWheel'].head_local
    wheel_rot.tail[1] = fl_sensor.tail.y + 0.3
    wheel_rot.parent = damper_center
    
    fl_wheel.parent = wheel_rot
    
    #####################################Pose Constraints#################################
    bpy.ops.object.mode_set(mode='POSE')
    
    # Locked Track constraint wheelFront -> steeringWheel
    wheel_front = ob.pose.bones['wheelFront']
    cns1 = wheel_front.constraints.new('LOCKED_TRACK')
    cns1.target = ob
    cns1.subtarget = 'steeringWheel'
    
    # Copy Location constraint FLWheel -> FLSensor
    fl_wheel = ob.pose.bones['FLWheel']
    cns3b = fl_wheel.constraints.new('COPY_LOCATION')
    cns3b.target = ob
    cns3b.subtarget = 'FLSensor'
    cns3b.use_x = False
    cns3b.use_y = False
    # Damped Track constraint FLWheel -> damperFront
    cns3 = fl_wheel.constraints.new('DAMPED_TRACK')
    cns3.track_axis = "TRACK_X"
    cns3.target = ob
    cns3.subtarget = 'damperFront'
    # Copy Location constraint FLWheel -> damperFront
    cns3b = fl_wheel.constraints.new('COPY_LOCATION')
    cns3b.target = ob
    cns3b.subtarget = 'damperFront'
    cns3b.head_tail = 1
    cns3b.use_y = False
    cns3b.use_z = False
    # Copy Rotation constraint FLWheel -> wheelFront
    cns2 = fl_wheel.constraints.new('COPY_ROTATION')
    cns2.target = ob
    cns2.subtarget = 'wheelFront'
    cns2.use_x = False
    cns2.use_y = False
    
    # Copy Location constraint FRWheel -> FRSensor
    fr_wheel = ob.pose.bones['FRWheel']
    cns3b = fr_wheel.constraints.new('COPY_LOCATION')
    cns3b.target = ob
    cns3b.subtarget = 'FRSensor'
    cns3b.use_x = False
    cns3b.use_y = False
    # Damped Track constraint FRWheel -> damperFront
    cns3 = fr_wheel.constraints.new('DAMPED_TRACK')
    cns3.track_axis = "TRACK_NEGATIVE_X"
    cns3.target = ob
    cns3.subtarget = 'damperFront'
    cns3.head_tail = 1
    # Copy Rotation constraint FRWheel -> wheelFront
    cns3a = fr_wheel.constraints.new('COPY_ROTATION')
    cns3a.target = ob
    cns3a.subtarget = 'wheelFront'
    cns3a.use_x = False
    cns3a.use_y = False
    # Copy Rotation constraint RRWheel -> BLWHeel
    cns3c = fr_wheel.constraints.new('COPY_ROTATION')
    cns3c.target = ob
    cns3c.subtarget = 'FLWheel'
    cns3c.use_y = False
    cns3c.use_z = False
    
    # Copy Location constraint BRWheel -> BRSensor
    br_wheel = ob.pose.bones['BRWheel']
    cns3b = br_wheel.constraints.new('COPY_LOCATION')
    cns3b.target = ob
    cns3b.subtarget = 'BRSensor'
    cns3b.use_x = False
    cns3b.use_y = False
    # Damped Track constraint BRWheel -> damperBack
    cns3 = br_wheel.constraints.new('DAMPED_TRACK')
    cns3.track_axis = "TRACK_NEGATIVE_X"
    cns3.head_tail = 1
    cns3.target = ob
    cns3.subtarget = 'damperBack'
    # Copy Rotation constraint BRWheel -> BLWHeel
    cns3c = br_wheel.constraints.new('COPY_ROTATION')
    cns3c.target = ob
    cns3c.subtarget = 'FLWheel'
    cns3c.use_y = False
    cns3c.use_z = False
    
    # Copy Location constraint BLWheel -> BLSensor
    bl_wheel = ob.pose.bones['BLWheel']
    cns3b = bl_wheel.constraints.new('COPY_LOCATION')
    cns3b.target = ob
    cns3b.subtarget = 'BLSensor'
    cns3b.use_x = False
    cns3b.use_y = False
    # Damped Track constraint BLWheel -> damperBack
    cns3 = bl_wheel.constraints.new('DAMPED_TRACK')
    cns3.track_axis = "TRACK_X"
    cns3.target = ob
    cns3.subtarget = 'damperBack'
    # Copy Location constraint BLWheel -> damperBack
    cns3b = bl_wheel.constraints.new('COPY_LOCATION')
    cns3b.target = ob
    cns3b.subtarget = 'damperBack'
    cns3b.head_tail = 1
    cns3b.use_y = False
    cns3b.use_z = False
    # Copy Rotation constraint BLWheel -> BLWHeel
    cns3c = bl_wheel.constraints.new('COPY_ROTATION')
    cns3c.target = ob
    cns3c.subtarget = 'FLWheel'
    cns3c.use_y = False
    cns3c.use_z = False
    
    # Transformation constraint Body -> damper
    damper_center = ob.pose.bones['Body']
    cns4 = damper_center.constraints.new('TRANSFORM')
    cns4.target = ob
    cns4.subtarget = 'damper'
    cns4.from_min_x = -0.3
    cns4.from_max_x = 0.3
    cns4.from_min_y = -0.3
    cns4.from_max_y = 0.3
    cns4.map_to_x_from = "Y"
    cns4.map_to_z_from = "X"
    cns4.map_to = "ROTATION"
    cns4.to_min_x = -6
    cns4.to_max_x = 6
    cns4.to_min_z = -7
    cns4.to_max_z = 7
    cns4.owner_space = 'LOCAL'
    cns4.target_space = 'LOCAL'
    # Transformation constraint Body -> damper
    damper_center = ob.pose.bones['Body']
    cns4 = damper_center.constraints.new('TRANSFORM')
    cns4.target = ob
    cns4.subtarget = 'damper'
    cns4.from_min_z = -0.1
    cns4.from_max_z = 0.1
    cns4.map_to_y_from = "Z"
    cns4.to_min_y = -0.1
    cns4.to_max_y = 0.1
    cns4.owner_space = 'LOCAL'
    cns4.target_space = 'LOCAL'
    
    # Copy Location constraint axis -> damperBack
    axis = ob.pose.bones['axis']
    cns5 = axis.constraints.new('COPY_LOCATION')
    cns5.target = ob
    cns5.subtarget = 'damperBack'
    cns5.head_tail = 0.5
    # Tract To constraint axis -> damperFront
    cns6 = axis.constraints.new('TRACK_TO')
    cns6.target = ob
    cns6.subtarget = 'damperFront'
    cns6.head_tail = 0.5
    cns6.use_target_z = True
    cns6.owner_space = 'POSE'
    cns6.target_space = 'POSE'
    # Damped Track constraint axis -> damperBack
    cns7 = axis.constraints.new('DAMPED_TRACK')
    cns7.influence = 0.5
    cns7.target = ob
    cns7.subtarget = 'damperBack'
    cns7.track_axis = "TRACK_X"
    cns7.influence = 0.5
    
    # Copy Location constraint damperBack -> BRWheel
    damper_back = ob.pose.bones['damperBack']
    cns8 = damper_back.constraints.new('COPY_LOCATION')
    cns8.target = ob
    cns8.subtarget = 'BRWheel'
    # Tract To constraint damperBack -> BLWheel
    cns9 = damper_back.constraints.new('TRACK_TO')
    cns9.target = ob
    cns9.subtarget = 'BLWheel'
    
    # Copy Location constraint damperFront -> FRWheel
    damper_front = ob.pose.bones['damperFront']
    cns10 = damper_front.constraints.new('COPY_LOCATION')
    cns10.target = ob
    cns10.subtarget = 'FRWheel'
    # Tract To constraint damperFront -> FLWheel
    cns11 = damper_front.constraints.new('TRACK_TO')
    cns11.target = ob
    cns11.subtarget = 'FLWheel'
    
    # Copy Location constraint FLSensor -> 
    fl_sensor = ob.pose.bones['FLSensor']
    fl_sensor.lock_location = (True, False, True)
    cns = fl_sensor.constraints.new('SHRINKWRAP')
    # Copy Location constraint FRSensor -> 
    fr_sensor = ob.pose.bones['FRSensor']
    fr_sensor.lock_location = (True, False, True)
    cns = fr_sensor.constraints.new('SHRINKWRAP')
    # Copy Location constraint BLSensor -> 
    bl_sensor = ob.pose.bones['BLSensor']
    bl_sensor.lock_location = (True, False, True)
    cns = bl_sensor.constraints.new('SHRINKWRAP')
    # Copy Location constraint BRSensor -> 
    br_sensor = ob.pose.bones['BRSensor']
    br_sensor.lock_location = (True, False, True)
    cns = br_sensor.constraints.new('SHRINKWRAP')
    
    # Copy Location constraint WheelRot -> FLSensor
    wheel_rot = ob.pose.bones['WheelRot']
    wheel_rot.rotation_mode = "XYZ"
    wheel_rot.lock_location = (True, True, True)
    wheel_rot.lock_rotation = (False, True, True)
    
    cns = wheel_rot.constraints.new('COPY_LOCATION')
    cns.target = ob
    cns.subtarget = 'FLSensor'
    cns.use_x = False
    cns.use_y = False
    
    #############################################Add Driver#########################
    # add empty
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.add(type="EMPTY", location=(0, 0, 0))
    empty = bpy.context.active_object
    empty.name = "carDriver"
    empty.empty_draw_size = 2
    empty.show_x_ray = True
    empty.empty_draw_type = "ARROWS"
    
    fl_wheel.rotation_mode = "XYZ"
    
    fcurve = ob.pose.bones["FLWheel"].driver_add('rotation_euler', 0)
    drv = fcurve.driver
    drv.type = 'AVERAGE'
    var = drv.variables.new()
    var.name = 'x'
    var.type = 'TRANSFORMS'
    
    targ = var.targets[0]
    targ.id = empty
    targ.transform_type = 'LOC_Y'
    targ.transform_space = "LOCAL_SPACE"
    
    global fmod
    
    fmod = fcurve.modifiers[0]
    fmod.mode = 'POLYNOMIAL'
    fmod.poly_order = 1
    fmod.coefficients = (0, 1.0)
    
    # parent body bone
    ob.parent = empty
    
    bpy.ops.object.select_all(action="TOGGLE")
    ob.select = True
    
    print("Generate Finished")


def CreateCarMetaRig(origin):  # create Car meta rig
    # create meta rig
    amt = bpy.data.armatures.new('CarMetaRigData')
    rig = bpy.data.objects.new('CarMetaRig', amt)
    rig.location = origin
    rig.show_x_ray = True
    # link to scene
    scn = bpy.context.scene
    scn.objects.link(rig)
    scn.objects.active = rig
    scn.update()
    
    # create meta rig bones
    bpy.ops.object.mode_set(mode='EDIT')
    body = amt.edit_bones.new('Body')
    body.head = (0, 0, 0)
    body.tail = (0, 0, 0.8)
    
    frw = amt.edit_bones.new('FLWheel')
    frw.head = (0.9, -2, 0)
    frw.tail = (0.9, -2.5, 0)
    
    flw = amt.edit_bones.new('FRWheel')
    flw.head = (-0.9, -2, 0)
    flw.tail = (-0.9, -2.5, 0)
    
    brw = amt.edit_bones.new('BLWheel')
    brw.head = (0.9, 2, 0)
    brw.tail = (0.9, 1.5, 0)
    
    blw = amt.edit_bones.new('BRWheel')
    blw.head = (-0.9, 2, 0)
    blw.tail = (-0.9, 1.5, 0)
    
    # swith to object mode
    bpy.ops.object.mode_set(mode='OBJECT')


########### Toggle ###############
class Object_Toggle(bpy.types.Operator):
    bl_idname = "object.toggle"
    bl_label = "Toggle to Edit mode"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        bpy.ops.object.editmode_toggle()
        return {'FINISHED'}


class Object_Toggle(bpy.types.Operator):
    bl_idname = "uv.cube_project1"
    bl_label = "Toggle to Edit mode"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        if context.mode != 'EDIT_MESH':
            bpy.ops.object.editmode_toggle()
        if bpy.context.active_object.name == 'Cube':
            bpy.ops.mesh.select_all()
        bpy.ops.uv.cube_project()
        return {'FINISHED'}


#### delete keyframes in a range for selected bones #####
class DELETE_KEYFRAMES_RANGE(bpy.types.Operator):
    bl_idname = "pose.delete_keyframes"
    bl_label = "Delete Keyframes"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Delete all keyframes for selected bones in a time range"
    
    @classmethod
    def poll(cls, context):
        obj = bpy.context.object
        return obj.type == 'ARMATURE' and obj.mode == 'POSE'
    
    def execute(self, context):
        wm = bpy.context.window_manager
        arm = bpy.context.object
        act = arm.animation_data.action
        delete = []
        
        # get selected bones names
        sel = [b.name for b in arm.data.bones if b.select]
        
        # get bone names from fcurve data_path
        for fcu in act.fcurves:
            name = fcu.data_path.split(sep='"', maxsplit=2)[1]
            
            # check if bone is selected and got keyframes in range
            if name in sel:
                for kp in fcu.keyframe_points:
                    if wm.del_range_start <= kp.co[0] <= wm.del_range_end:
                        delete.append((fcu.data_path, kp.co[0]))
        
        # delete keyframes
        for kp in delete:
            arm.keyframe_delete(kp[0], index=-1, frame=kp[1])
        
        context.scene.frame_set(context.scene.frame_current)
        return {'FINISHED'}


### move keyframes
drag_max = 30


def acciones(objetos):
    act = []
    for obj in objetos:
        try:
            if obj.animation_data:
                act.append(obj.animation_data.action)
            if obj.data.shape_keys and obj.data.shape_keys.animation_data:
                act.append(obj.data.shape_keys.animation_data.action)
        except:
            pass
    total = {}
    for a in act: total[a] = 1
    return total.keys()


def offset(act, val):
    for fcu in act.fcurves:
        if bpy.context.window_manager.sel:
            puntox = [p for p in fcu.keyframe_points if p.select_control_point]
        else:
            puntox = fcu.keyframe_points
        for k in puntox:
            k.co[0] += val
            k.handle_left[0] += val
            k.handle_right[0] += val


### select keys       
def drag(self, context):
    wm = context.window_manager
    if bpy.context.selected_objects:
        for act in acciones(bpy.context.selected_objects):
            offset(act, wm.drag)
    if wm.drag:
        wm.drag = 0
    refresco()


def refresco():
    f = bpy.context.scene.frame_current
    bpy.context.scene.frame_set(f)


### apply keys
class Apply(bpy.types.Operator):
    bl_idname = 'offset.apply'
    bl_label = 'Apply'
    bl_description = 'Move Keys to selected objects'
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return (bpy.context.selected_objects)
    
    def execute(self, context):
        for act in acciones(bpy.context.selected_objects):
            offset(act, context.window_manager.off)
        refresco()
        return {'FINISHED'}


### reset    
class Reset(bpy.types.Operator):
    bl_idname = 'offset.reset'
    bl_label = 'Reset'
    bl_description = 'Reset sliders to zero'
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        context.window_manager.off = 0
        return {'FINISHED'}
    
    ######## Turn Around Camera ########


class RunAction(bpy.types.Operator):
    bl_idname = "object.rotate_around"
    bl_label = "Turnaround"
    bl_description = "Create camera rotation around selected object"
    
    # ------------------------------
    # Execute
    # ------------------------------
    def execute(self, context):
        # ----------------------
        # Save old data
        # ----------------------
        scene = context.scene
        select_object = context.active_object
        camera = bpy.data.objects[bpy.context.scene.camera.name]
        saved_cursor = bpy.context.scene.cursor_location.copy()  # cursor position
        saved_frame = scene.frame_current
        if not scene.use_cursor:
            bpy.ops.view3d.snap_cursor_to_selected()
        
        # -------------------------
        # Create empty and parent
        # -------------------------
        bpy.ops.object.empty_add(type='PLAIN_AXES')
        my_empty = bpy.data.objects[bpy.context.active_object.name]
        
        my_empty.location = select_object.location
        saved_state = my_empty.matrix_world
        my_empty.parent = select_object
        my_empty.name = 'MCH_Rotation_target'
        my_empty.matrix_world = saved_state
        
        # -------------------------
        # Parent camera to empty
        # -------------------------
        saved_state = camera.matrix_world
        camera.parent = my_empty
        camera.matrix_world = saved_state
        
        # -------------------------
        # Now add revolutions
        # (make empty active object)
        # -------------------------
        bpy.ops.object.select_all(False)
        my_empty.select = True
        bpy.context.scene.objects.active = my_empty
        # save current configuration
        saved_interpolation = context.user_preferences.edit.keyframe_new_interpolation_type
        # change interpolation mode
        context.user_preferences.edit.keyframe_new_interpolation_type = 'LINEAR'
        # create first frame
        my_empty.rotation_euler = (0, 0, 0)
        my_empty.empty_draw_size = 0.1
        bpy.context.scene.frame_set(scene.frame_start)
        my_empty.keyframe_insert(data_path='rotation_euler', frame=(scene.frame_start))
        # Dolly zoom
        if scene.dolly_zoom != "0":
            bpy.data.cameras[camera.name].lens = scene.camera_from_lens
            bpy.data.cameras[camera.name].keyframe_insert('lens', frame=(scene.frame_start))
        
        # Calculate rotation XYZ
        if scene.inverse_x:
            i_x = -1
        else:
            i_x = 1
        
        if (scene.inverse_y):
            i_y = -1
        else:
            i_y = 1
        
        if scene.inverse_z:
            i_z = -1
        else:
            i_z = 1
        
        x_rot = (math.pi * 2) * scene.camera_revol_x * i_x
        y_rot = (math.pi * 2) * scene.camera_revol_y * i_y
        z_rot = (math.pi * 2) * scene.camera_revol_z * i_z
        
        # create middle frame
        if scene.back_forw:
            my_empty.rotation_euler = (x_rot, y_rot, z_rot)
            my_empty.keyframe_insert(data_path='rotation_euler', frame=((scene.frame_end - scene.frame_start) / 2))
            # reverse
            x_rot = x_rot * -1
            y_rot = y_rot * -1
            z_rot = 0
        
        # Dolly zoom
        if scene.dolly_zoom == "2":
            bpy.data.cameras[camera.name].lens = scene.camera_to_lens
            bpy.data.cameras[camera.name].keyframe_insert('lens', frame=((scene.frame_end - scene.frame_start) / 2))
        
        # create last frame
        my_empty.rotation_euler = (x_rot, y_rot, z_rot)
        my_empty.keyframe_insert(data_path='rotation_euler', frame=(scene.frame_end))
        # Dolly zoom
        if scene.dolly_zoom != "0":
            if scene.dolly_zoom == "1":
                bpy.data.cameras[camera.name].lens = scene.camera_to_lens  # final
            else:
                bpy.data.cameras[camera.name].lens = scene.camera_from_lens  # back to init
            
            bpy.data.cameras[camera.name].keyframe_insert('lens', frame=scene.frame_end)
        
        # Track constraint
        if scene.track:
            bpy.context.scene.objects.active = camera
            bpy.ops.object.constraint_add(type='TRACK_TO')
            bpy.context.object.constraints[-1].track_axis = 'TRACK_NEGATIVE_Z'
            bpy.context.object.constraints[-1].up_axis = 'UP_Y'
            bpy.context.object.constraints[-1].target = bpy.data.objects[my_empty.name]
        
        # back previous configuration
        context.user_preferences.edit.keyframe_new_interpolation_type = saved_interpolation
        bpy.context.scene.cursor_location = saved_cursor
        
        # -------------------------
        # Back to old selection
        # -------------------------
        bpy.ops.object.select_all(False)
        select_object.select = True
        bpy.context.scene.objects.active = select_object
        bpy.context.scene.frame_set(saved_frame)
        
        return {'FINISHED'}


############## Menu set List ###############

types_enum = [("MODELING", "  Modeling", "", "MOD_ARMATURE", 1), ("ANIMATION", "  Animation", "", "MOD_SMOOTH", 2),
              ("RIGGING", "  Rigging", "", "MOD_SKIN", 3), ("UVTOOLS", "  UV Tools", "", "MOD_SCREW", 4),
              ("LIGHTING", "  Lighting", "", "MOD_EXPLODE", 5), ("RENDERING", "  Rendering", "", "CAMERA_DATA", 6),
              ("DYNAMICS", "  Dynamics", "", "MOD_DYNAMICPAINT", 7)]

bpy.types.Scene.menu_type = EnumProperty(name="", default="MODELING", items=types_enum)


############## Base Panel ##############
class VIEW3D_PT_tools_vismaya():
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "VisMaya"


############## Shelfs Panel ##############
class Vismaya_Shelfs(VIEW3D_PT_tools_vismaya, bpy.types.Panel):
    bl_label = "Shelfs"
    
    def draw(self, context):
        toolsettings = context.tool_settings
        layout = self.layout
        
        ########## Menu set ##########
        scn = context.scene
        col = layout.column(align=True)
        row = col.row(align=True)
        row.prop(scn, 'menu_type', text="Menu set", icon_only=True)
        row.separator()
        row.separator()
        if context.mode == "EDIT_MESH" or context.mode == "EDIT_ARMATURE":
            a = "Toggle to Object mode"
            ico = "EDITMODE_HLT"
        else:
            a = "Toggle to Edit mode"
            ico = "OBJECT_DATAMODE"
        col = layout.column(align=True)
        row = col.row(align=True)
        
        if bpy.context.active_object.name == 'Camera' or bpy.context.active_object.name == 'Lamp':
            row.enabled = False
        else:
            row.enabled = True
        row.operator("object.toggle", text=a, icon=ico)
        
        if scn.menu_type == "MODELING":
            layout.separator()
            col = layout.column(align=True)
            row = col.row(align=True)
            row.enabled = False
            if context.mode == 'EDIT_MESH':
                row.enabled = True
            row.operator("extrudenormal.selected", text="Extrude", icon='CURVE_PATH')
            row.separator()
            row.menu("INFO_MT_edit_mesh_extrude_indiv", icon='MOD_TRIANGULATE')
            
            col = layout.column(align=True)
            row = col.row(align=True)
            row.enabled = False
            if context.mode == 'EDIT_MESH':
                row.enabled = True
            row.operator("mesh.bridge_edge_loops", text="Bridge", icon='MESH_DATA')
            row.separator()
            row.operator("transform.edge_slide", text="Edge Slide", icon='EDGESEL')
            
            col = layout.column(align=True)
            row = col.row(align=True)
            row.enabled = False
            if context.mode == 'EDIT_MESH':
                row.enabled = True
            row.operator("mesh.inset", text="Inset Face", icon='FACESEL')
            row.separator()
            row.operator("mesh.edge_face_add", text="Make Edge/Face", icon='UV_ISLANDSEL')
            
            col = layout.column(align=True)
            row = col.row(align=True)
            row.enabled = False
            if context.mode == 'EDIT_MESH':
                row.enabled = True
            row.operator("mesh.subdivide", text="Subdivide", icon='FULLSCREEN_ENTER')
            row.separator()
            row.operator("mesh.unsubdivide", text="Un Subdivide", icon='FULLSCREEN_EXIT')
            
            col = layout.column(align=True)
            row = col.row(align=True)
            row.enabled = False
            if context.mode == 'EDIT_MESH':
                row.enabled = True
            row.operator("duplicate.selected", icon='ROTATECOLLECTION')
            row.separator()
            row.operator("mesh.merge", text="Merge", icon='GROUP')
            
            col = layout.column(align=True)
            row = col.row(align=True)
            row.enabled = False
            if context.mode == 'EDIT_MESH':
                row.enabled = True
            row.menu("Vismaya_MT_edit_mesh_delete", text="  Delete", icon='FORCE_SMOKEFLOW')
            row.separator()
            row.operator_menu_enum("mesh.separate", "type", text="  Separate", icon='MOD_DECIM')
            
            col = layout.column(align=True)
            row = col.row(align=True)
            row.enabled = False
            if context.mode == 'EDIT_MESH':
                row.enabled = True
            row.operator("mesh.bevel", text="Chamfer", icon='MOD_PARTICLES').vertex_only = True
            row.separator()
            row.operator("mesh.bevel", text="Bevel", icon='LAMP_POINT')
            
            col = layout.column(align=True)
            row = col.row(align=True)
            row.enabled = False
            if context.mode == 'EDIT_MESH':
                row.enabled = True
            row.operator("object.join", text="Join(Combine)", icon='CONSTRAINT_DATA')
            row.separator()
            row.operator("transform.edge_crease", text="Crease Tool", icon='RADIO')
            
            col = layout.column(align=True)
            row = col.row(align=True)
            row.enabled = False
            if context.mode == 'EDIT_MESH':
                row.enabled = True
            row.operator("mesh.fill", text="Fill Hole", icon='PROP_ON')
            row.separator()
            row.operator("mesh.remove_doubles", text="Clean Up", icon='PARTICLEMODE')
            
            col = layout.column(align=True)
            row = col.row(align=True)
            row.enabled = False
            if context.mode == 'EDIT_MESH':
                row.enabled = True
            row.operator("mesh.quads_convert_to_tris", text="Triangle", icon='MOD_DISPLACE')
            row.separator()
            row.menu("Vismaya_MT_edit_mesh_mirror", text="  Mirror", icon='MOD_MIRROR')
            row.separator()
            row.operator("mesh.tris_convert_to_quads", text="Quadrangulate", icon='MOD_MESHDEFORM')
        
        if scn.menu_type == "LIGHTING":
            obj = bpy.context.scene.objects.active
            layout.label(text="Tri-Lighting:")
            layout.operator("object.trilighting", text="Add Tri-Lighting")
        
        if scn.menu_type == "RENDERING":
            batcher = bpy.context.scene.batch_render
            layout.label("Batch Rendering:")
            layout.operator("batch_render.render", text="Launch rendering")
            layout.operator("batch_render.add_new", text="Add new set")
            layout.operator('batch_render.remove', text="Delete selected", icon='CANCEL')
            layout.row()
            count = 0
            # Print a control knob for every item currently defined
            for it in batcher.frame_ranges:
                layout.label(text="Batch " + str(count + 1))
                layout.prop(it, 'start_frame', text="Start frame")
                layout.prop(it, 'end_frame', text="End frame")
                layout.prop(it, 'reso_x', text="Resolution X")
                layout.prop(it, 'reso_y', text="Resolution Y")
                layout.prop(it, 'reso_percentage', text="Resolution percentage")
                layout.prop(it, 'samples', text="Samples (if using Cycles)")
                layout.prop(it, 'camera', text="Select camera")
                layout.prop(it, 'filepath', text="Output path")
                layout.label(text="Enabled layers")
                row = layout.row()
                i = 0
                for it2 in it.layers:
                    i += 1
                    row.prop(it2, 'active', text=str(i))
                    if (i % 5 == 0):
                        row = layout.row()
                layout.prop(it, 'markedForDeletion', text="Delete")
                layout.row()
                count += 1
        
        if scn.menu_type == "RIGGING":
            scn = bpy.context.scene
            obj = bpy.context.object
            layout.label(text="Shape Keys Presets")
            row = layout.row(align=True)
            if len(obj.shape_preset_list.keys()) > 0:
                split = row.split(percentage=0.35)
                row = split.row()
                row.prop(obj, 'preset_category', text='', icon='SHAPEKEY_DATA')
                split = split.split(percentage=1.0)
                row = split.row()
                row.prop(obj, 'category_name', emboss=True)
                row.operator('category.for_checked', text='', icon='MOD_ARRAY')
            
            row = layout.row()
            if len(obj.shape_preset_list.keys()) > 0 and obj.shape_preset_list[
                obj.shape_preset_index].name != 'All_to_0':
                
                layout.prop(obj, 'new_preset_name', emboss=True)
            else:
                layout.prop(obj, 'new_preset_name', emboss=False)
            
            row = layout.row()
            if len(obj.shape_preset_list) > 0:
                rows = 6
            else:
                rows = 2
            row.template_list('OS_UL_ShapePresets', '', obj, 'shape_preset_list', obj, 'shape_preset_index', rows=rows)
            col = row.column(align=True)
            col.operator('save.preset', text='', icon='ZOOMIN')
            col.operator('delete.preset', text='', icon='ZOOMOUT')
            col.menu('MENU_MT_PresetsSpecials', icon='DOWNARROW_HLT', text='')
            
            if rows == 6:
                for letter in 'ab':
                    col.separator()
                col.operator('preset.move_up', text='', icon='TRIA_UP')
                col.operator('preset.move_down', text='', icon='TRIA_DOWN')
                
                row = layout.row()
                split = row.split(percentage=0.7)
                row = split.row()
                row.prop(obj, 'select_all_presets', text='', icon='FILE_TICK')
                
                row.prop(obj, 'shapekeys_group_mode', text='', icon='CONSTRAINT')
                
                if obj.shapekeys_group_mode:
                    row.prop(obj, 'group_level_value')
                
                selected = [preset for preset in obj.shape_preset_list.keys() if
                            obj.shape_preset_list[preset].select_preset]
                row = layout.row()
                
                split = row.split(percentage=0.5)
                col = split.column(align=True)
                col.operator('raw.apply_button', text='Single Raw', icon='MESH_CUBE')
                if len(selected) > 1:
                    col.operator('multiraw.apply_button', text='Multi Raw', icon='GROUP')
                split = split.split(percentage=1)
                col = split.column(align=True)
                col.operator('gentle.apply_button', text='Single Gentle', icon='MESH_CUBE')
                if len(selected) > 1:
                    col.operator('multigentle.apply_button', text='Multi Gentle', icon='GROUP')
                
                row = layout.row()
                box = row.box()
                box.operator('insert.keyframes', icon='KEYINGSET')
                row = layout.row()
                row.alignment = 'CENTER'
                row.operator('reset.shapekeys_button', text='', icon='LOOP_BACK')
                row.operator('sort.shapekeys_button', text='', icon='SORTALPHA')
                row.operator('mute.all_button', text='', icon='VISIBLE_IPO_OFF')
                row.operator('unmute.all_button', text='', icon='VISIBLE_IPO_ON')
            
            else:
                row = layout.row()
                row.prop(obj, 'shapekeys_group_mode', text='', icon='CONSTRAINT')
                if obj.shapekeys_group_mode:
                    split = row.split(percentage=0.55)
                    row = split.row()
                    row.prop(obj, 'group_level_value')
            layout.label("Bone Tool:")
            col = layout.column(align=True)
            row = col.row(align=True)
            row.enabled = False
            if context.mode == 'EDIT_ARMATURE':
                row.enabled = True
            row.operator("appendl.op", icon="FORWARD")
            row.separator()
            row.operator("appendr.op", icon="BACK")
            
            col = layout.column(align=True)
            row = col.row(align=True)
            row.enabled = False
            if context.mode == 'EDIT_ARMATURE':
                row.enabled = True
            row.operator("autobonesuffix.op", text="Auto Suffix", icon="FULLSCREEN_ENTER")
            row.separator()
            row.operator("flipsuffix.op", text="Flip Suffixes", icon="FULLSCREEN_EXIT")
            
            col = layout.column(align=True)
            row = col.row(align=True)
            row.enabled = False
            if context.mode == 'EDIT_ARMATURE':
                row.enabled = True
            row.operator("setmiddle.op", text="Set Middle", icon="PMARKER")
            row.separator()
            row.operator("mirrorbones.op", icon="ARROW_LEFTRIGHT")
            
            col = layout.column(align=True)
            row = col.row(align=True)
            row.enabled = False
            if context.mode == 'EDIT_ARMATURE':
                row.enabled = True
            row.operator("batchrename.op", icon="FILE_TEXT")
            row.separator()
            row.operator("selectl.op", icon="FORWARD")
            
            col = layout.column(align=True)
            row = col.row(align=True)
            row.enabled = False
            if context.mode == 'EDIT_ARMATURE':
                row.enabled = True
            row.operator("selectr.op", icon="BACK")
            row.separator()
            row.operator("selectm.op", icon="PMARKER")
            
            col = layout.column(align=True)
            row = col.row(align=True)
            row.enabled = False
            if context.mode == 'EDIT_ARMATURE':
                row.enabled = True
            row.operator("selectnonsuffix.op", icon="ZOOMOUT")
            row.separator()
            row.operator("selectvampire.op", icon="FRAME_NEXT")
            row.separator()
            row.operator("object.select_pattern", icon="OUTLINER_DATA_FONT")
            
            layout.label("Car Rig:")
            col = layout.column(align=True)
            row = col.row(align=True)
            row.enabled = False
            if context.mode == 'OBJECT':
                row.enabled = True
            
            row.operator("car.meta_rig", text="Car(Meta-Rig)", icon='AUTO')
            
            col = layout.column(align=True)
            row = col.row(align=True)
            row.operator("object.joint_tool", icon='GROUP_BONE')
            row.separator()
            row.operator("object.ik_handle_tool")
            
            col = layout.column(align=True)
            row = col.row(align=True)
            row.operator("object.insert_joint_tool", icon='CONSTRAINT_BONE')
            row.separator()
            row.operator("object.ik_spline")
            
            col = layout.column(align=True)
            row = col.row(align=True)
            row.operator("skele.ton", icon='SNAP_SURFACE')
            row.operator("object.disconnect_joint", icon='UNLINKED')
            
            col = layout.column(align=True)
            row = col.row(align=True)
            row.operator("object.connect_joint", icon='AUTOMERGE_ON')
            row.separator()
            row.operator("object.remove_joint", icon='ACTION')
            col = layout.column(align=True)
            row = col.row(align=True)
            row.menu("VIEW3D_MT_mirror", icon='MOD_MIRROR')
            row.separator()
            row.operator("object.orient_join", icon='AUTOMERGE_ON')
        
        if scn.menu_type == "UVTOOLS":  # this doesn't work
            
            col = layout.column(align=True)
            row = col.row(align=True)
            col = layout.column(align=True)
            row = col.row(align=True)
            
            col = layout.column(align=True)
            row = col.row(align=True)
            col = layout.column(align=True)
            row = col.row(align=True)
            row.operator("mesh.mark_seam", icon="SORTTIME")
            row.separator()
            row.operator("mesh.mark_seam", text='Clear Seam', icon="SORTSIZE").clear = True
            
            col = layout.column(align=True)
            row = col.row(align=True)
            col.label("Unwrap:")
            row.operator("uv.cube_project1", text="Planner Mapping", icon="SURFACE_NSURFACE")
            row.separator()
            row.operator("uv.cylinder_project", text="Cylindrical Mapping", icon="SURFACE_NCYLINDER")
            row.separator()
            row.operator("uv.sphere_project", text="Spherical Mapping", icon="SURFACE_NSPHERE")
            
            col = layout.column(align=True)
            row = col.row(align=True)
            row.operator("uv.smart_project", text="Automatic Mapping", icon="GROUP_VERTEX")
            row.separator()
            row.operator("uv.project_from_view", text="Create UV's based on camera ", icon="MOD_REMESH")
            
            col = layout.column(align=True)
            row = col.row(align=True)
            row.operator("mesh.uv_texture_add", text="Create New UV Set", icon="UV_FACESEL")
            row.separator()
            row.operator("mesh.uv_texture_add", text="Set Current UV Set", icon="UV_VERTEXSEL")
        
        if scn.menu_type == "DYNAMICS":
            layout.label("--------- UPDATE SOON ---------")
        
        if scn.menu_type == "ANIMATION":
            userpref = context.user_preferences
            edit = userpref.edit
            col = layout.column(align=True)
            row = col.row(align=True)
            row.operator("anim.keyframe_insert_menu", text="Set Key", icon='KEY_HLT')
            row.prop(toolsettings, "use_keyframe_insert_auto", text="Auto Key")
            
            col = layout.column(align=True)
            row = col.row(align=True)
            col.label("Tangents:")
            col.prop(edit, "keyframe_new_interpolation_type", text='Keys')
            col.separator()
            col.prop(edit, "keyframe_new_handle_type", text="Handles")
            col.separator()
            
            layout.label("Turnaround Camera:")
            scene = context.scene
            if (context.active_object is not None):
                if (context.active_object.type != 'CAMERA'):
                    buf = context.active_object.name
                    row = layout.row(align=False)
                    row.operator("object.rotate_around", icon='OUTLINER_DATA_CAMERA')
                    row.label(buf, icon='MESH_DATA')
                    row = layout.row()
                    row.prop(scene, "use_cursor")
                    row = layout.row(align=False)
                    row.prop(scene, "camera")
                    row = layout.row()
                    row.prop(scene, "frame_start")
                    row.prop(scene, "frame_end")
                    row = layout.row()
                    row.prop(scene, "camera_revol_x")
                    row.prop(scene, "camera_revol_y")
                    row.prop(scene, "camera_revol_z")
                    row = layout.row()
                    row.prop(scene, "inverse_x")
                    row.prop(scene, "inverse_y")
                    row.prop(scene, "inverse_z")
                    row = layout.row()
                    row.prop(scene, "back_forw")
                    row = layout.row()
                    row.prop(scene, "dolly_zoom")
                    if (scene.dolly_zoom != "0"):
                        row = layout.row()
                        row.prop(scene, "camera_from_lens")
                        row.prop(scene, "camera_to_lens")
                    row = layout.row()
                    row.prop(scene, "track")
                
                else:
                    buf = "No valid object selected"
                    layout.label(buf, icon='MESH_DATA')
            
            layout.separator()
            layout.label("Move and Delete Keys:")
            wm = context.window_manager
            layout = self.layout
            layout.prop(wm, 'drag', slider=True)
            column = layout.column(align=True)
            column.prop(wm, 'off', slider=False)
            column.prop(wm, 'sel')
            
            row = layout.row(align=True)
            row.operator('offset.reset', icon="FILE_REFRESH")
            row.operator('offset.apply', icon="FILE_TICK")
            col = layout.column(align=True)
            col.label(text="Delete Range Keys:")
            
            layout = self.layout
            row = layout.row()
            row.prop(wm, 'del_range_start')
            row.prop(wm, 'del_range_end')
            layout.operator('pose.delete_keyframes', icon='KEY_DEHLT')
            layout.separator()
            
            layout.label("Ghost Object:")
            arm = context.object.data
            layout.prop(arm, "ghost_type", expand=True)
            split = layout.split()
            col = split.column(align=True)
            
            if arm.ghost_type == 'RANGE':
                col.prop(arm, "ghost_frame_start", text="Start")
                col.prop(arm, "ghost_frame_end", text="End")
                col.prop(arm, "ghost_size", text="Step")
            elif arm.ghost_type == 'CURRENT_FRAME':
                col.prop(arm, "ghost_step", text="Range")
                col.prop(arm, "ghost_size", text="Step")
            
            col = split.column()
            col.label(text="Display:")
            col.prop(arm, "show_only_ghost_selected", text="Selected Only")


############## Transform Panel ##############
class Vismaya_TransformPanel(VIEW3D_PT_tools_vismaya, bpy.types.Panel):
    bl_label = "Transform"
    
    def draw(self, context):
        layout = self.layout
        
        col = layout.column(align=True)
        row = col.row(align=True)
        row.operator("transform.manipul_translate", icon='MAN_TRANS')
        row.separator()
        row.operator("transform.manipul_rotate", icon='MAN_ROT')
        row.separator()
        row.operator("transform.manipul_resize", icon='MAN_SCALE')
        row.separator()
        
        col = layout.column(align=True)
        row = col.row(align=True)
        row.operator("freeze_transform.selected", icon="FORCE_VORTEX")
        
        layout.label(text="Reset Transform")
        layout.operator("reset_transform.selected", icon="META_CUBE")
        layout.operator("reset_armature.selected", icon="GROUP_BONE")
        
        layout.label(text="Pivot")
        col = layout.column(align=True)
        row = col.row(align=True)
        row.operator_menu_enum("transform.set_pivot", "type", icon="CURSOR")
        row.operator("object.origin_set", text="Reset Pivot", icon="FILE_REFRESH").type = 'ORIGIN_CENTER_OF_MASS'
        
        layout.label(text="Freeze/UnFreeze Objects")
        col = layout.column(align=True)
        row = col.row(align=True)
        if vismaya_tools.mesh == 0:
            typ = 'Freez Mesh'
        else:
            typ = 'UnFreez Mesh'
        row.operator("object.mesh_all", text=typ, icon="MOD_SOLIDIFY")
        row.separator()
        if vismaya_tools.lamp == 0:
            typ = 'Freez Lamp'
        else:
            typ = 'UnFreez Lamp'
        row.operator("object.lamp_all", text=typ, icon="LIGHTPAINT")
        
        col = layout.column(align=True)
        row = col.row(align=True)
        
        if vismaya_tools.curve == 0:
            typ = 'Freez Curve'
        else:
            typ = 'UnFreez Curve'
        row.operator("object.curve_all", text=typ, icon="MOD_CURVE")
        row.separator()
        if vismaya_tools.bone == 0:
            typ = 'Freez Bone'
        else:
            typ = 'UnFreez Bone'
        row.operator("object.bone_all", text=typ, icon="WPAINT_HLT")
        col = layout.column(align=True)
        row = col.row(align=True)
        if vismaya_tools.particles == 0:
            typ = 'Freez Particles'
        else:
            typ = 'UnFreez Particles'
        row.operator("object.particles_all", text=typ, icon="MOD_PARTICLES")
        row.separator()
        if vismaya_tools.camera == 0:
            typ = 'Freez Camera'
        else:
            typ = 'UnFreez Camera'
        row.operator("object.camera_all", text=typ, icon="RESTRICT_RENDER_OFF")
        
        row.separator()
        layout.label(text="Constraint  Menu")
        obj = context.object
        layout.operator_menu_enum("object.constraint_add1", "type", text="  Add Object Constraint",
                                  icon="CONSTRAINT_DATA")
        
        for con in obj.constraints:
            self.draw_constraint(context, con)


############## Snapping Panel ##############
class Vismaya_SnappingPanel(VIEW3D_PT_tools_vismaya, bpy.types.Panel):
    bl_label = "Snapping"
    
    def draw(self, context):
        layout = self.layout
        
        obj = context.active_object
        toolsettings = context.tool_settings
        if obj:
            mode = obj.mode
        
        # Snap
        if not obj or mode not in {'SCULPT', 'VERTEX_PAINT', 'WEIGHT_PAINT', 'TEXTURE_PAINT'}:
            snap_element = toolsettings.snap_element
            # row = layout.row(align=True)
            col = layout.column(align=True)
            row = col.row(align=True)
            row.prop(toolsettings, "use_snap", text="On/Off")
            row.separator()
            col = layout.column(align=True)
            row = col.row(align=True)
            row.prop(toolsettings, "snap_element", icon_only=True)
            if snap_element != 'INCREMENT':
                col = layout.column(align=True)
                row = col.row(align=True)
                row.prop(toolsettings, "snap_target", text="Target")
                if obj:
                    if mode in {'OBJECT', 'POSE'} and snap_element != 'VOLUME':
                        row.prop(toolsettings, "use_snap_align_rotation", text="")
                    elif mode == 'EDIT':
                        row.prop(toolsettings, "use_snap_self", text="")
            
            if snap_element == 'VOLUME':
                row.prop(toolsettings, "use_snap_peel_object", text="")
            elif snap_element == 'FACE':
                row.prop(toolsettings, "use_snap_project", text="")
        
        # AutoMerge editing
        if obj:
            if (mode == 'EDIT' and obj.type == 'MESH'):
                layout.prop(toolsettings, "use_mesh_automerge", text="Auto Merge Vertices", icon='AUTOMERGE_ON')


############## Parenting Panel ##############
class Vismaya_ParentingPanel(VIEW3D_PT_tools_vismaya, bpy.types.Panel):
    bl_label = "Parenting"
    
    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        row = col.row(align=True)
        row.operator("object.parent_set", text="Set Parent", icon="ROTATECOLLECTION")
        row.operator("object.parent_clear", text="Reset Parent", icon="ROTACTIVE")


############## History Panel ##############
class Vismaya_HistoryPanel(VIEW3D_PT_tools_vismaya, bpy.types.Panel):
    bl_label = "History"
    
    def draw(self, context):
        layout = self.layout
        
        col = layout.column(align=True)
        row = col.row(align=True)
        row.operator("repeat.history", icon="MOD_BUILD")
        row.separator()
        row.operator("delete.history", icon="FULLSCREEN", text="Delete History")
        
        col = layout.column(align=True)
        row = col.row(align=True)
        row.operator("object.del_node", icon='DOT')
        
        col = layout.column(align=True)
        row = col.row(align=True)
        if vismaya_tools.opps1 == 1:
            scn = context.scene
            row.prop(scn, "mod_list")
            row.operator("ba.delete_data_obs")


############## View Panel ##############
class Vismaya_ViewPanel(VIEW3D_PT_tools_vismaya, bpy.types.Panel):
    bl_label = "View / Objects by Type"
    
    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        row = col.row(align=True)
        row.operator("object.frame_selected", icon="MOD_MESHDEFORM")
        row.operator("object.show_all", icon="WORLD_DATA")
        row.separator()
        layout.label(text="Objects by Type (Object Mode)")
        layout.operator_menu_enum("object.hide_by_type", "type", text="  Hide By Type", icon="SOLO_OFF")
        layout.operator_menu_enum("object.show_by_type", "type", text="  Show By Type", icon="SOLO_ON")
        layout.operator_menu_enum("object.sselect_by_type", "type", text="  Select By Type", icon="STICKY_UVS_LOC")
        layout.operator_menu_enum("object.deselect_by_type", "type", text="  Deselect By Type",
                                  icon="STICKY_UVS_DISABLE")


############## ProductionFolder Panel ##############
class Vismaya_ProductionFolderPanel(VIEW3D_PT_tools_vismaya, bpy.types.Panel):
    bl_label = "Production Folder"
    
    def draw(self, context):
        layout = self.layout
        layout.operator("productionfolder_scene.selected", text="Create Production", icon="FILE_FOLDER")
        layout.operator("production_scene.selected", text="Set Production", icon="NEWFOLDER")
        if vismaya_tools.pfopath != "":
            layout.operator("file.production_folder", text="Show Production", icon="SHOW_PRODUCTION")


bpy.types.WindowManager.off = bpy.props.IntProperty(name='Move Keys', min=-1000, soft_min=-250, max=1000, soft_max=250,
                                                    default=0,
                                                    description='Offset value for f-curves in selected objects')
bpy.types.WindowManager.drag = bpy.props.IntProperty(name='Drag', min=-drag_max, max=drag_max, default=0,
                                                     description='Drag to offset keyframes', update=drag)
bpy.types.WindowManager.sel = bpy.props.BoolProperty(name='Selected keys',
                                                     description='Only offset Selected keyframes in selected objects')
bpy.types.WindowManager.del_range_start = bpy.props.IntProperty(name='From', soft_min=0, min=-5000, soft_max=250,
                                                                max=5000, default=25,
                                                                description='Delete keyframes range start')
bpy.types.WindowManager.del_range_end = bpy.props.IntProperty(name='To', soft_min=0, min=-5000, soft_max=250,
                                                              max=5000, default=75,
                                                              description='Delete keyframes range end')


def menu_func(self, context):
    self.layout.operator(AddTorusKnot.bl_idname, text="Torus Knot", icon="MESH_CUBE")


############ Car Rig Panel ###########
class UImetaRigGenerate(bpy.types.Panel):
    bl_label = "Car Rig"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"
    
    @classmethod
    def poll(cls, context):
        if not context.armature:
            return False
        return True
    
    def draw(self, context):
        obj = bpy.context.active_object
        if obj.mode in {"POSE", "OBJECT"}:
            self.layout.operator("car.rig_generate", text='Generate')


class AddCarMetaRig(bpy.types.Operator):
    bl_idname = "car.meta_rig"
    bl_label = "Add car meta rig"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        CreateCarMetaRig((0, 0, 0))
        return {'FINISHED'}


class GenerateRig(bpy.types.Operator):
    # Generates a rig from metarig
    
    bl_idname = "car.rig_generate"
    bl_label = "Generate Car Rig"
    bl_options = {'UNDO'}
    
    def execute(self, context):
        generate((0, 0, 0))
        return {"FINISHED"}


########## Remove Properties ######################

def remove_properties():
    objlist = [obj for obj in bpy.context.scene.objects.keys() if
               bpy.data.objects[obj].type == 'MESH']
    proplist = [
        'shape_preset_data',
        'shape_preset_list',
        'shape_preset_index',
        'new_preset_name',
        'select_all_presets',
        'shapekeys_group_mode',
        'group_level_value',
        'category_name',
        'preset_category'
    ]
    for obj in objlist:
        for prop in proplist:
            try:
                del bpy.data.objects[obj][prop]
            except:
                pass
    
    del bpy.types.Object.shape_preset_list
    del bpy.types.Object.shape_preset_index
    del bpy.types.Object.new_preset_name
    del bpy.types.Object.select_all_presets
    del bpy.types.Object.shapekeys_group_mode
    del bpy.types.Object.group_level_value
    del bpy.types.Object.preset_category
    del bpy.types.Object.category_name


######## Save Properties ###############
def save_properties():
    bpy.types.Object.preset_category = EnumProperty(items=func.category_items, name='Category',
                                                    update=func.show_category,
                                                    description='Select a category of presets.')
    bpy.types.Object.category_name = StringProperty(name='',
                                                    description='Enter category here to assign it to highlighted preset.',
                                                    update=func.set_category)
    bpy.types.Object.shape_preset_list = CollectionProperty(type=OBJECT_PT_PresetNames)
    bpy.types.Object.shape_preset_index = IntProperty(update=func.show_active_preset)
    bpy.types.Object.new_preset_name = StringProperty(name='Name', update=func.rename_shape_preset)
    bpy.types.Object.select_all_presets = BoolProperty(name='All', description='Selects all your presets.',
                                                       update=func.select_all_presets)
    bpy.types.Object.shapekeys_group_mode = BoolProperty(name='Group',
                                                         description='Group Mode. All shape keys whose <number of first letters> are the same will be saved in preset.')
    bpy.types.Object.group_level_value = IntProperty(name='', min=1, max=10, default=3,
                                                     description='Number of letters the script has to consider to recognize a group of shape keys.')


######## Registration ################
def register():
    bpy.types.Scene.mod_list = bpy.props.EnumProperty(name="Target",
                                                      items=Delete_Unused_nodes.mod_data,
                                                      description="Module choice made for orphan deletion")
    bpy.types.Scene
    bpy.utils.register_module(__name__)
    bpy.types.Scene.batch_render = PointerProperty(type=BatchRenderData, name='Batch Render',
                                                   description='Settings used for batch rendering')
    save_properties()
    bpy.types.INFO_MT_armature_add.prepend(menu_func)
    
    bpy.types.Scene.camera_revol_x = bpy.props.FloatProperty(name='X', min=0, max=25
                                                             , default=0, precision=2
                                                             , description='Number total of revolutions in X axis')
    bpy.types.Scene.camera_revol_y = bpy.props.FloatProperty(name='Y', min=0, max=25
                                                             , default=0, precision=2
                                                             , description='Number total of revolutions in Y axis')
    bpy.types.Scene.camera_revol_z = bpy.props.FloatProperty(name='Z', min=0, max=25
                                                             , default=1, precision=2
                                                             , description='Number total of revolutions in Z axis')
    
    bpy.types.Scene.inverse_x = bpy.props.BoolProperty(name="-X", description="Inverse rotation", default=False)
    bpy.types.Scene.inverse_y = bpy.props.BoolProperty(name="-Y", description="Inverse rotation", default=False)
    bpy.types.Scene.inverse_z = bpy.props.BoolProperty(name="-Z", description="Inverse rotation", default=False)
    bpy.types.Scene.use_cursor = bpy.props.BoolProperty(name="Use cursor position",
                                                        description="Use cursor position instead of object origin",
                                                        default=False)
    bpy.types.Scene.back_forw = bpy.props.BoolProperty(name="Back and forward",
                                                       description="Create back and forward animation", default=False)
    
    bpy.types.Scene.dolly_zoom = bpy.props.EnumProperty(
        items=(('0', "None", ""), ('1', "Dolly zoom", ""), ('2', "Dolly zoom B/F", "")),
        name="Lens Effects", description="Create a camera lens movement")
    
    bpy.types.Scene.camera_from_lens = bpy.props.FloatProperty(name='From', min=1, max=500, default=35, precision=3
                                                               , description='Start lens value')
    bpy.types.Scene.camera_to_lens = bpy.props.FloatProperty(name='To', min=1, max=500, default=35, precision=3
                                                             , description='End lens value')
    
    bpy.types.Scene.track = bpy.props.BoolProperty(name="Create track constraint",
                                                   description="Add a track constraint to the camera", default=False)


def unregister():
    remove_properties()
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_armature_add.remove(menu_func)
    
    del bpy.types.Scene.camera_revol_x
    del bpy.types.Scene.camera_revol_y
    del bpy.types.Scene.camera_revol_z
    del bpy.types.Scene.inverse_x
    del bpy.types.Scene.inverse_y
    del bpy.types.Scene.inverse_z
    del bpy.types.Scene.use_cursor
    del bpy.types.Scene.back_forw
    del bpy.types.Scene.dolly_zoom
    del bpy.types.Scene.camera_from_lens
    del bpy.types.Scene.camera_to_lens
    del bpy.types.Scene.track


if __name__ == "__main__":
    register()
