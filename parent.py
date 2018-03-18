import bpy


class IK_Handle_Tool(bpy.types.Operator):
    bl_idname = 'object.ik_handle_tool'
    bl_label = 'IK Handle Tool'
    
    def execute(self, context):
        return {'FINISHED'}


class IK_Spline_Tool(bpy.types.Operator):
    bl_idname = 'object.ik_spline'
    bl_label = 'IK Spline'
    
    def execute(self, context):
        return {'FINISHED'}


class Orient_Joint(bpy.types.Operator):
    bl_idname = 'object.orient_joint'
    bl_label = 'Orient Joint'
    
    def execute(self, context):
        # bpy.ops.armature.fill()
        return {'FINISHED'}


class Reroot_Skeleton(bpy.types.Operator):
    bl_idname = "skele.ton"
    bl_label = "Reroot Skeleton"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        edit_bones = bpy.context.object.data.edit_bones
        for bone in edit_bones:
            if bone.select == True:
                bn = bone.name
            if not bone.parent:
                bp = bone.name
        for bones in edit_bones:
            if bones.name == bn:
                bpy.ops.armature.parent_clear()
        for bones in edit_bones:
            if bones.name == bp:
                bones.select = True
        for bones in edit_bones:
            if bones.name == bp:
                if bones.select == True:
                    bpy.ops.armature.parent_set(type='CONNECTED')
        return {'FINISHED'}


class Joint_Tool(bpy.types.Operator):
    bl_idname = 'object.joint_tool'
    bl_label = 'Joint Tool'
    
    def execute(self, context):
        if bpy.context.mode == 'OBJECT':
            bpy.ops.object.armature_add()
        else:
            bpy.ops.armature.bone_primitive_add()
        return {'FINISHED'}


class Insert_Joint(bpy.types.Operator):
    bl_idname = 'object.insert_joint_tool'
    bl_label = 'Insert Joint'
    
    def execute(self, context):
        bpy.ops.armature.fill()
        return {'FINISHED'}


class Remove_Joint(bpy.types.Operator):
    bl_idname = 'object.remove_joint'
    bl_label = 'Remove Joint'
    
    def execute(self, context):
        bpy.ops.armature.delete()
        return {'FINISHED'}


class Disconnect_Joint(bpy.types.Operator):
    bl_idname = 'object.disconnect_joint'
    bl_label = 'Disconnect Joint'
    
    def execute(self, context):
        bpy.ops.armature.split()
        return {'FINISHED'}


class Connect_Joint(bpy.types.Operator):
    bl_idname = 'object.connect_joint'
    bl_label = 'Connect Joint'
    
    def execute(self, context):
        bpy.ops.armature.parent_set(type='CONNECTED')
        return {'FINISHED'}
