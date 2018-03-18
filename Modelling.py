import bpy

from bpy.types import Operator, Panel
from bpy.props import (StringProperty,
                       EnumProperty,
                       FloatProperty,
                       BoolProperty)



import bmesh , random , math
from bpy.types import Header, Menu
import os
import getpass
from bpy.props import EnumProperty, PointerProperty, BoolProperty
from bpy.props import IntProperty, FloatProperty ,FloatVectorProperty
from bpy.props import PointerProperty, StringProperty, BoolProperty, EnumProperty, IntProperty, CollectionProperty
from mathutils import Vector
from bpy_extras.io_utils import ExportHelper
from platform import system as currentOS
from bl_ui.properties_paint_common import UnifiedPaintPanel
pfopath=""
path = ""
ti = 0
value = 0.01
delta1 = 0
deltay1 = 0
x = 0
y = 0
z = 0


############## Delete Menu ##################
class Vismaya_MT_edit_mesh_delete(bpy.types.Menu):    
    bl_label = "Delete"
    def draw(self, context):
        layout = self.layout

        layout.operator("mesh.delete", text="Vertices")   
        layout.operator("mesh.delete", text="Edges").type="EDGE"
        layout.operator("mesh.delete", text="Faces").type="FACE"         
        layout.operator("mesh.delete_edgeloop", text="Edge Loop")


################ Mirror Menu ##################
class Vismaya_MT_edit_mesh_mirror(bpy.types.Menu):
    bl_label = "Mirror"

    def draw(self, context):
        layout = self.layout

        layout.operator("mirror.selected", text="Interactive Mirror")

        layout.separator()

        props = layout.operator("mirror.selected", text="Global X") 
        props.con_x =  True
        props.orientation = 'GLOBAL'
        props = layout.operator("mirror.selected", text="Global Y")
        props.con_y =  True
        props.orientation = 'GLOBAL'
        props = layout.operator("mirror.selected", text="Global Z")
        props.con_z =  True
        props.orientation = 'GLOBAL'

        if context.edit_object:
            layout.separator()

            props = layout.operator("mirror.selected", text="Local X") 
            props.con_x =  True
            props.orientation = 'LOCAL'
            props = layout.operator("mirror.selected", text="Local Y")
            props.con_y =  True
            props.orientation = 'LOCAL'
            props = layout.operator("mirror.selected", text="Local Z")
            props.con_z =  True
            props.orientation = 'LOCAL'


