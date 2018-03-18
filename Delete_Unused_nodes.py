import bpy

mod_data = [tuple(["actions"] * 3), tuple(["armatures"] * 3),
            tuple(["cameras"] * 3), tuple(["curves"] * 3),
            tuple(["fonts"] * 3), tuple(["grease_pencil"] * 3),
            tuple(["groups"] * 3), tuple(["images"] * 3),
            tuple(["lamps"] * 3), tuple(["lattices"] * 3),
            tuple(["libraries"] * 3), tuple(["materials"] * 3),
            tuple(["meshes"] * 3), tuple(["metaballs"] * 3),
            tuple(["node_groups"] * 3), tuple(["objects"] * 3),
            tuple(["sounds"] * 3), tuple(["texts"] * 3),
            tuple(["textures"] * 3), ]

if bpy.app.version[1] >= 60:
    mod_data.append(tuple(["speakers"] * 3), )


class DeleteOrphansOp(bpy.types.Operator):
    """Remove all orphaned objects of a selected type from the project."""
    bl_idname = "ba.delete_data_obs"
    bl_label = "Delete Orphans"
    
    def execute(self, context):
        target = context.scene.mod_list
        target_coll = eval("bpy.data." + target)
        
        num_deleted = len([x for x in target_coll if x.users == 0])
        num_kept = len([x for x in target_coll if x.users == 1])
        
        for item in target_coll:
            if item.users == 0:
                target_coll.remove(item)
        
        msg = "Removed %d orphaned %s objects. Kept %d non-orphans" % (num_deleted, target, num_kept)
        self.report({'INFO'}, msg)
        return {'FINISHED'}
