bl_info = {
    "name": "Heavypoly Hotkeys",
    "description": "Hotkeys",
    "author": "Vaughan Ling",
    "version": (0, 2, 0),
    "blender": (5, 2, 0),
    "location": "",
    "warning": "",
    "wiki_url": "",
    "category": "Hotkeys"
    }

import bpy
import os

def kmi_props_setattr(kmi_props, attr, value):
    try:
        setattr(kmi_props, attr, value)
    except AttributeError:
        print("Warning: property '%s' not found in keymap item '%s'" %
              (attr, kmi_props.__class__.__name__))
    except Exception as e:
        print("Warning: %r" % e)

def Keymap_Heavypoly():

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    k_viewfit = 'MIDDLEMOUSE'
    k_manip = 'LEFTMOUSE'
    k_cursor = 'RIGHTMOUSE'
    k_nav = 'MIDDLEMOUSE'
    k_menu = 'SPACE'
    k_select = 'LEFTMOUSE'


    def Global_Keys():

        kmi = km.keymap_items.new("screen.userpref_show","TAB","PRESS", ctrl=True)
        # kmi = km.keymap_items.new("view3d.smart_scale","S","PRESS")
        kmi = km.keymap_items.new("wm.window_fullscreen_toggle","F11","PRESS")
        kmi = km.keymap_items.new('screen.animation_play', 'PERIOD', 'PRESS')
        #kmi = km.keymap_items.new("view3d.hp_duplicate_move","D","PRESS", shift=True)
#        kmi = km.keymap_items.new("wm.call_menu_pie","SPACE","PRESS", shift=True).properties.name='HP_MT_popup_uber'
#        kmi = km.keymap_items.new("wm.call_menu_pie","Z","PRESS").properties.name='HP_MT_popup_uber'
        kmi = km.keymap_items.new("popup.hp_properties", 'P',"PRESS", ctrl=True, shift=True)
        kmi = km.keymap_items.new("popup.hp_materials", 'V',"PRESS", shift=True)
    # kmi = km.keymap_items.new('gpencil.blank_frame_add', 'B', 'PRESS', key_modifier='FOUR')
# "ACCENT_GRAVE"
#Window
    km = kc.keymaps.new('Window', space_type='EMPTY', region_type='WINDOW', modal=False)
    Global_Keys()
    kmi = km.keymap_items.new('object.hide_viewport', 'H', 'PRESS')
    kmi = km.keymap_items.new('wm.save_homefile', 'U', 'PRESS', ctrl=True)
    kmi = km.keymap_items.new('transform.translate', 'SPACE', 'PRESS')
    #kmi = km.keymap_items.new('object.modal_translate', 'SPACE', 'PRESS')

    kmi = km.keymap_items.new('view3d.smart_delete', 'X', 'PRESS')
    kmi = km.keymap_items.new('mesh.dissolve_mode', 'X', 'PRESS',ctrl=True)
#kmi = km.keymap_items.new('transform.resize', 'SPACE', 'PRESS', alt=True)
    kmi = km.keymap_items.new('transform.rotate', 'C', 'PRESS')
    kmi = km.keymap_items.new("wm.call_menu_pie", k_menu,"PRESS",ctrl=True ,shift=True, alt=True).properties.name="HP_MT_pie_areas"
    kmi = km.keymap_items.new("wm.call_menu_pie", 'TAB',"PRESS",shift=True).properties.name="HP_MT_pie_areas"
    kmi = km.keymap_items.new("wm.revert_without_prompt","N","PRESS", alt=True)
    kmi = km.keymap_items.new("screen.redo_last","D","PRESS")
    kmi = km.keymap_items.new('wm.console_toggle', 'TAB', 'PRESS', ctrl=True, shift=True)

    kmi = km.keymap_items.new("wm.call_menu_pie","S","PRESS", ctrl=True).properties.name="HP_MT_pie_save"
    kmi = km.keymap_items.new("wm.call_menu_pie","S","PRESS", ctrl=True, shift=True).properties.name="HP_MT_pie_importexport"
    kmi = km.keymap_items.new('script.reload', 'U', 'PRESS', shift=True)
    kmi = km.keymap_items.new("screen.repeat_last","THREE","PRESS", ctrl=True, shift=True)
    kmi = km.keymap_items.new("ed.undo","TWO","PRESS", ctrl=True, shift=True)
    kmi = km.keymap_items.new('screen.frame_jump', 'PERIOD', 'PRESS', shift=True)



# Map Image
    km = kc.keymaps.new('Image', space_type='IMAGE_EDITOR', region_type='WINDOW', modal=False)
    Global_Keys()
    kmi = km.keymap_items.new('image.view_all', k_viewfit, 'PRESS', ctrl=True, shift=True)
    kmi_props_setattr(kmi.properties, 'fit_view', True)
    kmi = km.keymap_items.new('image.view_pan', k_nav, 'PRESS', shift=True)
    kmi = km.keymap_items.new('image.view_zoom', k_nav, 'PRESS', ctrl=True)

