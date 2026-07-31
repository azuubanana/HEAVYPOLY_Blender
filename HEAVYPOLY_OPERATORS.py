bl_info = {
    "name": "Heavypoly Operators",
    "description": "Operators that make for smooth blending",
    "author": "Vaughan Ling",
    "version": (0, 1, 0),
    "blender": (5, 2, 0),
    "location": "",
    "warning": "",
    "wiki_url": "",
    "category": "Operators"
    }

import bpy
from mathutils import Vector, Matrix
import math
import os
import bmesh
from bpy.types import Menu
from bpy.types import Operator
from bpy.props import BoolProperty
from mathutils import Color

class HP_OT_unhide(bpy.types.Operator):
    bl_idname = "mesh.hp_unhide"         # unique identifier for buttons and menu items to reference.
    bl_label = "Unhide and keep selection"       # display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}  # enable undo for the operator.

    def execute(self, context):
        ## 1 Save selection
        bpy.ops.object.vertex_group_add()
        bpy.ops.object.vertex_group_assign()
        ## 2 Unhide
        bpy.ops.mesh.reveal()
        ## 3 Deselect all
        bpy.ops.mesh.select_all(action='DESELECT')
        ## 4 Recall selection
        bpy.ops.object.vertex_group_select()
        bpy.ops.object.vertex_group_remove(all=False, all_unlocked=False)
        return {'FINISHED'}

class HP_OT_loopcut(bpy.types.Operator):
    bl_idname = "mesh.hp_loopcut"         # unique identifier for buttons and menu items to reference.
    bl_label = "Loopcut with tablet modals"       # display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}  # enable undo for the operator.


    def modal(self, context, event):
        if event.type == 'MOUSEMOVE' and event.value == 'PRESS':
            print('Mousemove...')
            bpy.ops.mesh.loopcut_slide('INVOKE_DEFAULT')
            return {'RUNNING_MODAL'}
        if event.type in {'RIGHTMOUSE', 'ESC'}:  # Cancel
            return {'CANCELLED'}
        elif event.type == 'MOUSEMOVE' and event.value == 'RELEASE':
            bpy.context.scene.tool_settings.mesh_select_mode = (False, True, False)
            print('Release...')
            return {'CANCELLED'}
        return {'RUNNING_MODAL'}
    def invoke(self, context, event):

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

class HP_OT_smart_snap_cursor(bpy.types.Operator):
    bl_idname = "view3d.smart_snap_cursor"        # unique identifier for buttons and menu items to reference.
    bl_label = ""         # display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}  # enable undo for the operator.
    def invoke(self, context, event):
        try:
            if context.active_object.mode == 'EDIT':
                if context.active_object.type == 'MESH':
                    if  context.object.data.total_vert_sel == 0:
                        bpy.ops.view3d.snap_cursor_to_center()
                    else:
                        bpy.ops.view3d.snap_cursor_to_selected()
                else:
                    bpy.ops.view3d.snap_cursor_to_selected()
            elif len(bpy.context.selected_objects) > 0:
                bpy.ops.view3d.snap_cursor_to_selected()
            else:
                bpy.ops.view3d.snap_cursor_to_center()
        except:
            bpy.ops.view3d.snap_cursor_to_center()
            #bpy.context.scene.tool_settings.transform_pivot_point = 'CURSOR'
        return {'FINISHED'}

class HP_OT_smart_snap_origin_collection(bpy.types.Operator):
    bl_idname = "view3d.smart_snap_origin_collection"        # unique identifier for buttons and menu items to reference.
    bl_label = "Smart Snap Origin Collection"         # display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}  # enable undo for the operator.
    def invoke(self, context, event):
        print('smartsnaporigincollection')
        try:
            if context.active_object.mode == 'EDIT':
                if context.active_object.type == 'MESH':
                    if  context.object.data.total_vert_sel == 0:
                        bpy.ops.view3d.snap_cursor_to_center()
                        bpy.ops.object.mode_set(mode='OBJECT')
                        bpy.ops.object.origin_set(type = 'ORIGIN_CURSOR')
                        bpy.ops.object.mode_set(mode='EDIT')
                    else:
                        bpy.ops.view3d.snap_cursor_to_selected()
                        bpy.ops.object.mode_set(mode='OBJECT')
                        bpy.ops.object.instance_offset_from_cursor()
                        bpy.ops.object.mode_set(mode='EDIT')
                else:
                    bpy.ops.view3d.snap_cursor_to_selected()
                    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
                    bpy.ops.object.origin_set(type = 'ORIGIN_CURSOR')
                    #bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
                    bpy.ops.object.mode_set(mode='EDIT', toggle=False)
            elif len(bpy.context.selected_objects) > 0:
                bpy.ops.view3d.snap_cursor_to_selected()
                bpy.ops.object.instance_offset_from_cursor()
            else:
                #bpy.ops.view3d.snap_cursor_to_center()
                #bpy.ops.object.origin_set(type = 'ORIGIN_CURSOR')
                bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
            #bpy.context.scene.tool_settings.transform_pivot_point = 'MEDIAN_POINT'
        except:
            return {'FINISHED'}
        return {'FINISHED'}
class HP_OT_smart_snap_origin(bpy.types.Operator):
    bl_idname = "view3d.smart_snap_origin"        # unique identifier for buttons and menu items to reference.
    bl_label = ""         # display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}  # enable undo for the operator.
    def invoke(self, context, event):
        print('smartsnaporigin')
        cursor_start_location = bpy.context.scene.cursor.location * 1
        # print(cursor_start_location)
        try:
            if context.active_object.mode == 'EDIT':
                if context.active_object.type == 'MESH':
                    if  context.object.data.total_vert_sel == 0:
                        bpy.ops.view3d.snap_cursor_to_center()
                        bpy.ops.object.mode_set(mode='OBJECT')
                        bpy.ops.object.origin_set(type = 'ORIGIN_CURSOR')
                        bpy.ops.object.mode_set(mode='EDIT')
                    else:
                        bpy.ops.view3d.snap_cursor_to_selected()
                        bpy.ops.object.mode_set(mode='OBJECT')
                        bpy.ops.object.origin_set(type = 'ORIGIN_CURSOR')
                        bpy.ops.object.mode_set(mode='EDIT')
                else:
                    bpy.ops.view3d.snap_cursor_to_selected()
                    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
                    bpy.ops.object.origin_set(type = 'ORIGIN_CURSOR')
                    #bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
                    bpy.ops.object.mode_set(mode='EDIT', toggle=False)
            elif len(bpy.context.selected_objects) > 0:
                bpy.ops.object.origin_set(type = 'ORIGIN_GEOMETRY')
            else:
                #bpy.ops.view3d.snap_cursor_to_center()
                #bpy.ops.object.origin_set(type = 'ORIGIN_CURSOR')
                bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
            #bpy.context.scene.tool_settings.transform_pivot_point = 'MEDIAN_POINT'
            print(cursor_start_location)
            bpy.context.scene.cursor.location = (cursor_start_location[0],cursor_start_location[1],cursor_start_location[2])
        except:
            return {'FINISHED'}
        return {'FINISHED'}

class HP_OT_duplicate_move(bpy.types.Operator):
    bl_idname = "view3d.hp_duplicate_move"
    bl_label = ""
    bl_options = {'REGISTER'}
    def invoke(self, context, event):
        if context.active_object.mode == 'OBJECT':
            bpy.ops.object.duplicate('INVOKE_DEFAULT', False)
            bpy.ops.transform.translate('INVOKE_DEFAULT', False)

        if context.active_object.mode == 'EDIT':
            bpy.ops.mesh.duplicate('INVOKE_DEFAULT', False)
            bpy.ops.transform.translate('INVOKE_DEFAULT', False)

        return {'FINISHED'}



class HP_OT_PushAndSlide(bpy.types.Operator):
    bl_idname = "mesh.push_and_slide"        # unique identifier for buttons and menu items to reference.
    bl_label = "Push And Slide"         # display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}  # enable undo for the operator.

    def invoke(self, context, event):
        if tuple(bpy.context.scene.tool_settings.mesh_select_mode) == (True, False, False):
            bpy.ops.transform.vert_slide('INVOKE_DEFAULT', mirror=False, correct_uv=True)
        elif tuple(bpy.context.scene.tool_settings.mesh_select_mode) == (False, False, True):
            bpy.ops.transform.shrink_fatten('INVOKE_DEFAULT', use_even_offset=True, mirror=False)
        else:
            bpy.ops.transform.edge_slide('INVOKE_DEFAULT', mirror=False, correct_uv=True)
        return {'FINISHED'}


