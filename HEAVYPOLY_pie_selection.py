bl_info = {
    "name": "Pie Selection",
    "description": "Select Modes",
    "author": "Vaughan Ling",
    "version": (0, 2, 0),
    "blender": (5, 2, 0),
    "location": "",
    "warning": "",
    "wiki_url": "",
    "category": "Pie Menu"
    }

import bpy
from bpy.types import Menu

# Select Pie
class HP_MT_pie_select(Menu):
    bl_label = "Select"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        mode = context.mode

        # left
        if bpy.context.mode == 'OBJECT':
            split = pie.split()
            col = split.column()
            col.scale_y=1.5
            col.operator("object.select_grouped", text="Similar")
            col.operator("view3d.selectsmartsimilar", text="Similar Name")
        else:
            split = pie.split()
            col = split.column()
            col.scale_y=1.5
            col.operator("mesh.select_similar", text="Similar")
            col.operator("mesh.hp_select_border", text="Border")

        # Right
        match bpy.context.mode:
            case "EDIT_MESH":
                pie.operator("mesh.faces_select_linked_flat", text="Select Flat").sharpness=0.2
            case "SCULPT":
                pie.operator("object.voxel_remesh", text="Remesh", icon='NONE')
            case _:
                split = pie.split()
                col = split.column()
                col.scale_y=1.5
                col.operator("object.select_grouped", text="Select Collection", icon='NONE').type='COLLECTION'
                col.operator("object.hp_select_hierarchy", text="Select Hierarchy")
                


        # bottom
        if mode == 'OBJECT':
            #pie.operator("wm.hp_open_extra_pie", text="Extra", icon='MESH_CUBE')
            pie.operator("object.mode_set", text="Object", icon='MESH_CUBE').mode = 'OBJECT'
        else:
            pie.operator("object.mode_set", text="Object", icon='MESH_CUBE').mode = 'OBJECT'
        # top

        match bpy.context.object.type:
            case "GPENCIL":
                pie.operator('object.mode_set', text = 'GP Edit', icon='EDITMODE_HLT').mode='EDIT_GPENCIL'
            case "GREASEPENCIL":
                pie.operator('object.mode_set', text = 'GP Edit', icon='EDITMODE_HLT').mode='EDIT'
            case "META":
                pie.operator('object.mode_set', text = 'Edit', icon='META_DATA').mode='EDIT'
            case "ARMATURE":
                pie.operator('object.mode_set', text = 'Edit', icon='NONE').mode='EDIT'
            case "LATTICE":
                pie.operator('object.mode_set', text = 'Edit', icon='NONE').mode='EDIT'
            case _:
                pie.operator("object.selectmodesmart", text="Edge", icon='NONE').selectmode='EDGE'

        # topleft
        match bpy.context.object.type:
            case "GPENCIL":
                pie.operator('object.mode_set', text = 'GP Draw', icon='GREASEPENCIL').mode='PAINT_GPENCIL'
            case "GREASEPENCIL":
                pie.operator('object.mode_set', text = 'GP Draw', icon='GREASEPENCIL').mode='PAINT_GREASE_PENCIL'
            case "ARMATURE":
                pie.operator('object.mode_set', text = 'Pose', icon='NONE').mode='POSE'
            case "META":
                split = pie.split()
                col = split.column()
                col.scale_x=1.1
                col.label(text="")
            case "LATTICE":
                split = pie.split()
            case _:
                pie.operator("object.selectmodesmart", text="Vert", icon='NONE').selectmode='VERT'

        # topright
        match bpy.context.object.type:
            case "GPENCIL":
                pie.operator('object.mode_set', text = "GP Sculpt", icon="SCULPTMODE_HLT").mode="SCULPT_GPENCIL"
            case "GREASEPENCIL":
                pie.operator('object.mode_set', text = "GP Sculpt", icon="SCULPTMODE_HLT").mode="SCULPT_GREASE_PENCIL"
            case "META":
                split = pie.split()
                col = split.column()
                col.scale_x=1.1
                col.label(text="")
            case "LATTICE":
                split = pie.split()
            case _:
                pie.operator("object.selectmodesmart", text="Face", icon='NONE').selectmode='FACE'

        # bottomleft
        split = pie.split()
        col = split.column()
        col.scale_y=1.5
        col.separator()
        col.separator()
        col.separator()
        col.separator()
        col.separator()
        col.operator('object.separate_and_select', text = 'Split To New Object')

        col.operator('object.join', text = 'Join Objects')
        prop = col.operator('object.parent_set', text = 'Set Parent')
        prop.type = 'OBJECT'
        prop.keep_transform=True
        col.operator('object.parent_clear', text = 'Remove Parent').type='CLEAR_KEEP_TRANSFORM'

        #bottomright
        split = pie.split()
        col = split.column()
        col.scale_y=1.5
        # One separator fewer than upstream: the extra "Draw with GP" row made
        # this column overlap the Select Collection / Select Hierarchy column.
        col.separator()
        col.separator()
        col.separator()
        col.separator()
        col.separator()
        col.separator()


        match (bpy.context.object.type if bpy.context.object else "NONE"):
            case "MESH":
                col.operator('object.mode_set', text = 'Sculpt', icon='SCULPTMODE_HLT').mode='SCULPT'
                col.operator('object.mode_set', text = 'Vertex Paint', icon='VPAINT_HLT').mode='VERTEX_PAINT'
                col.operator('object.mode_set', text = 'Weight Paint', icon='WPAINT_HLT').mode='WEIGHT_PAINT'
                col.operator('object.mode_set', text = 'Texture Paint', icon='BRUSH_DATA').mode='TEXTURE_PAINT'
                col.operator('object.sculpt_mode_with_dynotopo', text = 'Sculpt With Dynotopo', icon='SCULPTMODE_HLT')
            case "GPENCIL":
                col.operator('object.mode_set', text = 'Vertex Paint', icon='VPAINT_HLT').mode='VERTEX_GPENCIL'
                col.operator('object.mode_set', text = 'Weight Paint', icon='WPAINT_HLT').mode='WEIGHT_GPENCIL'
            case "GREASEPENCIL":
                col.operator('object.mode_set', text = 'Vertex Paint', icon='VPAINT_HLT').mode='VERTEX_GREASE_PENCIL'
                col.operator('object.mode_set', text = 'Weight Paint', icon='WPAINT_HLT').mode='WEIGHT_GREASE_PENCIL'
            case "LATTICE":
                col.operator('object.mode_set', text = 'Weight Paint', icon='WPAINT_HLT').mode='WEIGHT_PAINT'
            case "ARMATURE":
                pass
            case "META":
                pass

            # Particles Will be removed in later versions, keeping it on the bottom for organisation
            case bpy.context.object.particle_systems:
                col.operator('object.mode_set', text = 'Particle Edit', icon='PARTICLEMODE').mode='PARTICLE_EDIT'

            # New datatypes can easily be added above pass
            case _:
                pass

        # Always available: spawn a fresh Grease Pencil and start drawing.
        col.separator()
        col.operator('object.hp_draw_with_gp', text='Draw with GP', icon='GREASEPENCIL')