# Map Node Editor
    km = kc.keymaps.new('Node Editor', space_type='NODE_EDITOR', region_type='WINDOW', modal=False)
    kmi = km.keymap_items.new('node.view_selected', k_viewfit, 'PRESS', ctrl=True, shift=True)
# Map View2D
    km = kc.keymaps.new('View2D', space_type='EMPTY', region_type='WINDOW', modal=False)

# Map Animation
    km = kc.keymaps.new('Animation', space_type='EMPTY', region_type='WINDOW', modal=False)
    kmi = km.keymap_items.new('anim.change_frame', k_nav, 'PRESS')
    kmi = km.keymap_items.new('anim.change_frame', k_select, 'PRESS', alt = True)
    kmi = km.keymap_items.new('action.select_box', 'LEFTMOUSE', 'CLICK_DRAG', shift=True)
    kmi_props_setattr(kmi.properties, 'mode', 'ADD')
    kmi = km.keymap_items.new('action.select_box', 'LEFTMOUSE', 'CLICK_DRAG', ctrl=True)
    kmi_props_setattr(kmi.properties, 'mode', 'SUB')
    kmi = km.keymap_items.new('action.select_box', 'LEFTMOUSE', 'CLICK_DRAG')
    kmi_props_setattr(kmi.properties, 'mode', 'SET')
# Map DOPESHEET_EDITOR
    km = kc.keymaps.new('Dopesheet', space_type='DOPESHEET_EDITOR', region_type='WINDOW', modal=False)
    Global_Keys()
    #Dopesheet transform fix
    kmi = km.keymap_items.new('transform.transform', 'SPACE', 'PRESS', repeat=True)
    kmi.properties.mode = 'TIME_TRANSLATE'
    print(f"Created keymap: {km.name}")
    print(f"Added keymap item: {kmi.idname} ({kmi.type})")


    kmi = km.keymap_items.new('time.cursor_set', k_select, 'PRESS', alt = True)
    kmi = km.keymap_items.new('time.start_frame_set', 'S', 'PRESS')
    kmi = km.keymap_items.new('time.end_frame_set', 'E', 'PRESS')
    kmi = km.keymap_items.new('time.view_all', k_viewfit, 'PRESS', ctrl=True, shift=True)

# Map Graph Editor
    km = kc.keymaps.new('Graph Editor', space_type='GRAPH_EDITOR', region_type='WINDOW', modal=False)
    Global_Keys()
    kmi = km.keymap_items.new('graph.view_selected', k_viewfit, 'PRESS', ctrl=True, shift=True)
    kmi = km.keymap_items.new('graph.cursor_set', k_select, 'PRESS', alt = True)
    kmi = km.keymap_items.new('graph.select_box', 'LEFTMOUSE', 'CLICK_DRAG', shift=True)
    kmi_props_setattr(kmi.properties, 'mode', 'ADD')
    kmi = km.keymap_items.new('graph.select_box', 'LEFTMOUSE', 'CLICK_DRAG', ctrl=True)
    kmi_props_setattr(kmi.properties, 'mode', 'SUB')
    kmi = km.keymap_items.new('graph.select_box', 'LEFTMOUSE', 'CLICK_DRAG')
    kmi_props_setattr(kmi.properties, 'mode', 'SET')
# Map UV Editor
    km = kc.keymaps.new('UV Editor', space_type='EMPTY', region_type='WINDOW', modal=False)
    Global_Keys()
    kmi = km.keymap_items.new('image.view_selected', k_viewfit, 'PRESS', ctrl=True, shift=True)
    kmi = km.keymap_items.new("wm.call_menu_pie", k_menu,"PRESS",ctrl=True, alt=True).properties.name="HP_MT_pie_rotate90"
# Map Mask Editing
#    km = kc.keymaps.new('Mask Editing', space_type='EMPTY', region_type='WINDOW', modal=False)
#3D View
    km = kc.keymaps.new('3D View', space_type='VIEW_3D', region_type='WINDOW', modal=False)
    Global_Keys()
    kmi = km.keymap_items.new("view3d.smart_scale","S","PRESS")
    kmi = km.keymap_items.new("view3d.hp_draw","D","PRESS", ctrl=True)
