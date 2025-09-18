import bmesh
import bpy
from mathutils import Matrix, Vector

bl_info = {
    "name": "Origin to Selected Faces (Align to XY)",
    "author": "Iñigo Moreno i Caireta",
    "version": (1, 3),
    "blender": (3, 0, 0),
    "location": "Object > Set Origin",
    "description": "Set origin to median of selected faces and align them to XY plane",
    "category": "Object",
}


def set_origin_faces(obj, sel_faces):
    bm = bmesh.from_edit_mesh(obj.data)
    all_verts = set()
    for f in sel_faces:
        all_verts.update(f.verts)
    median = sum((v.co for v in all_verts), Vector()) / len(all_verts)

    # ------------------------------------------------------------
    # Compute average normal of selected faces
    # ------------------------------------------------------------
    normal = sum((f.normal for f in sel_faces), Vector()).normalized()
    if normal.length < 1e-6:
        raise RuntimeError("Face normal is zero length; cannot orient.")

    # ------------------------------------------------------------
    # Build rotation matrix to align normal to Z axis
    # ------------------------------------------------------------
    z_axis = Vector((0, 0, 1))
    rot_axis = normal.cross(z_axis)

    if rot_axis.length < 1e-6:
        # Normal is already aligned or opposite
        if normal.dot(z_axis) > 0:
            rot_mat = Matrix.Identity(3)
        else:
            rot_mat = Matrix.Rotation(3.14159265, 3, Vector((1, 0, 0)))
    else:
        rot_axis.normalize()
        angle = normal.angle(z_axis)
        rot_mat = Matrix.Rotation(angle, 3, rot_axis)

    # ------------------------------------------------------------
    # Move vertices so that median is at origin
    # Then apply rotation to flatten on XY plane
    # ------------------------------------------------------------
    for v in bm.verts:
        # Move relative to median
        v.co -= median
        # Apply rotation
        v.co = rot_mat @ v.co

    # Update mesh
    bmesh.update_edit_mesh(obj.data)

    vertex_transform = Matrix.Translation(median) @ Matrix.Translation(Vector((0, 0, 0)))  # 
    vertex_transform = Matrix.Translation(median) @ rot_mat.inverted().to_4x4()

    # Multiply object world matrix by vertex transform to keep object in place
    obj.matrix_world = obj.matrix_world @ vertex_transform


class OBJECT_OT_origin_to_faces_xy(bpy.types.Operator):
    """Set origin to median of selected faces and align them to XY plane"""
    bl_idname = "object.origin_to_faces_xy"
    bl_label = "Origin to Selected Faces (Align to XY)"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.active_object
        if not obj or obj.type != 'MESH':
            self.report({'ERROR'}, "Active object must be a mesh")
            return {'CANCELLED'}

        # Switch to Edit Mode to access bmesh
        bpy.ops.object.mode_set(mode='EDIT')
        bm = bmesh.from_edit_mesh(obj.data)
        sel_faces = [f for f in bm.faces if f.select]

        if not sel_faces:
            self.report({'ERROR'}, "No faces selected in Edit Mode")
            return {'CANCELLED'}

        # Run the main operation
        try:
            set_origin_faces(obj, sel_faces)
        except Exception as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}

        bpy.ops.object.mode_set(mode='OBJECT')
        return {'FINISHED'}


def menu_func(self, context):
    self.layout.operator(
        OBJECT_OT_origin_to_faces_xy.bl_idname,
        icon='NONE'
    )


def register():
    bpy.utils.register_class(OBJECT_OT_origin_to_faces_xy)
    bpy.types.VIEW3D_MT_object.append(menu_func)


def unregister():
    bpy.types.VIEW3D_MT_object.remove(menu_func)
    bpy.utils.unregister_class(OBJECT_OT_origin_to_faces_xy)


if __name__ == "__main__":
    register()
