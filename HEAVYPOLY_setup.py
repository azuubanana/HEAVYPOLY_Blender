"""HEAVYPOLY setup panel.

Lives in Preferences > Add-ons > HEAVYPOLY. One big "Apply All" button for
beginners, with the individual steps tucked away behind a collapsed section.

Nothing is applied automatically except the keymap, which is registered the
normal way when the add-on is enabled.
"""

import os
import re
import shutil

import bpy
from bpy.types import Operator, AddonPreferences
from bpy.props import BoolProperty, StringProperty


WORKSPACE_PREFIX = "HP "
STARTUP_FILE = "HP_Startup.blend"
BACKUP_NAME = "HP_userpref_backup.blend"
KEYMAP_BACKUP_NAME = "HP_keymap_backup.py"
STARTUP_BACKUP_NAME = "HP_startup_backup.blend"

# Pie menus should appear instantly, not unfold.
PIE_ANIMATION_TIMEOUT = 0


# ---------------------------------------------------------------- paths


def _package_dir():
    return os.path.dirname(os.path.abspath(__file__))


def _startup_source():
    return os.path.join(_package_dir(), STARTUP_FILE)


def _startup_target():
    return os.path.join(_config_dir(), "startup.blend")


def _startup_backup():
    return os.path.join(_config_dir(), STARTUP_BACKUP_NAME)


def _config_dir():
    return bpy.utils.user_resource('CONFIG')


def _backup_path():
    return os.path.join(_config_dir(), BACKUP_NAME)


def _keymap_backup_path():
    return os.path.join(_config_dir(), KEYMAP_BACKUP_NAME)


def _addon_version():
    """Read the version straight out of blender_manifest.toml."""
    path = os.path.join(_package_dir(), "blender_manifest.toml")
    try:
        text = open(path, encoding="utf-8").read()
    except Exception:
        return ""
    match = re.search(r'^version\s*=\s*"([^"]*)"', text, re.MULTILINE)
    return match.group(1) if match else ""


def _modified_keymap_count():
    """How many shortcuts the user has changed by hand."""
    kc = bpy.context.window_manager.keyconfigs.user
    if kc is None:
        return 0
    count = 0
    for km in kc.keymaps:
        for kmi in km.keymap_items:
            if getattr(kmi, "is_user_modified", False):
                count += 1
    return count


def _prefs():
    try:
        return bpy.context.preferences.addons[__package__].preferences
    except (KeyError, AttributeError):
        return None


# ---------------------------------------------------------------- backup


def _make_backup(report=None):
    """Copy the current userpref.blend aside, once, before we touch anything."""
    if os.path.exists(_backup_path()):
        return True
    src = os.path.join(_config_dir(), "userpref.blend")
    if not os.path.exists(src):
        try:
            bpy.ops.wm.save_userpref()
        except Exception as e:
            if report:
                report({'WARNING'}, "Could not write preferences: %r" % (e,))
            return False
    try:
        shutil.copy2(src, _backup_path())
        print("[HEAVYPOLY] backed up preferences to %s" % _backup_path())
        return True
    except Exception as e:
        if report:
            report({'WARNING'}, "Backup failed: %r" % (e,))
        return False


# ---------------------------------------------------------------- workspaces


def _append_workspaces(report=None):
    """Append every HP-prefixed workspace from the bundled blend file."""
    path = _startup_source()
    if not os.path.exists(path):
        if report:
            report({'ERROR'}, "%s is missing from the add-on." % STARTUP_FILE)
        return []

    before = {ws.name for ws in bpy.data.workspaces}
    try:
        with bpy.data.libraries.load(path, link=False) as (data_from, data_to):
            wanted = [n for n in data_from.workspaces if n.startswith(WORKSPACE_PREFIX)]
            if not wanted:
                wanted = list(data_from.workspaces)
            data_to.workspaces = wanted
    except Exception as e:
        if report:
            report({'ERROR'}, "Could not read %s: %r" % (STARTUP_FILE, e))
        return []

    appended = [ws for ws in bpy.data.workspaces if ws.name not in before]
    if not appended:
        if report:
            report({'INFO'}, "Workspaces were already present.")
    return appended


