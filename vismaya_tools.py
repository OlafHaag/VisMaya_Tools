import bpy

from bpy.types import Operator, Panel
from bpy.props import (StringProperty,
                       EnumProperty,
                       FloatProperty,
                       BoolProperty)
import os
from bpy_extras.io_utils import ExportHelper
from platform import system as currentOS

mesh = 0
curve = 0
lamp = 0
bone = 0
camera = 0
particles = 0
pfopath = ""
opps = 0
opps1 = 0


class TRANSFORM_Scale(bpy.types.Operator):
    bl_idname = "transform.manipul_resize"
    bl_label = "Scale"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        bpy.context.space_data.transform_manipulators = {'SCALE'}
        
        return {'FINISHED'}


class TRANSFORM_Rotate(bpy.types.Operator):
    bl_idname = "transform.manipul_rotate"
    bl_label = "Rotate"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        bpy.context.space_data.transform_manipulators = {'ROTATE'}
        
        return {'FINISHED'}


class TRANSFORM_Translate(bpy.types.Operator):
    bl_idname = "transform.manipul_translate"
    bl_label = "Move"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        bpy.context.space_data.transform_manipulators = {'TRANSLATE'}
        
        return {'FINISHED'}


############ Set Pivot ##############
class TRANSFORM_Set_Pivot(bpy.types.Operator):
    bl_idname = 'transform.set_pivot'
    bl_label = '  Set Pivot'
    bl_options = {'UNDO', 'REGISTER'}
    
    type = bpy.props.EnumProperty(items=(
        ('BOUNDING BOX CENTER', 'Bounding Box Center', ''),
        ('3D CURSOR', '3D Cursor', ''),
        ('INDIVIDUAL ORIGINS', 'Individual Origins', ''),
        ('MEDIAN POINT', 'Median Point', ''),
        ('ACTIVE ELEMENT', 'Active Element', '')),
        
        name='Type',
        description='Type',
        default='BOUNDING BOX CENTER',
        options={'ANIMATABLE'})
    
    def execute(self, context):
        if self.type == 'BOUNDING BOX CENTER':
            bpy.context.space_data.pivot_point = 'BOUNDING_BOX_CENTER'
        else:
            if self.type == '3D CURSOR':
                bpy.context.space_data.pivot_point = 'CURSOR'
            else:
                if self.type == 'INDIVIDUAL ORIGINS':
                    bpy.context.space_data.pivot_point = 'INDIVIDUAL_ORIGINS'
                else:
                    if self.type == 'MEDIAN POINT':
                        bpy.context.space_data.pivot_point = 'MEDIAN_POINT'
                    else:
                        if self.type == 'ACTIVE ELEMENT':
                            bpy.context.space_data.pivot_point = 'ACTIVE_ELEMENT'
        
        return {'FINISHED'}