############## Extrude Normal #############
class Extrude_Normal(bpy.types.Operator):
    bl_idname = "extrudenormal.selected"
    bl_label = "Extrude and Move on Normals"
    bl_options = {'REGISTER', 'UNDO'}
    
    location = FloatVectorProperty(name = "Vector", subtype = 'TRANSLATION',default = (0.0,0.0,0.0,),min = -100.0, max = 100.0,soft_min = -10,soft_max = 10,step = 0.1 ,size =3)
    
    orientation = EnumProperty(items = (('one', 'Global','GLOBAL',1),('two','Local','LOCAL',2),('three', 'Normal', 'NORMAL',  3),('four', 'Gimbal','GIMBAL', 4),('five', 'View', 'VIEW', 5)),default = 'three',name = "")  
    
    propo_edit = EnumProperty(items = (('one','Disable','DISABLED','PROP_OFF', 1),('two','Enable','ENABLED','PROP_ON',2),('three', 'Projected (2D)','PROJECTED', 'PROP_ON',3),('four', 'Connected', 'CONNECTED','PROP_CON',4)),default = 'one',name = "")  
    
    propo_edit_fall = EnumProperty(items = (('one', 'Smooth','SMOOTH','SMOOTHCURVE', 1),('two','Sphere','SPHERE','SPHERECURVE', 2),('three', 'Root','ROOT','ROOTCURVE', 3),('four', 'Sharp','SHARP','SHARPCURVE', 4),('five','Linear','LINEAR', 'LINCURVE', 5),('six','Constant','CONSTANT', 'NOCURVE',6),('seven', 'Random', 'RANDOM','RNDCURVE', 7)),default = 'one',name = "")
    
    propo_size = FloatProperty(name = "", description = "", default = 1, min = 0.001, max = 100.000)
    
    con_x = BoolProperty(name="x", description="", default=False)
    con_y = BoolProperty(name="y", description="", default=False)
    con_z = BoolProperty(name="z", description="", default=True)
    
    release = BoolProperty(name="release on confirm", description="release on confirm", default=False)
    
    texture = BoolProperty(name="Edit Texture", description="", default=False)
    
    def draw(self, context):
        layout = self.layout
        
        row = layout.column(align = True)
        row.prop(self,'location')
        layout.label("Constraint Axis")
        layout.prop(self,'con_x')
        layout.prop(self,'con_y')
        layout.prop(self,'con_z')
        layout.label("Orientation")
        layout.prop(self,"orientation")
        layout.label("Proportional Edit")
        layout.prop(self,'propo_edit')
        layout.label("Proportional Edit Falloff")
        layout.prop(self,'propo_edit_fall')
        layout.label("Proportional size")
        layout.prop(self,'propo_size')
        layout.prop(self,'release')
        layout.prop(self, 'texture')
    
    def normal(self,con_x,con_y,con_z,orien,con,fall,propsize,texture, release):
        bpy.ops.mesh.extrude_region_move(MESH_OT_extrude_region={"mirror":False}, TRANSFORM_OT_translate={"value":self.location, "constraint_axis":(con_x, con_y, con_z), "constraint_orientation":orien, "mirror":False, "proportional":con, "proportional_edit_falloff":fall, "proportional_size":propsize, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "texture_space":texture, "release_confirm":release})
        
        
    def execute(self, context):      
        
        if self.con_x == True:
            con_x = True
        else:
            con_x = False
            
        if self.con_y == True:
            con_y = True
        else:
            con_y = False
        
        if self.con_z == True:
            con_z = True
        else:
            con_z = False
        
        if self.orientation == 'one':
            orien = 'GLOBAL'    
        if self.orientation == 'two':
            orien = 'LOCAL' 
        if self.orientation == 'three':
            orien = 'NORMAL' 
        if self.orientation == 'four':
            orien = 'GIMBAL' 
        if self.orientation == 'five':
            orien = 'VIEW' 
            
        if self.propo_edit == 'one':
            con = 'DISABLED'
        elif self.propo_edit == 'two':             
            con = 'ENABLED'            
        elif self.propo_edit == 'three':
            con = 'PROJECTED'            
        elif self.propo_edit == 'four':
            con = 'CONNECTED'
            
        if self.propo_edit_fall == 'one':
            fall = 'SMOOTH'
        elif self.propo_edit_fall == 'two':             
            fall = 'SPHERE'            
        elif self.propo_edit_fall == 'three':
            fall = 'ROOT'            
        elif self.propo_edit_fall == 'four':
            fall = 'SHARP'    
        elif self.propo_edit_fall == 'five':
            fall = 'LINEAR'
        elif self.propo_edit_fall == 'six':
            fall = 'CONSTANT' 
        elif self.propo_edit_fall == 'seven':
            fall = 'RANDOM'
            
        if self.texture == True:            
            texture = True
        else:           
            texture = False
            
        if self.release == True:
            release = True
        else:
            release = False
        propsize = self.propo_size
        
        self.normal(con_x,con_y,con_z,orien,con,fall,propsize,texture,release)

        return {'FINISHED'}
        
    def modal(self, context, event):
        global ti, delta1, deltay1,x,y,z
        if context.active_object.mode == 'EDIT':
            mesh = context.object.data
            scene = bpy.context.scene  
            totface = mesh.total_face_sel
            delta = event.mouse_x - self.first_mouse_x - delta1
            deltay = event.mouse_y - self.first_mouse_y - deltay1
            delta1 = delta1 + delta
            deltay1 = deltay1 + deltay
            bm=bmesh.from_edit_mesh(mesh)
            if ti == 0:
                bpy.ops.mesh.extrude_region_move()
                ti = 1            
            if event.type == 'MOUSEMOVE':                
                if totface >= 1: 
                    for v in bm.faces:
                        if v.select:
                            if v.normal.x == 1.0 or v.normal.x == -1.0:
                                bpy.ops.transform.translate(value=(delta * 0.02, 0, 0))
                                x += delta * 0.02
                            elif v.normal.y == 1.0 or v.normal.y == -1.0:
                                bpy.ops.transform.translate(value=(0, delta * 0.02, 0))
                                y += delta * 0.02
                            elif v.normal.z == 1.0 or v.normal.z == -1.0:
                                bpy.ops.transform.translate(value=(0, 0, delta * 0.02))
                                z += delta * 0.02                                
                            else:
                                bpy.ops.transform.translate(value=(delta * v.normal.x/50, delta * v.normal.y/50, delta * v.normal.z/50),constraint_axis=(True, False, False),constraint_orientation='GLOBAL',mirror=False,proportional='DISABLED', proportional_edit_falloff='SMOOTH',proportional_size=1,snap=False,snap_target='CLOSEST',snap_point=(0, 0, 0),snap_align=False,snap_normal=(0, 0, 0),release_confirm = False,)    
                                x += delta * v.normal.x/50
                                y += delta * v.normal.y/50
                                z += delta * v.normal.z/50
                else:
                    bpy.ops.transform.translate(value=(delta * 0.02, deltay * 0.02, 0))
                    x += delta * 0.02
                    y += deltay * 0.02                
                bm.normal_update()
                self.location = (x, y, z)
          #  elif event.type == 'LEFTMOUSE':
                ti = 0
                delta1=0
                deltay1=0
                x = 0
                y = 0
                z = 0
                return {'FINISHED'}

            elif event.type in {'RIGHTMOUSE', 'ESC'}:
                if totface >= 1:                
                    for v in bm.faces:
                        if v.select:                            
                            bpy.ops.transform.translate(value=(-x/totface,-y/totface,-z/totface)) 
                else:                    
                    bpy.ops.transform.translate(value=(-x,-y, 0))
                ti = 0
                delta1=0
                deltay1=0
                x = 0
                y = 0
                z = 0  
                return {'CANCELLED'}
        else:
            return {'CANCELLED'}
        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        if context.object:
            self.first_mouse_x = event.mouse_x
            self.first_mouse_y = event.mouse_y
            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "No active object, could not finish")
            return {'CANCELLED'}
        return {'FINISHED'}


