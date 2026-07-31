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
KEYMAP_AUTOSAVE_NAME = "HP_keymap_autosave.py"
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


def _keymap_autosave_path():
    """Separate from the manual backup, so a rescue never overwrites it."""
    return os.path.join(_config_dir(), KEYMAP_AUTOSAVE_NAME)


def _autosave_keymap():
    try:
        bpy.ops.preferences.keyconfig_export(filepath=_keymap_autosave_path(),
                                             all=False)
        print("[HEAVYPOLY] keymap auto-saved to %s" % _keymap_autosave_path())
        return True
    except Exception as e:
        print("[HEAVYPOLY] keymap auto-save failed: %r" % (e,))
        return False


def _addon_version():
    """Read the version straight out of blender_manifest.toml."""
    path = os.path.join(_package_dir(), "blender_manifest.toml")
    try:
        text = open(path, encoding="utf-8").read()
    except Exception:
        return ""
    match = re.search(r'^version\s*=\s*"([^"]*)"', text, re.MULTILINE)
    return match.group(1) if match else ""


# Shortcuts HEAVYPOLY disables on purpose (keymap name, key type). These
# read as "user modified" to Blender, but they are ours, so the "changed
# from the defaults" counter must not blame them on the user.
INTENTIONAL_DISABLES = (
    ("Object Non-modal", 'TAB'),   # stock Edit Mode toggle; Tab is subdiv
)


def _is_intentional_disable(km, kmi):
    if not kmi.active and any(km.name == name and kmi.type == key
                              for name, key in INTENTIONAL_DISABLES):
        return True
    # Space repurposed from Confirm to Y-axis lock in the Transform Modal
    # Map (see Keymap_Heavypoly_TransformModal) - ours too, not the user's.
    if (km.name == 'Transform Modal Map' and kmi.type == 'SPACE'
            and getattr(kmi, 'propvalue', '') == 'AXIS_Y'):
        return True
    return False


def _modified_keymap_count():
    """How many shortcuts the user has changed by hand."""
    kc = bpy.context.window_manager.keyconfigs.user
    if kc is None:
        return 0
    count = 0
    for km in kc.keymaps:
        for kmi in km.keymap_items:
            if (getattr(kmi, "is_user_modified", False)
                    and not _is_intentional_disable(km, kmi)):
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

    # Anything already called "HP ..." means a previous Apply already ran.
    existing = [ws for ws in bpy.data.workspaces
                if ws.name.startswith(WORKSPACE_PREFIX)]
    if existing:
        if report:
            report({'INFO'}, "Workspaces already present.")
        return existing

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


def _scene_is_untouched():
    """True when nothing would be lost by reloading the startup file."""
    return not bpy.data.filepath and not bpy.data.is_dirty


def _open_new_file():
    """Deferred so the operator that called us has finished first."""
    try:
        bpy.ops.wm.read_homefile()
    except Exception as e:
        print("[HEAVYPOLY] could not open a new file: %r" % (e,))
    return None


def _enable_node_wrangler(report=None):
    """Switch on Node Wrangler (Ctrl+T and friends in the shader editor).

    Blender ships it disabled, so Ctrl+T silently does nothing until someone
    finds the add-on list. Depending on the build it lives either as the
    legacy bundled add-on "node_wrangler" or as the extension
    "bl_ext.blender_org.node_wrangler", so match on the last name part. If
    neither exists (moved to the online extension platform), say so loudly
    instead of failing silently.
    """
    import addon_utils

    enabled = set(bpy.context.preferences.addons.keys())
    candidates = [m.__name__ for m in addon_utils.modules()
                  if m.__name__.split(".")[-1] == "node_wrangler"]
    for name in candidates:
        if name in enabled:
            print("[HEAVYPOLY] Node Wrangler already enabled (%s)" % name)
            return True
        try:
            addon_utils.enable(name, default_set=True, persistent=True)
            print("[HEAVYPOLY] enabled Node Wrangler (%s)" % name)
            return True
        except Exception as e:
            print("[HEAVYPOLY] could not enable %s: %r" % (name, e))

    message = ("Node Wrangler is not installed - get it from "
               "Preferences > Get Extensions.")
    if report:
        report({'WARNING'}, message)
    print("[HEAVYPOLY] " + message)
    return False