########### Freeze Transformation ###########
class Set_Freezetransform(bpy.types.Operator):
    bl_idname = "freeze_transform.selected"
    bl_label = "Freeze Transform"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        
        str = context.active_object.type
        if str.startswith('EMPTY') or str.startswith('SPEAKER') or str.startswith('CAMERA') or str.startswith(
                'LAMP') or str.startswith('FONT'):
            # Location
            context.active_object.delta_location += context.active_object.location
            context.active_object.location = [0, 0, 0]
            
            # Rotation
            
            rotX = bpy.context.active_object.rotation_euler.x
            rotDeltaX = bpy.context.active_object.delta_rotation_euler.x
            bpy.context.active_object.delta_rotation_euler.x = rotX + rotDeltaX
            
            rotY = bpy.context.active_object.rotation_euler.y
            rotDeltaY = bpy.context.active_object.delta_rotation_euler.y
            bpy.context.active_object.delta_rotation_euler.y = rotDeltaY + rotY
            
            rotZ = bpy.context.active_object.rotation_euler.z
            rotDeltaZ = bpy.context.active_object.delta_rotation_euler.z
            bpy.context.active_object.delta_rotation_euler.z = rotDeltaZ + rotZ
            
            rquatW = context.active_object.rotation_quaternion.w
            rquatX = context.active_object.rotation_quaternion.x
            rquatY = context.active_object.rotation_quaternion.y
            rquatZ = context.active_object.rotation_quaternion.z
            
            drquatW = context.active_object.delta_rotation_quaternion.w
            drquatX = context.active_object.delta_rotation_quaternion.x
            drquatY = context.active_object.delta_rotation_quaternion.y
            drquatZ = context.active_object.delta_rotation_quaternion.z
            
            context.active_object.delta_rotation_quaternion.w = 1.0
            context.active_object.delta_rotation_quaternion.x = rquatX + drquatX
            context.active_object.delta_rotation_quaternion.y = rquatY + drquatY
            context.active_object.delta_rotation_quaternion.z = rquatZ + drquatZ
            
            context.active_object.rotation_quaternion.w = 1.0
            context.active_object.rotation_quaternion.x = 0.0
            context.active_object.rotation_quaternion.y = 0.0
            context.active_object.rotation_quaternion.z = 0.0
            
            bpy.context.active_object.rotation_euler.x = 0
            bpy.context.active_object.rotation_euler.y = 0
            bpy.context.active_object.rotation_euler.z = 0
            
            # Scale
            context.active_object.delta_scale.x += (
                                                               context.active_object.scale.x - 1) * context.active_object.delta_scale.x
            context.active_object.delta_scale.y += (
                                                               context.active_object.scale.y - 1) * context.active_object.delta_scale.y
            context.active_object.delta_scale.z += (
                                                               context.active_object.scale.z - 1) * context.active_object.delta_scale.z
            context.active_object.scale = [1, 1, 1]
            
            return {'FINISHED'}
        else:
            context.active_object.delta_location += context.active_object.location
            context.active_object.location = [0, 0, 0]
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
            
            return {'FINISHED'}


################ Production Folder #################
class Set_Production_Folder(bpy.types.Operator, ExportHelper):
    '''Save selected objects to a chosen format'''
    bl_idname = "production_scene.selected"
    bl_label = "Set Production"
    bl_options = {'REGISTER', 'UNDO'}
    
    filename_ext = bpy.props.StringProperty(
        default="",
        options={'HIDDEN'},
    )
    
    def invoke(self, context, event):
        self.filename_ext = ".blend"
        self.filepath = pfopath + "/prod/scenes/untitled"
        return ExportHelper.invoke(self, context, event)
    
    def execute(self, context):
        bpy.ops.wm.save_mainfile(
            filepath=self.filepath,
        )
        return {'FINISHED'}


class Production_Folder(bpy.types.Operator, ExportHelper):
    """Open the Production Folder in a file Browser"""
    bl_idname = "productionfolder_scene.selected"
    bl_label = "Create Production"
    bl_options = {'REGISTER', 'UNDO'}
    
    filename_ext = bpy.props.StringProperty(
        # --- If we hides this, both 2menu works but 2nd shows only run time error after creating folder.
        default="",
        options={'HIDDEN'},
    )
    
    filter_glob = bpy.props.StringProperty(
        default="",
        options={'HIDDEN'},
    )
    
    def invoke(self, context, event):
        self.filepath = "Production Folder"
        return ExportHelper.invoke(self, context, event)
    
    def execute(self, context):
        try:
            global pfopath
            pfopath = self.filepath
            folder_path = self.filepath
            path = folder_path + '/preprod'
            if not os.path.exists(path): os.makedirs(path)
            path = folder_path + '/prod'
            if not os.path.exists(path): os.makedirs(path)
            path = folder_path + '/ref'
            if not os.path.exists(path): os.makedirs(path)
            path = folder_path + '/resources'
            if not os.path.exists(path): os.makedirs(path)
            path = folder_path + '/wip'
            if not os.path.exists(path): os.makedirs(path)
            path1 = folder_path + '/prod/scenes'
            if not os.path.exists(path1): os.makedirs(path1)
            path1 = folder_path + '/prod/sets'
            if not os.path.exists(path1): os.makedirs(path1)
            path1 = folder_path + '/prod/props/textures'
            if not os.path.exists(path1): os.makedirs(path1)
            path1 = folder_path + '/prod/chars/textures'
            if not os.path.exists(path1): os.makedirs(path1)
            path1 = folder_path + '/prod/envs/textures'
            if not os.path.exists(path1): os.makedirs(path1)
            path1 = folder_path + '/prod/mattes/textures'
            if not os.path.exists(path1): os.makedirs(path1)
            self.report({'INFO'}, "Production folder created.")
        except ValueError:
            self.report({'INFO'}, "No Production folder created yet")
            return {'FINISHED'}
        return {'FINISHED'}