############## Extrude Vertices ############### 
class Extrude_indiv_vertices(bpy.types.Operator):
    bl_idname = "extrude_indiv_verts.selected"
    bl_label = "Vertices only"
    bl_options = {'REGISTER', 'UNDO'}
    
    location = FloatVectorProperty(name = "Vector", subtype = 'TRANSLATION',default = (0.0,0.0,0.0,),min = -100.0, max = 100.0,soft_min = -10,soft_max = 10,step = 0.1 ,size =3)
    
    orientation = EnumProperty(items = (('one', 'Global','GLOBAL',1),('two','Local','LOCAL',2),('three', 'Normal', 'NORMAL',  3),('four', 'Gimbal','GIMBAL', 4),('five', 'View', 'VIEW', 5)),default = 'one',name = "")  
    
    propo_edit = EnumProperty(items = (('one','Disable','DISABLED','PROP_OFF', 1),('two','Enable','ENABLED','PROP_ON',2),('three', 'Projected (2D)','PROJECTED', 'PROP_ON',3),('four', 'Connected', 'CONNECTED','PROP_CON',4)),default = 'one',name = "")  
    
    propo_edit_fall = EnumProperty(items = (('one', 'Smooth','SMOOTH','SMOOTHCURVE', 1),('two','Sphere','SPHERE','SPHERECURVE', 2),('three', 'Root','ROOT','ROOTCURVE', 3),('four', 'Sharp','SHARP','SHARPCURVE', 4),('five','Linear','LINEAR', 'LINCURVE', 5),('six','Constant','CONSTANT', 'NOCURVE',6),('seven', 'Random', 'RANDOM','RNDCURVE', 7)),default = 'one',name = "")
    
    propo_size = FloatProperty(name = "", description = "", default = 1, min = 0.001, max = 100.000)
    
    con_x = BoolProperty(name="x", description="", default=False)
    con_y = BoolProperty(name="y", description="", default=False)
    con_z = BoolProperty(name="z", description="", default=False)
    
    release = BoolProperty(name="release on confirm", description="release on confirm", default=False)
    
    texture = BoolProperty(name="Edit Texture", description="", default=False)
    
    def draw(self, context):
        layout = self.layout
       
        layout.label("Extrude Only Vertices")
        row = layout.column(align = True)
        row.prop(self,'location')
        layout.label("Constraint Axis")
        layout.prop(self,'con_x')
        layout.prop(self,'con_y')
        layout.prop(self,'con_z')
        layout.label("Orientation")
        layout.prop(self,"orientation")
        layout.label("Proportional Edit")
        layout.prop(self,'propo_edit')
        layout.label("Proportional Edit Falloff")
        layout.prop(self,'propo_edit_fall')
        layout.label("Proportional size")
        layout.prop(self,'propo_size')
        layout.prop(self,'release')
        layout.prop(self, 'texture')
    
    def normal(self,context,con_x,con_y,con_z,orien,con,fall,propsize,texture, release):
       
            bpy.ops.mesh.extrude_vertices_move(MESH_OT_extrude_verts_indiv={"mirror":False}, TRANSFORM_OT_translate={"value":self.location, "constraint_axis":(con_x, con_y, con_z), "constraint_orientation":orien, "mirror":False, "proportional":con, "proportional_edit_falloff":fall, "proportional_size":propsize, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "texture_space":texture, "release_confirm":release})

    def execute(self, context):      
        
        
        if self.con_x == True:
            con_x = True
        else:
            con_x = False
            
        if self.con_y == True:
            con_y = True
        else:
            con_y = False
        
        if self.con_z == True:
            con_z = True
        else:
            con_z = False
        
        if self.orientation == 'one':
            orien = 'GLOBAL'    
        if self.orientation == 'two':
            orien = 'LOCAL' 
        if self.orientation == 'three':
            orien = 'NORMAL' 
        if self.orientation == 'four':
            orien = 'GIMBAL' 
        if self.orientation == 'five':
            orien = 'VIEW' 
            
        if self.propo_edit == 'one':
            con = 'DISABLED'
        elif self.propo_edit == 'two':             
            con = 'ENABLED'            
        elif self.propo_edit == 'three':
            con = 'PROJECTED'            
        elif self.propo_edit == 'four':
            con = 'CONNECTED'
            
        if self.propo_edit_fall == 'one':
            fall = 'SMOOTH'
        elif self.propo_edit_fall == 'two':             
            fall = 'SPHERE'            
        elif self.propo_edit_fall == 'three':
            fall = 'ROOT'            
        elif self.propo_edit_fall == 'four':
            fall = 'SHARP'    
        elif self.propo_edit_fall == 'five':
            fall = 'LINEAR'
        elif self.propo_edit_fall == 'six':
            fall = 'CONSTANT' 
        elif self.propo_edit_fall == 'seven':
            fall = 'RANDOM'
            
        if self.texture == True:            
            texture = True
        else:           
            texture = False
            
        if self.release == True:
            release = True
        else:
            release = False
        propsize = self.propo_size
        
        self.normal(context,con_x,con_y,con_z,orien,con,fall,propsize,texture,release)

        return {'FINISHED'}
       
        
    def modal(self, context, event):
        global ti, delta1, deltay1, et, x, y,z
        delta = 0
        mesh = context.object.data
        selected_mode = context.tool_settings.mesh_select_mode
        totedge = mesh.total_edge_sel

        if context.active_object.mode == 'EDIT':
            if ti == 0:                
                bpy.ops.mesh.extrude_vertices_move()
                ti = 1
            bm=bmesh.from_edit_mesh(mesh) 
               
            if event.type == 'MOUSEMOVE':
          
                delta = event.mouse_x - self.first_mouse_x - delta1
                deltay = event.mouse_y - self.first_mouse_y - deltay1
                delta1 = delta1 + delta
                deltay1 = deltay1 + deltay
                bpy.ops.transform.translate(value=(delta * 0.02, deltay * 0.02, delta * 0.02))
                bm.normal_update()
                x = x + delta * 0.02
                y = y + deltay * 0.02
                z = z + delta * 0.02
                self.location = (x, y, z)
           # elif event.type == 'LEFTMOUSE':                 
                ti = 0
                delta1=0
                deltay1=0
                x = 0
                y = 0
                z = 0
                return {'FINISHED'}
            elif event.type in {'RIGHTMOUSE', 'ESC'}:
              
                bpy.ops.transform.translate(value=(-x, -y, -z))
                ti = 0
                delta1=0
                deltay1=0
                x = 0
                y = 0
                z = 0
                return {'CANCELLED'}
        else:
            return {'CANCELLED'}
        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        if context.object:
            self.first_mouse_x = event.mouse_x
            self.first_mouse_y = event.mouse_y
            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "No active object, could not finish")
            return {'CANCELLED'}
        return {'FINISHED'} 

