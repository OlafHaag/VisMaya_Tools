import bpy

#Append a '.L' to the end of all selected bones names
class AppendL(bpy.types.Operator):
    'Put a .L to the end of the names of selected bones' #tooltip
    bl_idname='appendl.op'
    bl_label='Append .L'
    
    
    def execute(self, context):
        loopcount=2 #number of times to loop
        loopnum=0
        while loopnum<loopcount: #loop to make sure all bones end in .L, rather than .L.001 (such bones would now end in .L.001.L)
            for e in bpy.context.selected_editable_bones:
                if e.name.endswith(".L"):
                    print (e.name+" ends in .L already")
                elif e.name.endswith(".R"):
                    print (e.name+" ends in .R - replacing with .L")
                    e.name=e.name.replace('','')[:-2]
                    e.name += '.L' 
                elif e.name.endswith(".M"):
                    print (e.name+" ends in .M - replacing with .L")
                    e.name=e.name.replace('','')[:-2]
                    e.name += '.L' 
                elif e.name.endswith(".R.001"):
                    print (e.name+" ends in .R.001 - replacing with .L")
                    e.name=e.name.replace('','')[:-6]
                    e.name += '.L'
                else:
                    e.name += '.L' 
            loopnum+=1
        return {'FINISHED'}


#Append a '.R' to the end of all selected bones names
class AppendR(bpy.types.Operator):
    'Put a .R to the end of the names of selected bones' #tooltip
    bl_idname='appendr.op'
    bl_label='Append .R'
    
    def execute(self, context):
        loopcount=2 #number of times to loop
        loopnum=0
        while loopnum<loopcount: #loop to make sure all bones end in .R, rather than .R.001 (such bones would now end in .R.001.R)
            for e in bpy.context.selected_editable_bones:
                if e.name.endswith(".R"):
                    print (e.name+" ends in .R already")
                elif e.name.endswith(".L"):
                    print (e.name+" ends in .L - replacing with .R")
                    e.name=e.name.replace('','')[:-2]
                    e.name += '.R' 
                elif e.name.endswith(".M"):
                    print (e.name+" ends in .M - replacing with .R")
                    e.name=e.name.replace('','')[:-2]
                    e.name += '.R' 
                elif e.name.endswith(".L.001"):
                    print (e.name+" ends in .L.001 - replacing with .R")
                    e.name=e.name.replace('','')[:-6]
                    e.name += '.R'
                else:
                    e.name += '.R' 
            loopnum+=1
        return {'FINISHED'}    
    
    
#Flips .L and .R suffixes for selected bones
class FlipSuffix(bpy.types.Operator):
    'Flips .L and .R suffixes for selected bones'
    bl_idname='flipsuffix.op'
    bl_label='Flip Suffixes'
    
    def execute (self,context):
        loopcount=3
        loopnum=0
        while loopnum<loopcount:
            for e in bpy.context.selected_editable_bones:
                if e.name.endswith(".R"):
                    e.name=e.name.replace('','')[:-2]
                    e.name+='.L'
                    print (e.name+" ends in .R, replacing with .L")
                elif e.name.endswith(".L"):
                    e.name=e.name.replace('','')[:-2]
                    e.name+='.R'
                    print (e.name+" ends in .L, replacing with .R")
                elif e.name.endswith(".M"):
                    print (e.name+" ends in .M, doing nothing")
                else:
                    print (e.name+" ends in neither .R, .L or .M")
            loopnum+=1
        for e in bpy.context.selected_editable_bones:
            if e.name.endswith("R.001"):
                e.name=e.name.replace('','')[:-4]
            elif e.name.endswith("L.001"):
                e.name=e.name.replace('','')[:-4]
        return {'FINISHED'}    
    
    
