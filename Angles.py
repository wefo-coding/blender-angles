# # # # # # # # # # # # # # # # # #
#             Angles              #
#        by Florian Otten         #
# # # # # # # # # # # # # # # # # #

bl_info = { "name": "Angles",
            "description": "With this addon you can create angles and align meshes.",
            "author": "Florian Otten",
            "version": (0, 2),
            "blender": (2, 79, 0),
            "location": "View3D > Tools > Angles",
            "support": "COMMUNITY",
            "wiki_url": "http://code.we-fo.de/blender/angles/",
            "tracker_url": "http://webentwicklung-otten.de/Home/Contact/",
            "category": "Mesh" }


# # # # # # # # # # # # # # # # # #
#             Imports             #
# # # # # # # # # # # # # # # # # #

import bpy
import bmesh
import math
from mathutils import *
from math import *


# # # # # # # # # # # # # # # # # #
#            Functions            #
# # # # # # # # # # # # # # # # # #

def dotproduct(v1, v2):
    """
    Hilfsfunktion zum Berechne des Winkels zwischen zwei Vektoren.
    """
    return sum((a*b) for a, b in zip(v1, v2))

def length(v):
    """
    Hilfsfunktion zum Berechne des Winkels zwischen zwei Vektoren.
    """
    return math.sqrt(dotproduct(v, v))

def angle(v1, v2):
    """
    Berechnet den Winkel zwischen zwei Vektoren.
    """
    return math.acos(dotproduct(v1, v2) / (length(v1) * length(v2)))

def setOrientation(inverse = False):
    """
    Erzeugt anhand drei ausgewählter Punkte ein lokales Koordinatensystem.
    Die Z-Achse wird an den zuletzt gewählten Punkten ausgerichtet oder
    an den ersten beiden, wenn inverse auf True gesetzt wird.
    """
    
    # Speichere das aktuelle Objekt. #
    obj = bpy.context.object
    
    # Prüfe ob ein aktives Objekt vorhanden ist und dies vom Typ Mesh ist. #
    if obj == None or obj.type != 'MESH':
        return False
    
    # Speichere den aktuellen Modus um ihn nach der Operation wieder herzustellen. #
    mode = obj.mode
    
    # Wechsle in den Edit mode. #
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_mode(type='VERT')
    bm = bmesh.from_edit_mesh(bpy.context.object.data)
    
    # Prüfe ob 3 Punkte zum Ausrichten der Orientation ausgewählt wurden. #
    if len(bm.select_history) != 3:
        bpy.ops.object.mode_set(mode=mode)
        return False
    
    # Speichere die Koordinaten der 3 Punkte. #
    if inverse:
        coA = bm.select_history[2].co
        coM = bm.select_history[1].co
        coE = bm.select_history[0].co
    else:
        coA = bm.select_history[0].co
        coM = bm.select_history[1].co
        coE = bm.select_history[2].co
    
    # Lokale in Globale Koordinaten umwandeln. #
    mat = obj.matrix_world
    coA = mat * coA
    coM = mat * coM
    coE = mat * coE
    
    # Berechne die Koordinaten eines Punktes der auf der Y-Achse liegen soll. #
    coY = (coA - coM).cross(coE - coM) + coM
    
    # Berechne die Koordinaten eines Punktes der auf der X-Achse liegen soll. #
    coX = (coY - coM).cross(coE - coM) + coM
    
    # Berechne Vektoren des neuen lokalen Koordinatensystems. #
    vX = coX - coM
    vY = coY - coM
    vZ = coE - coM
    
    vX.normalize()
    vY.normalize()
    vZ.normalize()
    
    # Erzeuge Matrix des neuen lokalen Koordinatensystems. #
    mAlign = Matrix([[vX[0],vY[0],vZ[0]],[vX[1],vY[1],vZ[1]],[vX[2],vY[2],vZ[2]]])
    
    # Erzeuge neue Orientation mit der berechneten Matrix. #
    bpy.ops.transform.create_orientation(name='Aligned', overwrite=True)
    bpy.context.scene.orientations['Aligned'].matrix = mAlign
    
    # Wechsle in den ursprünglichen Modus zurück. #
    bpy.ops.object.mode_set(mode=mode)
    
    # Erfolgsmeldung. #
    return True