def _apply_preferences(report=None):
    """Turn off the pie unfold animation; turn on Node Wrangler."""
    try:
        bpy.context.preferences.view.pie_animation_timeout = PIE_ANIMATION_TIMEOUT
        _enable_node_wrangler(report)
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


# ---------------------------------------------------------------- what's new

# Newest first. Shown once after an update. Keep the lines short - the
# popup does not wrap text. English only, per "No Japanese in the UI".
WHATS_NEW = (
    ("1.25.0", (
        "Cut Out to Mesh: Grid fill is now built per piece, so",
        "nearby leaves no longer get webbed together.",
        "New Separate Islands checkbox right in the cut-out redo",
        "panel - pieces split off with per-piece origins in one go.",
    )),
    ("1.24.0", (
        "Cut Out to Mesh: new Fill option. Triangles (default) for",
        "flat cards, or Grid (Quads) for pieces you will bend,",
        "rig or animate - even quads with the rim snapped to the",
        "outline. Grid Size sets the quad size in pixels.",
    )),
    ("1.23.0", (
        "Cut Out to Mesh picks its cutoff per image now, guesses",
        "the background colour from the image border, and fills",
        "specks and pinholes (Min Size). Inset resets each run.",
        "Bottom origin goes under the lowest geometry, not the",
        "middle of the bounding box (cutout and Separate Islands).",
        "This popup waits until after Apply All opens the new file.",
    )),
    ("1.22.0", (
        "Separate Islands: each piece's origin now goes to its",
        "bottom center by default (change it in the redo panel).",
        "Troubleshooting panel reorganised, with when-to-use notes.",
        "What's New button always visible here; the popup after",
        "updates now actually opens.",
        "Diagnostic report understands extension installs.",
        "'1 shortcut changed' no longer counts HEAVYPOLY's own Tab fix.",
    )),
    ("1.21.0", (
        "N panel > HP Tools: Copy Diagnostic Report. One click,",
        "then paste it to your teacher when something is wrong.",
        "Cut Out to Mesh: Inset, Origin and Thickness options,",
        "plus a Separate Islands button.",
        "This What's New popup.",
    )),
    ("1.20.0", (
        "HP Tools tab in the 3D View sidebar (press N).",
        "Cut Out to Mesh: trim a pasted image plane to its outline.",
        "Tab toggles subdivision on the first press.",
        "Apply Preferences now also turns on Node Wrangler.",
    )),
)


def _version_tuple(version):
    try:
        return tuple(int(part) for part in version.split("."))
    except Exception:
        return (0,)


def _whats_new_entries(prefs):
    """Changelog entries newer than what the user last saw."""
    baseline = _version_tuple(prefs.seen_version or prefs.applied_version or "0")
    return [(v, lines) for v, lines in WHATS_NEW
            if _version_tuple(v) > baseline]


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
    """Turn off the pie menu animation and turn on Node Wrangler"""
    bl_idname = "hp.setup_apply_preferences"
    bl_label = "Apply Preferences"

    def execute(self, context):
        _make_backup(self.report)
        if _apply_preferences(self.report):
            self.report({'INFO'}, "Pie animation off, Node Wrangler on.")
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
    bl_label = "Set Up HEAVYPOLY"

    def invoke(self, context, event):
        if _scene_is_untouched():
            return self.execute(context)
        return context.window_manager.invoke_props_dialog(self, width=360)

    def draw(self, context):
        col = self.layout.column()
        col.label(text="This opens a new file so the setup takes effect.",
                  icon='ERROR')
        col.label(text="Unsaved changes will be lost.")

    def execute(self, context):
        _make_backup(self.report)

        try:
            from . import HEAVYPOLY_HOTKEYS
            HEAVYPOLY_HOTKEYS.register()
        except Exception as e:
            print("[HEAVYPOLY] keymap step failed: %r" % (e,))

        _apply_preferences()
        startup_ok = _install_startup_file(self.report)

        prefs = _prefs()
        if prefs:
            prefs.applied_startup = startup_ok
            prefs.applied_workspaces = True
            prefs.applied_version = _addon_version()

        # Loading the startup file is what actually shows the result. Appending
        # workspaces to the current scene only ever produced a half-applied
        # look that differed from File > New.
        if startup_ok:
            bpy.app.timers.register(_open_new_file, first_interval=0.1)
            self.report({'INFO'}, "HEAVYPOLY is set up. Have fun.")
        else:
            self.report({'WARNING'},
                        "Set up, but the startup file could not be installed.")
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

        # Importing only adds the preset. Without this it stays inactive and
        # nothing appears to change.
        name = os.path.splitext(os.path.basename(_keymap_backup_path()))[0]
        keyconfigs = context.window_manager.keyconfigs
        imported = keyconfigs.get(name)
        if imported is not None:
            keyconfigs.active = imported
            self.report({'INFO'}, "Keymap '%s' is now active." % name)
        else:
            self.report({'WARNING'},
                        "Imported, but could not activate '%s'. "
                        "Pick it in Preferences > Keymap." % name)
        return {'FINISHED'}