class Show_Production_Folder(bpy.types.Operator):
    bl_idname = "file.production_folder"
    bl_label = "Show Project"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        try:
            bpy.ops.wm.path_open(filepath=pfopath)
        except ValueError:
            self.report({'INFO'}, "No project folder yet")
            return {'FINISHED'}
        return {'FINISHED'}


############### Freeze/ UnFreeze Objects ##############
class OBJECT_OT_mesh_all(bpy.types.Operator):
    bl_idname = "object.mesh_all"
    bl_label = "Freez / UnFreez Mesh"
    
    def execute(self, context):
        objects = []
        eligible_objects = []
        objects = bpy.context.scene.objects
        # objects = scene.objects
        # Only Specific Types? + Filter layers
        for obj in objects:
            for i in range(0, 20):
                if obj.layers[i]:
                    if obj.type == 'MESH':
                        if obj not in eligible_objects:
                            eligible_objects.append(obj)
        objcts = eligible_objects
        if mesh == 0:
            global mesh
            mesh = 1
            for obj in objcts:  # deselect all objects
                obj.hide_select = True
        else:
            global mesh
            mesh = 0
            for obj in objcts:  # deselect all objects
                obj.hide_select = False
        return {'FINISHED'}


class OBJECT_OT_curve_all(bpy.types.Operator):
    bl_idname = "object.curve_all"
    bl_label = "Freez / UnFreez Curve"
    
    def execute(self, context):
        objects = []
        eligible_objects = []
        objects = bpy.context.scene.objects
        for obj in objects:
            for i in range(0, 20):
                if obj.layers[i]:
                    if obj.type == 'CURVE':
                        if obj not in eligible_objects:
                            eligible_objects.append(obj)
        objcts = eligible_objects
        if curve == 0:
            global curve
            curve = 1
            for obj in objcts:  # deselect all objects
                obj.hide_select = True
        else:
            global curve
            curve = 0
            for obj in objcts:  # deselect all objects
                obj.hide_select = False
        return {'FINISHED'}


class OBJECT_OT_lamp_all(bpy.types.Operator):
    bl_idname = "object.lamp_all"
    bl_label = "Freez / UnFreez Lamp"
    
    def execute(self, context):
        objects = []
        eligible_objects = []
        objects = bpy.context.scene.objects
        # objects = scene.objects
        # Only Specific Types? + Filter layers
        for obj in objects:
            for i in range(0, 20):
                if obj.layers[i]:
                    if obj.type == 'LAMP':
                        if obj not in eligible_objects:
                            eligible_objects.append(obj)
        objcts = eligible_objects
        if lamp == 0:
            global lamp
            lamp = 1
            for obj in objcts:  # deselect all objects
                obj.hide_select = True
        else:
            global curve
            lamp = 0
            for obj in objcts:  # deselect all objects
                obj.hide_select = False
        
        return {'FINISHED'}


class OBJECT_OT_bone_all(bpy.types.Operator):
    bl_idname = "object.bone_all"
    bl_label = "Freez / UnFreez Bone"
    
    def execute(self, context):
        objects = []
        eligible_objects = []
        objects = bpy.context.scene.objects
        for obj in objects:
            for i in range(0, 20):
                if obj.layers[i]:
                    if obj.type == 'ARMATURE':
                        if obj not in eligible_objects:
                            eligible_objects.append(obj)
        objcts = eligible_objects
        if bone == 0:
            global bone
            bone = 1
            for obj in objcts:  # deselect all objects
                obj.hide_select = True
        else:
            global bone
            bone = 0
            for obj in objcts:  # deselect all objects
                obj.hide_select = False
        return {'FINISHED'}


class OBJECT_OT_camera_all(bpy.types.Operator):
    bl_idname = "object.camera_all"
    bl_label = "Freez / UnFreez Camera"
    
    def execute(self, context):
        objects = []
        eligible_objects = []
        objects = bpy.context.scene.objects
        for obj in objects:
            for i in range(0, 20):
                if obj.layers[i]:
                    if obj.type == 'CAMERA':
                        if obj not in eligible_objects:
                            eligible_objects.append(obj)
        objcts = eligible_objects
        if camera == 0:
            global camera
            camera = 1
            for obj in objcts:  # deselect all objects
                obj.hide_select = True
        else:
            global camera
            camera = 0
            for obj in objcts:  # deselect all objects
                obj.hide_select = False
        return {'FINISHED'}