def alignObject(toAlign, inverse = False):
    """
    Richtet ein Objekt an den 3 zuletzt gewählten Punkten aus.
    Der vorletzte und letze Punkt bilden die Z-Achse.
    """
    
    # Speichere das aktive Objekt. #
    obj = bpy.context.object
    
    # Es muss ein Objekt aktiv sein und das auszurichtende Objekt vorhanden sein. #
    if toAlign is None or type(toAlign) is not bpy.types.Object:
        return False
    
    # Setze Orientierung. #
    if not setOrientation(inverse):
        return False
    
    # Speichere den aktuellen Modus um ihn nach der Operation wieder herzustellen. #
    mode = obj.mode
    
    # Wechsle in den Edit mode. #
    bpy.ops.object.mode_set(mode='EDIT')
    bm = bmesh.from_edit_mesh(obj.data)
    
    # Speichere die Koordinaten des Mittelpunktes. #
    coM = Vector(bm.select_history[1].co)
    
    # Wechsle in den Object mode. #
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Deselektiere alle Objekte. #
    bpy.ops.object.select_all(action='DESELECT')
    
    # Objekt ausrichten. #
    toAlign.location = coM
    toAlign.parent = obj
    toAlign.select = True
    bpy.ops.transform.transform(mode='ALIGN', constraint_orientation='Aligned')
    bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
    toAlign.select = False
    
    # Selectiere aktives Objekt. #
    obj.select = True
    
    # Wechsle in den zuvor gesicherten Modus. #
    bpy.ops.object.mode_set(mode=mode)
    
    return True
    

def addAlignedObject(profile, selectNewObj = True, inverse = False):
    """
    Fügt ein Objekt ein und richtet es an den 3 zuletzt gewählten Punkten aus.
    Der vorletzte und letze Punkt bilden die Z-Achse.
    """
    
    # Profil muss vom Typ Mesh sein. #
    if type(profile) is not bpy.types.Mesh:
        return None
    
    # Erstelle das Objekt hinzu. #
    newObj = bpy.data.objects.new(profile.name, profile)
    bpy.context.scene.objects.link(newObj)
    
    # Richte Object aus. #
    if not alignObject(newObj, inverse):
        bpy.data.objects.remove(newObj)
        return None
    
    # Wechsle in den ObjectMode und wähle das neue Objekt als aktives Objekt aus, wenn gewuenscht.#
    if selectNewObj:
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.scene.objects.active = newObj
        newObj.select = True
    
    # Gebe das neue Objekt zurück. #
    return newObj

def extrudeAngle(angle, inverse = False):
    """
    Hilfsfunktion für addAngle.
    """
    
    # Speichere aktives Objekt. #
    obj = bpy.context.object
    
    # Wechsle in den Edit mode. #
    bpy.ops.object.mode_set(mode='EDIT')
    
    # Extrude alles um eine Einheit. #
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.extrude_region_move(
        TRANSFORM_OT_translate={
            "value":(0,0,1), 
            "constraint_axis":(False, False, True), 
            "constraint_orientation":'NORMAL'
        }
    )
    bm = bmesh.from_edit_mesh(obj.data)
    bm.verts.ensure_lookup_table()
    
    # Die Neuen Punkte auf die Schnittpunkte mit dem Anderen Objekt setzen. #
    minZ = 0
    for x in range(0, int(len(bm.verts)/2)):
        if inverse:
            bm.verts[x+int(len(bm.verts)/2)].co.z = -1* bm.verts[x].co.x / math.tan(angle)
            minZ = min(-1* bm.verts[x+int(len(bm.verts)/2)].co.z, minZ)
        else:
            bm.verts[x+int(len(bm.verts)/2)].co.z = bm.verts[x].co.x / math.tan(angle)
            minZ = min(bm.verts[x+int(len(bm.verts)/2)].co.z, minZ)
    
    # Die alten Punkte auf Höhe des niedrigsten Punktes setzen. #
    for x in range(0, int(len(bm.verts)/2)):
        if inverse:
            bm.verts[x].co.z = -minZ
        else:
            bm.verts[x].co.z = minZ
    
    # Wechsle in den Object mode. #
    bpy.ops.object.mode_set(mode='OBJECT')

