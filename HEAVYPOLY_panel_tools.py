"""N-panel tab for operators that have no keyboard shortcut.

Lives in the 3D View sidebar (press N) under the "HP Tools" tab. This is the
home for commands that are useful but not worth a hotkey — right now the two
clipboard-image tools, with room for more as they arrive.

The buttons grey themselves out when their operator's poll fails (for example
Key Out Background needs something selected), so the panel stays visible in
every mode and tells the user why a command is unavailable rather than hiding.
"""

import bpy


class HP_PT_tools(bpy.types.Panel):
    bl_label = "HEAVYPOLY Tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "HP Tools"

    def draw(self, context):
        layout = self.layout

        column = layout.column(align=True)
        column.scale_y = 1.5  # roomy targets for pen tablets
        column.label(text="Image", icon='IMAGE_DATA')
        column.operator("object.hp_paste_image_plane",
                        text="Paste Image as Plane", icon='IMAGE_REFERENCE')
        column.operator("object.hp_key_out_background",
                        text="Key Out Background", icon='IMAGE_ALPHA')
        column.operator("object.hp_cutout_mesh",
                        text="Cut Out to Mesh", icon='MESH_DATA')
        column.operator("object.hp_separate_islands",
                        text="Separate Islands", icon='MOD_EXPLODE')

        layout.separator()
        column = layout.column(align=True)
        column.scale_y = 1.5
        column.label(text="Support", icon='QUESTION')
        column.operator("hp.copy_diagnostic",
                        text="Copy Diagnostic Report", icon='COPYDOWN')


classes = (
    HP_PT_tools,
)
register, unregister = bpy.utils.register_classes_factory(classes)


if __name__ == "__main__":
    register()