class OBJECT_OT_particules_all(bpy.types.Operator):
    bl_idname = "object.particles_all"
    bl_label = "Freez / UnFreez Praticles"
    
    def execute(self, context):
        objects = []
        eligible_objects = []
        objects = bpy.context.scene.objects
        for obj in objects:
            for i in range(0, 20):
                if obj.layers[i]:
                    if obj.type == 'PARTICLES':
                        if obj not in eligible_objects:
                            eligible_objects.append(obj)
        objcts = eligible_objects
        if particles == 0:
            global particles
            particles = 1
            for obj in objcts:  # deselect all objects
                obj.hide_select = True
        else:
            global particles
            particles = 0
            for obj in objcts:  # deselect all objects
                obj.hide_select = False
        return {'FINISHED'}
    
    def invoke(self, context, event):
        return {'RUNNING_MODAL'}


########### Snap Element ##############
class Set_Snap_face(bpy.types.Operator):
    bl_idname = "snap_face.selected"
    bl_label = "Face"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        bpy.context.scene.tool_settings.use_snap = True
        bpy.context.scene.tool_settings.snap_element = 'FACE'
        return {'FINISHED'}


class Set_Snap_edge(bpy.types.Operator):
    bl_idname = "snap_edge.selected"
    bl_label = "Edges"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        bpy.context.scene.tool_settings.use_snap = True
        bpy.context.scene.tool_settings.snap_element = 'EDGE'
        return {'FINISHED'}


class Set_Snap_vertex(bpy.types.Operator):
    bl_idname = "snap_vertex.selected"
    bl_label = "Vertex"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        bpy.context.scene.tool_settings.use_snap = True
        bpy.context.scene.tool_settings.snap_element = 'VERTEX'
        
        return {'FINISHED'}


class Set_Snap_grid(bpy.types.Operator):
    bl_idname = "snap_grid.selected"
    bl_label = "Grid"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        bpy.context.scene.tool_settings.use_snap = True
        bpy.context.scene.tool_settings.snap_element = 'INCREMENT'
        
        return {'FINISHED'}


############ Reset Transformation ###########
class Set_Reset_transform(bpy.types.Operator):
    bl_idname = "reset_transform.selected"
    bl_label = "Reset Object Transform"
    
    def execute(self, context):
        bpy.context.object.location = [0, 0, 0]
        bpy.context.object.rotation_euler = [0, 0, 0]
        bpy.context.object.scale = [1, 1, 1]
        return {'FINISHED'}


class Set_Reset_Armature_transform(bpy.types.Operator):
    bl_idname = "reset_armature.selected"
    bl_label = "Reset Armature Transform"
    
    def execute(self, context):
        obj = bpy.context.object.name
        if obj == 'Armature':
            bpy.ops.object.mode_set(mode='POSE', toggle=False)
            bpy.ops.pose.scale_clear()
            bpy.ops.pose.rot_clear()
            bpy.ops.pose.loc_clear()
        return {'FINISHED'}


##################### object by type ######################


class OBJECT_OT_HideShowByTypeTemplate():
    bl_options = {'UNDO', 'REGISTER'}
    
    type = bpy.props.EnumProperty(items=(
        ('MESH', 'Mesh', ''),
        ('CURVE', 'Curve', ''),
        ('SURFACE', 'Surface', ''),
        ('META', 'Meta', ''),
        ('FONT', 'Font', ''),
        ('ARMATURE', 'Armature', ''),
        ('LATTICE', 'Lattice', ''),
        ('EMPTY', 'Empty', ''),
        ('CAMERA', 'Camera', ''),
        ('LAMP', 'Lamp', ''),
        ('ALL', 'All', '')),
        name='Type',
        description='Type',
        default='LAMP',
        options={'ANIMATABLE'})
    
    def execute(self, context):
        
        scene = bpy.context.scene
        objects = []
        eligible_objects = []
        
        # Only Selected?
        if self.hide_selected:
            objects = bpy.context.selected_objects
        else:
            objects = scene.objects
            
            # Only Specific Types? + Filter layers
        for obj in objects:
            for i in range(0, 20):
                if obj.layers[i] & scene.layers[i]:
                    if self.type == 'ALL' or obj.type == self.type:
                        if obj not in eligible_objects:
                            eligible_objects.append(obj)
        objects = eligible_objects
        eligible_objects = []
        
        # Only Render Restricted?
        if self.hide_render_restricted:
            for obj in objects:
                if obj.hide_render == self.hide_or_show:
                    eligible_objects.append(obj)
            objects = eligible_objects
            eligible_objects = []
        
        # Perform Hiding / Showing
        for obj in objects:
            obj.hide = self.hide_or_show
        
        return {'FINISHED'}
    
    def invoke(self, context, event):
        return self.execute(context)