def addAngle(profile):
    """
    Fügt einen Winkel mit gegebenen Profil an einem Knickpunkt ein.
    Dazu werden die 3 zuletzt ausgewählten Punkte verwendet.
    """
    
    # Profil muss vom Typ Mesh sein. #
    if type(profile) is not bpy.types.Mesh:
        return None
    
    # Erstelle Kopie vom Profil um das urspruengliche Mesh nicht zu veraendern. #
    profile = profile.copy()
    
    # Füge ersten Teil hinzu. #
    partA = addAlignedObject(profile, False, False)
    if partA is None:
        return None
    
    # Berechne Vector der Z-Achse. #
    matrixA = partA.matrix_world
    directionA = Vector([matrixA[0][2], matrixA[1][2], matrixA[2][2]])
    
    # Füge zweiten Teil hinzu. #
    partB = addAlignedObject(profile, True, True)
    if partB is None:
        return None
    
    # Berechne Vector der Z-Achse. #
    matrixB = partB.matrix_world
    directionB = Vector([matrixB[0][2], matrixB[1][2], matrixB[2][2]])
    
    # Drehe Objekt um 180 Grad um die x-Achse. #
    bpy.ops.transform.rotate(
        value = math.pi,
        constraint_axis = (True, False, False),
        constraint_orientation='LOCAL'
    )
    
    # Wechsle in den Edit mode. #
    bpy.ops.object.mode_set(mode='EDIT')
    
    # Setze alle Z-Werte der Vertices auf 0, um eine Ebene zu haben. #
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.transform.resize(
        value=(1, 1, 0), 
        constraint_axis=(False, False, True), 
        constraint_orientation='Aligned')
    
    # Lösche doppelte Vertices. #
    bpy.ops.mesh.remove_doubles()
    
    # Berechne Winkel zwischen Objekten. #
    angleAB = angle(directionA, directionB)
    
    # Wechsle in den Object mode. #
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Mache Mesh zum SingelUser. #
    bpy.ops.object.make_single_user(obdata=True)
    
    # Extrudiere die beiden Teile. #
    extrudeAngle(angleAB/2)
    bpy.context.scene.objects.active = partA
    extrudeAngle(angleAB/2, True)
    
    # Verschmelze die beiden Teile. #
    bpy.ops.object.select_all(action='DESELECT')
    partA.select = True
    partB.select = True
    bpy.ops.object.join()
    
    # Wechsle in den Edit mode. #
    bpy.ops.object.mode_set(mode='EDIT')
    
    # Entferne doppelte Punkte und innere Fläche. #
    bpy.ops.mesh.remove_doubles()
    bpy.ops.mesh.delete(type='FACE')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.remove_doubles()
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.mesh.select_all(action='DESELECT')
    
    # Wechsle in den Object mode. #
    bpy.ops.object.mode_set(mode='OBJECT')
    
    return partA


# # # # # # # # # # # # # # # # # #
#           Properties            #
# # # # # # # # # # # # # # # # # #

class AngelesProps(bpy.types.PropertyGroup):
    
    #Profile
    profile = bpy.props.PointerProperty(
        type = bpy.types.Mesh,
        name = "Profile", 
        description = "..."
        )
    
    #ToAlign
    to_align = bpy.props.PointerProperty(
        type = bpy.types.Object,
        name = "To Align", 
        description = "..."
        )


# # # # # # # # # # # # # # # # # #
#            Operators            #
# # # # # # # # # # # # # # # # # #