#    kmi = km.keymap_items.new('view3d.render_border', 'B', 'PRESS', shift=True)
#    kmi = km.keymap_items.new('view3d.clear_render_border', 'B', 'PRESS', shift=True, ctrl=True)
    kmi = km.keymap_items.new('mesh.hp_extrude', 'SPACE', 'PRESS', shift=True)

    kmi = km.keymap_items.new('view3d.render_border', 'B', 'PRESS',shift=True, ctrl=True)
    kmi = km.keymap_items.new("wm.call_menu_pie", k_menu,"PRESS",ctrl=True ,shift=True, alt=True).properties.name="HP_MT_pie_areas"
    kmi = km.keymap_items.new('view3d.view_selected', k_nav, 'PRESS', ctrl=True, shift=True)
    kmi = km.keymap_items.new('view3d.move', k_nav, 'PRESS', shift=True)
    kmi = km.keymap_items.new('view3d.zoom', k_nav, 'PRESS', ctrl=True)
    kmi = km.keymap_items.new('view3d.rotate', k_nav, 'PRESS')
    kmi = km.keymap_items.new('view3d.manipulator', k_manip, 'PRESS')
    kmi = km.keymap_items.new("wm.call_menu_pie", k_menu,"PRESS",ctrl=True).properties.name="HP_MT_pie_select"
    kmi = km.keymap_items.new("wm.call_menu_pie", k_menu, 'PRESS',ctrl=True, alt=True).properties.name="HP_MT_pie_rotate90"
    kmi = km.keymap_items.new("wm.call_menu_pie", 'V', 'PRESS').properties.name="HP_MT_pie_view"
    kmi = km.keymap_items.new('wm.call_menu_pie', k_menu,'PRESS',ctrl=True, shift=True).properties.name="HP_MT_pie_pivots"
    kmi = km.keymap_items.new('object.hp_paste_image_plane', 'V', 'PRESS', ctrl=True, shift=True)
    kmi = km.keymap_items.new("wm.call_menu_pie","Z","PRESS").properties.name="HP_MT_pie_shading"
    kmi = km.keymap_items.new("wm.call_menu_pie","D","PRESS",ctrl=True, shift=True).properties.name="HP_MT_pie_specials"
    kmi = km.keymap_items.new("wm.call_menu_pie","ONE","PRESS").properties.name="HP_MT_pie_modifiers"
    kmi = km.keymap_items.new("wm.call_menu_pie","X","PRESS",shift=True).properties.name="HP_MT_pie_symmetry"
    kmi = km.keymap_items.new('wm.call_menu_pie', 'B', 'PRESS',ctrl=True).properties.name="HP_MT_pie_boolean"
    kmi = km.keymap_items.new("screen.repeat_last","Z","PRESS",ctrl=True, alt=True)
    kmi = km.keymap_items.new("screen.repeat_last","WHEELINMOUSE","PRESS",ctrl=True, shift=True, alt=True)
    kmi = km.keymap_items.new("ed.undo","WHEELOUTMOUSE","PRESS",ctrl=True, shift=True, alt=True)
    kmi = km.keymap_items.new("view3d.screencast_keys","U","PRESS",alt=True)
    kmi = km.keymap_items.new('view3d.select_lasso', 'LEFTMOUSE', 'CLICK_DRAG', shift=True, ctrl=True)
    kmi = km.keymap_items.new('view3d.select_box', 'LEFTMOUSE', 'CLICK_DRAG',ctrl=True).properties.mode='SUB'
    kmi = km.keymap_items.new('view3d.select_box', 'LEFTMOUSE', 'CLICK_DRAG',shift=True).properties.mode='ADD'
    kmi = km.keymap_items.new('view3d.select_box', 'LEFTMOUSE', 'CLICK_DRAG').properties.mode='SET'
    kmi = km.keymap_items.new("wm.search_menu","FIVE","PRESS")
    kmi = km.keymap_items.new("view3d.subdivision_toggle","TAB","PRESS")
    # kmi = km.keymap_items.new("view3d.smart_snap_cursor","RIGHTMOUSE","PRESS",ctrl=True)
    kmi = km.keymap_items.new("view3d.smart_snap_origin","RIGHTMOUSE","PRESS",ctrl=True, shift=True)
    kmi = km.keymap_items.new("view3d.smart_snap_cursor","RIGHTMOUSE","PRESS",ctrl=True)
    kmi = km.keymap_items.new("view3d.smart_snap_origin_collection","RIGHTMOUSE","PRESS",ctrl=True, shift=True, alt=True)


#Mesh
    km = kc.keymaps.new(name='Mesh')
    Global_Keys()
    # Double move operator
    #kmi = km.keymap_items.new("wm.modal_move_operator", 'SPACE', 'PRESS')
    #kmi = km.keymap_items.new('wm.toolbar', 'SPACE', 'PRESS')
    kmi = km.keymap_items.new('view3d.render_border', 'Z', 'PRESS', shift=True)
    # kmi = km.keymap_items.new('view3d.clear_render_border', 'Z', 'PRESS', shift=True, ctrl=True)
    kmi = km.keymap_items.new("mesh.dupli_extrude_cursor", 'E', 'PRESS')
    kmi = km.keymap_items.new("transform.edge_bevelweight", 'E', 'PRESS', ctrl=True, shift=True)
    #kmi = km.keymap_items.new('transform.translate', 'LEFTMOUSE', 'CLICK_DRAG')
    kmi = km.keymap_items.new('view3d.select_through_border', 'LEFTMOUSE', 'CLICK_DRAG')
    kmi = km.keymap_items.new('view3d.select_through_border_add', 'LEFTMOUSE', 'CLICK_DRAG',shift=True)
    kmi = km.keymap_items.new('view3d.select_through_border_sub', 'LEFTMOUSE', 'CLICK_DRAG',ctrl=True)
    kmi = km.keymap_items.new("wm.call_menu_pie","A","PRESS", shift=True).properties.name="HP_MT_pie_add"
    kmi = km.keymap_items.new("wm.call_menu","W","PRESS").properties.name="VIEW3D_MT_edit_mesh_context_menu"
    kmi = km.keymap_items.new("screen.userpref_show","TAB","PRESS", ctrl=True)
    kmi = km.keymap_items.new("view3d.subdivision_toggle","TAB","PRESS")