def _bring_to_front(workspaces):
    """Move the new tabs to the left and activate the first one."""
    window = bpy.context.window
    if window is None or not workspaces:
        return

    for ws in reversed(workspaces):
        try:
            screen = ws.screens[0] if ws.screens else None
            with bpy.context.temp_override(workspace=ws, screen=screen, window=window):
                bpy.ops.workspace.reorder_to_front()
        except Exception as e:
            print("[HEAVYPOLY] could not reorder '%s': %r" % (ws.name, e))

    try:
        window.workspace = workspaces[0]
    except Exception as e:
        print("[HEAVYPOLY] could not activate '%s': %r" % (workspaces[0].name, e))


def _apply_preferences(report=None):
    """Turn off the pie unfold animation so menus appear instantly."""
    try:
        bpy.context.preferences.view.pie_animation_timeout = PIE_ANIMATION_TIMEOUT
        bpy.ops.wm.save_userpref()
        return True
    except Exception as e:
        if report:
            report({'WARNING'}, "Could not update preferences: %r" % (e,))
        print("[HEAVYPOLY] preferences step failed: %r" % (e,))
        return False


def _install_startup_file(report=None):
    """Copy the bundled startup file over Blender's, so File > New uses it.

    This only touches files on disk. The scene you are working in right now
    is left completely alone.
    """
    src = _startup_source()
    if not os.path.exists(src):
        if report:
            report({'ERROR'}, "%s is missing from the add-on." % STARTUP_FILE)
        return False

    dst = _startup_target()
    try:
        if os.path.exists(dst) and not os.path.exists(_startup_backup()):
            shutil.copy2(dst, _startup_backup())
            print("[HEAVYPOLY] backed up startup.blend")
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
        print("[HEAVYPOLY] installed %s as startup.blend" % STARTUP_FILE)
        return True
    except Exception as e:
        if report:
            report({'ERROR'}, "Could not install the startup file: %r" % (e,))
        return False


# ---------------------------------------------------------------- operators


class HP_OT_setup_apply_keymap(Operator):
    """Re-apply the HEAVYPOLY keymap"""
    bl_idname = "hp.setup_apply_keymap"
    bl_label = "Apply Keymap"

    def execute(self, context):
        _make_backup(self.report)
        try:
            from . import HEAVYPOLY_HOTKEYS
            HEAVYPOLY_HOTKEYS.register()
        except Exception as e:
            self.report({'ERROR'}, "Keymap failed: %r" % (e,))
            return {'CANCELLED'}
        self.report({'INFO'}, "Keymap applied.")
        return {'FINISHED'}


class HP_OT_setup_apply_preferences(Operator):
    """Turn off the pie menu animation"""
    bl_idname = "hp.setup_apply_preferences"
    bl_label = "Apply Preferences"

    def execute(self, context):
        _make_backup(self.report)
        if _apply_preferences(self.report):
            self.report({'INFO'}, "Pie animation disabled.")
        return {'FINISHED'}


class HP_OT_setup_install_startup(Operator):
    """Make File > New open the HEAVYPOLY startup file"""
    bl_idname = "hp.setup_install_startup"
    bl_label = "Install Startup File"

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        if not _install_startup_file(self.report):
            return {'CANCELLED'}
        prefs = _prefs()
        if prefs:
            prefs.applied_startup = True
        self.report({'INFO'}, "Startup file installed. Try File > New.")
        return {'FINISHED'}


class HP_OT_setup_load_workspaces(Operator):
    """Add the HEAVYPOLY workspaces, keeping the existing ones"""
    bl_idname = "hp.setup_load_workspaces"
    bl_label = "Load Workspaces"

    def execute(self, context):
        appended = _append_workspaces(self.report)
        _bring_to_front(appended)
        prefs = _prefs()
        if prefs:
            prefs.applied_workspaces = True
        if appended:
            self.report({'INFO'}, "Added %d workspace(s)." % len(appended))
        return {'FINISHED'}


class HP_OT_setup_replace_workspaces(Operator):
    """Add the HEAVYPOLY workspaces and remove all the others"""
    bl_idname = "hp.setup_replace_workspaces"
    bl_label = "Replace Workspaces"

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        appended = _append_workspaces(self.report)
        if not appended:
            self.report({'WARNING'}, "Nothing was added, so nothing was removed.")
            return {'CANCELLED'}
        _bring_to_front(appended)

        keep = {ws.name for ws in appended}
        removed = 0
        for ws in list(bpy.data.workspaces):
            if ws.name in keep:
                continue
            try:
                bpy.data.workspaces.remove(ws)
                removed += 1
            except Exception as e:
                print("[HEAVYPOLY] could not remove '%s': %r" % (ws.name, e))

        prefs = _prefs()
        if prefs:
            prefs.applied_workspaces = True
        self.report({'INFO'}, "Added %d, removed %d." % (len(appended), removed))
        return {'FINISHED'}