class HP_OT_extrude(Operator):
    bl_label = "Context Sensitive Extrude"
    bl_idname = "mesh.hp_extrude"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return (obj is not None and obj.mode == 'EDIT')

    def invoke(self, context, event):
        if bpy.context.object.type == 'CURVE':
            bpy.ops.curve.extrude()
            bpy.ops.transform.translate('INVOKE_DEFAULT')
            return {'FINISHED'}

        mesh = context.object.data
        selface = mesh.total_face_sel
        seledge = mesh.total_edge_sel
        selvert = mesh.total_vert_sel

        if selvert == 0:
            bpy.ops.mesh.select_mode(type='VERT')
            bpy.ops.mesh.dupli_extrude_cursor('INVOKE_DEFAULT')
            return {'FINISHED'}
        if selvert > 0 and seledge == 0:
            bpy.ops.mesh.extrude_region_move('INVOKE_DEFAULT')
            return {'FINISHED'}
        if seledge > 0 and selface == 0:
            bpy.ops.mesh.extrude_region_move('INVOKE_DEFAULT')
            return {'FINISHED'}

        bpy.ops.mesh.extrude_region_move('EXEC_DEFAULT')

        if mesh.total_face_sel != selface:
            bpy.ops.transform.shrink_fatten('INVOKE_DEFAULT', use_even_offset=True)
            return {'FINISHED'}

        bpy.ops.transform.shrink_fatten('INVOKE_DEFAULT', use_even_offset=True)
        return {'FINISHED'}

    

class HP_OT_SmartScale(Operator):
    bl_idname = "view3d.smart_scale"        # unique identifier for buttons and menu items to reference.
    bl_label = "Context Sensitive Scale"         # display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}  # enable undo for the operator.
    # @classmethod
    # def poll(cls, context):
        # obj = context.active_object
        # return (obj is not None and obj.mode == 'OBJECT')
    def invoke(self, context, event):
        modal = False
        try:
            for ob in bpy.context.selected_objects:
                if ob.mode == 'OBJECT' and ob.children == () and ob.data.users == 1 and ob.type == 'MESH':
                    modal = True
                    print('running modal')
        except:
            pass
        if modal:
            context.window_manager.modal_handler_add(self)
            print('Scaling MODAL')
        bpy.ops.transform.resize('INVOKE_DEFAULT', mirror=True)
        return {'RUNNING_MODAL'}
    def modal(self, context, event):
        print("MODAL " + event.type)
        if event.type == 'MOUSEMOVE':
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
            return {'FINISHED'}
        # if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
        #     print('Applying Scale')
        #     return {'FINISHED'}
        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            return {'CANCELLED'}
        else:
            return {'RUNNING_MODAL'}
class HP_OT_SmartBevel(bpy.types.Operator):
    bl_idname = "view3d.smart_bevel"        # unique identifier for buttons and menu items to reference.
    bl_label = "Smart Bevel"         # display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}  # enable undo for the operator.

    def invoke(self, context, event):
        if context.active_object.mode == 'OBJECT':
            print('Only works in Edit Mode')
            #bpy.ops.view3d.hp_draw('INVOKE_DEFAULT')
        else:
            me = bpy.context.object.data
            bm = bmesh.from_edit_mesh(me)
            sel = []
            for v in bm.verts:
                if v.select:
                    sel.append(v)
            if len(sel) == 0:
                print('Nothing Selected')
                # bpy.ops.view3d.hp_draw('INVOKE_DEFAULT')
            else:
                if tuple(bpy.context.scene.tool_settings.mesh_select_mode) == (True, False, False):
                    bpy.ops.mesh.bevel('INVOKE_DEFAULT',clamp_overlap=True,affect='VERTICES')
                    return {'FINISHED'}
                elif tuple(bpy.context.scene.tool_settings.mesh_select_mode) == (False, False, True):
                    bpy.ops.mesh.select_mode(type = 'EDGE')
                    print('edge mode...')
                    bpy.ops.mesh.region_to_loop('INVOKE_DEFAULT')
                    print('selecting border...')
                    me = bpy.context.object.data
                    bm = bmesh.from_edit_mesh(me)
                    sel = []
                    for v in bm.verts:
                        if v.select:
                            sel.append(v)
                    if len(sel) == 0:
                        bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.mesh.bevel('INVOKE_DEFAULT', clamp_overlap=True, miter_outer='ARC')
            bpy.ops.mesh.remove_doubles()

        return {'FINISHED'}




class HP_OT_SeparateAndSelect(bpy.types.Operator):
    bl_idname = "object.separate_and_select"        # unique identifier for buttons and menu items to reference.
    bl_label = "Separate and Select"         # display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}  # enable undo for the operator.
    def execute(self, context):

        bases = bpy.context.selected_objects
        if bpy.context.object.type == 'MESH':
            bpy.ops.mesh.separate(type='SELECTED')
        elif bpy.context.object.type == 'GPENCIL':
            bpy.ops.gpencil.stroke_separate(mode='POINT')
        elif bpy.context.object.type == 'GREASEPENCIL':
            bpy.ops.grease_pencil.stroke_separate(mode='POINT')

            # bpy.ops.gpencil.stroke_split()
        elif bpy.context.object.type == 'CURVE':
            bpy.ops.curve.separate()
        if bpy.context.object.type == 'GPENCIL':
            bpy.ops.gpencil.editmode_toggle()
        elif bpy.context.object.type == 'GREASEPENCIL':
            bpy.ops.object.mode_set('EDIT', toggle=True)
        else:
            bpy.ops.object.editmode_toggle()
            
        for b in bases:
            b.select_set(state=False)
        selected = bpy.context.selected_objects
        bpy.context.view_layer.objects.active = selected[-1]
        if bpy.context.object.type == 'GPENCIL':
            bpy.ops.gpencil.editmode_toggle()
        elif bpy.context.object.type == 'GREASEPENCIL':
            bpy.ops.grease_pencil.editmode_toggle()
        else:
            bpy.ops.object.editmode_toggle()
        if bpy.context.object.type == 'MESH':
            bpy.ops.mesh.select_all(action='SELECT')
        if bpy.context.object.type == 'CURVE':
            bpy.ops.curve.select_all(action='SELECT')
        return {'FINISHED'}

class HP_OT_SmartShadeSmooth(bpy.types.Operator):
    bl_idname = "view3d.smart_shade_smooth_toggle"        # unique identifier for buttons and menu items to reference.
    bl_label = "Smart Shade Smooth"         # display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}  # enable undo for the operator.

    def invoke(self, context, event):
        isedit = False
        for ob in bpy.context.selected_objects:
            if ob.type == 'MESH':
                if ob.mode == 'EDIT':
                    isedit = True
                    bpy.ops.object.editmode_toggle()
                bpy.ops.object.shade_smooth()
                # Blender 4.1+ removed Mesh.use_auto_smooth / auto_smooth_angle.
                # shade_auto_smooth() adds the 'Smooth by Angle' node group instead.
                bpy.ops.object.shade_auto_smooth(angle=0.436332)
                if isedit:
                    bpy.ops.object.editmode_toggle()
        return {'FINISHED'}

class HP_OT_toggle_render_material(bpy.types.Operator):
    bl_idname = "view3d.toggle_render_material"        # unique identifier for buttons and menu items to reference.
    bl_label = ""         # display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}  # enable undo for the operator.

    def invoke(self, context, event):
        if bpy.context.space_data.viewport_shade != 'MATERIAL':
            bpy.context.space_data.viewport_shade = 'MATERIAL'
        elif bpy.context.space_data.viewport_shade == 'MATERIAL':
            bpy.context.space_data.viewport_shade = 'RENDERED'
        return {'FINISHED'}



