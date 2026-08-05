"""Built-in Screencast Keys overlay for Blender 5.2.

Draws recently pressed keyboard keys and mouse buttons in the corner of the
3D View, for recording tutorials. Toggle it from the "HP Tools" N-panel tab
(HEAVYPOLY_panel_tools.py).

Why this exists alongside HP_OT_setup_screencast (HEAVYPOLY_setup.py):
that operator helps enable the real, official Screencast Keys extension
(GPL, extensions.blender.org) - the preferred option, and the reason
nothing here is a copy of it (see CLAUDE.md on GPL). But as of testing on
1.29.0, the official extension's *listing* on extensions.blender.org
rejects install on Blender 5.2.0/windows-x64 ("not found in the remote
repository") even though its own manifest declares no upper version bound -
an upstream indexing gap, not a bug in this add-on. Until that's fixed
upstream, this from-scratch overlay is the only working option for
students on 5.2. Keep both buttons: switch back to recommending the real
extension once it installs cleanly again.

This does NOT record video or audio - nothing here can capture the screen.
It only draws the key overlay; pair it with whatever screen recorder you
already use (OBS, QuickTime, Xbox Game Bar, ...).

Written from scratch against the 5.2 API, without ever reading the GPL
extension's source. Uses blf only, no bgl (removed in 5.0, see CLAUDE.md)
and no gpu module, to keep the API surface this depends on as small as
possible.

Implementation note: a single toggle operator is used for both start and
stop. The first invocation goes modal and keeps running in the background
(PASS_THROUGH on every event, so it never intercepts a shortcut). A second
invocation - from clicking the panel button again - is a *different*
operator instance; it just flips the shared "running" flag back to False and
finishes immediately. The original modal loop notices the flag on its next
event or timer tick and tears itself down there. This is the standard way to
run a background modal operator in Blender; see HEAVYPOLY_draw_primitives.py
for the (non-background) modal + draw_handler pattern this borrows from.
"""

import time

import bpy
import blf
from bpy.props import BoolProperty, EnumProperty, IntProperty


# How long an entry stays on screen after being pressed, how many are kept
# around at once, and how long before expiry it spends fading out.
ENTRY_LIFETIME = 2.5
MAX_ENTRIES = 8
FADE_TAIL = 0.6

MODIFIER_TYPES = {
    'LEFT_SHIFT', 'RIGHT_SHIFT', 'LEFT_CTRL', 'RIGHT_CTRL',
    'LEFT_ALT', 'RIGHT_ALT', 'OSKEY',
}
MOUSE_LABELS = {
    'LEFTMOUSE': "Mouse L",
    'RIGHTMOUSE': "Mouse R",
    'MIDDLEMOUSE': "Mouse M",
}
# Events we never want to show, either because they're not a "press" a
# student made (timers, deactivate) or because scrolling was deliberately
# left out to keep the overlay from filling up during navigation.
IGNORED_TYPES = {
    'MOUSEMOVE', 'INBETWEEN_MOUSEMOVE', 'TIMER', 'TIMER0', 'TIMER1',
    'TIMER_REPORT', 'TIMER_JOBS', 'TIMER_AUTOSAVE', 'WINDOW_DEACTIVATE',
    'TEXTINPUT', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE', 'WHEELINMOUSE',
    'WHEELOUTMOUSE', 'NDOF_MOTION', 'MOUSESMARTZOOM',
    'ACTIONZONE_AREA', 'ACTIONZONE_REGION', 'ACTIONZONE_FULLSCREEN', 'NONE',
}
KEY_LABELS = {
    'SPACE': "Space", 'RET': "Enter", 'NUMPAD_ENTER': "Enter", 'ESC': "Esc",
    'TAB': "Tab", 'BACK_SPACE': "Backspace", 'DEL': "Delete",
    'LEFT_ARROW': "←", 'RIGHT_ARROW': "→",
    'UP_ARROW': "↑", 'DOWN_ARROW': "↓",
    'PERIOD': ".", 'COMMA': ",", 'SEMI_COLON': ";", 'QUOTE': "'",
    'MINUS': "-", 'EQUAL': "=", 'SLASH': "/", 'BACK_SLASH': "\\",
    'LEFT_BRACKET': "[", 'RIGHT_BRACKET': "]", 'GRAVE': "`",
    'ZERO': "0", 'ONE': "1", 'TWO': "2", 'THREE': "3", 'FOUR': "4",
    'FIVE': "5", 'SIX': "6", 'SEVEN': "7", 'EIGHT': "8", 'NINE': "9",
}

# Module-level so a fresh operator invocation (the "stop" click) can signal
# the already-running instance without holding a reference to it.
_state = {"handle": None, "timer": None, "history": []}


def _key_label(event_type):
    if event_type in KEY_LABELS:
        return KEY_LABELS[event_type]
    if event_type.startswith("NUMPAD_"):
        return "Numpad " + event_type[len("NUMPAD_"):].replace('_', ' ').title()
    return event_type.replace('_', ' ').title()


def _chord_label(event):
    base = MOUSE_LABELS.get(event.type) or _key_label(event.type)

    mods = []
    if event.ctrl:
        mods.append("Ctrl")
    if event.alt:
        mods.append("Alt")
    if event.shift:
        mods.append("Shift")
    if event.oskey:
        mods.append("Cmd")
    if mods:
        return " + ".join(mods) + " + " + base
    return base