class HP_OT_setup_apply_all(Operator):
    """Apply everything: keymap, preferences, startup file and workspaces"""
    bl_idname = "hp.setup_apply_all"
    bl_label = "Apply All"

    def execute(self, context):
        _make_backup(self.report)

        try:
            from . import HEAVYPOLY_HOTKEYS
            HEAVYPOLY_HOTKEYS.register()
        except Exception as e:
            print("[HEAVYPOLY] keymap step failed: %r" % (e,))

        _apply_preferences()
        startup_ok = _install_startup_file(self.report)

        # Also add the workspaces to the file that is open right now, so the
        # user does not have to restart or press File > New to see anything.
        appended = _append_workspaces()
        _bring_to_front(appended)

        prefs = _prefs()
        if prefs:
            prefs.applied_startup = startup_ok
            prefs.applied_workspaces = True
            prefs.applied_version = _addon_version()

        self.report({'INFO'}, "HEAVYPOLY is set up. Have fun.")
        return {'FINISHED'}


class HP_OT_setup_save_keymap(Operator):
    """Write your current shortcuts to a file you can reload later"""
    bl_idname = "hp.setup_save_keymap"
    bl_label = "Save My Keymap"

    def execute(self, context):
        path = _keymap_backup_path()
        try:
            bpy.ops.preferences.keyconfig_export(filepath=path, all=False)
        except Exception as e:
            self.report({'ERROR'}, "Could not save the keymap: %r" % (e,))
            return {'CANCELLED'}
        self.report({'INFO'}, "Saved to %s" % path)
        print("[HEAVYPOLY] keymap saved to %s" % path)
        return {'FINISHED'}


class HP_OT_setup_load_keymap(Operator):
    """Load the shortcuts you saved earlier"""
    bl_idname = "hp.setup_load_keymap"
    bl_label = "Load My Keymap"

    @classmethod
    def poll(cls, context):
        return os.path.exists(_keymap_backup_path())

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        try:
            bpy.ops.preferences.keyconfig_import(filepath=_keymap_backup_path(),
                                                 keep_original=True)
        except Exception as e:
            self.report({'ERROR'}, "Could not load the keymap: %r" % (e,))
            return {'CANCELLED'}
        self.report({'INFO'}, "Keymap restored.")
        return {'FINISHED'}


class HP_OT_setup_restore(Operator):
    """Restore the preferences saved before HEAVYPOLY was first applied"""
    bl_idname = "hp.setup_restore"
    bl_label = "Restore My Settings"

    @classmethod
    def poll(cls, context):
        return os.path.exists(_backup_path())

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        target = os.path.join(_config_dir(), "userpref.blend")
        try:
            shutil.copy2(_backup_path(), target)
            if os.path.exists(_startup_backup()):
                shutil.copy2(_startup_backup(), _startup_target())
            elif os.path.exists(_startup_target()):
                os.remove(_startup_target())
            bpy.ops.wm.read_userpref()
        except Exception as e:
            self.report({'ERROR'}, "Restore failed: %r" % (e,))
            return {'CANCELLED'}
        self.report({'INFO'}, "Preferences restored.")
        return {'FINISHED'}


# ---------------------------------------------------------------- preferences


class HP_OT_setup_welcome(Operator):
    """Shown once after installing or after a feature update"""
    bl_idname = "hp.setup_welcome"
    bl_label = "HEAVYPOLY"

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=380)

    def draw(self, context):
        layout = self.layout
        prefs = _prefs()
        first_time = not (prefs and prefs.applied_version)

        col = layout.column()
        if first_time:
            col.label(text="HEAVYPOLY is installed.", icon='CHECKMARK')
            col.label(text="Press OK to set up the keymap, workspaces")
            col.label(text="and startup file.")
        else:
            col.label(text="HEAVYPOLY was updated to %s." % _addon_version(),
                      icon='FILE_REFRESH')
            col.label(text="Press OK to apply the new startup file.")

        col.separator()
        col.label(text="Then open File > New to start fresh.", icon='INFO')

        modified = _modified_keymap_count()
        if modified:
            col.separator()
            box = col.box()
            box.label(text="%d shortcut(s) differ from the defaults."
                           % modified, icon='KEYINGSET')
            box.operator("hp.setup_save_keymap", icon='FILE_TICK')

    def execute(self, context):
        return bpy.ops.hp.setup_apply_all()