#    kmi = km.keymap_items.new('mesh.select_all', k_select, 'CLICK', ctrl=True)
#    kmi_props_setattr(kmi.properties, 'action', 'INVERT')
    kmi = km.keymap_items.new('mesh.shortest_path_pick', 'LEFTMOUSE', 'CLICK',ctrl=True, shift=True).properties.use_fill=True
    kmi = km.keymap_items.new('mesh.select_linked', k_select, 'DOUBLE_CLICK')
    kmi_props_setattr(kmi.properties, 'delimit', {'SEAM'})
    kmi = km.keymap_items.new('mesh.select_linked', k_select, 'DOUBLE_CLICK', shift=True)
    kmi_props_setattr(kmi.properties, 'delimit', {'SEAM'})
    kmi = km.keymap_items.new('mesh.select_more', 'WHEELINMOUSE', 'PRESS',ctrl=True, shift=True)
    kmi = km.keymap_items.new('mesh.select_less', 'WHEELOUTMOUSE', 'PRESS',ctrl=True, shift=True)
    kmi = km.keymap_items.new('mesh.select_more', 'Z', 'PRESS',alt=True)
    kmi = km.keymap_items.new('mesh.select_next_item', 'WHEELINMOUSE', 'PRESS', shift=True)
    kmi = km.keymap_items.new('mesh.select_next_item', 'Z', 'PRESS', shift=True)
    kmi = km.keymap_items.new('mesh.select_prev_item', 'WHEELOUTMOUSE', 'PRESS', shift=True)
    kmi = km.keymap_items.new('mesh.edgering_select', k_select, 'DOUBLE_CLICK', alt=True).properties.extend = False
    kmi = km.keymap_items.new('mesh.loop_multi_select', k_select, 'DOUBLE_CLICK', alt=True, shift=True)
    kmi = km.keymap_items.new('mesh.loop_select', k_select, 'PRESS', alt=True, shift=True).properties.extend = True
    kmi = km.keymap_items.new('mesh.loop_select', k_select, 'PRESS', alt=True).properties.extend = False
    kmi = km.keymap_items.new('mesh.normals_make_consistent', 'N', 'PRESS', ctrl=True).properties.inside = False
    kmi = km.keymap_items.new("wm.call_menu_pie","FOUR","PRESS").properties.name="GPENCIL_PIE_tool_palette"
    kmi = km.keymap_items.new("mesh.select_prev_item","TWO","PRESS")
    kmi = km.keymap_items.new("mesh.select_next_item","THREE","PRESS")
    kmi = km.keymap_items.new("mesh.select_less","TWO","PRESS", ctrl=True)
    kmi = km.keymap_items.new("mesh.select_more","THREE","PRESS", ctrl=True)
    kmi = km.keymap_items.new("mesh.inset", "SPACE", "PRESS", alt=True)
    kmi = km.keymap_items.new("mesh.push_and_slide","G","PRESS", shift=True)
#    kmi_props_setattr(kmi.properties, 'use_even_offset', True)
    kmi = km.keymap_items.new('object.separate_and_select', 'P', 'PRESS')
    kmi = km.keymap_items.new('mesh.bridge_edge_loops', 'B', 'PRESS', shift=True)
    kmi = km.keymap_items.new('mesh.bridge_edge_loops', 'B', 'PRESS', ctrl=True, shift=True).properties.number_cuts = 12
    kmi = km.keymap_items.new('transform.edge_bevelweight','B', 'PRESS', alt=True).properties.value = 1
    kmi = km.keymap_items.new('view3d.smart_bevel','B', 'PRESS')
    kmi = km.keymap_items.new('mesh.merge', 'J', 'PRESS', ctrl=True)
    kmi_props_setattr(kmi.properties, 'type', 'LAST')
    kmi = km.keymap_items.new('mesh.hp_unhide', 'H', 'PRESS', ctrl=True, shift=True)
#Grease Pencil
    km = kc.keymaps.new('Grease Pencil', space_type='EMPTY', region_type='WINDOW', modal=False)
    Global_Keys()
    # gpencil.* was replaced by grease_pencil.* in 4.3; see Keymap_Heavypoly_GP()
    # kmi = km.keymap_items.new('gpencil.select_box', k_select,'CLICK_DRAG')
    # kmi_props_setattr(kmi.properties, 'mode', 'SET')
    # kmi_props_setattr(kmi.properties, 'wait_for_input',False)
    # kmi = km.keymap_items.new('gpencil.select_box', k_select,'CLICK_DRAG', ctrl=True)
    # kmi_props_setattr(kmi.properties, 'mode', 'SUB')
    # kmi_props_setattr(kmi.properties, 'wait_for_input',False)
    # kmi = km.keymap_items.new('gpencil.select_box', k_select, 'CLICK_DRAG', shift=True)
    # kmi_props_setattr(kmi.properties, 'mode', 'ADD')
    # kmi_props_setattr(kmi.properties, 'wait_for_input',False)