class HP_OT_setup_cleanup(Operator):
    """Remove duplicate workspaces and shortcuts left by older versions"""
    bl_idname = "hp.setup_cleanup"
    bl_label = "Clean Up Duplicates"

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=340)

    @staticmethod
    def _kmi_signature(kmi):
        # The properties matter. Every HEAVYPOLY pie is wm.call_menu_pie on the
        # same key pattern and only the menu name differs, so ignoring them
        # made completely different shortcuts look identical.
        props = []
        try:
            for prop in kmi.properties.bl_rna.properties:
                if prop.identifier == "rna_type":
                    continue
                try:
                    value = getattr(kmi.properties, prop.identifier)
                except Exception:
                    continue
                if hasattr(value, "__iter__") and not isinstance(value, str):
                    try:
                        value = tuple(value)
                    except Exception:
                        value = repr(value)
                props.append((prop.identifier, value))
        except Exception:
            props.append(("<unreadable>", id(kmi)))

        return (kmi.idname, kmi.type, kmi.value, kmi.map_type,
                kmi.ctrl, kmi.shift, kmi.alt, kmi.oskey, kmi.key_modifier,
                tuple(sorted(props, key=lambda item: item[0])))

    def _count_duplicates(self, context):
        workspaces = 0
        for ws in bpy.data.workspaces:
            if not ws.name.startswith(WORKSPACE_PREFIX):
                continue
            tail = ws.name.rsplit(".", 1)[-1]
            if len(tail) == 3 and tail.isdigit():
                workspaces += 1

        items = 0
        keyconfigs = context.window_manager.keyconfigs
        for kc in (keyconfigs.addon, keyconfigs.user):
            if kc is None:
                continue
            for km in kc.keymaps:
                seen = set()
                for kmi in km.keymap_items:
                    signature = self._kmi_signature(kmi)
                    if signature in seen:
                        items += 1
                    else:
                        seen.add(signature)
        return workspaces, items

    def draw(self, context):
        layout = self.layout
        workspaces, items = self._count_duplicates(context)
        col = layout.column()
        col.label(text="Remove %d duplicate workspace(s)" % workspaces)
        col.label(text="and %d duplicate shortcut(s)?" % items)
        col.separator()
        col.label(text="Your keymap is auto-saved first.", icon='INFO')
        col.label(text="Undo with Load Auto-Saved Keymap.")

    def execute(self, context):
        # Always take a keymap snapshot before deleting anything.
        _autosave_keymap()

        # Workspaces: "HP Modeling.001" and friends
        removed_ws = 0
        for ws in list(bpy.data.workspaces):
            if not ws.name.startswith(WORKSPACE_PREFIX):
                continue
            tail = ws.name.rsplit(".", 1)[-1]
            if len(tail) == 3 and tail.isdigit():
                try:
                    bpy.data.workspaces.remove(ws)
                    removed_ws += 1
                except Exception as e:
                    print("[HEAVYPOLY] could not remove '%s': %r" % (ws.name, e))

        # Keymap items: the old unregister() stacked a fresh copy every reload
        removed_kmi = 0
        keyconfigs = context.window_manager.keyconfigs
        for kc in (keyconfigs.addon, keyconfigs.user):
            if kc is None:
                continue
            for km in kc.keymaps:
                seen = set()
                for kmi in list(km.keymap_items):
                    signature = self._kmi_signature(kmi)
                    if signature in seen:
                        try:
                            km.keymap_items.remove(kmi)
                            removed_kmi += 1
                        except Exception:
                            pass
                    else:
                        seen.add(signature)

        self.report({'INFO'}, "Removed %d workspace(s) and %d duplicate shortcut(s)."
                    % (removed_ws, removed_kmi))
        return {'FINISHED'}