def _feature_change(old, new):
    """True when major or minor moved. Patch releases stay quiet."""
    if not new:
        return False
    if not old:
        return True
    return old.split(".")[:2] != new.split(".")[:2]


def _show_welcome():
    """Called once from a timer, so the UI is ready."""
    prefs = _prefs()
    if prefs is None:
        return 0.5   # preferences not registered yet, try again shortly
    if _feature_change(prefs.applied_version, _addon_version()):
        try:
            bpy.ops.hp.setup_welcome('INVOKE_DEFAULT')
        except Exception as e:
            print("[HEAVYPOLY] could not open the welcome dialog: %r" % (e,))
    return None


class HEAVYPOLY_Preferences(AddonPreferences):
    bl_idname = __package__

    show_manual: BoolProperty(
        name="Manual Setup",
        default=False,
    )
    applied_startup: BoolProperty(default=False)
    applied_workspaces: BoolProperty(default=False)
    applied_version: StringProperty(default="")

    def draw(self, context):
        layout = self.layout

        current = _addon_version()
        applied = self.applied_startup and self.applied_workspaces

        box = layout.box()
        if not applied:
            row = box.row()
            row.alert = True
            row.label(text="Not applied yet - click Apply All to start", icon='ERROR')
        elif current and self.applied_version != current:
            # The add-on was updated. The startup file and the keymap only
            # change when Apply All runs, so say so rather than doing it.
            col = box.column(align=True)
            row = col.row()
            row.alert = True
            row.label(text="Updated to %s" % current, icon='ERROR')
            col.label(text="Apply All to get the new startup file.")
            col.label(text="Save your keymap first if you changed any shortcuts.")
            col.operator("hp.setup_save_keymap", icon='FILE_TICK')
        else:
            box.label(text="Applied  (%s)" % (current or "?"), icon='CHECKMARK')

        modified = _modified_keymap_count()
        if modified:
            box.label(text="%d shortcut(s) changed from the defaults." % modified,
                      icon='KEYINGSET')

        col = layout.column()
        col.scale_y = 2.0
        col.operator("hp.setup_apply_all", icon='CHECKMARK')

        layout.separator()

        header = layout.row()
        header.prop(self, "show_manual",
                    icon='TRIA_DOWN' if self.show_manual else 'TRIA_RIGHT',
                    emboss=False)

        if not self.show_manual:
            return

        box = layout.box()
        col = box.column(align=True)
        col.operator("hp.setup_apply_keymap", icon='KEYINGSET')
        col.operator("hp.setup_apply_preferences", icon='PREFERENCES')
        col.operator("hp.setup_install_startup", icon='FILE_BLEND')
        col.operator("hp.setup_load_workspaces", icon='WORKSPACE')
        col.operator("hp.setup_replace_workspaces", icon='WORKSPACE')

        col.separator()
        row = col.row(align=True)
        row.operator("hp.setup_save_keymap", icon='FILE_TICK')
        row.operator("hp.setup_load_keymap", icon='FILE_REFRESH')

        col.separator()
        col.operator("hp.setup_restore", icon='LOOP_BACK')

        box.label(text="Save your own File > Defaults > Save Startup File "
                       "afterwards to override it.", icon='INFO')
        if not os.path.exists(_backup_path()):
            box.label(text="No backup yet. One is made the first time you apply.",
                      icon='INFO')


classes = (
    HP_OT_setup_apply_keymap,
    HP_OT_setup_apply_preferences,
    HP_OT_setup_install_startup,
    HP_OT_setup_load_workspaces,
    HP_OT_setup_replace_workspaces,
    HP_OT_setup_apply_all,
    HP_OT_setup_save_keymap,
    HP_OT_setup_load_keymap,
    HP_OT_setup_restore,
    HP_OT_setup_welcome,
    HEAVYPOLY_Preferences,
)

_register_classes, _unregister_classes = bpy.utils.register_classes_factory(classes)


def register():
    _register_classes()
    # Blender is still booting when add-ons register, so defer the dialog.
    bpy.app.timers.register(_show_welcome, first_interval=1.0)


def unregister():
    if bpy.app.timers.is_registered(_show_welcome):
        bpy.app.timers.unregister(_show_welcome)
    _unregister_classes()