#Image Paint
    km = kc.keymaps.new(name='Image Paint')
    kmi = km.keymap_items.new('paint.sample_color', 'S', 'PRESS')
#Object Mode
    km = kc.keymaps.new(name='Object Mode')
    Global_Keys()
    # kmi = km.keymap_items.new('view3d.smart_bevel','B', 'PRESS')
    #kmi = km.keymap_items.new('object.select_all', k_select, 'CLICK_DRAG')
    #kmi_props_setattr(kmi.properties, 'action', 'DESELECT')
#    kmi = km.keymap_items.new('object.select_all', k_select, 'CLICK', ctrl=True)
#    kmi_props_setattr(kmi.properties, 'action', 'INVERT')
    kmi = km.keymap_items.new('object.hide_view_clear', 'H', 'PRESS', ctrl=True, shift=True)

#Sculpt Mode
    km = kc.keymaps.new(name='Sculpt')
    Global_Keys()
    kmi = km.keymap_items.new("wm.call_menu_pie", 'V', 'PRESS').properties.name="HP_MT_pie_view"

# Map Curve
    km = kc.keymaps.new('Curve', space_type='EMPTY', region_type='WINDOW', modal=False)
    kmi = km.keymap_items.new('curve.subdivide', 'R', 'PRESS', ctrl=True)
    Global_Keys()
    kmi = km.keymap_items.new('curve.select_linked', k_select, 'DOUBLE_CLICK', shift=True)
    kmi = km.keymap_items.new('curve.select_linked_pick', k_select, 'DOUBLE_CLICK')
    kmi = km.keymap_items.new('curve.reveal', 'H', 'PRESS', ctrl=True, shift=True)
    kmi = km.keymap_items.new('curve.shortest_path_pick', k_select, 'PRESS', ctrl=True, shift=True)
    kmi = km.keymap_items.new('curve.draw', 'LEFTMOUSE', 'PRESS', alt=True)

# Outliner
    km = kc.keymaps.new('Outliner', space_type='OUTLINER', region_type='WINDOW', modal=False)
    kmi = km.keymap_items.new('outliner.show_active', k_nav, 'PRESS', ctrl=True, shift=True)
    Global_Keys()

    kmi = km.keymap_items.new('wm.delete_without_prompt', 'X', 'PRESS')

# Lattice
    km = kc.keymaps.new(name='Lattice')
    Global_Keys()
    kmi = km.keymap_items.new('view3d.select_box', 'LEFTMOUSE', 'CLICK_DRAG', shift=False, ctrl=False)
    kmi = km.keymap_items.new('view3d.select_box', 'LEFTMOUSE', 'CLICK_DRAG', shift=True, ctrl=False)
    kmi_props_setattr(kmi.properties, 'mode', 'ADD')
    kmi = km.keymap_items.new('view3d.select_box', 'LEFTMOUSE', 'CLICK_DRAG', shift=False, ctrl=True)
    kmi_props_setattr(kmi.properties, 'mode', 'SUB')





# ---------------------------------------------------------------- 5.x additions

# Grease Pencil keymap names moved around in 4.3 (GPv3). Try every spelling.
# NOT "Grease Pencil" - that one is the annotation keymap and is live in the
# 3D View in every mode, so a double click registered there ate the mesh one.
GP_EDIT_KEYMAPS = (
    "Grease Pencil Edit Mode",
    "Grease Pencil Stroke Edit Mode",
)
GP_PAINT_KEYMAPS = (
    "Grease Pencil Paint Mode",
    "Grease Pencil Stroke Paint Mode",
)
GP_SCULPT_KEYMAPS = (
    "Grease Pencil Sculpt Mode",
    "Grease Pencil Stroke Sculpt Mode",
)
# Modes that object.transfer_mode can hop between.
TRANSFER_MODE_KEYMAPS = (
    "Sculpt",
    "Vertex Paint",
    "Weight Paint",
    "Image Paint",
) + GP_PAINT_KEYMAPS + GP_SCULPT_KEYMAPS


def _existing_keymap_names(candidates):
    """Return only the keymap names Blender actually ships in this version."""
    kc = bpy.context.window_manager.keyconfigs.get('Blender')
    if kc is None:
        return list(candidates)
    found = [name for name in candidates if kc.keymaps.get(name)]
    return found or [candidates[0]]


def Keymap_Heavypoly_GP():
    """Double click selects a whole stroke, the way it does on meshes."""
    kc = bpy.context.window_manager.keyconfigs.addon
    if kc is None:
        return
    for name in _existing_keymap_names(GP_EDIT_KEYMAPS):
        km = kc.keymaps.new(name, space_type='EMPTY', region_type='WINDOW', modal=False)
        kmi = km.keymap_items.new('grease_pencil.hp_select_linked_pick',
                                  'LEFTMOUSE', 'DOUBLE_CLICK')
        kmi_props_setattr(kmi.properties, 'extend', False)
        kmi = km.keymap_items.new('grease_pencil.hp_select_linked_pick',
                                  'LEFTMOUSE', 'DOUBLE_CLICK', shift=True)
        kmi_props_setattr(kmi.properties, 'extend', True)
        print("[HEAVYPOLY] GP double click select registered in '%s'" % name)


