import bpy
import mathutils
from bpy.props import *
import math, os
from bpy_extras.io_utils import (ExportHelper, ImportHelper)


class TriLighting(bpy.types.Operator):
    """TriL ightning"""
    bl_idname = "object.trilighting"  # unique identifier for buttons and menu items to reference.
    bl_label = "Tri-Lighting Creator"  # display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}  # enable undo for the operator.
    
    height = bpy.props.FloatProperty(name="Height", default=5)
    distance = bpy.props.FloatProperty(name="Distance", default=5, min=0.1, subtype="DISTANCE")
    energy = bpy.props.IntProperty(name="Base Energy", default=3, min=1)
    contrast = bpy.props.IntProperty(name="Contrast", default=50, min=-100, max=100, subtype="PERCENTAGE")
    left_angle = bpy.props.IntProperty(name="Left Angle", default=26, min=1, max=90, subtype="ANGLE")
    right_angle = bpy.props.IntProperty(name="Right Angle", default=45, min=1, max=90, subtype="ANGLE")
    back_angle = bpy.props.IntProperty(name="Back Angle", default=235, min=90, max=270, subtype="ANGLE")
    
    Light_Type_List = [('POINT', 'Point', 'Point Light'),
                       ('SUN', 'Sun', 'Sun Light'),
                       ('SPOT', 'Spot', 'Spot Light'),
                       ('HEMI', 'Hemi', 'Hemi Light'),
                       ('AREA', 'Area', 'Area Light')]
    primary_type = EnumProperty(attr='tl_type',
                                name='Key Type',
                                description='Choose the type off Key Light you would like',
                                items=Light_Type_List, default='HEMI')
    
    secondary_type = EnumProperty(attr='tl_type',
                                  name='Fill+Back Type',
                                  description='Choose the type off secondary Light you would like',
                                  items=Light_Type_List, default='POINT')
    
    def execute(self, context):
        scene = context.scene
        view = context.space_data
        if view.type == 'VIEW_3D' and not view.lock_camera_and_layers:
            camera = view.camera
        else:
            camera = scene.camera
        
        if camera is None:
            cam_data = bpy.data.cameras.new(name='Camera')
            cam_obj = bpy.data.objects.new(name='Camera', object_data=cam_data)
            scene.objects.link(cam_obj)
            scene.camera = cam_obj
            bpy.ops.view3d.camera_to_view()
            camera = cam_obj
            bpy.ops.view3d.viewnumpad(type='TOP')
        
        obj = bpy.context.scene.objects.active
        
        #####Calculate Energy for each Lamp
        
        if (self.contrast > 0):
            key_energy = self.energy
            back_energy = (self.energy / 100) * abs(self.contrast)
            fill_energy = (self.energy / 100) * abs(self.contrast)
        else:
            key_energy = (self.energy / 100) * abs(self.contrast)
            back_energy = self.energy
            fill_energy = self.energy
        
        print(self.contrast)
        
        #####Calculate Direction for each Lamp
        # Calculate current Distance and get Delta
        obj_position = obj.location
        cam_position = camera.location
        
        delta_position = cam_position - obj_position
        vector_length = math.sqrt((pow(delta_position.x, 2) + pow(delta_position.y, 2) + pow(delta_position.z, 2)))
        single_vector = (1 / vector_length) * delta_position
        
        # Calc back position
        single_back_vector = single_vector.copy()
        single_back_vector.x = math.cos(math.radians(self.back_angle)) * single_vector.x + (
                -math.sin(math.radians(self.back_angle)) * single_vector.y)
        single_back_vector.y = math.sin(math.radians(self.back_angle)) * single_vector.x + (
                math.cos(math.radians(self.back_angle)) * single_vector.y)
        backx = obj_position.x + self.distance * single_back_vector.x
        backy = obj_position.y + self.distance * single_back_vector.y
        
        back_data = bpy.data.lamps.new(name="TriLamp-Back", type=self.secondary_type)
        back_data.energy = back_energy
        
        back_lamp = bpy.data.objects.new(name="TriLamp-Back", object_data=back_data)
        scene.objects.link(back_lamp)
        back_lamp.location = (backx, backy, self.height)
        
        track_to_back = back_lamp.constraints.new(type="TRACK_TO")
        track_to_back.target = obj
        track_to_back.track_axis = "TRACK_NEGATIVE_Z"
        track_to_back.up_axis = "UP_Y"
        
        # Calc right position
        single_right_vector = single_vector.copy()
        single_right_vector.x = math.cos(math.radians(self.right_angle)) * single_vector.x + (
                -math.sin(math.radians(self.right_angle)) * single_vector.y)
        single_right_vector.y = math.sin(math.radians(self.right_angle)) * single_vector.x + (
                math.cos(math.radians(self.right_angle)) * single_vector.y)
        rightx = obj_position.x + self.distance * single_right_vector.x
        righty = obj_position.y + self.distance * single_right_vector.y
        
        right_data = bpy.data.lamps.new(name="TriLamp-Fill", type=self.secondary_type)
        right_data.energy = fill_energy
        right_lamp = bpy.data.objects.new(name="TriLamp-Fill", object_data=right_data)
        scene.objects.link(right_lamp)
        right_lamp.location = (rightx, righty, self.height)
        track_to_right = right_lamp.constraints.new(type="TRACK_TO")
        track_to_right.target = obj
        track_to_right.track_axis = "TRACK_NEGATIVE_Z"
        track_to_right.up_axis = "UP_Y"
        
        # Calc left position
        single_left_vector = single_vector.copy()
        single_left_vector.x = math.cos(math.radians(-self.left_angle)) * single_vector.x + (
                -math.sin(math.radians(-self.left_angle)) * single_vector.y)
        single_left_vector.y = math.sin(math.radians(-self.left_angle)) * single_vector.x + (
                math.cos(math.radians(-self.left_angle)) * single_vector.y)
        leftx = obj_position.x + self.distance * single_left_vector.x
        lefty = obj_position.y + self.distance * single_left_vector.y
        
        left_data = bpy.data.lamps.new(name="TriLamp-Key", type=self.primary_type)
        left_data.energy = key_energy
        
        left_lamp = bpy.data.objects.new(name="TriLamp-Key", object_data=left_data)
        scene.objects.link(left_lamp)
        left_lamp.location = (leftx, lefty, self.height)
        track_to_left = left_lamp.constraints.new(type="TRACK_TO")
        track_to_left.target = obj
        track_to_left.track_axis = "TRACK_NEGATIVE_Z"
        track_to_left.up_axis = "UP_Y"
        
        return {'FINISHED'}