class HP_OT_Smart_Delete(bpy.types.Operator):
    bl_idname = "view3d.smart_delete"
    bl_label = "Smart Delete"
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context, event):
        obj = context.object
        objType = getattr(obj, 'type', '')
        act = bpy.context.active_object

        try:
            if not act:
                for o in bpy.context.selected_objects:
                    bpy.context.view_layer.objects.active = o
                    act = bpy.context.active_object

            actname = act.name if act else ""

            # Object mode deletion logic
            if context.active_object.mode == 'OBJECT':
                if '_Cutter' in actname:
                    bpy.ops.object.delete(use_global=False)
                    for obj in bpy.context.view_layer.objects:
                        bpy.context.view_layer.objects.active = obj
                        bpy.ops.object.modifier_remove(modifier=actname)
                else:
                    bpy.ops.object.delete(use_global=False)

            # Edit mode deletion for different object types
            elif objType == 'CURVE':
                if context.active_object.mode != 'OBJECT':
                    bpy.ops.curve.delete(type='VERT')

            # Grease Pencil handling (GPENCIL for 4.2, GREASEPENCIL for 4.3+)
            elif objType in {'GPENCIL', 'GREASEPENCIL'}:
                if context.active_object.mode != 'OBJECT':
                    if bpy.app.version < (4, 3, 0):
                        bpy.ops.gpencil.delete(type='POINTS')
                    else:
                        # Blender 4.3+ Grease Pencil API handling
                        bpy.ops.grease_pencil.delete()

            # Meta object handling
            elif objType == 'META':
                if context.active_object.mode != 'OBJECT':
                    bpy.ops.mball.delete_metaelems()

            # Mesh handling
            elif objType == 'MESH':
                if context.active_object.mode != 'OBJECT':
                    if tuple(bpy.context.scene.tool_settings.mesh_select_mode) == (False, False, True):
                        bpy.ops.mesh.delete(type='FACE')
                    else:
                        bpy.ops.mesh.delete(type='VERT')

        except Exception as e:
            print(f"Error in Smart Delete: {e}")
        
        return {'FINISHED'}







class HP_OT_Subdivision_Toggle(bpy.types.Operator):
    bl_idname = "view3d.subdivision_toggle"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context, event):

        # Now that Tab reaches this in Object Mode for every object type
        # (the stock Tab used to eat it there), skip objects that cannot
        # take a Subdivision modifier instead of erroring on them.
        supported = {'MESH', 'CURVE', 'SURFACE', 'FONT'}
        for o in bpy.context.selected_objects:
            if o.type not in supported:
                continue
            bpy.context.view_layer.objects.active = o
            if 0 < len([m for m in bpy.context.object.modifiers if m.type == "SUBSURF"]):
                if bpy.context.object.modifiers["Subsurf_Base"].show_viewport == False:
                    bpy.context.object.modifiers["Subsurf_Base"].show_render = True
                    bpy.context.object.modifiers["Subsurf_Base"].show_viewport = True
                else:
                    bpy.context.object.modifiers["Subsurf_Base"].show_render = False
                    bpy.context.object.modifiers["Subsurf_Base"].show_viewport = False

            else:
                o.modifiers.new("Subsurf_Base", "SUBSURF")
                bpy.context.object.modifiers["Subsurf_Base"].name = "Subsurf_Base"
                bpy.context.object.modifiers["Subsurf_Base"].render_levels = 3
                bpy.context.object.modifiers["Subsurf_Base"].levels = 3
                bpy.context.object.modifiers["Subsurf_Base"].show_in_editmode = True
                bpy.context.object.modifiers["Subsurf_Base"].show_on_cage = False
                bpy.context.object.modifiers["Subsurf_Base"].subdivision_type = 'CATMULL_CLARK'

        return {'FINISHED'}

class HP_OT_SaveWithoutPrompt(bpy.types.Operator):
    bl_idname = "wm.save_without_prompt"
    bl_label = "Save without prompt"

    def execute(self, context):
        bpy.ops.wm.save_mainfile()
        return {'FINISHED'}
class HP_OT_RevertWithoutPrompt(bpy.types.Operator):
    bl_idname = "wm.revert_without_prompt"
    bl_label = "Revert without prompt"

    def execute(self, context):
        bpy.ops.wm.revert_mainfile()
        return {'FINISHED'}
class HP_OT_DeleteWithoutPrompt(bpy.types.Operator):
    bl_idname = "wm.delete_without_prompt"
    bl_label = "Delete without prompt"

    def execute(self, context):
        bpy.ops.object.delete()
        return {'FINISHED'}


class HP_OT_SetCollectionCenter(bpy.types.Operator):
    bl_idname = "view3d.hp_set_collection_center"         # unique identifier for buttons and menu items to reference.
    bl_label = "Set Collection Center"       # display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}  # enable undo for the operator.

    def execute(self, context):
        ## 1 Save selection
        bpy.ops.view3d.snap_cursor_to_selected()
        #bpy.ops.view3d.snap_cursor_to_selected()
       # bpy.ops.object.instance_offset_from_cursor()
        return {'FINISHED'}

#### MOVE SPACE Y AXIS #####


