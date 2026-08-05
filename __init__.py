"""HEAVYPOLY - pie menus and hotkeys for Blender 5.2.

Original work (c) 2022 Vaughan Ling, MIT licensed. See LICENSE.md.
"""

import bpy
from . import HEAVYPOLY__menu_master
from . import HEAVYPOLY_draw_primitives
from . import HEAVYPOLY_HOTKEYS
from . import HEAVYPOLY_OPERATORS
from . import HEAVYPOLY_panel_properties
from . import HEAVYPOLY_panel_render
from . import HEAVYPOLY_panel_tools
from . import HEAVYPOLY_pie_add
from . import HEAVYPOLY_pie_areas
from . import HEAVYPOLY_pie_boolean
from . import HEAVYPOLY_pie_import_export
from . import HEAVYPOLY_pie_pivots
from . import HEAVYPOLY_pie_rotate_90
from . import HEAVYPOLY_pie_save
from . import HEAVYPOLY_pie_selection
from . import HEAVYPOLY_pie_shading
from . import HEAVYPOLY_pie_specials
from . import HEAVYPOLY_pie_symmetry
from . import HEAVYPOLY_pie_view
from . import HEAVYPOLY_popup_materials
from . import HEAVYPOLY_popup_properties
from . import HEAVYPOLY_popup_render
from . import HEAVYPOLY_screencast_keys
from . import HEAVYPOLY_select_through_border
from . import jmQuickPipe
from . import HEAVYPOLY_pie_extra
from . import HEAVYPOLY_setup


# Keymap
addon_keymaps = []

def register():
    # If any module raises part-way through, the classes registered so far
    # stay in memory while Blender leaves the add-on switched off. Enabling
    # it again then fails with "already registered as a subclass". Clean up
    # instead, so a failed install leaves nothing behind.
    try:

        # Register your scripts
        HEAVYPOLY__menu_master.register()
        HEAVYPOLY_draw_primitives.register()
        HEAVYPOLY_OPERATORS.register()
        HEAVYPOLY_panel_properties.register()
        HEAVYPOLY_panel_render.register()
        HEAVYPOLY_panel_tools.register()
        HEAVYPOLY_pie_add.register()
        HEAVYPOLY_pie_areas.register()
        HEAVYPOLY_pie_boolean.register()
        HEAVYPOLY_pie_import_export.register()
        HEAVYPOLY_pie_pivots.register()
        HEAVYPOLY_pie_rotate_90.register()
        HEAVYPOLY_pie_save.register()
        HEAVYPOLY_pie_selection.register()
        HEAVYPOLY_pie_shading.register()
        HEAVYPOLY_pie_specials.register()
        HEAVYPOLY_pie_symmetry.register()
        HEAVYPOLY_pie_view.register()
        HEAVYPOLY_popup_materials.register()
        HEAVYPOLY_popup_properties.register()
        HEAVYPOLY_popup_render.register()
        HEAVYPOLY_screencast_keys.register()
        HEAVYPOLY_select_through_border.register()
        jmQuickPipe.register()
        HEAVYPOLY_pie_extra.register()
        HEAVYPOLY_setup.register()

        # Last, so every operator exists by the time we set kmi properties.
        HEAVYPOLY_HOTKEYS.register()


        # Register keyboard shortcuts
        wm = bpy.context.window_manager
        km = wm.keyconfigs.addon.keymaps.new(name="3D View", space_type="VIEW_3D")
        kmi = km.keymap_items.new("wm.call_menu", 'A', 'PRESS', ctrl=True, shift=True)
        kmi.properties.name = "VIEW3D_MT_add"
        addon_keymaps.append((km, kmi))
    except Exception:
        unregister()
        raise


def unregister():
    # One module raising here used to abort the whole teardown, leaving parts
    # of the add-on registered and the next enable failing with
    # "already registered as a subclass".
    for module in (
        HEAVYPOLY__menu_master,
        HEAVYPOLY_draw_primitives,
        HEAVYPOLY_HOTKEYS,
        HEAVYPOLY_OPERATORS,
        HEAVYPOLY_panel_properties,
        HEAVYPOLY_panel_render,
        HEAVYPOLY_panel_tools,
        HEAVYPOLY_pie_add,
        HEAVYPOLY_pie_areas,
        HEAVYPOLY_pie_boolean,
        HEAVYPOLY_pie_import_export,
        HEAVYPOLY_pie_pivots,
        HEAVYPOLY_pie_rotate_90,
        HEAVYPOLY_pie_save,
        HEAVYPOLY_pie_selection,
        HEAVYPOLY_pie_shading,
        HEAVYPOLY_pie_specials,
        HEAVYPOLY_pie_symmetry,
        HEAVYPOLY_pie_view,
        HEAVYPOLY_popup_materials,
        HEAVYPOLY_popup_properties,
        HEAVYPOLY_popup_render,
        HEAVYPOLY_screencast_keys,
        HEAVYPOLY_select_through_border,
        jmQuickPipe,
        HEAVYPOLY_pie_extra,
        HEAVYPOLY_setup,
        #script2
    ):
        try:
            module.unregister()
        except Exception as e:
            print("[HEAVYPOLY] %s.unregister() failed: %r" % (module.__name__, e))

    wm = bpy.context.window_manager
    for km, kmi in addon_keymaps:
        try:
            km.keymap_items.remove(kmi)
        except Exception:
            pass
    addon_keymaps.clear()


if __name__ == "__main__":
    register()