#Add a .L, .R or .M to selected bone names based on bone's local X location
class AutoNameSuffix(bpy.types.Operator):
    'Add a .L, .R or .M to selected bone names based on bones local X location. Set Middle first to prevent inaccurate naming of middle bones'
    bl_idname='autobonesuffix.op'
    bl_label='Auto Name Suffix'
    
    def execute(self,context):
        loopcount=2 #number of times to loop
        loopnum=0
        while loopnum<loopcount:
            for e in bpy.context.selected_editable_bones:
                if e.center[0]<0:
                    if e.name.endswith(".R"):
                        print (e.name+" ends in .R already")
                    elif e.name.endswith(".L"):
                        print (e.name+" ends in .L - replacing with .R")
                        e.name=e.name.replace('','')[:-2]
                        e.name += '.R' 
                    elif e.name.endswith(".M"):
                        print (e.name+" ends in .M - replacing with .R")
                        e.name=e.name.replace('','')[:-2]
                        e.name += '.R' 
                    else:
                        e.name += '.R' 
                elif e.center[0]>0:
                    if e.name.endswith(".L"):
                        print (e.name+" ends in .L already")
                    elif e.name.endswith(".R"):
                        print (e.name+" ends in .R - replacing with .L")
                        e.name=e.name.replace('','')[:-2]
                        e.name += '.L' 
                    elif e.name.endswith(".M"):
                        print (e.name+" ends in .M - replacing with .L")
                        e.name=e.name.replace('','')[:-2]
                        e.name += '.L' 
                    else:
                        e.name += '.L' 
                else:
                    print ("blah")
                    if e.name.endswith(".M"):
                        print (e.name+" ends in .M already")
                    elif e.name.endswith(".R"):
                        print (e.name+" ends in .R - replacing with .M")
                        e.name=e.name.replace('','')[:-2]
                        e.name += '.M' 
                    elif e.name.endswith(".L"):
                        print (e.name+" ends in .L - replacing with .M")
                        e.name=e.name.replace('','')[:-2]
                        e.name += '.M' 
                    else:
                        e.name += '.M' 
            loopnum+=1
        #self.report({'INFO'}, "balh!")
        for e in bpy.context.selected_editable_bones:
            if e.name.endswith(".L.001.L"):
                e.name=e.name.replace('','')[:-6]
            elif e.name.endswith(".R.001.R"):
                e.name=e.name.replace('','')[:-6]
            elif e.name.endswith(".R.001.L"):
                e.name=e.name.replace('','')[:-8]
                e.name += ".L"
            elif e.name.endswith(".L.001.R"):
                e.name=e.name.replace('','')[:-8]
                e.name += ".R"
        return {'FINISHED'}    
    
    
#Is definitly in middle
class SetMiddle(bpy.types.Operator):
    'Makes sure that the selected bones are in the middle of local space and end in .M'
    bl_idname='setmiddle.op'
    bl_label='Set Middle'
    
    def execute(self,context):
        for e in bpy.context.selected_editable_bones:
            if e.name.endswith(".M"):
                print (e.name+" ends in .M already")
            elif e.name.endswith(".R"):
                print (e.name+" ends in .R - replacing with .M")
                e.name=e.name.replace('','')[:-2]
                e.name += '.M' 
            elif e.name.endswith(".L"):
                print (e.name+" ends in .L - replacing with .M")
                e.name=e.name.replace('','')[:-2]
                e.name += '.M' 
            else:
                e.name += '.M' 
            e.head.x=0
            e.tail.x=0
        return {'FINISHED'}    
    

#Mirrors selected bones
class MirrorBones(bpy.types.Operator):
    'Duplicates and mirrors the selected bones with correct names'
    bl_idname='mirrorbones.op'
    bl_label='Mirror Bones'
    
    def execute(self,context):
        bpy.ops.armature.duplicate()
        for e in bpy.context.selected_editable_bones:
            e.head.x=e.head.x*-1
            e.tail.x=e.tail.x*-1
            if e.name.endswith(".L.001"):
                e.name=e.name.replace('','')[:-5]
                e.name+='R'
            elif e.name.endswith('.R.001'):
                e.name=e.name.replace('','')[:-5]
                e.name+='L'
            elif e.name.endswith('.M.001'):
                oldname=e.name.replace('','')[:-4]
                self.report({'INFO'}, oldname+" ends in .M and was not mirrored")
            else:
                oldname=e.name.replace('','')[:-4]
                self.report({'INFO'}, "WARNING! "+oldname+" does not end in .L .R or .M")
        bpy.ops.object.select_pattern(pattern="*.M.001", case_sensitive=False, extend=False)
        bpy.ops.armature.delete()
        return {'FINISHED'}    
    
    