class HP_TranslateModalOperator(bpy.types.Operator):
    """Toggle Move Mode and Y Constraint"""
    bl_idname = "object.modal_translate"
    bl_label = "Modal Translate"
    bl_options = {'REGISTER', 'UNDO'}

    is_moving: bpy.props.BoolProperty(default=False)
    constrain_y: bpy.props.BoolProperty(default=False)

    def modal(self, context, event):
        # Listen for keypresses
        if event.type == 'SPACE' and event.value == 'PRESS':
            # Toggle Y-axis constraint
            self.constrain_y = not self.constrain_y
            self.report({'INFO'}, f"Y-axis constraint {'enabled' if self.constrain_y else 'disabled'}")
            
            # Restart the transform operator with updated constraints
            bpy.ops.transform.translate(
                'INVOKE_DEFAULT',
                constraint_axis=(False, self.constrain_y, False)  # X, Y, Z constraints
            )
            return {'RUNNING_MODAL'}

        if event.type in {'LEFTMOUSE', 'RET'}:  # Confirm operation
            self.report({'INFO'}, "Transform Confirmed")
            self.is_moving = False
            return {'FINISHED'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:  # Cancel operation
            self.report({'INFO'}, "Transform Canceled")
            self.is_moving = False
            bpy.ops.ed.undo()  # Undo the transform
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        # Start the transform operator
        self.is_moving = True
        self.constrain_y = False  # Default: no constraint
        bpy.ops.transform.translate('INVOKE_DEFAULT')

        # Add a modal handler for post-transform actions
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

class OBJECT_OT_set_camera_off_wire(bpy.types.Operator):
    """Turn OFF Camera Visibility, Display as WIRE, Shadow ON"""
    bl_idname = "object.set_camera_off_wire"
    bl_label = "Hide From Camera (Wire Display)"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT' and context.selected_objects

    def execute(self, context):
        is_cycles = context.scene.render.engine == 'CYCLES'
        for obj in context.selected_objects:
            if hasattr(obj, "visible_camera"):
                obj.visible_camera = False
            if is_cycles and hasattr(obj, "visible_shadow"):
                obj.visible_shadow = True
            obj.display_type = 'WIRE'
        self.report({'INFO'}, "Camera visibility OFF, Display as WIRE.")
        return {'FINISHED'}

class OBJECT_OT_set_camera_on_textured(bpy.types.Operator):
    """Turn ON Camera Visibility, Display as TEXTURED"""
    bl_idname = "object.set_camera_on_textured"
    bl_label = "Show in Camera (Textured Display)"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT' and context.selected_objects

    def execute(self, context):
        for obj in context.selected_objects:
            if hasattr(obj, "visible_camera"):
                obj.visible_camera = True
            obj.display_type = 'TEXTURED'
        self.report({'INFO'}, "Camera visibility ON, Display as TEXTURED.")
        return {'FINISHED'}

class OBJECT_OT_select_camera_hidden(bpy.types.Operator):
    """Select all geometry objects with Camera Visibility OFF"""
    bl_idname = "object.select_camera_hidden"
    bl_label = "Select Hidden From Camera"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.ops.object.select_all(action='DESELECT')
        count = 0
        geometry_types = {'MESH', 'CURVE', 'SURFACE', 'META', 'FONT'}

        for obj in context.scene.objects:
            if (
                obj.type in geometry_types
                and hasattr(obj, "visible_camera")
                and not obj.visible_camera
            ):
                obj.select_set(True)
                count += 1

        self.report({'INFO'}, f"Selected {count} camera-hidden geometry objects.")
        return {'FINISHED'}




def draw_func(self, context):
    layout = self.layout
    layout.separator()
    layout.operator("object.hp_key_out_background", icon='IMAGE_ALPHA')
    layout.operator("object.hp_cutout_mesh", icon='MESH_DATA')
    layout.separator()
    layout.operator("object.set_camera_off_wire", icon='HIDE_ON')
    layout.operator("object.set_camera_on_textured", icon='HIDE_OFF')
    layout.operator("object.select_camera_hidden", icon='RESTRICT_VIEW_ON')


# ---------------------------------------------------------------- symmetry

class HP_OT_toggle_symmetry(bpy.types.Operator):
    """Toggle mirror / symmetry on one axis for the current mode"""
    bl_idname = "object.hp_toggle_symmetry"
    bl_label = "Toggle Symmetry"
    bl_options = {'REGISTER', 'UNDO'}

    axis: bpy.props.EnumProperty(
        name="Axis",
        items=[('X', "X", ""), ('Y', "Y", ""), ('Z', "Z", "")],
        default='X',
    )

    def _candidates(self, context, axis):
        """Where the flag lives, most likely first.

        Blender 5.x drives the sculpt Symmetry panel from the mesh's own
        use_mirror_* flags. tool_settings.sculpt.use_symmetry_* still exists but
        no longer does anything, so checking it first meant reporting success
        while the panel never moved. Mesh first, paint structs as a fallback for
        object types that have no mesh.
        """
        tool_settings = context.scene.tool_settings
        mode = context.mode
        mesh = context.object.data if context.object else None

        if mesh is not None:
            yield mesh, "use_mirror_" + axis
            yield mesh, "use_symmetry_" + axis

        paint = None
        if mode == 'SCULPT':
            paint = getattr(tool_settings, "sculpt", None)
        elif mode == 'PAINT_VERTEX':
            paint = getattr(tool_settings, "vertex_paint", None)
        elif mode == 'PAINT_WEIGHT':
            paint = getattr(tool_settings, "weight_paint", None)
        elif mode == 'PAINT_TEXTURE':
            paint = getattr(tool_settings, "image_paint", None)

        if paint is not None:
            for name in ("use_symmetry_" + axis, "symmetry_" + axis,
                         "use_mirror_" + axis):
                yield paint, name
            unified = getattr(paint, "unified_paint_settings", None)
            if unified is not None:
                yield unified, "use_symmetry_" + axis

    def _report_options(self, context):
        """Print what actually exists, so a failure is diagnosable."""
        tool_settings = context.scene.tool_settings
        for name in ("sculpt", "vertex_paint", "weight_paint", "image_paint"):
            holder = getattr(tool_settings, name, None)
            if holder is None:
                continue
            found = [a for a in dir(holder)
                     if "symmetr" in a.lower() or "mirror" in a.lower()]
            print("[HEAVYPOLY] tool_settings.%s: %s" % (name, found))
        if context.object and context.object.data:
            found = [a for a in dir(context.object.data)
                     if "symmetr" in a.lower() or "mirror" in a.lower()]
            print("[HEAVYPOLY] object.data: %s" % found)

    def execute(self, context):
        axis = self.axis.lower()

        for owner, attr in self._candidates(context, axis):
            if owner is None or not hasattr(owner, attr):
                continue
            try:
                value = not getattr(owner, attr)
                setattr(owner, attr, value)
            except Exception as e:
                print("[HEAVYPOLY] could not set %s: %r" % (attr, e))
                continue
            self.report({'INFO'}, "Symmetry %s: %s"
                        % (self.axis, "on" if value else "off"))
            print("[HEAVYPOLY] toggled %s.%s -> %s"
                  % (type(owner).__name__, attr, value))
            return {'FINISHED'}

        self.report({'WARNING'}, "No symmetry setting for mode %s." % context.mode)
        print("[HEAVYPOLY] symmetry target not found for mode %s" % context.mode)
        self._report_options(context)
        return {'CANCELLED'}


# ---------------------------------------------------------------- clipboard

# ---------------------------------------------------------------- images

def hp_image_has_transparency(image, samples=4096):
    """Does the image actually contain see-through pixels?

    image.depth only says the format has an alpha channel. Clipboard images
    are usually RGBA even when every pixel is opaque, and wiring alpha up for
    those makes the plane flicker for no reason. So sample the real pixels.
    """
    if image is None or image.channels < 4:
        return False

    try:
        pixel_count = image.size[0] * image.size[1]
    except Exception:
        return False
    if pixel_count <= 0:
        return False

    try:
        pixels = image.pixels[:]
    except Exception:
        return False

    step = max(1, pixel_count // max(1, samples))
    for index in range(0, pixel_count, step):
        if pixels[index * 4 + 3] < 0.999:
            return True

    # Edges are where cut-outs live, so check the border explicitly.
    width, height = image.size
    for x in range(0, width, max(1, width // 64)):
        for y in (0, height - 1):
            if pixels[(y * width + x) * 4 + 3] < 0.999:
                return True
    for y in range(0, height, max(1, height // 64)):
        for x in (0, width - 1):
            if pixels[(y * width + x) * 4 + 3] < 0.999:
                return True

    return False


def hp_set_transparency(material, method='DITHERED'):
    """Blender 4.2 replaced blend_method with surface_render_method."""
    if hasattr(material, "surface_render_method"):
        try:
            material.surface_render_method = method
            return
        except Exception as e:
            print("[HEAVYPOLY] surface_render_method failed: %r" % (e,))
    if hasattr(material, "blend_method"):
        try:
            material.blend_method = 'BLEND' if method == 'BLENDED' else 'CLIP'
        except Exception as e:
            print("[HEAVYPOLY] blend_method failed: %r" % (e,))



class HP_OT_paste_image_plane(bpy.types.Operator):
    """Paste the image on the clipboard as a plane facing front"""
    bl_idname = "object.hp_paste_image_plane"
    bl_label = "Paste Image as Plane"
    bl_options = {'REGISTER', 'UNDO'}

    height: bpy.props.FloatProperty(
        name="Height",
        description="Height of the plane in metres",
        default=2.0,
        min=0.001,
    )
    offset: bpy.props.FloatProperty(
        name="Offset",
        description="Distance in front of the selected object",
        default=1.0,
    )
    render_method: bpy.props.EnumProperty(
        name="Transparency",
        items=[
            ('DITHERED', "Dithered", "No sorting artefacts, best for cut-outs"),
            ('BLENDED', "Blended", "Accurate see-through, can flicker when planes overlap"),
        ],
        default='DITHERED',
    )
    key_out: bpy.props.BoolProperty(
        name="Key Out Background",
        description="Make one colour transparent, for images with no alpha",
        default=False,
    )
    key_color: bpy.props.FloatVectorProperty(
        name="Key Colour", subtype='COLOR', size=3,
        min=0.0, max=1.0, default=(1.0, 1.0, 1.0),
    )
    threshold: bpy.props.FloatProperty(
        name="Threshold",
        description="How close a pixel has to be to the key colour",
        default=0.10, min=0.0, max=1.732,
    )
    softness: bpy.props.FloatProperty(
        name="Softness",
        description="Width of the fade at the edge of the key",
        default=0.05, min=0.0, max=1.0,
    )
    key_invert: bpy.props.BoolProperty(
        name="Invert Key",
        description="Keep the key colour and drop everything else",
        default=False,
    )
    shadeless: bpy.props.BoolProperty(
        name="Shadeless",
        description="Use Emission instead of Principled, so the image reads "
                    "the same with no lights in the scene",
        default=False,
    )

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        column = layout.column()
        column.prop(self, "height")
        column.prop(self, "offset")
        column.prop(self, "shadeless")
        column.prop(self, "render_method")

        layout.separator()
        layout.prop(self, "key_out")
        keys = layout.column()
        keys.enabled = self.key_out
        keys.prop(self, "key_color")
        keys.prop(self, "threshold")
        keys.prop(self, "softness")
        keys.prop(self, "key_invert")

    @staticmethod
    def _find_image_editor(context):
        for window in context.window_manager.windows:
            for area in window.screen.areas:
                if area.type == 'IMAGE_EDITOR':
                    for region in area.regions:
                        if region.type == 'WINDOW':
                            return window, area, region
        return None, None, None

    def _grab_clipboard(self, context):
        """image.clipboard_paste only works from inside an Image Editor.

        temp_override alone was not enough - Blender still refused with "No
        image to paste" - so switch a real area over for a moment and invoke it
        the way the menu item does.
        """
        before = set(bpy.data.images.keys())

        def _added():
            names = set(bpy.data.images.keys()) - before
            return bpy.data.images[names.pop()] if names else None

        # An Image Editor that is already open is the best case.
        window, area, region = self._find_image_editor(context)
        if area is not None:
            try:
                with context.temp_override(window=window, area=area,
                                           region=region,
                                           space_data=area.spaces.active):
                    bpy.ops.image.clipboard_paste('INVOKE_DEFAULT')
            except Exception as e:
                print("[HEAVYPOLY] paste in existing editor failed: %r" % (e,))
            image = _added()
            if image is not None:
                return image

        # Otherwise borrow the largest area, flip it, paste, flip it back.
        screen = context.screen
        if screen is None or not screen.areas:
            return None
        area = max(screen.areas, key=lambda a: a.width * a.height)
        previous_type = area.type
        try:
            area.type = 'IMAGE_EDITOR'
            region = next((r for r in area.regions if r.type == 'WINDOW'), None)
            with context.temp_override(window=context.window, area=area,
                                       region=region,
                                       space_data=area.spaces.active):
                bpy.ops.image.clipboard_paste('INVOKE_DEFAULT')
        except Exception as e:
            print("[HEAVYPOLY] paste in borrowed editor failed: %r" % (e,))
        finally:
            try:
                area.type = previous_type
            except Exception:
                pass

        return _added()

    def _store_image(self, image):
        """Write next to the .blend when saved, otherwise pack it in.

        Either way the image survives closing Blender, which the raw clipboard
        paste does not.
        """
        blend_path = bpy.data.filepath
        if not blend_path:
            try:
                image.pack()
                print("[HEAVYPOLY] image packed into the .blend")
            except Exception as e:
                print("[HEAVYPOLY] could not pack the image: %r" % (e,))
            return

        folder = os.path.join(os.path.dirname(blend_path), "textures")
        try:
            os.makedirs(folder, exist_ok=True)
            name = bpy.path.clean_name(image.name) or "pasted"
            target = os.path.join(folder, name + ".png")
            index = 1
            while os.path.exists(target):
                target = os.path.join(folder, "%s_%03d.png" % (name, index))
                index += 1
            image.filepath_raw = target
            image.file_format = 'PNG'
            image.save()
            print("[HEAVYPOLY] image saved to %s" % target)
        except Exception as e:
            print("[HEAVYPOLY] could not save the image, packing instead: %r" % (e,))
            try:
                image.pack()
            except Exception:
                pass

    def _make_material(self, image):
        material = bpy.data.materials.new(name=image.name)
        material.use_nodes = True

        nodes = material.node_tree.nodes
        links = material.node_tree.links
        nodes.clear()

        output = nodes.new('ShaderNodeOutputMaterial')
        output.location = (300, 0)

        if self.shadeless:
            shader = nodes.new('ShaderNodeEmission')
            colour_input = 'Color'
        else:
            shader = nodes.new('ShaderNodeBsdfPrincipled')
            colour_input = 'Base Color'
        shader.location = (0, 0)

        texture = nodes.new('ShaderNodeTexImage')
        texture.location = (-340, 0)
        texture.image = image
        texture.interpolation = 'Cubic'

        links.new(texture.outputs['Color'], shader.inputs[colour_input])
        links.new(shader.outputs[0], output.inputs['Surface'])

        # Only wire alpha when the image really is see-through.
        if hp_image_has_transparency(image):
            if 'Alpha' in shader.inputs:
                links.new(texture.outputs['Alpha'], shader.inputs['Alpha'])
            else:
                mix = nodes.new('ShaderNodeMixShader')
                mix.location = (150, -160)
                transparent = nodes.new('ShaderNodeBsdfTransparent')
                transparent.location = (0, -220)
                links.new(texture.outputs['Alpha'], mix.inputs['Fac'])
                links.new(transparent.outputs[0], mix.inputs[1])
                links.new(shader.outputs[0], mix.inputs[2])
                links.new(mix.outputs[0], output.inputs['Surface'])

            hp_set_transparency(material, self.render_method)

        return material

    def execute(self, context):
        image = self._grab_clipboard(context)
        if image is None:
            self.report({'WARNING'}, "No image on the clipboard.")
            return {'CANCELLED'}

        self._store_image(image)

        target = context.active_object
        if target is not None and target.select_get():
            # In front of the object, along its local -Y.
            location = target.matrix_world @ Vector((0.0, -self.offset, 0.0))
        else:
            location = context.scene.cursor.location.copy()

        bpy.ops.mesh.primitive_plane_add(size=1.0, align='WORLD', location=location)
        plane = context.active_object
        plane.name = image.name

        # Stand it up facing -Y, so it reads correctly in front view.
        plane.rotation_euler = (math.radians(90.0), 0.0, 0.0)

        width, height = image.size
        aspect = (width / height) if height else 1.0
        plane.scale = (self.height * aspect, self.height, 1.0)

        material = self._make_material(image)
        plane.data.materials.append(material)

        if self.key_out:
            hp_apply_colour_key(material, self.key_color, self.threshold,
                                self.softness, self.key_invert,
                                self.render_method)
        else:
            hp_remove_colour_key(material)

        self.report({'INFO'}, "Pasted %s (%dx%d)" % (image.name, width, height))
        return {'FINISHED'}


def hp_apply_colour_key(material, key_color, threshold, softness, invert,
                        render_method='DITHERED'):
    """Insert a colour-distance key between the image texture and the shader.

    Any previous key is removed first, so calling this repeatedly - which is
    what happens while dragging the sliders in the redo panel - never stacks
    nodes up.
    """
    if not material.use_nodes:
        return False

    tree = material.node_tree
    nodes = tree.nodes
    links = tree.links

    texture = next((n for n in nodes if n.type == 'TEX_IMAGE' and n.image), None)
    if texture is None:
        return False

    shader = next((n for n in nodes
                   if n.type in {'BSDF_PRINCIPLED', 'EMISSION'}), None)
    if shader is None:
        return False

    for node in [n for n in nodes if n.label == "HP Key"]:
        nodes.remove(node)

    base_x, base_y = texture.location
    offset_y = base_y - 320

    difference = nodes.new('ShaderNodeMix')
    difference.label = "HP Key"
    difference.data_type = 'RGBA'
    difference.blend_type = 'DIFFERENCE'
    difference.location = (base_x + 200, offset_y)
    difference.inputs['Factor'].default_value = 1.0
    difference.inputs[7].default_value = (*key_color, 1.0)

    distance = nodes.new('ShaderNodeVectorMath')
    distance.label = "HP Key"
    distance.operation = 'LENGTH'
    distance.location = (base_x + 380, offset_y)

    ramp = nodes.new('ShaderNodeMapRange')
    ramp.label = "HP Key"
    ramp.location = (base_x + 560, offset_y)
    ramp.inputs['From Min'].default_value = threshold
    ramp.inputs['From Max'].default_value = threshold + max(softness, 1e-4)
    ramp.inputs['To Min'].default_value = 1.0 if invert else 0.0
    ramp.inputs['To Max'].default_value = 0.0 if invert else 1.0
    ramp.clamp = True

    links.new(texture.outputs['Color'], difference.inputs[6])
    links.new(difference.outputs[2], distance.inputs[0])
    links.new(distance.outputs['Value'], ramp.inputs['Value'])

    if 'Alpha' in shader.inputs:
        links.new(ramp.outputs['Result'], shader.inputs['Alpha'])
    else:
        output = next((n for n in nodes if n.type == 'OUTPUT_MATERIAL'), None)
        if output is None:
            return False
        mix = nodes.new('ShaderNodeMixShader')
        mix.label = "HP Key"
        mix.location = (base_x + 760, offset_y)
        transparent = nodes.new('ShaderNodeBsdfTransparent')
        transparent.label = "HP Key"
        transparent.location = (base_x + 560, offset_y - 160)
        links.new(ramp.outputs['Result'], mix.inputs['Fac'])
        links.new(transparent.outputs[0], mix.inputs[1])
        links.new(shader.outputs[0], mix.inputs[2])
        links.new(mix.outputs[0], output.inputs['Surface'])

    hp_set_transparency(material, render_method)
    return True


def hp_remove_colour_key(material):
    """Take the key back out and reconnect the shader directly."""
    if not material.use_nodes:
        return False

    tree = material.node_tree
    nodes = tree.nodes
    keyed = [n for n in nodes if n.label == "HP Key"]
    if not keyed:
        return False

    shader = next((n for n in nodes
                   if n.type in {'BSDF_PRINCIPLED', 'EMISSION'}), None)
    output = next((n for n in nodes if n.type == 'OUTPUT_MATERIAL'), None)
    for node in keyed:
        nodes.remove(node)
    if shader is not None and output is not None and not output.inputs['Surface'].links:
        tree.links.new(shader.outputs[0], output.inputs['Surface'])
    return True


class HP_OT_key_out_background(bpy.types.Operator):
    """Make one colour transparent on the selected objects"""
    bl_idname = "object.hp_key_out_background"
    bl_label = "Key Out Background"
    bl_options = {'REGISTER', 'UNDO'}

    key_color: bpy.props.FloatVectorProperty(
        name="Key Colour", subtype='COLOR', size=3,
        min=0.0, max=1.0, default=(1.0, 1.0, 1.0),
    )
    threshold: bpy.props.FloatProperty(
        name="Threshold",
        description="How close a pixel has to be to the key colour",
        default=0.10, min=0.0, max=1.732,
    )
    softness: bpy.props.FloatProperty(
        name="Softness",
        description="Width of the fade at the edge of the key",
        default=0.05, min=0.0, max=1.0,
    )
    invert: bpy.props.BoolProperty(
        name="Invert",
        description="Keep the key colour and drop everything else",
        default=False,
    )
    render_method: bpy.props.EnumProperty(
        name="Transparency",
        items=[
            ('DITHERED', "Dithered", "No sorting artefacts, best for cut-outs"),
            ('BLENDED', "Blended", "Accurate see-through, can flicker when planes overlap"),
        ],
        default='DITHERED',
    )

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT' and context.selected_objects

    def execute(self, context):
        done = 0
        seen = set()
        for obj in context.selected_objects:
            for slot in getattr(obj, "material_slots", []):
                material = slot.material
                if material is None or material.name in seen:
                    continue
                seen.add(material.name)
                if hp_apply_colour_key(material, self.key_color, self.threshold,
                                       self.softness, self.invert,
                                       self.render_method):
                    done += 1

        if not done:
            self.report({'WARNING'}, "No image texture found on the selection.")
            return {'CANCELLED'}

        self.report({'INFO'}, "Keyed %d material(s)." % done)
        return {'FINISHED'}


# ---------------------------------------------------------------- cut-out mesh
#
# Trims a textured plane to the image outline, like a foliage card. Written
# from scratch - the idea exists in paid add-ons (Leafig), but per CLAUDE.md
# no code is taken from them, only the behaviour as observed in their UI.

def hp_find_object_image(obj):
    """First image texture across the object's materials, or None."""
    for slot in getattr(obj, "material_slots", []):
        material = slot.material
        if material is None or not material.use_nodes:
            continue
        for node in material.node_tree.nodes:
            if node.type == 'TEX_IMAGE' and node.image is not None:
                return node.image
    return None


def hp_find_key_colour(obj):
    """The colour Key Out Background keyed on this object, or None."""
    for slot in getattr(obj, "material_slots", []):
        material = slot.material
        if material is None or not material.use_nodes:
            continue
        for node in material.node_tree.nodes:
            if node.label == "HP Key" and node.type == 'MIX':
                return tuple(node.inputs[7].default_value)[:3]
    return None


def hp_trace_mask_loops(binary):
    """Closed boundary loops of a boolean mask, foreground kept on the left.

    Runs on pixel corners, so coordinates go 0..W and 0..H. Walking with the
    foreground on the left makes outer outlines counter-clockwise and holes
    clockwise, which is how the caller tells them apart. Where two foreground
    pixels touch only diagonally the walk turns left, keeping the two blobs
    in separate loops instead of fusing them at a single point.
    """
    import numpy as np

    height, width = binary.shape
    grid = np.zeros((height + 2, width + 2), dtype=bool)
    grid[1:-1, 1:-1] = binary

    segments = {}

    def add(start, end):
        segments.setdefault(start, []).append(end)

    above, below = grid[1:, :], grid[:-1, :]
    left, right = grid[:, :-1], grid[:, 1:]
    for r, c in np.argwhere(above & ~below):   # fg above the line: walk +x
        add((int(c), int(r) + 1), (int(c) + 1, int(r) + 1))
    for r, c in np.argwhere(below & ~above):   # fg below: walk -x
        add((int(c) + 1, int(r) + 1), (int(c), int(r) + 1))
    for r, c in np.argwhere(left & ~right):    # fg left of the line: walk +y
        add((int(c) + 1, int(r)), (int(c) + 1, int(r) + 1))
    for r, c in np.argwhere(right & ~left):    # fg right: walk -y
        add((int(c) + 1, int(r) + 1), (int(c) + 1, int(r)))

    loops = []
    while segments:
        start = next(iter(segments))
        outs = segments[start]
        current = outs.pop()
        if not outs:
            del segments[start]
        direction = (current[0] - start[0], current[1] - start[1])
        loop = [start]
        closed = True
        while current != start:
            outs = segments.get(current)
            if not outs:
                closed = False   # dangling segment; should not happen
                break
            dx, dy = direction
            chosen = None
            for turn in ((-dy, dx), (dx, dy), (dy, -dx)):   # left, straight, right
                candidate = (current[0] + turn[0], current[1] + turn[1])
                if candidate in outs:
                    chosen, chosen_direction = candidate, turn
                    break
            if chosen is None:
                closed = False
                break
            outs.remove(chosen)
            if not outs:
                del segments[current]
            if chosen_direction != direction:
                loop.append(current)   # a corner; straight runs collapse
            current = chosen
            direction = chosen_direction
        if closed and len(loop) >= 3:
            loops.append([(x - 1, y - 1) for x, y in loop])   # un-pad
    return loops


def _hp_dp_simplify(points, epsilon):
    """Douglas-Peucker on an open polyline; endpoints are kept."""
    if epsilon <= 0 or len(points) < 3:
        return list(points)
    keep = [False] * len(points)
    keep[0] = keep[-1] = True
    stack = [(0, len(points) - 1)]
    while stack:
        a, b = stack.pop()
        if b - a < 2:
            continue
        ax, ay = points[a]
        bx, by = points[b]
        dx, dy = bx - ax, by - ay
        length = math.hypot(dx, dy)
        worst, worst_index = -1.0, -1
        for i in range(a + 1, b):
            px, py = points[i]
            if length < 1e-9:
                d = math.hypot(px - ax, py - ay)
            else:
                d = abs(dx * (py - ay) - dy * (px - ax)) / length
            if d > worst:
                worst, worst_index = d, i
        if worst > epsilon:
            keep[worst_index] = True
            stack.append((a, worst_index))
            stack.append((worst_index, b))
    return [p for p, k in zip(points, keep) if k]


def hp_simplify_loop(points, epsilon):
    """Douglas-Peucker for a closed loop: split at the far point, do halves."""
    if epsilon <= 0 or len(points) < 5:
        return list(points)
    first = points[0]
    split = max(range(1, len(points)),
                key=lambda i: (points[i][0] - first[0]) ** 2
                            + (points[i][1] - first[1]) ** 2)
    a = _hp_dp_simplify(points[:split + 1], epsilon)
    b = _hp_dp_simplify(points[split:] + [first], epsilon)
    return a[:-1] + b[:-1]


def _hp_loop_area(points):
    """Signed area; positive means counter-clockwise (an outer outline)."""
    area = 0.0
    for i in range(len(points)):
        x0, y0 = points[i]
        x1, y1 = points[(i + 1) % len(points)]
        area += x0 * y1 - x1 * y0
    return 0.5 * area


class HP_OT_cutout_mesh(bpy.types.Operator):
    """Trim the plane to the image outline and fill the inside with triangles"""
    bl_idname = "object.hp_cutout_mesh"
    bl_label = "Cut Out to Mesh"
    bl_options = {'REGISTER', 'UNDO'}

    channel: bpy.props.EnumProperty(
        name="Channel",
        description="What separates the image from its background",
        items=[
            ('ALPHA', "Alpha", "Use the image's own transparency"),
            ('DISTANCE', "Key Colour",
             "Distance from the background colour, like Key Out Background"),
        ],
        default='ALPHA',
    )
    background: bpy.props.FloatVectorProperty(
        name="Background", subtype='COLOR', size=3,
        min=0.0, max=1.0, default=(1.0, 1.0, 1.0),
    )
    smoothing: bpy.props.IntProperty(
        name="Smoothing",
        description="Blur passes over the mask before cutting; evens out noisy edges",
        default=0, min=0, max=16,
    )
    cutoff: bpy.props.FloatProperty(
        name="Cutoff",
        description="How opaque (or far from the background colour) a pixel "
                    "has to be to count as inside",
        default=0.5, min=0.0, max=1.0,
    )
    pixel_error: bpy.props.FloatProperty(
        name="Pixel Error",
        description="How far the outline may stray from the pixel boundary; "
                    "higher means fewer vertices",
        default=1.0, min=0.0, max=64.0,
    )
    inset: bpy.props.FloatProperty(
        name="Inset",
        description="Shrink the outline inward by this many pixels, hiding "
                    "the semi-transparent fringe at the edge",
        default=0.0, min=0.0, max=64.0,
        # Deliberately forgotten between runs. A remembered inset silently
        # ate the thin stems of the next image - erosion damage looks like
        # a broken tracer, not like a leftover setting.
        options={'SKIP_SAVE'},
    )
    min_size: bpy.props.FloatProperty(
        name="Min Size",
        description="Fill holes and drop specks smaller than this many "
                    "pixels across",
        default=4.0, min=0.0, max=256.0,
    )
    ignore_inner: bpy.props.BoolProperty(
        name="Ignore Inner",
        description="Skip holes inside the outline",
        default=False,
    )
    origin: bpy.props.EnumProperty(
        name="Origin",
        description="Where to put the object origin after cutting",
        items=[
            ('KEEP', "Keep", "Leave the origin where it is"),
            ('CENTER', "Center", "Middle of the cut-out"),
            ('BOTTOM', "Bottom",
             "Bottom middle - handy for plants and standees"),
        ],
        default='KEEP',
    )
    thickness: bpy.props.FloatProperty(
        name="Thickness",
        description="Add a Solidify modifier with this thickness; 0 removes it",
        default=0.0, min=0.0, max=10.0, subtype='DISTANCE',
    )
    # Original flat bounds and location of the mesh, captured on invoke so
    # that dragging the redo sliders keeps mapping onto the same rectangle
    # even though the mesh itself has already been replaced.
    rect: bpy.props.FloatVectorProperty(size=4, options={'HIDDEN', 'SKIP_SAVE'})
    orig_location: bpy.props.FloatVectorProperty(size=3, options={'HIDDEN', 'SKIP_SAVE'})
    rect_valid: bpy.props.BoolProperty(default=False, options={'HIDDEN', 'SKIP_SAVE'})

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return context.mode == 'OBJECT' and obj is not None and obj.type == 'MESH'

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        column = layout.column()
        column.prop(self, "channel")
        if self.channel == 'DISTANCE':
            column.prop(self, "background")
        column.prop(self, "smoothing")
        column.prop(self, "cutoff")
        layout.separator()
        column = layout.column()
        column.prop(self, "pixel_error")
        column.prop(self, "inset")
        column.prop(self, "min_size")
        column.prop(self, "ignore_inner")
        layout.separator()
        column = layout.column()
        column.prop(self, "origin")
        column.prop(self, "thickness")

    @staticmethod
    def _mesh_rect(obj):
        xs = [v.co.x for v in obj.data.vertices]
        ys = [v.co.y for v in obj.data.vertices]
        if (not xs or max(xs) - min(xs) < 1e-6
                or max(ys) - min(ys) < 1e-6):
            return (-0.5, 0.5, -0.5, 0.5)
        return (min(xs), max(xs), min(ys), max(ys))

    @staticmethod
    def _read_pixels(image, np):
        width, height = image.size
        channels = image.channels
        pixels = np.empty(width * height * channels, dtype=np.float32)
        image.pixels.foreach_get(pixels)
        return pixels.reshape(height, width, channels), channels

    def _build_mask(self, px, channels, np):
        """Foreground weight per pixel, 0..1. None if it cannot be built."""
        if self.channel == 'ALPHA':
            return px[:, :, 3].copy() if channels >= 4 else None
        if channels >= 3:
            rgb = px[:, :, :3]
        else:
            rgb = np.repeat(px[:, :, :1], 3, axis=2)
        background = np.array(self.background[:], dtype=np.float32)
        mask = np.sqrt(((rgb - background) ** 2).sum(axis=2)) / 1.7320508
        if channels >= 4:
            mask = mask * px[:, :, 3]   # transparent is background too
        return mask

    @staticmethod
    def _border_colour(px, channels, np):
        """Median colour of the image's outer ring - the likely background."""
        if channels < 3:
            return None
        border = np.concatenate((px[0, :, :3], px[-1, :, :3],
                                 px[:, 0, :3], px[:, -1, :3]))
        return tuple(float(v) for v in np.median(border, axis=0))

    @staticmethod
    def _otsu(mask, np):
        """Threshold that best splits the mask into two groups.

        A fixed 0.5 was a trap: pastel colours sit around 0.45 distance
        from white on this scale, so leaves came out riddled with holes
        while saturated shapes cut cleanly.
        """
        hist, _ = np.histogram(mask, bins=64, range=(0.0, 1.0))
        total = int(hist.sum())
        if total == 0:
            return None
        centers = (np.arange(64) + 0.5) / 64.0
        w0 = np.cumsum(hist)
        w1 = total - w0
        sum0 = np.cumsum(hist * centers)
        sum_all = float((hist * centers).sum())
        valid = (w0 > 0) & (w1 > 0)
        if not valid.any():
            return None
        mean0 = sum0 / np.maximum(w0, 1)
        mean1 = (sum_all - sum0) / np.maximum(w1, 1)
        between = w0 * w1 * (mean0 - mean1) ** 2
        between[~valid] = -1.0
        # Cleanly separated masks make a flat plateau of best splits;
        # argmax alone would take its left edge, hugging the background.
        # The middle of the plateau is the robust choice.
        best = float(between.max())
        plateau = np.nonzero(between >= best - abs(best) * 1e-9)[0]
        threshold = float(centers[int((plateau[0] + plateau[-1]) // 2)])
        return min(max(threshold, 0.1), 0.7)

    def invoke(self, context, event):
        obj = context.active_object
        self.rect = self._mesh_rect(obj)
        self.orig_location = obj.location[:]
        self.rect_valid = True

        try:
            import numpy as np
        except ImportError:
            np = None

        # Clipboard images are usually opaque, so alpha would select the
        # whole plane. Fall back to colour keying: reuse the colour Key Out
        # Background picked if it ran on this object, otherwise guess the
        # background from the image border. Then let Otsu pick the cutoff -
        # a per-image threshold instead of a one-size-fits-none 0.5.
        image = hp_find_object_image(obj)
        if image is not None and np is not None and min(image.size) >= 2:
            px, channels = self._read_pixels(image, np)
            if channels >= 4 and hp_image_has_transparency(image):
                self.channel = 'ALPHA'
            else:
                self.channel = 'DISTANCE'
                key_colour = hp_find_key_colour(obj)
                if key_colour is not None:
                    self.background = key_colour
                else:
                    guess = self._border_colour(px, channels, np)
                    if guess is not None:
                        self.background = guess
            mask = self._build_mask(px, channels, np)
            if mask is not None:
                cutoff = self._otsu(mask, np)
                if cutoff is not None:
                    self.cutoff = cutoff
                    print("[HEAVYPOLY] cutout auto cutoff %.2f" % cutoff)
        return self.execute(context)

    def execute(self, context):
        try:
            import numpy as np
        except ImportError:
            self.report({'ERROR'}, "This Blender build has no numpy.")
            return {'CANCELLED'}

        obj = context.active_object
        image = hp_find_object_image(obj)
        if image is None:
            self.report({'WARNING'}, "No image texture on the object's materials.")
            return {'CANCELLED'}

        width, height = image.size
        if width < 2 or height < 2:
            self.report({'WARNING'}, "Image has no pixels to trace.")
            return {'CANCELLED'}

        channels = image.channels
        if self.channel == 'ALPHA' and channels < 4:
            self.report({'WARNING'},
                        "Image has no alpha channel - switch Channel to Key Colour.")
            return {'CANCELLED'}

        pixels, channels = self._read_pixels(image, np)
        mask = self._build_mask(pixels, channels, np)
        if mask is None:
            self.report({'WARNING'},
                        "Image has no alpha channel - switch Channel to Key Colour.")
            return {'CANCELLED'}

        for _ in range(self.smoothing):
            padded = np.pad(mask, 1, mode='edge')
            mask = (padded[:-2, :-2] + padded[:-2, 1:-1] + padded[:-2, 2:]
                    + padded[1:-1, :-2] + padded[1:-1, 1:-1] + padded[1:-1, 2:]
                    + padded[2:, :-2] + padded[2:, 1:-1] + padded[2:, 2:]) / 9.0

        binary = mask >= max(self.cutoff, 1e-4)
        if not binary.any():
            self.report({'WARNING'}, "Everything is background - lower Cutoff "
                                     "or check the Channel setting.")
            return {'CANCELLED'}

        # Inset: erode the mask so the outline sits inside the fringe.
        for _ in range(int(round(self.inset))):
            padded = np.pad(binary, 1, mode='constant', constant_values=False)
            binary = (padded[:-2, :-2] & padded[:-2, 1:-1] & padded[:-2, 2:]
                      & padded[1:-1, :-2] & padded[1:-1, 1:-1] & padded[1:-1, 2:]
                      & padded[2:, :-2] & padded[2:, 1:-1] & padded[2:, 2:])
        if not binary.any():
            self.report({'WARNING'}, "Inset removed everything - lower it.")
            return {'CANCELLED'}

        loops = hp_trace_mask_loops(binary)
        if not loops:
            self.report({'WARNING'}, "Could not trace an outline.")
            return {'CANCELLED'}

        islands = holes = 0
        kept = []
        min_area = self.min_size * self.min_size
        for loop in loops:
            area = _hp_loop_area(loop)
            if abs(area) < min_area:
                continue   # speck island or pinhole: not worth geometry
            if area > 0.0:
                islands += 1
            else:
                if self.ignore_inner:
                    continue
                holes += 1
            simplified = hp_simplify_loop(loop, self.pixel_error)
            if len(simplified) >= 3:
                kept.append(simplified)

        if not kept:
            self.report({'WARNING'}, "Outline vanished - lower Pixel Error.")
            return {'CANCELLED'}

        if not self.rect_valid:
            self.rect = self._mesh_rect(obj)
            self.orig_location = obj.location[:]
            self.rect_valid = True
        x0, x1, y0, y1 = self.rect

        bm = bmesh.new()
        uv_of = {}   # UVs come from the pixel grid, recorded at creation
        for points in kept:
            verts = []
            for px, py in points:
                vert = bm.verts.new((x0 + (px / width) * (x1 - x0),
                                     y0 + (py / height) * (y1 - y0), 0.0))
                uv_of[vert] = (px / width, py / height)
                verts.append(vert)
            for i in range(len(verts)):
                bm.edges.new((verts[i], verts[(i + 1) % len(verts)]))

        bmesh.ops.triangle_fill(bm, use_beauty=True, use_dissolve=False,
                                edges=bm.edges[:],
                                normal=Vector((0.0, 0.0, 1.0)))
        if not bm.faces:
            bm.free()
            self.report({'WARNING'}, "Fill failed - try raising Pixel Error "
                                     "or Smoothing.")
            return {'CANCELLED'}

        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
        if sum(face.normal.z for face in bm.faces) < 0.0:
            bmesh.ops.reverse_faces(bm, faces=bm.faces[:])

        span_x = (x1 - x0) or 1.0
        span_y = (y1 - y0) or 1.0
        uv_layer = bm.loops.layers.uv.new("UVMap")
        for face in bm.faces:
            for face_loop in face.loops:
                uv = uv_of.get(face_loop.vert)
                if uv is None:   # a vert the fill created; map from position
                    co = face_loop.vert.co
                    uv = ((co.x - x0) / span_x, (co.y - y0) / span_y)
                face_loop[uv_layer].uv = uv

        # Origin: shift the geometry and move the object the opposite way,
        # so nothing appears to move in the viewport. Absolute, not
        # incremental - orig_location was captured on invoke, so dragging
        # the redo sliders cannot make the object creep.
        pivot = None
        if self.origin != 'KEEP':
            xs = [v.co.x for v in bm.verts]
            ys = [v.co.y for v in bm.verts]
            if self.origin == 'BOTTOM':
                # Where the mesh actually touches the bottom, not the middle
                # of the bounding box - a curved stem would otherwise leave
                # the origin floating in the air beside it.
                min_y = min(ys)
                band = (max(ys) - min_y) * 0.02 + 1e-6
                low_xs = [v.co.x for v in bm.verts if v.co.y <= min_y + band]
                pivot = Vector((sum(low_xs) / len(low_xs), min_y, 0.0))
            else:
                pivot = Vector(((min(xs) + max(xs)) / 2.0,
                                (min(ys) + max(ys)) / 2.0, 0.0))
            for vert in bm.verts:
                vert.co -= pivot

        bm.to_mesh(obj.data)
        bm.free()
        obj.data.update()

        if pivot is not None:
            obj.location = (Vector(self.orig_location)
                            + obj.matrix_world.to_3x3() @ pivot)
        else:
            obj.location = self.orig_location

        # Thickness: one Solidify modifier of our own, updated in place so
        # slider drags never stack copies.
        modifier = obj.modifiers.get("HP_Cutout_Solidify")
        if self.thickness > 0.0:
            if modifier is None or modifier.type != 'SOLIDIFY':
                modifier = obj.modifiers.new("HP_Cutout_Solidify", 'SOLIDIFY')
            modifier.thickness = self.thickness
            modifier.offset = 0.0
            modifier.use_even_offset = True
        elif modifier is not None:
            obj.modifiers.remove(modifier)

        self.report({'INFO'}, "Cut out %d island(s), %d hole(s), %d verts."
                    % (islands, holes, len(obj.data.vertices)))
        return {'FINISHED'}


class HP_OT_separate_islands(bpy.types.Operator):
    """Split the active mesh into one object per connected piece"""
    bl_idname = "object.hp_separate_islands"
    bl_label = "Separate Islands"
    bl_options = {'REGISTER', 'UNDO'}

    origin: bpy.props.EnumProperty(
        name="Origin",
        description="Where each piece's origin goes",
        items=[
            ('BOTTOM', "Bottom",
             "Bottom middle of each piece - for things that stand on the ground"),
            ('CENTER', "Center", "Middle of each piece"),
            ('KEEP', "Keep", "Leave the origins where they are"),
        ],
        default='BOTTOM',
    )

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return context.mode == 'OBJECT' and obj is not None and obj.type == 'MESH'

    @staticmethod
    def _set_origin(piece, mode):
        """Move the origin without moving the piece on screen.

        Bottom and centre are taken in world space, so a plane stood up by
        rotation still gets its origin at the visually lowest point.
        """
        matrix = piece.matrix_world
        coords = [matrix @ v.co for v in piece.data.vertices]
        xs = [c.x for c in coords]
        ys = [c.y for c in coords]
        zs = [c.z for c in coords]
        if mode == 'BOTTOM':
            # Under the lowest bit of geometry, not the bounding-box middle
            # - a curved stem should get its origin at the stem tip.
            min_z = min(zs)
            band = (max(zs) - min_z) * 0.02 + 1e-6
            low = [c for c in coords if c.z <= min_z + band]
            target = Vector((sum(c.x for c in low) / len(low),
                             sum(c.y for c in low) / len(low),
                             min_z))
        else:
            target = Vector(((min(xs) + max(xs)) / 2.0,
                             (min(ys) + max(ys)) / 2.0,
                             (min(zs) + max(zs)) / 2.0))
        local = matrix.inverted() @ target
        piece.data.transform(Matrix.Translation(-local))
        piece.matrix_world = matrix @ Matrix.Translation(local)
        piece.data.update()

    def execute(self, context):
        before = len(context.scene.objects)
        bpy.ops.object.mode_set(mode='EDIT')
        try:
            bpy.ops.mesh.separate(type='LOOSE')
        except Exception as e:
            print("[HEAVYPOLY] separate failed: %r" % (e,))
        bpy.ops.object.mode_set(mode='OBJECT')
        made = len(context.scene.objects) - before

        # Even when nothing separated (a single island), still place the
        # origin - and keep doing it on redo when the pieces already exist.
        if self.origin != 'KEEP':
            for piece in context.selected_objects:
                if piece.type == 'MESH' and piece.data.vertices:
                    self._set_origin(piece, self.origin)

        if made:
            self.report({'INFO'}, "Separated into %d objects." % (made + 1))
        else:
            self.report({'INFO'}, "Only one piece - origin set, nothing to "
                                  "separate.")
        return {'FINISHED'}


classes = (
    HP_OT_cutout_mesh,
    HP_OT_separate_islands,
    HP_OT_key_out_background,
    HP_OT_paste_image_plane,
    HP_OT_toggle_symmetry,
    HP_OT_SaveWithoutPrompt,
    HP_OT_RevertWithoutPrompt,
    HP_OT_DeleteWithoutPrompt,
    HP_OT_duplicate_move,
    HP_OT_Subdivision_Toggle,
    HP_OT_Smart_Delete,
    HP_OT_SmartShadeSmooth,
    HP_OT_SeparateAndSelect,
    HP_OT_PushAndSlide,
    HP_OT_SmartBevel,
    HP_OT_smart_snap_cursor,
    HP_OT_smart_snap_origin,
    HP_OT_smart_snap_origin_collection,
    HP_OT_extrude,
    HP_OT_loopcut,
    HP_OT_SmartScale,
    HP_OT_unhide,
    HP_OT_SetCollectionCenter,
    HP_TranslateModalOperator,
    OBJECT_OT_set_camera_off_wire,
    OBJECT_OT_set_camera_on_textured,
    OBJECT_OT_select_camera_hidden,

)
#register, unregister = bpy.utils.register_classes_factory(classes)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.VIEW3D_MT_object_context_menu.append(draw_func)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    bpy.types.VIEW3D_MT_object_context_menu.remove(draw_func)

if __name__ == "__main__":
    register()