class HP_OT_setup_reset_keymap(Operator):
    """Throw away keymap edits and rebuild the HEAVYPOLY defaults"""
    bl_idname = "hp.setup_reset_keymap"
    bl_label = "Reset Keymap to HP Default"

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=360)

    def draw(self, context):
        col = self.layout.column()
        col.label(text="Blender's keymap goes back to factory state,",
                  icon='ERROR')
        col.label(text="then HEAVYPOLY is applied on top.")
        col.label(text="Any shortcuts you changed yourself will be lost.")
        col.separator()
        col.label(text="Your keymap is auto-saved first.", icon='INFO')
        col.label(text="Undo with Load Auto-Saved Keymap.")

    def execute(self, context):
        _autosave_keymap()

        keyconfigs = context.window_manager.keyconfigs
        stock = keyconfigs.get("Blender")
        if stock is not None:
            try:
                keyconfigs.active = stock
            except Exception as e:
                print("[HEAVYPOLY] could not activate the stock keyconfig: %r" % (e,))

        # Put Blender's own keymap back to factory state as well. Without this,
        # anything deleted from the stock keymap stayed deleted and no amount
        # of re-registering HEAVYPOLY would bring it back.
        try:
            bpy.ops.preferences.keyconfig_restore()
        except Exception as e:
            print("[HEAVYPOLY] keyconfig_restore failed: %r" % (e,))

        try:
            from . import HEAVYPOLY_HOTKEYS
            HEAVYPOLY_HOTKEYS.unregister()
            HEAVYPOLY_HOTKEYS.register()
        except Exception as e:
            self.report({'ERROR'}, "Could not rebuild the keymap: %r" % (e,))
            return {'CANCELLED'}

        self.report({'INFO'}, "Keymap reset to the HEAVYPOLY defaults.")
        return {'FINISHED'}


class HP_OT_setup_load_autosave(Operator):
    """Load the keymap saved automatically before the last repair"""
    bl_idname = "hp.setup_load_autosave"
    bl_label = "Load Auto-Saved Keymap"

    @classmethod
    def poll(cls, context):
        return os.path.exists(_keymap_autosave_path())

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        path = _keymap_autosave_path()
        try:
            bpy.ops.preferences.keyconfig_import(filepath=path, keep_original=True)
        except Exception as e:
            self.report({'ERROR'}, "Could not load the keymap: %r" % (e,))
            return {'CANCELLED'}

        name = os.path.splitext(os.path.basename(path))[0]
        imported = context.window_manager.keyconfigs.get(name)
        if imported is not None:
            context.window_manager.keyconfigs.active = imported
        self.report({'INFO'}, "Auto-saved keymap restored.")
        return {'FINISHED'}


class HP_OT_setup_open_config(Operator):
    """Open the folder where Blender keeps its settings"""
    bl_idname = "hp.setup_open_config"
    bl_label = "Open Blender Settings Folder"

    def execute(self, context):
        # Two levels up from .../<version>/config is the folder holding every
        # installed version. Deleting the version folder is the real reset.
        folder = os.path.dirname(os.path.dirname(_config_dir()))
        try:
            bpy.ops.wm.path_open(filepath=folder)
        except Exception as e:
            self.report({'ERROR'}, "Could not open %s: %r" % (folder, e))
            return {'CANCELLED'}
        self.report({'INFO'}, folder)
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
        except Exception as e:
            self.report({'ERROR'}, "Restore failed: %r" % (e,))
            return {'CANCELLED'}

        # Calling wm.read_userpref() here used to disable this very add-on
        # while its classes were still registered, which made re-enabling it
        # fail with "already registered as a subclass". Restarting is clean.
        self.report({'WARNING'}, "Restored. Restart Blender to apply.")
        return {'FINISHED'}


# ---------------------------------------------------------------- preferences