############## Extrude Edges ############### 
class Extrude_indiv_edges(bpy.types.Operator):
    bl_idname = "extrude_indiv_edges.selected"
    bl_label = "Edges only"
    bl_options = {'REGISTER', 'UNDO'}
    
    location = FloatVectorProperty(name = "Vector", subtype = 'TRANSLATION',default = (0.0,0.0,0.0,),min = -100.0, max = 100.0,soft_min = -10,soft_max = 10,step = 0.1 ,size =3)
    
    orientation = EnumProperty(items = (('one', 'Global','GLOBAL',1),('two','Local','LOCAL',2),('three', 'Normal', 'NORMAL',  3),('four', 'Gimbal','GIMBAL', 4),('five', 'View', 'VIEW', 5)),default = 'one',name = "")  
    
    propo_edit = EnumProperty(items = (('one','Disable','DISABLED','PROP_OFF', 1),('two','Enable','ENABLED','PROP_ON',2),('three', 'Projected (2D)','PROJECTED', 'PROP_ON',3),('four', 'Connected', 'CONNECTED','PROP_CON',4)),default = 'one',name = "")  
    
    propo_edit_fall = EnumProperty(items = (('one', 'Smooth','SMOOTH','SMOOTHCURVE', 1),('two','Sphere','SPHERE','SPHERECURVE', 2),('three', 'Root','ROOT','ROOTCURVE', 3),('four', 'Sharp','SHARP','SHARPCURVE', 4),('five','Linear','LINEAR', 'LINCURVE', 5),('six','Constant','CONSTANT', 'NOCURVE',6),('seven', 'Random', 'RANDOM','RNDCURVE', 7)),default = 'one',name = "")
    
    propo_size = FloatProperty(name = "", description = "", default = 1, min = 0.001, max = 100.000)
    
    con_x = BoolProperty(name="x", description="", default=False)
    con_y = BoolProperty(name="y", description="", default=False)
    con_z = BoolProperty(name="z", description="", default=False)
    
    release = BoolProperty(name="release on confirm", description="release on confirm", default=False)
    
    texture = BoolProperty(name="Edit Texture", description="", default=False)
    
    def draw(self, context):
        layout = self.layout
  
        layout.label("Extrude Only Edges")
        row = layout.column(align = True)
        row.prop(self,'location')
        layout.label("Constraint Axis")
        layout.prop(self,'con_x')
        layout.prop(self,'con_y')
        layout.prop(self,'con_z')
        layout.label("Orientation")
        layout.prop(self,"orientation")
        layout.label("Proportional Edit")
        layout.prop(self,'propo_edit')
        layout.label("Proportional Edit Falloff")
        layout.prop(self,'propo_edit_fall')
        layout.label("Proportional size")
        layout.prop(self,'propo_size')
        layout.prop(self,'release')
        layout.prop(self, 'texture')
    
    def normal(self,context,con_x,con_y,con_z,orien,con,fall,propsize,texture, release):
         
            bpy.ops.mesh.extrude_edges_move(MESH_OT_extrude_edges_indiv={"mirror":False}, TRANSFORM_OT_translate={"value":self.location, "constraint_axis":(con_x, con_y, con_z), "constraint_orientation":orien, "mirror":False, "proportional":con, "proportional_edit_falloff":fall, "proportional_size":propsize, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "texture_space":texture, "release_confirm":release})
        

    def execute(self, context):      
        
        if self.con_x == True:
            con_x = True
        else:
            con_x = False
            
        if self.con_y == True:
            con_y = True
        else:
            con_y = False
        
        if self.con_z == True:
            con_z = True
        else:
            con_z = False
        
        if self.orientation == 'one':
            orien = 'GLOBAL'    
        if self.orientation == 'two':
            orien = 'LOCAL' 
        if self.orientation == 'three':
            orien = 'NORMAL' 
        if self.orientation == 'four':
            orien = 'GIMBAL' 
        if self.orientation == 'five':
            orien = 'VIEW' 
            
        if self.propo_edit == 'one':
            con = 'DISABLED'
        elif self.propo_edit == 'two':             
            con = 'ENABLED'            
        elif self.propo_edit == 'three':
            con = 'PROJECTED'            
        elif self.propo_edit == 'four':
            con = 'CONNECTED'
            
        if self.propo_edit_fall == 'one':
            fall = 'SMOOTH'
        elif self.propo_edit_fall == 'two':             
            fall = 'SPHERE'            
        elif self.propo_edit_fall == 'three':
            fall = 'ROOT'            
        elif self.propo_edit_fall == 'four':
            fall = 'SHARP'    
        elif self.propo_edit_fall == 'five':
            fall = 'LINEAR'
        elif self.propo_edit_fall == 'six':
            fall = 'CONSTANT' 
        elif self.propo_edit_fall == 'seven':
            fall = 'RANDOM'
            
        if self.texture == True:            
            texture = True
        else:           
            texture = False
            
        if self.release == True:
            release = True
        else:
            release = False
        propsize = self.propo_size
        
        self.normal(context,con_x,con_y,con_z,orien,con,fall,propsize,texture,release)

        return {'FINISHED'}
       
        
    def modal(self, context, event):
        global ti, delta1, deltay1, et, x, y,z
        delta = 0
        mesh = context.object.data
        selected_mode = context.tool_settings.mesh_select_mode
        totedge = mesh.total_edge_sel

        if context.active_object.mode == 'EDIT':
            if ti == 0:
                bpy.ops.mesh.extrude_edges_move()             
                ti = 1
            bm=bmesh.from_edit_mesh(mesh) 
               
            if event.type == 'MOUSEMOVE':
          
                delta = event.mouse_x - self.first_mouse_x - delta1
                deltay = event.mouse_y - self.first_mouse_y - deltay1
                delta1 = delta1 + delta
                deltay1 = deltay1 + deltay
                bpy.ops.transform.translate(value=(delta * 0.02, deltay * 0.02, delta * 0.02))
                bm.normal_update()
                x = x + delta * 0.02
                y = y + deltay * 0.02
                z = z + delta * 0.02
                self.location = (x, y, z)
         #   elif event.type == 'LEFTMOUSE':                 
                ti = 0
                delta1=0
                deltay1=0
                x = 0
                y = 0
                z = 0
                return {'FINISHED'}
            elif event.type in {'RIGHTMOUSE', 'ESC'}:
              
                bpy.ops.transform.translate(value=(-x, -y, -z))
                ti = 0
                delta1=0
                deltay1=0
                x = 0
                y = 0
                z = 0
                return {'CANCELLED'}
        else:
            return {'CANCELLED'}
        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        if context.object:
            self.first_mouse_x = event.mouse_x
            self.first_mouse_y = event.mouse_y
            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "No active object, could not finish")
            return {'CANCELLED'}
        return {'FINISHED'}

  