####### Draw with GP

GP_MATERIALS = ("Pencil", "Halftone", "Fill")
GP_SURFACE_OFFSET = 0.015


def _ensure_gp_material(name):
    """Return a Grease Pencil material of that name, creating it if needed."""
    mat = bpy.data.materials.get(name)
    if mat is not None and getattr(mat, "is_grease_pencil", False):
        return mat
    if mat is not None:
        # A non-GP material is squatting on the name - make a GP one alongside it.
        mat = None

    mat = bpy.data.materials.new(name=name)
    try:
        bpy.data.materials.create_gpencil_data(mat)
    except Exception as e:
        print("[HEAVYPOLY] could not create GP material data: %r" % (e,))
        return mat

    gp = mat.grease_pencil
    # White base so that vertex colour shows through unmodified.
    try:
        gp.color = (1.0, 1.0, 1.0, 1.0)
        gp.fill_color = (1.0, 1.0, 1.0, 1.0)
    except Exception:
        pass

    if name == "Fill":
        gp.show_stroke = False
        gp.show_fill = True
    else:
        gp.show_stroke = True
        gp.show_fill = False
    return mat


def _enable_vertex_colour_painting(context):
    """Make the active GP draw brush paint with vertex colour."""
    try:
        brush = context.tool_settings.gpencil_paint.brush
        settings = brush.gpencil_settings
        settings.vertex_color_factor = 1.0
        settings.vertex_mode = 'BOTH'
    except Exception as e:
        print("[HEAVYPOLY] could not switch the GP brush to vertex colour: %r" % (e,))


def _set_stroke_placement(context, on_surface):
    ts = context.scene.tool_settings
    try:
        if on_surface:
            ts.gpencil_stroke_placement_view3d = 'SURFACE'
            if hasattr(ts, "gpencil_surface_offset"):
                ts.gpencil_surface_offset = GP_SURFACE_OFFSET
        else:
            ts.gpencil_stroke_placement_view3d = 'ORIGIN'
    except Exception as e:
        print("[HEAVYPOLY] could not set stroke placement: %r" % (e,))
    # Draw on the view plane in both cases.
    try:
        ts.gpencil_sculpt.lock_axis = 'VIEW'
    except Exception as e:
        print("[HEAVYPOLY] could not set the drawing plane: %r" % (e,))