class HP_OT_copy_diagnostic(Operator):
    """Run the HP_Check diagnostic and copy the report to the clipboard"""
    bl_idname = "hp.copy_diagnostic"
    bl_label = "Copy Diagnostic Report"

    def execute(self, context):
        path = os.path.join(_package_dir(), "HP_Check.py")
        if not os.path.exists(path):
            self.report({'ERROR'}, "HP_Check.py is missing from the add-on.")
            return {'CANCELLED'}
        # HP_Check is written to run from the Text Editor; executing it here
        # builds the same module-level `report` string, which is all we need.
        namespace = {"__name__": "HP_Check", "__file__": path}
        try:
            source = open(path, encoding="utf-8").read()
            exec(compile(source, path, "exec"), namespace)
        except Exception as e:
            self.report({'ERROR'}, "Diagnostic failed: %r" % (e,))
            print("[HEAVYPOLY] HP_Check failed: %r" % (e,))
            return {'CANCELLED'}
        report = namespace.get("report") or "\n".join(namespace.get("lines", []))
        if not report:
            self.report({'ERROR'}, "Diagnostic produced no output.")
            return {'CANCELLED'}
        context.window_manager.clipboard = report
        self.report({'INFO'},
                    "Report copied - paste it to your teacher (Ctrl+V).")
        return {'FINISHED'}


class HP_OT_setup_whats_new(Operator):
    """What changed in recent HEAVYPOLY updates"""
    bl_idname = "hp.setup_whats_new"
    bl_label = "HEAVYPOLY - What's New"

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=440)

    def draw(self, context):
        col = self.layout.column()
        prefs = _prefs()
        entries = _whats_new_entries(prefs) if prefs else []
        if not entries:
            entries = list(WHATS_NEW[:1])   # opened by hand: show the latest
        for version, lines in entries:
            col.label(text="Version %s" % version, icon='INFO')
            for line in lines:
                col.label(text="      " + line)
            col.separator()
        col.label(text="Keymap and preference changes need Apply All.",
                  icon='ERROR')

    def execute(self, context):
        prefs = _prefs()
        if prefs:
            prefs.seen_version = _addon_version()
            try:
                bpy.ops.wm.save_userpref()
            except Exception as e:
                print("[HEAVYPOLY] could not save preferences: %r" % (e,))
        return {'FINISHED'}


def _whats_new_popup():
    """Show the changelog once after an update. Runs from a timer.

    Closing the popup with OK records the version; clicking it away does
    not, so it reappears on the next start. That is deliberate.
    """
    prefs = _prefs()
    if prefs is None:
        return 0.5   # preferences not registered yet, try again shortly
    if not prefs.applied_version:
        return None  # brand-new install; the first-run dialog covers it
    current = _addon_version()
    if (_version_tuple(prefs.seen_version or prefs.applied_version)
            >= _version_tuple(current)):
        return None
    if prefs.applied_version != current:
        # An update is pending. Showing the popup now buries it under the
        # Preferences window and the first click kills it - wait until
        # Apply All has run and the new file is open, then show it.
        return 5.0
    if not _whats_new_entries(prefs):
        prefs.seen_version = current   # nothing listed for this jump
        return None
    # Timers run without a window in their context, and invoke_props_dialog
    # refuses to open without one - that is why the 1.21.0 popup never
    # appeared. Borrow the first window.
    wm = bpy.context.window_manager
    if not wm.windows:
        return 0.5
    try:
        with bpy.context.temp_override(window=wm.windows[0]):
            bpy.ops.hp.setup_whats_new('INVOKE_DEFAULT')
    except Exception as e:
        print("[HEAVYPOLY] what's new popup failed: %r" % (e,))
    return None


def _first_run_setup():
    """Set everything up the first time the add-on is enabled.

    Runs from a timer so Blender has finished booting. Apply All opens a new
    file at the end, which is the finished state; installing mid-session is
    guarded by the confirmation inside Apply All itself.
    """
    prefs = _prefs()
    if prefs is None:
        return 0.5   # preferences not registered yet, try again shortly
    if prefs.applied_version:
        return None  # already set up at some point

    print("[HEAVYPOLY] first run - applying setup")
    try:
        bpy.ops.hp.setup_apply_all('INVOKE_DEFAULT')
    except Exception as e:
        print("[HEAVYPOLY] first run setup failed: %r" % (e,))
    return None