class SetOrientationOperator(bpy.types.Operator):
    
    bl_idname = "angles.set_orientation"
    bl_label = "Set Orientation"
    bl_options = {'REGISTER', 'UNDO'}
    
    # Properties
    inverse = bpy.props.BoolProperty(
        name = "Inverse",
        default = False,
        description = "..."
    )
    
    # Execute
    def execute(self, context):
        if setOrientation(self.inverse):
            return {'FINISHED'}
        self.report({'ERROR'}, "Please select exactly 3 vertices.")
        return {'CANCELLED'}

class AlignObjectOperator(bpy.types.Operator):
    
    bl_idname = "angles.align_object"
    bl_label = "Align Object"
    bl_options = {'REGISTER', 'UNDO'}
    
    # Properties
    inverse = bpy.props.BoolProperty(
        name = "Inverse",
        default = False,
        description = "..."
    )
    
    # Execute
    def execute(self, context):
        if alignObject(context.scene.angles.to_align, self.inverse):
            return {'FINISHED'}
        self.report({'ERROR'}, "Please select exactly 3 vertices and the object, you want to align.")
        return {'CANCELLED'}

class AddAngleOperator(bpy.types.Operator):
    
    bl_idname = "angles.add_angle"
    bl_label = "Add Angle"
    bl_options = {'REGISTER', 'UNDO'}
    
    # Execute
    def execute(self, context):
        if addAngle(context.scene.angles.profile) is not None:
            return {'FINISHED'}
        self.report({'ERROR'}, "Please select exactly 3 vertices and the mesh, you want to use as profile.")
        return {'CANCELLED'}
    

# # # # # # # # # # # # # # # # # #
#             Panels              #
# # # # # # # # # # # # # # # # # #

class OrientationPanel(bpy.types.Panel):
    
    bl_idname = "MESH_PT_orientation"
    bl_label = "Orientation"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Angles"
    
    # Draw Panel
    def draw(self, context):
        layout = self.layout
        layout.operator(SetOrientationOperator.bl_idname)

class AlignPanel(bpy.types.Panel):
    
    bl_idname = "MESH_PT_align"
    bl_label = "Align"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Angles"
    
    # Draw Panel
    def draw(self, context):
        layout = self.layout
        layout.prop(context.scene.angles, "to_align")
        layout.operator(AlignObjectOperator.bl_idname)

class AnglesPanel(bpy.types.Panel):
    
    bl_idname = "MESH_PT_angles"
    bl_label = "Angles"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Angles"
    
    # Draw Panel
    def draw(self, context):
        layout = self.layout
        layout.prop(context.scene.angles, "profile")
        layout.operator(AddAngleOperator.bl_idname)

 
# # # # # # # # # # # # # # # # # #
#          Registration           #
# # # # # # # # # # # # # # # # # #

def register():
    
    # Properties
    bpy.utils.register_class(AngelesProps)
    
    # Operators
    bpy.utils.register_class(SetOrientationOperator)
    bpy.utils.register_class(AlignObjectOperator)
    bpy.utils.register_class(AddAngleOperator)
    
    # Panels
    bpy.utils.register_class(OrientationPanel)
    bpy.utils.register_class(AlignPanel)
    bpy.utils.register_class(AnglesPanel)
    
    # Set Properties
    bpy.types.Scene.angles = bpy.props.PointerProperty(type=AngelesProps)
    
def unregister():
    
    # Delete Properties
    del bpy.types.Scene.angles
    
    # Panels
    bpy.utils.unregister_class(AnglesPanel)
    bpy.utils.unregister_class(AlignPanel)
    bpy.utils.unregister_class(OrientationPanel)
    
    # Operators
    bpy.utils.unregister_class(SetOrientationOperator)
    bpy.utils.unregister_class(AlignObjectOperator)
    bpy.utils.unregister_class(AddAngleOperator)
    
    # Properties
    bpy.utils.unregister_class(AngelesProps)