class OBJECT_OT_HideByType(OBJECT_OT_HideShowByTypeTemplate, bpy.types.Operator):
    bl_idname = 'object.hide_by_type'
    bl_label = 'Hide By Type'
    hide_or_show = bpy.props.BoolProperty(
        name="Hide",
        description="Inverse effect",
        options={'HIDDEN'},
        default=1)
    hide_selected = bpy.props.BoolProperty(
        name="Selected",
        description="Hide only selected objects",
        default=0)
    hide_render_restricted = bpy.props.BoolProperty(
        name="Only Render-Restricted",
        description="Hide only render restricted objects",
        default=0)


class OBJECT_OT_ShowByType(OBJECT_OT_HideShowByTypeTemplate, bpy.types.Operator):
    bl_idname = 'object.show_by_type'
    bl_label = 'Show By Type'
    hide_or_show = bpy.props.BoolProperty(
        name="Hide",
        description="Inverse effect",
        options={'HIDDEN'},
        default=0)
    hide_selected = bpy.props.BoolProperty(
        name="Selected",
        options={'HIDDEN'},
        default=0)
    hide_render_restricted = bpy.props.BoolProperty(
        name="Only Renderable",
        description="Show only non render restricted objects",
        default=0)


class OBJECT_OT_DeselectByType(bpy.types.Operator):
    bl_idname = 'object.deselect_by_type'
    bl_label = 'Deselect By Type'
    bl_options = {'UNDO', 'REGISTER'}
    
    type = bpy.props.EnumProperty(items=(
        ('MESH', 'Mesh', ''),
        ('CURVE', 'Curve', ''),
        ('SURFACE', 'Surface', ''),
        ('META', 'Meta', ''),
        ('FONT', 'Font', ''),
        ('ARMATURE', 'Armature', ''),
        ('LATTICE', 'Lattice', ''),
        ('EMPTY', 'Empty', ''),
        ('CAMERA', 'Camera', ''),
        ('LAMP', 'Lamp', ''),
        ('ALL', 'All', '')),
        name='Type',
        description='Type',
        default='LAMP',
        options={'ANIMATABLE'})
    
    def execute(self, context):
        
        scene = bpy.context.scene
        objects = []
        eligible_objects = []
        objects = bpy.context.selected_objects
        # objects = scene.objects
        # Only Specific Types? + Filter layers
        for obj in objects:
            for i in range(0, 20):
                if obj.layers[i]:
                    if self.type == 'ALL' or obj.type == self.type:
                        if obj not in eligible_objects:
                            eligible_objects.append(obj)
        objects = eligible_objects
        # Perform Hiding / Showing
        for obj in objects:
            obj.select = False
        return {'FINISHED'}


class OBJECT_OT_SelectByType(bpy.types.Operator):
    bl_idname = 'object.sselect_by_type'
    bl_label = 'Select By Type'
    bl_options = {'UNDO', 'REGISTER'}
    
    type = bpy.props.EnumProperty(items=(
        ('MESH', 'Mesh', ''),
        ('CURVE', 'Curve', ''),
        ('SURFACE', 'Surface', ''),
        ('META', 'Meta', ''),
        ('FONT', 'Font', ''),
        ('ARMATURE', 'Armature', ''),
        ('LATTICE', 'Lattice', ''),
        ('EMPTY', 'Empty', ''),
        ('CAMERA', 'Camera', ''),
        ('LAMP', 'Lamp', ''),
        ('ALL', 'All', '')),
        name='Type',
        description='Type',
        default='LAMP',
        options={'ANIMATABLE'})
    
    def execute(self, context):
        
        objects = []
        eligible_objects = []
        objects = bpy.context.scene.objects
        # objects = scene.objects
        # Only Specific Types? + Filter layers
        for obj in objects:
            for i in range(0, 20):
                if obj.layers[i]:
                    if self.type == 'ALL' or obj.type == self.type:
                        if obj not in eligible_objects:
                            eligible_objects.append(obj)
        objects = eligible_objects
        # Perform Hiding / Showing
        for obj in objects:
            obj.select = True
        return {'FINISHED'}