############## Extrude Faces ###############  
class Extrude_individual_faces(bpy.types.Operator):
    bl_idname = "extrudeindividual_face.selected"
    bl_label = "Individual Faces "
    bl_options = {'REGISTER', 'UNDO'}
    
    offset = FloatProperty(name = "", description = "", default = 0.0, min = -10.0, max = 10.0,precision = 2,subtype = 'FACTOR')
    propo_edit = EnumProperty(items = (('one', 'DISABLED', 'Disable','PROP_OFF', 1),('two', 'ENABLED','Enable','PROP_ON',2),('three', 'PROJECTED', 'Projected (2D)','PROP_ON',3),('four', 'CONNECTED', 'Connected','PROP_CON',4)),default = 'one', name = "")  
    propo_edit_fall = EnumProperty(items = (('one', 'SMOOTH', 'Smooth','SMOOTHCURVE', 1),('two', 'SPHERE','Sphere','SPHERECURVE', 2),('three', 'ROOT', 'Root','ROOTCURVE', 3),('four', 'SHARP', 'Sharp','SHARPCURVE', 4),('five', 'LINEAR', 'Linear','LINCURVE', 5),('six', 'CONSTANT', 'Constant','NOCURVE',6),('seven', 'RANDOM', 'Random','RNDCURVE', 7)),default = 'one',name = "")
    
    propo_size = FloatProperty(name = "", description = "", default = 1, min = 0.001, max = 100.000)
    release = BoolProperty(name="release on confirm", description="release on confirm", default=False)
    
    def draw(self,context):
        
        layout = self.layout
        layout.label("Shirnk/Fatten")
        layout.label("Offset")
        layout.prop(self, 'offset', slider = True)  
        layout.label("Proportional Edit") 
        layout.prop(self,'propo_edit')     
        layout.label("Proportional Edit Falloff")
        layout.prop(self,'propo_edit_fall')  
        layout.label("Proportional size")
        layout.prop(self,'propo_size')
        layout.prop(self, 'release')
        
    def extrude (self,con,fall,release):
        
        bpy.ops.mesh.extrude_faces_move(MESH_OT_extrude_faces_indiv={"mirror":False}, TRANSFORM_OT_shrink_fatten={"value":self.offset, "mirror":False, "proportional":con, "proportional_edit_falloff":fall, "proportional_size":1, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "release_confirm":release})       
        
    def execute(self, context):        
        
        if self.propo_edit == 'one':
            con = 'DISABLED'
        elif self.propo_edit == 'two':             
            con = 'ENABLED'            
        elif self.propo_edit == 'three':
            con = 'PROJECTED'            
        elif self.propo_edit == 'four':
            con = 'CONNECTED'
       
        if self.propo_edit_fall == 'one':
            fall = 'SMOOTH'
        elif self.propo_edit_fall == 'two':             
            fall = 'SPHERE'            
        elif self.propo_edit_fall == 'three':
            fall = 'ROOT'            
        elif self.propo_edit_fall == 'four':
            fall = 'SHARP'    
        elif self.propo_edit_fall == 'five':
            fall = 'LINEAR'
        elif self.propo_edit_fall == 'six':
            fall = 'CONSTANT' 
        elif self.propo_edit_fall == 'seven':
            fall = 'RANDOM'
        
        if self.release == True:
            release = True
        else:
            release = False
        self.extrude(con,fall,release)
        
        return {'FINISHED'}
        
    def modal(self, context, event):
        global ti, delta1, deltay1, et, x
        delta = 0
        mesh = context.object.data
        selected_mode = context.tool_settings.mesh_select_mode
        totface = mesh.total_face_sel
        totedge = mesh.total_edge_sel
        self.offset += 0.01
        #self.value = bpy.context.scene.offset
        if context.active_object.mode == 'EDIT':
            if ti == 0:
                if selected_mode[2] and totface>=1:                    
                    bpy.ops.mesh.extrude_faces_move()
                ti = 1
            bm=bmesh.from_edit_mesh(mesh) 
               
            if event.type == 'MOUSEMOVE':
                if totface >= 1:
                    for v in bm.faces:
                        v.normal_update()                                               
                        if v.select:
                            et = "face"
                            delta = self.first_mouse_x - event.mouse_x - delta1
                            deltay = self.first_mouse_y - event.mouse_y - deltay1
                            delta1 = delta1 + delta
                            deltay1 = deltay1 + deltay                                                     
                            bpy.ops.transform.shrink_fatten(value= delta* 0.02, mirror=False, proportional = 'DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1.0, snap=False, snap_target='CLOSEST', snap_point=(0.0, 0.0, 0.0), snap_align=False, snap_normal=(0.0, 0.0, 0.0), release_confirm=False)                                                      
                            
                            x = x + delta * 0.02                           
                    self.offset = x
                
            
         #   elif event.type == 'LEFTMOUSE':                 
                ti = 0
                x = 0
                return {'FINISHED'}
            elif event.type in {'RIGHTMOUSE', 'ESC'}:
                if totface >= 1:                
                    for v in bm.faces:
                        if v.select:
                            bpy.ops.transform.shrink_fatten(value=-x/totface)    
                
                ti = 0
                delta1=0
                deltay1=0
                x = 0                
                return {'CANCELLED'}
        else:
            return {'CANCELLED'}
        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        if context.object:
            self.first_mouse_x = event.mouse_x
            self.first_mouse_y = event.mouse_y
            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "No active object, could not finish")
            return {'CANCELLED'}
        return {'FINISHED'}