class HP_OT_draw_with_gp(bpy.types.Operator):
    """Add a new Grease Pencil object and jump straight into draw mode"""
    bl_idname = "object.hp_draw_with_gp"
    bl_label = "Draw with GP"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        target = context.active_object
        # A GP object as the target would parent a sketch to a sketch - ignore it.
        if target is not None and target.type in {'GPENCIL', 'GREASEPENCIL'}:
            target = None

        if context.object and context.object.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

        location = target.matrix_world.translation.copy() if target else context.scene.cursor.location.copy()

        try:
            bpy.ops.object.grease_pencil_add(type='EMPTY', align='WORLD', location=location)
        except AttributeError:
            bpy.ops.object.gpencil_add(type='EMPTY', align='WORLD', location=location)

        gp = context.active_object
        if gp is None:
            self.report({'ERROR'}, "Could not create a Grease Pencil object.")
            return {'CANCELLED'}

        if target is not None:
            gp.name = "GP_" + target.name
            # Match the target's collection.
            try:
                for coll in list(gp.users_collection):
                    coll.objects.unlink(gp)
                for coll in target.users_collection:
                    coll.objects.link(gp)
            except Exception as e:
                print("[HEAVYPOLY] could not move the GP to the target collection: %r" % (e,))
            # Parent without moving it.
            gp.parent = target
            gp.matrix_parent_inverse = target.matrix_world.inverted()

        # Respect scene depth: strokes on the far side of a mesh stay hidden.
        try:
            gp.data.stroke_depth_order = '3D'
        except Exception as e:
            print("[HEAVYPOLY] could not set stroke depth order: %r" % (e,))
        gp.show_in_front = False

        for name in GP_MATERIALS:
            mat = _ensure_gp_material(name)
            if mat is not None:
                gp.data.materials.append(mat)
        if gp.data.materials:
            gp.active_material_index = 0

        _set_stroke_placement(context, on_surface=target is not None)

        for mode in ('PAINT_GREASE_PENCIL', 'PAINT_GPENCIL'):
            try:
                bpy.ops.object.mode_set(mode=mode)
                break
            except (TypeError, RuntimeError):
                continue
        else:
            self.report({'WARNING'}, "Created the GP object but could not enter draw mode.")

        _enable_vertex_colour_painting(context)
        return {'FINISHED'}


class HP_OT_gp_select_linked_pick(bpy.types.Operator):
    """Select the whole stroke under the mouse"""
    bl_idname = "grease_pencil.hp_select_linked_pick"
    bl_label = "Select Linked Pick"
    bl_options = {'REGISTER', 'UNDO'}

    extend: bpy.props.BoolProperty(name="Extend", default=False)

    def invoke(self, context, event):
        # Grease Pencil has no *_pick variant of select_linked, so do it in two
        # steps: grab the point under the cursor, then grow to its whole stroke.
        try:
            bpy.ops.view3d.select('INVOKE_DEFAULT',
                                  extend=self.extend,
                                  deselect=False,
                                  toggle=False)
        except Exception as e:
            print("[HEAVYPOLY] could not pick a point: %r" % (e,))
            return {'CANCELLED'}

        for module_name in ("grease_pencil", "gpencil"):
            module = getattr(bpy.ops, module_name, None)
            if module is None or not hasattr(module, "select_linked"):
                continue
            try:
                module.select_linked()
                return {'FINISHED'}
            except RuntimeError as e:
                print("[HEAVYPOLY] %s.select_linked failed: %r" % (module_name, e))

        self.report({'WARNING'}, "No Grease Pencil select_linked operator found.")
        return {'FINISHED'}


class HP_OT_gp_canvas(bpy.types.Operator):
    bl_idname = "view3d.gp_canvas"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}
    type: bpy.props.StringProperty(name="Front")
    def execute(self, context):
        # This used to assign to a local variable, so the axis never changed.
        axis = {
            'Front': 'AXIS_Y',
            'Top': 'AXIS_Z',
            'Side': 'AXIS_X',
            'View': 'VIEW',
            'Cursor': 'CURSOR',
        }.get(self.type)

        if axis is None:
            self.report({'WARNING'}, "Unknown canvas axis: %s" % self.type)
            return {'CANCELLED'}

        context.tool_settings.gpencil_sculpt.lock_axis = axis
        return {'FINISHED'}

class HP_OT_sculpt_mode_with_dynotopo(bpy.types.Operator):
    bl_idname = "object.sculpt_mode_with_dynotopo"      # unique identifier for buttons and menu items to reference.
    bl_label = ""      # display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}  # enable undo for the operator.
    def invoke(self, context, event):
        bpy.ops.object.mode_set(mode='SCULPT')
        if not bpy.context.sculpt_object.use_dynamic_topology_sculpting:
            bpy.ops.sculpt.dynamic_topology_toggle()
        return {'FINISHED'}