###################### Constraints ##############################

class ConstraintButtonsPanel():
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOL_PROPS"
    
    def draw_constraint(self, context, con):
        layout = self.layout
        box = layout.template_constraint(con)
        
        if box:
            # match enum type to our functions, avoids a lookup table.
            getattr(self, con.type)(context, box, con)
            
            if con.type not in {'RIGID_BODY_JOINT', 'NULL'}:
                box.prop(con, "influence")
    
    def space_template(self, layout, con, target=True, owner=True):
        if target or owner:
            
            split = layout.split(percentage=0.2)
            
            split.label(text="Space:")
            row = split.row()
            
            if target:
                row.prop(con, "target_space", text="")
            
            if target and owner:
                row.label(icon='ARROW_LEFTRIGHT')
            
            if owner:
                row.prop(con, "owner_space", text="")
    
    def target_template(self, layout, con, subtargets=True):
        layout.prop(con, "target")  # XXX limiting settings for only 'curves' or some type of object
        
        if con.target and subtargets:
            if con.target.type == 'ARMATURE':
                layout.prop_search(con, "subtarget", con.target.data, "bones", text="Bone")
                
                if hasattr(con, "head_tail"):
                    row = layout.row()
                    row.label(text="Head/Tail:")
                    row.prop(con, "head_tail", text="")
            elif con.target.type in {'MESH', 'LATTICE'}:
                layout.prop_search(con, "subtarget", con.target, "vertex_groups", text="Vertex Group")
    
    def COPY_LOCATION(self, context, layout, con):
        
        split = layout.split()
        
        col = split.column()
        col.prop(con, "use_x", text="X")
        col.prop(con, "use_y", text="Y")
        col.prop(con, "use_z", text="Z")
        
        col = split.column()
        sub = col.column()
        sub.active = con.use_x
        sub.prop(con, "invert_x", text="Invert")
        sub.active = con.use_y
        sub.prop(con, "invert_y", text="Invert")
        sub.active = con.use_z
        sub.prop(con, "invert_z", text="Invert")
        layout.prop(con, "use_offset", text="Maintain Offset")
        self.space_template(layout, con)
    
    def COPY_ROTATION(self, context, layout, con):
        
        split = layout.split()
        
        col = split.column()
        col.prop(con, "use_x", text="X")
        col.prop(con, "use_y", text="Y")
        col.prop(con, "use_z", text="Z")
        
        col = split.column()
        sub = col.column()
        sub.active = con.use_x
        sub.prop(con, "invert_x", text="Invert")
        sub.active = con.use_y
        sub.prop(con, "invert_y", text="Invert")
        sub.active = con.use_z
        sub.prop(con, "invert_z", text="Invert")
        
        layout.prop(con, "use_offset", text="Maintain Offset")
        
        self.space_template(layout, con)
    
    def COPY_SCALE(self, context, layout, con):
        
        row = layout.row(align=True)
        row.prop(con, "use_x", text="X")
        row.prop(con, "use_y", text="Y")
        row.prop(con, "use_z", text="Z")
        
        layout.prop(con, "use_offset", text="Maintain Offset")
        
        self.space_template(layout, con)
    
    def DAMPED_TRACK(self, context, layout, con):
        
        row = layout.row()
        row.label(text="To:")
        row.prop(con, "track_axis", expand=True)
    
    def TRACK_TO(self, context, layout, con):
        
        row = layout.row()
        row.label(text="To:")
        row.prop(con, "track_axis", expand=True)
        
        row = layout.row()
        row.prop(con, "up_axis", text="Up")
        row.prop(con, "use_target_z")
        
        self.space_template(layout, con)