############## Extrude Individual Menu ###############         
class INFO_MT_edit_mesh_extrude_indiv(Menu):    
    bl_label = "  Extrude Individual"
    def draw(self, context):
        layout = self.layout
        select_mode = context.tool_settings.mesh_select_mode
        if select_mode[2]:
            layout.operator("extrudeindividual_face.selected")   
        elif select_mode[1]:
            layout.operator("extrude_indiv_edges.selected")
        else:
            layout.operator("extrude_indiv_verts.selected")

############## Duplicate ###############    
class Duplicate(bpy.types.Operator):
    bl_idname = "duplicate.selected"
    bl_label = "Duplicate"
    bl_options = {'REGISTER', 'UNDO'}
    
    location = FloatVectorProperty(name = "Vector", subtype = 'TRANSLATION',default = (0.0,0.0,0.0,),min = -100.0, max = 100.0,soft_min = -10,soft_max = 10,step = 0.1 ,size =3)
    
    orientation = EnumProperty(items = (('one', 'Global','GLOBAL',1),('two','Local','LOCAL',2),('three', 'Normal', 'NORMAL',  3),('four', 'Gimbal','GIMBAL', 4),('five', 'View', 'VIEW', 5)),default = 'one',name = "")  
    
    propo_edit = EnumProperty(items = (('one','Disable','DISABLED','PROP_OFF', 1),('two','Enable','ENABLED','PROP_ON',2),('three', 'Projected (2D)','PROJECTED', 'PROP_ON',3),('four', 'Connected', 'CONNECTED','PROP_CON',4)),default = 'one',name = "")  
    
    propo_edit_fall = EnumProperty(items = (('one', 'Smooth','SMOOTH','SMOOTHCURVE', 1),('two','Sphere','SPHERE','SPHERECURVE', 2),('three', 'Root','ROOT','ROOTCURVE', 3),('four', 'Sharp','SHARP','SHARPCURVE', 4),('five','Linear','LINEAR', 'LINCURVE', 5),('six','Constant','CONSTANT', 'NOCURVE',6),('seven', 'Random', 'RANDOM','RNDCURVE', 7)),default = 'one',name = "")
    
    propo_size = FloatProperty(name = "", description = "", default = 1, min = 0.001, max = 100.000)
    
    con_x = BoolProperty(name="x", description="", default=False)
    con_y = BoolProperty(name="y", description="", default=False)
    con_z = BoolProperty(name="z", description="", default=False)
    
    release = BoolProperty(name="release on confirm", description="release on confirm", default=False)
    
    texture = BoolProperty(name="Edit Texture", description="", default=False)
    
    mode = IntProperty(name = "",min = 0,max = 1000, default = 1)
    
    link = BoolProperty(name="Linked", description="", default=False)      
    
    def draw(self, context):
        layout = self.layout
        
        if context.active_object.mode == 'EDIT': 
            layout.label("Mode")
            layout.prop(self,'mode')
        else:
            layout.prop(self,'link')
            
        row = layout.column(align = True)
        row.prop(self,'location')
        layout.label("Constraint Axis")
        layout.prop(self,'con_x')
        layout.prop(self,'con_y')
        layout.prop(self,'con_z')
        layout.label("Orientation")
        layout.prop(self,"orientation")
        layout.label("Proportional Edit")
        layout.prop(self,'propo_edit')
        layout.label("Proportional Edit Falloff")
        layout.prop(self,'propo_edit_fall')
        layout.label("Proportional size")
        layout.prop(self,'propo_size')
        layout.prop(self,'release')
        layout.prop(self, 'texture')
    
    def normal(self,context,link,con_x,con_y,con_z,orien,con,fall,propsize,texture, release):
        if context.active_object.mode == 'EDIT':        
            bpy.ops.mesh.duplicate_move(MESH_OT_duplicate={"mode":self.mode}, TRANSFORM_OT_translate={"value":self.location, "constraint_axis":(con_x, con_y, con_z), "constraint_orientation":orien, "mirror":False, "proportional":con, "proportional_edit_falloff":fall, "proportional_size":propsize, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "texture_space":texture, "release_confirm":release})
        
        else:
            bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked":link, "mode":'TRANSLATION'}, TRANSFORM_OT_translate={"value":self.location, "constraint_axis":(con_x, con_y, con_z), "constraint_orientation":orien, "mirror":False, "proportional":con, "proportional_edit_falloff":fall, "proportional_size":propsize, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "texture_space":texture, "release_confirm":release})


    def execute(self, context):      
       
       
        if self.link == True:
            link = True
        else:
            link = False
            
        if self.con_x == True:
            con_x = True
        else:
            con_x = False
            
        if self.con_y == True:
            con_y = True
        else:
            con_y = False
        
        if self.con_z == True:
            con_z = True
        else:
            con_z = False
        
        if self.orientation == 'one':
            orien = 'GLOBAL'    
        if self.orientation == 'two':
            orien = 'LOCAL' 
        if self.orientation == 'three':
            orien = 'NORMAL' 
        if self.orientation == 'four':
            orien = 'GIMBAL' 
        if self.orientation == 'five':
            orien = 'VIEW' 
            
        if self.propo_edit == 'one':
            con = 'DISABLED'
        elif self.propo_edit == 'two':             
            con = 'ENABLED'            
        elif self.propo_edit == 'three':
            con = 'PROJECTED'            
        elif self.propo_edit == 'four':
            con = 'CONNECTED'
            
        if self.propo_edit_fall == 'one':
            fall = 'SMOOTH'
        elif self.propo_edit_fall == 'two':             
            fall = 'SPHERE'            
        elif self.propo_edit_fall == 'three':
            fall = 'ROOT'            
        elif self.propo_edit_fall == 'four':
            fall = 'SHARP'    
        elif self.propo_edit_fall == 'five':
            fall = 'LINEAR'
        elif self.propo_edit_fall == 'six':
            fall = 'CONSTANT' 
        elif self.propo_edit_fall == 'seven':
            fall = 'RANDOM'
            
        if self.texture == True:            
            texture = True
        else:           
            texture = False
            
        if self.release == True:
            release = True
        else:
            release = False
        propsize = self.propo_size   
        self.normal(context,link,con_x,con_y,con_z,orien,con,fall,propsize,texture,release)

        return {'FINISHED'}
    def modal(self, context, event):
        global ti, delta1, deltay1,x, y,z
        mesh = context.object.data
        object = context.object
        delta = event.mouse_x - self.first_mouse_x - delta1
        deltay = event.mouse_y - self.first_mouse_y - deltay1
        delta1 = delta1 + delta
        deltay1 = deltay1 + deltay
        if ti == 0:
            if context.active_object.mode == 'EDIT':
                bpy.ops.mesh.duplicate_move()
            else:
                bpy.ops.object.duplicate_move()
            ti = 1            
        if event.type == 'MOUSEMOVE':
            bpy.ops.transform.translate(value=(delta * 0.02, deltay * 0.02, 0))
            x += delta * 0.02
            y += deltay * 0.02
            self.location = (x,y,z)
     #   elif event.type == 'LEFTMOUSE':
            x = 0
            y = 0
            ti = 0
            delta1=0
            deltay1=0
            return {'FINISHED'}
        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            bpy.ops.transform.translate(value=(-x,-y, 0))
            ti = 0
            delta1=0
            deltay1=0
            x = 0
            y = 0
            return {'CANCELLED'}
        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        if context.object:
            self.first_mouse_x = event.mouse_x
            self.first_mouse_y = event.mouse_y
            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "No active object, could not finish")
            return {'CANCELLED'}
        return {'FINISHED'}
    

 