#Select all bones with .L suffix
class SelectL(bpy.types.Operator):
    'Appends all bones with .L suffix to selection'
    bl_idname='selectl.op'
    bl_label='Select .L'
    
    def execute(self,context):
        bpy.ops.object.select_pattern(pattern="*.L", case_sensitive=False, extend=True)
        return {'FINISHED'}
    
    
#Select all bones with .R suffix
class SelectR(bpy.types.Operator):
    'Appends all bones with .R suffix to selection'
    bl_idname='selectr.op'
    bl_label='Select .R'
    
    def execute(self,context):
        bpy.ops.object.select_pattern(pattern="*.R", case_sensitive=False, extend=True)
        return {'FINISHED'}
    
    
#Select all bones with .M suffix
class SelectM(bpy.types.Operator):
    'Appends all bones with .M suffix to selection'
    bl_idname='selectm.op'
    bl_label='Select .M'
    
    def execute(self,context):
        bpy.ops.object.select_pattern(pattern="*.M", case_sensitive=False, extend=True)
        return {'FINISHED'}    
    
    
#Select all bones that don't have any suffix (.L .R or .M)
class SelectNonSuffix(bpy.types.Operator):
    'Select all bones that do not have any suffix (.L .R or .M)'
    bl_idname='selectnonsuffix.op'
    bl_label='Select Non-Suffixed'
    
    def execute(self,context):
        bpy.ops.object.select_pattern(pattern="SweetJesusThisIsOneUnlikelyBoneName!oasdbngsdhdfnLJKSDNFH", case_sensitive=True, extend=False)        
        bpy.ops.object.select_pattern(pattern="*.M", case_sensitive=False, extend=True)        
        bpy.ops.object.select_pattern(pattern="*.L", case_sensitive=False, extend=True)
        bpy.ops.object.select_pattern(pattern="*.R", case_sensitive=False, extend=True)
        bpy.ops.armature.select_inverse()
        return {'FINISHED'}
    
    
#Select all bones that don't have a mirror of themselves
class SelectVampire(bpy.types.Operator):
    'Select all bones that do not have a mirror of themselves'
    bl_idname='selectvampire.op'
    bl_label='Select Vampires'
    
    def execute(self,context):
        bpy.ops.object.select_pattern(pattern="*", case_sensitive=False, extend=False)
        for x in bpy.context.selected_editable_bones:
            ismirror=0
            for y in bpy.context.selected_editable_bones:
                if x.name.endswith(".L")==False and x.name.endswith('.R')==False and x.name.endswith('.M')==False:
                    ismirror=0
                elif x.name!=y.name:
                    xbase=x.name.replace('','')[:-2]
                    ybase=y.name.replace('','')[:-2]
                    if xbase==ybase:
                        ismirror+=1
            if ismirror==0:
                x.name+="._nomirror_!"
        bpy.ops.object.select_pattern(pattern="*._nomirror_!", case_sensitive=False, extend=False)
        for x in bpy.context.selected_editable_bones:
            x.name=x.name.replace('','')[:-12]
        return {'FINISHED'}  
    
    
#Rename all selected bones to match the active bone name.
class BatchRename(bpy.types.Operator):
    'Rename all selected bones to match the active bone name with an index'
    bl_idname='batchrename.op'
    bl_label='Batch Rename'
    
    def execute(self,context):
        for e in bpy.context.selected_editable_bones:
            e.name=bpy.context.active_bone.name
        return {'FINISHED'}


       
                    
def menu_func(self, context):
	self.layout.operator(AddTorusKnot.bl_idname, text="Torus Knot", icon="MESH_CUBE")

 