class OBJECT_OT_Constraint(ConstraintButtonsPanel, bpy.types.Operator):
    bl_idname = 'object.constraint_add1'
    bl_label = 'Add Object Constraint'
    bl_options = {'UNDO', 'REGISTER'}
    
    type = bpy.props.EnumProperty(items=(
        ('POINT', 'Point', ''),
        ('AIM', 'Aim', ''),
        ('ORIENT', 'Orient', ''),
        ('SCALE', 'Scale', ''),
        ('PARENT', 'Parent', '')),
        
        name='Type',
        description='Type',
        default='POINT',
        options={'ANIMATABLE'})
    
    def execute(self, context):
        obj = context.active_object
        
        active = context.active_object
        n = 0
        selected = context.selected_objects[:]
        selected.remove(active)
        for j in selected:
            n = n + 1
        if n == 1:
            if self.type == 'POINT':
                bpy.ops.object.constraint_add(type='COPY_LOCATION')
                for i in selected:
                    point1 = active.constraints["Copy Location"]
                    point1.target = i
                    bpy.context.active_object.constraints['Copy Location'].name = 'Point'
                    bpy.context.object.constraints["Point"].use_offset = True
            else:
                if self.type == 'ORIENT':
                    bpy.ops.object.constraint_add(type='COPY_ROTATION')
                    for i in selected:
                        active.constraints["Copy Rotation"].target = i
                        bpy.context.active_object.constraints['Copy Rotation'].name = 'Orient'
                        bpy.context.object.constraints["Orient"].use_offset = True
                else:
                    if self.type == 'SCALE':
                        bpy.ops.object.constraint_add(type='COPY_SCALE')
                        for i in selected:
                            active.constraints["Copy Scale"].target = i
                            bpy.context.active_object.constraints['Copy Scale'].name = 'Scale'
                            bpy.context.object.constraints["Scale"].use_offset = True
                    else:
                        if self.type == 'AIM':
                            if obj.type == 'CAMERA':
                                bpy.ops.object.constraint_add(type='DAMPED_TRACK')
                                for i in selected:
                                    active.constraints["Damped Track"].target = i
                                    bpy.context.active_object.constraints['Damped Track'].name = 'Aim'
                            else:
                                bpy.ops.object.constraint_add(type='TRACK_TO')
                                for i in selected:
                                    active.constraints["Track To"].target = i
                                    bpy.context.active_object.constraints['Track To'].name = 'Aim'
                        else:
                            if self.type == 'PARENT':
                                if obj.type == bpy.screens.transform_manipulator:
                                    bpy.ops.object.constraint_add(type='COPY_LOCATION')
                                if obj.type == 'CAMERA':
                                    bpy.ops.object.constraint_add(type='COPY_ROTATION')
        
        return {'FINISHED'}


class Object_Frame_Selected(bpy.types.Operator):
    bl_idname = "object.frame_selected"
    bl_label = "Frame Selected"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        bpy.ops.view3d.view_selected()
        return {'FINISHED'}


class Object_Show_All(bpy.types.Operator):
    bl_idname = "object.show_all"
    bl_label = "Show_all"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        bpy.ops.view3d.view_all()
        return {'FINISHED'}


class Object_repeat_tool(bpy.types.Operator):
    bl_idname = "repeat.tool"
    bl_label = "Repeat Tool"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        return {'FINISHED'}


class Object_delete_history(bpy.types.Operator):
    bl_idname = "delete.history"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        bpy.ops.ed.undo()
        bpy.ops.ed.redo()
        for i in range(1, 64):
            bpy.ops.ed.undo_push(message="")
        return {'CANCELLED'}


class Object_repeat_history(bpy.types.Operator):
    bl_idname = "repeat.history"
    bl_label = "Repeat History"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        bpy.ops.screen.repeat_last()
        return {'CANCELLED'}


class Object_Del_history(bpy.types.Operator):
    bl_idname = "object.del_node"
    bl_label = "Delete Unused Node"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        if opps1 == 0:
            global opps1
            opps1 = 1
        
        else:
            global opps1
            opps1 = 0
        return {'FINISHED'}


class Object_View_Port(bpy.types.Operator):
    bl_idname = "object.viewport_nav"
    bl_label = "Viewport Navigation"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        if opps == 0:
            global opps
            opps = 1
        
        else:
            global opps
            opps = 0
        return {'FINISHED'}