class HP_OT_SelectModeSmart(bpy.types.Operator):
    """SelectModeSmart"""      # blender will use this as a tooltip for menu items and buttons.
    bl_idname = "object.selectmodesmart"        # unique identifier for buttons and menu items to reference.
    bl_label = "Select Mode Smart"         # display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}  # enable undo for the operator.
    selectmode : bpy.props.StringProperty(name="SelectMode")
    def invoke(self, context, event):
        def select(selectmode):
            bpy.ops.mesh.select_mode(type=selectmode)

        match bpy.context.mode:
            case "OBJECT":
                match bpy.context.object.type:
                    case "MESH":
                        bpy.ops.object.mode_set(mode='EDIT')
                        select(self.selectmode)
                    case "GPENCIL":
                        bpy.ops.object.mode_set(mode='GPENCIL_PAINT')
                    case "GPENCIL":
                        bpy.ops.object.mode_set(mode='PAINT_GREASE_PENCIL')
                    case "CURVE" | "FONT":
                        bpy.ops.object.mode_set(mode='EDIT')
            case "EDIT_MESH":
                select(self.selectmode)
            case "GPENCIL_PAINT":
                bpy.context.mode = "OBJECT"
            case "PAINT_GREASE_PENCIL":
                bpy.context.mode = "OBJECT"
            case _:
                bpy.ops.object.mode_set(mode="EDIT")
        return {'FINISHED'}

class HP_OT_SelectSmartSimilar(bpy.types.Operator):
    """SelectSmartVert"""      # blender will use this as a tooltip for menu items and buttons.
    bl_idname = "view3d.selectsmartsimilar"        # unique identifier for buttons and menu items to reference.
    bl_label = "Select Smart Similar"         # display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}  # enable undo for the operator.

    def invoke(self, context, event):
        if bpy.context.mode=='OBJECT':
            name = bpy.context.active_object.name
            name = str(name.split('.')[0]) + "*"
            bpy.ops.object.select_pattern(pattern=name)

        else:
            bpy.ops.mesh.select_similar()
        return {'FINISHED'}


class HP_OT_SelectSmartLinkedAndLoop(bpy.types.Operator):
    """SelectSmartVert"""      # blender will use this as a tooltip for menu items and buttons.
    bl_idname = "mesh.selectsmartlinkedandloop"        # unique identifier for buttons and menu items to reference.
    bl_label = "Select Smart Linked And Loop"         # display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}  # enable undo for the operator.

    def invoke(self, context, event):
        if tuple(bpy.context.scene.tool_settings.mesh_select_mode) == (False, True, False):
            bpy.ops.mesh.loop_multi_select()
        else:
            bpy.ops.mesh.select_linked(delimit={'SEAM'})
        return {'FINISHED'}
class HP_OT_select_border(bpy.types.Operator):
    """Select Border"""    # blender will use this as a tooltip for menu items and buttons.
    bl_idname = "mesh.hp_select_border"        # unique identifier for buttons and menu items to reference.
    bl_label = "Select Border"        # display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}  # enable undo for the operator.

    def invoke(self, context, event):
        bpy.ops.mesh.select_mode(type='EDGE')
        bpy.ops.mesh.region_to_loop()
        return {'FINISHED'}
    
class HP_OT_select_hierarchy(bpy.types.Operator):
    """Select Hierarchy"""    # blender will use this as a tooltip for menu items and buttons.
    bl_idname = "object.hp_select_hierarchy"        # unique identifier for buttons and menu items to reference.
    bl_label = "Select Hierarchy"        # display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}  # enable undo for the operator.

    def invoke(self, context, event):
        selection = bpy.context.active_object
        if selection:  # Ensure there is an active object.
            bpy.ops.object.select_grouped(type='CHILDREN_RECURSIVE')
            selection.select_set(True)  # Call the method, passing `True` to select the object.
        return {'FINISHED'}
    
class HP_OT_extra_pie(bpy.types.Operator):
    """Open Second Pie Menu"""
    bl_idname = "wm.hp_open_extra_pie"
    bl_label = "Open Extra Pie"

    def execute(self, context):
        bpy.ops.wm.call_menu_pie(name="HP_MT_pie_extra")
        return {'FINISHED'}


classes = (
    HP_MT_pie_select,
    HP_OT_SelectModeSmart,
    HP_OT_SelectSmartLinkedAndLoop,
    HP_OT_SelectSmartSimilar,
    HP_OT_sculpt_mode_with_dynotopo,
    HP_OT_gp_canvas,
    HP_OT_draw_with_gp,
    HP_OT_gp_select_linked_pick,
    HP_OT_select_border,
    HP_OT_select_hierarchy,
    HP_OT_extra_pie,
)
register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()