def Keymap_Heavypoly_TransferMode():
    """Alt+LMB hops to whatever object is under the cursor, keeping the mode."""
    kc = bpy.context.window_manager.keyconfigs.addon
    if kc is None:
        return
    if not hasattr(bpy.ops.object, "transfer_mode"):
        print("[HEAVYPOLY] object.transfer_mode not available - skipped")
        return
    for name in TRANSFER_MODE_KEYMAPS:
        try:
            km = kc.keymaps.new(name=name)
            km.keymap_items.new('object.transfer_mode', 'LEFTMOUSE', 'PRESS', alt=True)
        except Exception as e:
            print("[HEAVYPOLY] transfer_mode not bound in '%s': %r" % (name, e))



# Modes that expose a mirror / symmetry toggle.
SYMMETRY_KEYMAPS = (
    "Mesh",
    "Sculpt",
    "Vertex Paint",
    "Weight Paint",
    "Image Paint",
)


def Keymap_Heavypoly_Symmetry():
    """Ctrl+Shift+X / Y / Z toggles symmetry for whichever mode you're in."""
    kc = bpy.context.window_manager.keyconfigs.addon
    if kc is None:
        return
    for name in SYMMETRY_KEYMAPS:
        try:
            km = kc.keymaps.new(name=name)
        except Exception as e:
            print("[HEAVYPOLY] symmetry keymap '%s' failed: %r" % (name, e))
            continue
        for axis in ('X', 'Y', 'Z'):
            kmi = km.keymap_items.new('object.hp_toggle_symmetry', axis, 'PRESS',
                                      ctrl=True, shift=True)
            kmi_props_setattr(kmi.properties, 'axis', axis)



def disable_pie_kmi(km, menu_name, type, value, shift=False, ctrl=False,
                    alt=False, retries=10):
    """Disable a stock pie menu by the menu it opens.

    wm.call_menu_pie is used by both Blender and HEAVYPOLY, so matching on the
    operator alone would switch off our own pie as well.
    """
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.get('Blender')
    keymap = kc.keymaps.get(km) if kc else None
    if keymap is None:
        print("[HEAVYPOLY] keymap '%s' not found - skipped" % km)
        return

    for kmi in keymap.keymap_items:
        if kmi.idname != 'wm.call_menu_pie':
            continue
        if (kmi.type, kmi.value, kmi.shift, kmi.ctrl, kmi.alt) != (type, value, shift, ctrl, alt):
            continue
        if getattr(kmi.properties, 'name', None) != menu_name:
            continue
        kmi.active = False
        print("Disabled pie", menu_name)
        return

    if retries > 0:
        bpy.app.timers.register(
            lambda: disable_pie_kmi(km, menu_name, type, value, shift, ctrl,
                                    alt, retries - 1),
            first_interval=0.1)



def Keymap_Heavypoly_TransformModal(retries=20):
    """Space locks to Y while a transform is running.

    Move / Rotate / Scale share the Transform Modal Map, so one entry covers
    all three. X and Z are Blender defaults and left alone.

    Modal key-maps are rejected by the add-on keyconfig ("Modal key-maps not
    supported for add-on key-config"), so repurpose the stock Space = Confirm
    entry in the user keyconfig instead of adding a new one. Changing an
    existing item rather than appending keeps this reversible.
    """
    kc = bpy.context.window_manager.keyconfigs.user
    km = kc.keymaps.get('Transform Modal Map') if kc else None
    if km is None:
        if retries > 0:
            bpy.app.timers.register(
                lambda: Keymap_Heavypoly_TransformModal(retries - 1),
                first_interval=0.2)
        else:
            print("[HEAVYPOLY] Transform Modal Map not found")
        return

    for kmi in km.keymap_items:
        if kmi.type != 'SPACE' or kmi.value != 'PRESS':
            continue
        if kmi.propvalue == 'AXIS_Y':
            return          # already done
        if kmi.propvalue == 'CONFIRM':
            try:
                kmi.propvalue = 'AXIS_Y'
                kmi.active = True
                print("[HEAVYPOLY] Space = Y axis lock registered")
            except Exception as e:
                print("[HEAVYPOLY] could not repurpose Space: %r" % (e,))
            return

    print("[HEAVYPOLY] no Space entry in Transform Modal Map to repurpose")


def Keymap_Heavypoly_TransformModal_Restore():
    """Put Space back to Confirm when the add-on is switched off."""
    kc = bpy.context.window_manager.keyconfigs.user
    km = kc.keymaps.get('Transform Modal Map') if kc else None
    if km is None:
        return
    for kmi in km.keymap_items:
        if kmi.type == 'SPACE' and kmi.propvalue == 'AXIS_Y':
            try:
                kmi.propvalue = 'CONFIRM'
            except Exception:
                pass
            return