def _record(event):
    if event.value != 'PRESS' or event.is_repeat:
        return
    if event.type in IGNORED_TYPES or event.type in MODIFIER_TYPES:
        return

    label = _chord_label(event)
    history = _state["history"]
    now = time.time()
    # The same physical press can arrive twice in edge cases (e.g. a
    # keymap item consuming then re-emitting it); collapse those.
    if history and history[-1]["label"] == label and now - history[-1]["time"] < 0.15:
        return
    history.append({"label": label, "time": now})
    del history[:-MAX_ENTRIES]


def _prune():
    now = time.time()
    history = _state["history"]
    history[:] = [entry for entry in history if now - entry["time"] < ENTRY_LIFETIME]


def _draw_callback():
    context = bpy.context
    region = context.region
    if region is None:
        return

    _prune()
    history = _state["history"]
    if not history:
        return

    wm = context.window_manager
    corner = wm.hp_screencast_corner
    top_half = corner.startswith('TOP')
    right_half = corner.endswith('RIGHT')

    font_size = wm.hp_screencast_font_size
    margin = 24
    line_height = int(font_size * 1.45)  # keeps entries from overlapping at any size
    font_id = 0
    blf.size(font_id, font_size)

    now = time.time()
    entries = list(reversed(history))  # newest first, closest to the corner
    for index, entry in enumerate(entries):
        remaining = ENTRY_LIFETIME - (now - entry["time"])
        alpha = 1.0 if remaining > FADE_TAIL else max(0.0, remaining / FADE_TAIL)
        text = entry["label"]

        y = (region.height - margin - line_height - index * line_height
             if top_half else margin + index * line_height)

        if right_half:
            width, _height = blf.dimensions(font_id, text)
            x = region.width - margin - width
        else:
            x = margin

        # Drop shadow so the text stays legible over any viewport content.
        blf.color(font_id, 0.0, 0.0, 0.0, alpha * 0.8)
        blf.position(font_id, x + 1, y - 1, 0)
        blf.draw(font_id, text)

        blf.color(font_id, 1.0, 1.0, 1.0, alpha)
        blf.position(font_id, x, y, 0)
        blf.draw(font_id, text)


class HP_OT_screencast_keys_toggle(bpy.types.Operator):
    """Show recently pressed keys and mouse buttons in the 3D View, for recording tutorials"""
    bl_idname = "view3d.hp_screencast_keys_toggle"
    bl_label = "Toggle Screencast Keys"

    def invoke(self, context, event):
        wm = context.window_manager
        if wm.hp_screencast_running:
            # A modal loop is already running; tell it to stop on its next
            # tick instead of reaching into it directly.
            wm.hp_screencast_running = False
            return {'FINISHED'}

        wm.hp_screencast_running = True
        _state["history"] = []
        _state["handle"] = bpy.types.SpaceView3D.draw_handler_add(
            _draw_callback, (), 'WINDOW', 'POST_PIXEL')
        _state["timer"] = wm.event_timer_add(0.1, window=context.window)
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        if not context.window_manager.hp_screencast_running:
            self._stop(context)
            return {'CANCELLED'}

        _record(event)
        if context.area:
            context.area.tag_redraw()
        return {'PASS_THROUGH'}

    def _stop(self, context):
        wm = context.window_manager
        if _state["handle"] is not None:
            bpy.types.SpaceView3D.draw_handler_remove(_state["handle"], 'WINDOW')
            _state["handle"] = None
        if _state["timer"] is not None:
            try:
                wm.event_timer_remove(_state["timer"])
            except Exception:
                pass
            _state["timer"] = None
        _state["history"] = []
        if context.screen:
            for area in context.screen.areas:
                if area.type == 'VIEW_3D':
                    area.tag_redraw()


def _force_stop():
    """Remove the draw handler even if the modal loop never gets a last
    tick to clean up after itself - e.g. the add-on is disabled mid-recording."""
    if _state["handle"] is not None:
        try:
            bpy.types.SpaceView3D.draw_handler_remove(_state["handle"], 'WINDOW')
        except Exception:
            pass
        _state["handle"] = None
    _state["timer"] = None
    _state["history"] = []


classes = (
    HP_OT_screencast_keys_toggle,
)
_register_classes, _unregister_classes = bpy.utils.register_classes_factory(classes)


def register():
    _register_classes()
    bpy.types.WindowManager.hp_screencast_running = BoolProperty(default=False)
    bpy.types.WindowManager.hp_screencast_corner = EnumProperty(
        name="Corner",
        description="Where the key overlay is drawn in the 3D View",
        items=(
            ('BOTTOM_LEFT', "Bottom Left", ""),
            ('BOTTOM_RIGHT', "Bottom Right", ""),
            ('TOP_LEFT', "Top Left", ""),
            ('TOP_RIGHT', "Top Right", ""),
        ),
        default='BOTTOM_LEFT',
    )
    bpy.types.WindowManager.hp_screencast_font_size = IntProperty(
        name="Text Size",
        description="Size of the key overlay text in the 3D View",
        default=18, min=10, max=48,
    )


def unregister():
    _force_stop()
    _unregister_classes()
    del bpy.types.WindowManager.hp_screencast_font_size
    del bpy.types.WindowManager.hp_screencast_corner
    del bpy.types.WindowManager.hp_screencast_running


if __name__ == "__main__":
    register()