class HEAVYPOLY_Preferences(AddonPreferences):
    bl_idname = __package__

    show_manual: BoolProperty(
        name="Manual Setup",
        default=False,
    )
    show_trouble: BoolProperty(
        name="Troubleshooting",
        default=False,
    )
    applied_startup: BoolProperty(default=False)
    applied_workspaces: BoolProperty(default=False)
    applied_version: StringProperty(default="")
    # Last version whose What's New popup was dismissed with OK. Kept apart
    # from applied_version, which tracks the setup state - closing the popup
    # must not silence the "Apply All to get the new keymap" banner.
    seen_version: StringProperty(default="")

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

        # Always reachable, not only right after an update - pressing
        # Apply All used to make the only What's New button vanish.
        box.operator("hp.setup_whats_new", text="What's New", icon='INFO')

        col = layout.column()
        col.scale_y = 2.0
        col.operator("hp.setup_apply_all", icon='CHECKMARK')

        layout.separator()

        # --- individual setup steps ---
        header = layout.row()
        header.prop(self, "show_manual",
                    icon='TRIA_DOWN' if self.show_manual else 'TRIA_RIGHT',
                    emboss=False)
        if self.show_manual:
            box = layout.box()
            col = box.column(align=True)
            col.operator("hp.setup_apply_keymap", icon='KEYINGSET')
            col.operator("hp.setup_apply_preferences", icon='PREFERENCES')
            col.operator("hp.setup_install_startup", icon='FILE_BLEND')
            col.operator("hp.setup_load_workspaces", icon='WORKSPACE')
            col.operator("hp.setup_replace_workspaces", icon='WORKSPACE')
            box.label(text="Save your own File > Defaults > Save Startup File "
                           "afterwards to override it.", icon='INFO')

        # --- rescue tools, kept apart from the setup steps ---
        header = layout.row()
        header.prop(self, "show_trouble",
                    icon='TRIA_DOWN' if self.show_trouble else 'TRIA_RIGHT',
                    emboss=False)
        if self.show_trouble:
            # Grouped mild-to-drastic, each with a line on when to use it.
            # This section used to be one undifferentiated pile of buttons.
            box = layout.box()
            box.label(text="Something wrong? Start here:", icon='QUESTION')
            box.operator("hp.copy_diagnostic", icon='COPYDOWN')
            box.label(text="One click, then paste the report to your teacher.")

            box = layout.box()
            box.label(text="Your own shortcuts:", icon='KEYINGSET')
            row = box.row(align=True)
            row.operator("hp.setup_save_keymap", icon='FILE_TICK')
            row.operator("hp.setup_load_keymap", icon='FILE_REFRESH')
            box.label(text="Save before updating if you changed any keys.")

            box = layout.box()
            box.label(text="Keys acting strange?", icon='ERROR')
            col = box.column(align=True)
            col.operator("hp.setup_cleanup", icon='BRUSH_DATA')
            col.operator("hp.setup_reset_keymap", icon='LOOP_BACK')
            col.operator("hp.setup_load_autosave", icon='RECOVER_LAST')
            hints = box.column(align=True)
            hints.label(text="Clean Up - one key triggers two things at once.")
            hints.label(text="Reset - shortcuts are a mess, start over fresh.")
            hints.label(text="Auto-Saved - undo a repair that made it worse.")

            box = layout.box()
            box.label(text="Last resort:", icon='TRASH')
            box.operator("hp.setup_restore", icon='TRASH')
            box.label(text="Back to how everything was before HEAVYPOLY.")
            box.operator("hp.setup_open_config", icon='FILE_FOLDER')
            box.label(text="Close Blender, then delete the version folder "
                           "for a full reset.")

            if not os.path.exists(_backup_path()):
                box.label(text="No backup yet. One is made the first time "
                               "you set up.", icon='INFO')


classes = (
    HP_OT_setup_apply_keymap,
    HP_OT_setup_apply_preferences,
    HP_OT_setup_install_startup,
    HP_OT_setup_load_workspaces,
    HP_OT_setup_replace_workspaces,
    HP_OT_setup_apply_all,
    HP_OT_setup_save_keymap,
    HP_OT_setup_load_keymap,
    HP_OT_setup_cleanup,
    HP_OT_setup_reset_keymap,
    HP_OT_setup_load_autosave,
    HP_OT_setup_open_config,
    HP_OT_setup_restore,
    HP_OT_copy_diagnostic,
    HP_OT_setup_whats_new,
    HEAVYPOLY_Preferences,
)

_register_classes, _unregister_classes = bpy.utils.register_classes_factory(classes)


def register():
    _register_classes()
    # Blender is still booting when add-ons register, so defer the dialogs.
    bpy.app.timers.register(_first_run_setup, first_interval=1.0)
    bpy.app.timers.register(_whats_new_popup, first_interval=2.0)


def unregister():
    for timer in (_first_run_setup, _whats_new_popup):
        if bpy.app.timers.is_registered(timer):
            bpy.app.timers.unregister(timer)
    _unregister_classes()