def disable_modal_kmi(km, propvalue, type, value, retries=10):
    """Switch off a stock entry in a modal keymap.

    Modal items are identified by propvalue rather than an operator name.
    """
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.get('Blender')
    keymap = kc.keymaps.get(km) if kc else None
    if keymap is None:
        print("[HEAVYPOLY] modal keymap '%s' not found - skipped" % km)
        return

    for kmi in keymap.keymap_items:
        if getattr(kmi, 'propvalue', None) != propvalue:
            continue
        if (kmi.type, kmi.value) != (type, value):
            continue
        kmi.active = False
        print("Disabled modal", propvalue)
        return

    if retries > 0:
        bpy.app.timers.register(
            lambda: disable_modal_kmi(km, propvalue, type, value, retries - 1),
            first_interval=0.1)


#Function to disable keymap confict
def disable_default_kmi(km=None, idname=None, retries=1):
    wm = bpy.context.window_manager

    if not (km and idname) or retries < 1:
        return

    # the default keyconfig
    kc = wm.keyconfigs.get('Blender')
    keymap = kc.keymaps.get(km) if kc else None
    if keymap is None:
        # Keymap names change between Blender versions - never abort register()
        print("[HEAVYPOLY] keymap '%s' not found - skipped" % km)
        return
    for kmi in keymap.keymap_items:
        if kmi.idname == idname:
            kmi.active = False
            print("Disabled", kmi.name)
            return

    # add some delay
    bpy.app.timers.register(
        lambda: disable_default_kmi(km, idname,retries - 1),
        first_interval=0.1)
    
def disable_specific_kmi(km=None, idname=None, type=None, value=None, shift=None, ctrl=None, alt=None,  retries=1):
    wm = bpy.context.window_manager
    if not (km and idname) or retries < 1:
        return
    # the default keyconfig
    kc = wm.keyconfigs.get('Blender')
    keymap = kc.keymaps.get(km) if kc else None
    if keymap is None:
        print("[HEAVYPOLY] keymap '%s' not found - skipped" % km)
        return
    for kmi in keymap.keymap_items:
        if kmi.idname == idname and kmi.type == type and kmi.value == value and kmi.shift == shift and kmi.ctrl == ctrl and kmi.alt == alt:
            kmi.active = False
            print("Disabled", kmi.name)
            return

    # add some delay
    bpy.app.timers.register(
        lambda: disable_specific_kmi(km, idname, type, value, shift, ctrl, alt, retries - 1),
        first_interval=0.1)

def get_active_kmi(space: str, **kwargs) -> bpy.types.KeyMapItem:
    kc = bpy.context.window_manager.keyconfigs.active
    km = kc.keymaps.get(space)
    if km:
        for kmi in km.keymap_items:
            for key, val in kwargs.items():
                if getattr(kmi, key) != val and val is not None:
                    break
            else:
                return kmi


def deactivate_kmi(space: str, **kwargs):
    """Deactivate a stock keymap item if it exists.

    get_active_kmi() returns None when the keymap or the item is missing,
    which happens whenever Blender renames a keymap between versions.
    Assigning to None used to raise AttributeError and abort register(),
    leaving every later conflict-removal unapplied.
    """
    try:
        kmi = get_active_kmi(space, **kwargs)
    except Exception as e:
        print("[HEAVYPOLY] keymap lookup failed for '%s': %r" % (space, e))
        return
    if kmi is None:
        print("[HEAVYPOLY] keymap item not found in '%s' (%s) - skipped" % (space, kwargs))
        return
    kmi.active = False
    print("Disabled", kmi.name)


# Every keymap item this add-on adds, so unregister() can take them away again.
addon_keymaps = []


def _snapshot(kc):
    """Remember which keymap items already existed, per keymap."""
    if kc is None:
        return {}
    return {km.name: {kmi.id for kmi in km.keymap_items} for km in kc.keymaps}


def _record_new_items(kc, before):
    """Store whatever appeared since the snapshot."""
    if kc is None:
        return
    for km in kc.keymaps:
        known = before.get(km.name, set())
        for kmi in km.keymap_items:
            if kmi.id not in known:
                addon_keymaps.append((km, kmi))


