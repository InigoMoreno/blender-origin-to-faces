import bpy
import bmesh
from mathutils import Vector, Matrix

bl_info = {
    "name": "Origin to Selected Faces (Align to XY)",
    "author": "Iñigo Moreno i Caireta",
    "version": (1, 1),
    "blender": (3, 0, 0),
    "location": "Object > Set Origin",
    "description": "Set origin to median of selected faces and align them to XY plane",
    "category": "Object",
}


def set_origin_faces(obj, faces):
    """Compute median, align faces to XY, set origin without moving geometry."""
    verts = {v for f in faces for v in f.verts}
    median_local = sum((v.co for v in verts), Vector()) / len(verts)
    avg_normal_local = sum((f.normal for f in faces), Vector()).normalized()

    world_median = obj.matrix_world @ median_local
    world_normal = (obj.matrix_world.to_3x3() @ avg_normal_local).normalized()

    z_axis = Vector((0, 0, 1))
    if world_normal.length < 1e-6:
        raise RuntimeError("Normal is zero length; cannot orient.")

    rot_axis = world_normal.cross(z_axis)
    if rot_axis.length < 1e-6:
        if world_normal.dot(z_axis) > 0:
            rot_mat = Matrix.Identity(3)
        else:
            rot_mat = Matrix.Rotation(3.14159265, 3, Vector((1, 0, 0)))
    else:
        rot_axis.normalize()
        angle = world_normal.angle(z_axis)
        rot_mat = Matrix.Rotation(angle, 3, rot_axis)

    # Apply transformation without moving geometry
    bpy.ops.object.mode_set(mode='OBJECT')
    orig_world = obj.matrix_world.copy()

    new_world_matrix = rot_mat.to_4x4()
    new_world_matrix.translation = world_median
    mesh_adjust = (new_world_matrix.inverted() @ orig_world)
    obj.data.transform(mesh_adjust)
    obj.matrix_world = new_world_matrix


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
        icon='ORIGIN_CURSOR'
    )


def register():
    bpy.utils.register_class(OBJECT_OT_origin_to_faces_xy)
    bpy.types.VIEW3D_MT_object_origin_set.append(menu_func)


def unregister():
    bpy.types.VIEW3D_MT_object_origin_set.remove(menu_func)
    bpy.utils.unregister_class(OBJECT_OT_origin_to_faces_xy)


if __name__ == "__main__":
    register()