def register():
    # Apply Keymap / Apply All call this again, so clear our previous items
    # first. Without this every press stacked another copy of every shortcut.
    if addon_keymaps:
        print("[HEAVYPOLY] clearing %d previously registered items" % len(addon_keymaps))
        unregister()

    kc = bpy.context.window_manager.keyconfigs.addon
    before = _snapshot(kc)

    Keymap_Heavypoly()
    Keymap_Heavypoly_GP()
    Keymap_Heavypoly_TransferMode()
    Keymap_Heavypoly_Symmetry()
    Keymap_Heavypoly_TransformModal()

    _record_new_items(kc, before)
    print("[HEAVYPOLY] registered %d keymap items" % len(addon_keymaps))
    disable_default_kmi('Object Mode', 'transform.resize')
    disable_specific_kmi('Object Mode', 'transform.translate','LEFTMOUSE','CLICK_DRAG',False,False,False)
    disable_default_kmi('Object Mode', 'object.delete')
    disable_default_kmi('Object Mode', 'screen.animation_play')

    disable_specific_kmi('Curve', 'transform.translate','LEFTMOUSE','CLICK_DRAG',False,False,False)
    disable_specific_kmi('Curves', 'transform.translate','LEFTMOUSE','CLICK_DRAG',False,False,False)
    disable_specific_kmi('Curves', 'transform.translate','LEFTMOUSE','CLICK_DRAG',False,False,False)
    disable_specific_kmi('Grease Pencil Edit Mode', 'wm.call_menu','X','PRESS',False,False,False)



    disable_default_kmi('Object Mode', 'object.delete')

    disable_default_kmi('Window', 'screen.animation_play')

    disable_default_kmi('Frames', 'screen.animation_play')

    disable_default_kmi('Mesh', 'wm.call_menu')
    # E is HEAVYPOLY's Extrude to Cursor. Blender puts its own extrude on the
    # same key in the same keymap, so both fired and the new vertex followed
    # the mouse instead of staying put.
    disable_specific_kmi('Mesh', 'view3d.edit_mesh_extrude_move_normal',
                         'E', 'PRESS', False, False, False)
    # Z is HEAVYPOLY's shading pie; Blender's own shading pie sits on the same
    # key. Matched by menu name so we don't switch off our own.
    disable_pie_kmi('3D View', 'VIEW3D_MT_shading_pie', 'Z', 'PRESS')
    # Ctrl+Shift+X is HEAVYPOLY's symmetry toggle. Blender puts the colour
    # sampler on the same key in every paint mode, and that fired first, which
    # is why symmetry only worked in Edit Mode.
    for _paint_km in ('Sculpt', 'Vertex Paint', 'Image Paint'):
        disable_specific_kmi(_paint_km, 'paint.sample_color',
                             'X', 'PRESS', True, True, False)
    disable_specific_kmi('Weight Paint', 'paint.weight_sample_group',
                         'X', 'PRESS', True, True, False)
    # Tab is HEAVYPOLY's subdivision toggle, but Blender's stock Tab (toggle
    # Edit Mode) lives in the Object Non-modal keymap, which is checked
    # before the generic 3D View keymap where ours sits. So in Object Mode
    # the first press entered Edit Mode - that is also what makes the
    # mode-dot column appear in the Outliner - and only the second press,
    # now resolved through the Mesh keymap, reached the subdivision toggle.
    # Mode switching stays available through the selection pie.
    disable_specific_kmi('Object Non-modal', 'object.editmode_toggle',
                         'TAB', 'PRESS', False, False, False)

    disable_specific_kmi('Sculpt', 'paint.brush_select','V','PRESS',False,False,False)
    
    disable_specific_kmi('3D View Tool: Select Box', 'view3d.select_box','LEFTMOUSE','CLICK_DRAG',False,False,False)
    disable_specific_kmi('3D View Tool: Select Box', 'view3d.select_box','LEFTMOUSE','CLICK_DRAG',True,False,False)
    disable_specific_kmi('3D View Tool: Select Box', 'view3d.select_box','LEFTMOUSE','CLICK_DRAG',False,True,False)
    disable_specific_kmi('3D View Tool: Select Box', 'view3d.select_box','LEFTMOUSE','CLICK_DRAG',True,True,False)
    
    
    deactivate_kmi("3D View Tool: Move",
                   idname="transform.translate",
                   type='LEFTMOUSE',
                   value='CLICK_DRAG',
                   shift=False,
                   ctrl=False,
                   alt=False)
    deactivate_kmi("Pose",
                   idname="transform.translate",
                   type='LEFTMOUSE',
                   value='CLICK_DRAG',
                   shift=False,
                   ctrl=False,
                   alt=False)
    deactivate_kmi("Mesh",
                   idname="wm.call_menu",
                   type='X',
                   shift=False,
                   ctrl=False,
                   alt=False)
    # Blender 4.3+ renamed the Grease Pencil keymaps, so try both spellings.
    for _gp_km in ("Grease Pencil Edit Mode", "Grease Pencil Edit Mode Legacy"):
        deactivate_kmi(_gp_km,
                       idname="wm.call_menu",
                       type='X',
                       shift=False,
                       ctrl=False,
                       alt=False)
    deactivate_kmi("Frames",
                   idname="screen.animation_play",
                   type='SPACE',
                   shift=True,
                   ctrl=True,
                   alt=False)

        

    


def unregister():
    Keymap_Heavypoly_TransformModal_Restore()
    # This used to call Keymap_Heavypoly() again, which registered a second
    # copy of every shortcut instead of removing the first.
    for km, kmi in reversed(addon_keymaps):
        try:
            km.keymap_items.remove(kmi)
        except Exception:
            pass
    addon_keymaps.clear()

if __name__ == "__main__":
    register()
