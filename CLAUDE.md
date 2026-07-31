# CLAUDE.md — working notes for this repository

Context for anyone (human or AI) picking this up. Read this before changing code.

---

## What this repository is

A fork of [HEAVYPOLY](https://github.com/HEAVYPOLY/HEAVYPOLY_Blender) by Vaughan
Ling, updated for **Blender 5.2** and repackaged as an extension.

The lineage is:

```
HEAVYPOLY/HEAVYPOLY_Blender     original, MIT, last targeted ~3.6-4.0
  └─ Renart84/HEAVYPOLY_Blender  community fork for 4.1-4.5
       └─ this fork              5.2, restructured as an extension
```

**Licence is MIT.** Keep `LICENSE.md` and the `Copyright (c) 2022 Vaughan Ling`
line intact. Do not paste in code from GPL add-ons — that would force the whole
fork to GPL. Algorithms and ideas are fine; copied source is not.

**Who uses it.** Azusa Tojo teaches a Japanese-language Blender course; the
students are the primary audience. Most of them are beginners and many are on
macOS. Anything that adds a manual step, a hidden folder, or an OS-specific
instruction costs real support time.

---

## Structure

The add-on files sit at the repository root (that is what an extension zip
wants — `blender_manifest.toml` must be at the archive root).

```
blender_manifest.toml    extension manifest; version lives here
__init__.py              imports every module and registers them in order
HEAVYPOLY_*.py           the add-on itself
HP_Nodes.blend           geometry node groups used by the Specials pie
HP_Startup.blend         shipped startup file (5.2, contains "HP Modeling")
HP_Check.py              standalone diagnostic, not imported by the add-on
build_release.py         release tool — NOT part of the add-on
docs/                    GitHub Pages: the extension repository
  index.json             what Blender reads
  heavypoly-<ver>.zip    the built add-on
```

`docs/` and `build_release.py` are excluded from the zip by `build_release.py`.

---

## Releasing

From the repository root:

```
python build_release.py 1.20.0
git add -A && git commit -m "Release 1.20.0" && git push
```

That bumps the manifest, builds `docs/heavypoly-<ver>.zip`, hashes it,
regenerates `docs/index.json`, and deletes the previous zip. **Never hand-edit
`docs/index.json`** — the hash has to match the archive or installs fail.

A correct build reports **33 files, 0.6 MB** (was 32 before
`HEAVYPOLY_panel_tools.py` in 1.20.0). If the count or size jumps,
something that should be excluded got swept in.

Students install by adding this repository URL once:

```
https://azuubanana.github.io/HEAVYPOLY_Blender/index.json
```

Blender then handles updates. On first enable the add-on applies itself
automatically (keymap, preferences, startup file) and opens a new file.

---

## Hard-won knowledge

Things that cost hours to work out. Please don't re-derive them.

### Blender API changes that bit us

| Symptom | Cause |
|---|---|
| Two whole files silently missing | `bgl` was **removed in 5.0**. `import bgl` at the top killed `draw_primitives` and `select_through_border` |
| Specials pie laid out wrong | Blender **silently skips** layout items whose operator doesn't exist, so every slot after the missing one shifts by one position |
| Auto Smooth broken | 4.1 turned it into an Essentials node group. Use `bpy.ops.object.shade_auto_smooth()`; never hard-code the asset path or socket ids (`Input_1` etc. change between versions) |
| Console flooded | EEVEE Next dropped `shadow_cube_size`, `shadow_cascade_size`, `use_shadow_high_bitdepth`, `use_soft_shadows`, `shadow_buffer_bias`. Panels warned on every redraw |
| Sculpt symmetry did nothing | **`tool_settings.sculpt.use_symmetry_*` still exists in 5.2 but is inert.** The Symmetry panel reads `mesh.use_mirror_*`. Check the mesh first |
| Paint panels erroring | 5.0 moved `unified_paint_settings` onto the mode-specific `Paint` struct |
| Transparency flicker | 4.2 replaced `blend_method` with `surface_render_method`; `DITHERED` avoids sort artefacts, `BLENDED` does not |
| GP operators missing | GPv3 (4.3) renamed `gpencil.*` to `grease_pencil.*`. There is no `_pick` variant of `select_linked` |

### Traps specific to this add-on

**`hasattr(bpy.ops.x, "y")` is always True.** `bpy.ops` resolves lazily. To test
whether an operator exists, call it and catch the exception.

**Modal keymaps cannot go in the add-on keyconfig.** Blender raises
"Modal key-maps not supported for add-on key-config". `Space` = Y-axis lock is
therefore done by repurposing the stock `CONFIRM` entry in the *user*
keyconfig, and put back on unregister.

**Register hotkeys last.** `kmi.properties.axis = 'X'` silently fails if the
operator isn't registered yet — you get `property 'axis' not found` warnings and
every binding falls back to its default. `__init__.py` calls
`HEAVYPOLY_HOTKEYS.register()` after every other module for this reason.

**`unregister()` used to re-register.** The original code called
`Keymap_Heavypoly()` from `unregister()`, stacking another copy of every
shortcut on each reload. One user ended up with 25 bindings on `E` and 17
duplicate workspaces. `register()` now clears `addon_keymaps` first.

**A failed `register()` leaves classes behind.** Blender switches the add-on off
but does not call `unregister()`, so re-enabling fails with "already registered
as a subclass". `register()` now calls `unregister()` on its own exception.

### Keymap conflicts — the recurring one

HEAVYPOLY binds over Blender's defaults but does not always remove them. When
two items share a key **inside the same keymap**, both fire.

Found and fixed so far:

| Key | Blender's entry | Effect before |
|---|---|---|
| `E` (Mesh) | `view3d.edit_mesh_extrude_move_normal` | Double extrude, vertex followed the mouse |
| `Z` (3D View) | `VIEW3D_MT_shading_pie` | Two pies at once |
| `Ctrl+Shift+X` (paint modes) | `paint.sample_color` | Symmetry toggle never reached |
| `Space` (Transform Modal) | `CONFIRM` | Y-axis lock impossible |
| `Tab` (Object Non-modal) | `object.editmode_toggle` | First press entered Edit Mode (making the Outliner's mode-dot column appear); subdiv toggle only fired from the second press. Object Non-modal is checked before the generic 3D View keymap, but after Mesh — hence the press-count asymmetry |

**How to diagnose:** Preferences > Keymap, `Key-Binding` tab, type the chord.
Entries under *different* keymaps (Mesh vs Sculpt vs 3D View) are fine — those
are different modes. Two entries under the *same* keymap heading are the bug.

`wm.call_menu_pie` needs `disable_pie_kmi()`, which matches on the menu name;
matching on the operator alone would disable our own pie too.

**Beware the keymap named `Grease Pencil`.** It is the annotation keymap and is
live in the 3D View in *every* mode. Registering a double click there ate the
mesh double click. Use `Grease Pencil Edit Mode`.

**Disabling by idname in the default keyconfig can silently miss.** The
`disable_*` helpers edit `keyconfigs['Blender']` and match on the operator
name. For Tab in `Object Non-modal` that did nothing on a real 5.2 install —
either the idname differs from 4.x or the entry that actually fires is the
copy in `keyconfigs.user`. `disable_stock_tab()` matches by key alone, skips
our own binding, covers both keyconfigs, and prints what it switched off.
If another disable ever "doesn't take", suspect the same two causes first.

**Our own disables read as user edits.** Disabling a stock item in
`keyconfigs.user` marks it `is_user_modified`, so the preferences panel said
"1 shortcut(s) changed from the defaults" forever (survives reinstalls —
the disable is re-applied on every register). `_modified_keymap_count()`
now skips entries listed in `INTENTIONAL_DISABLES`; add to that list when
disabling anything else in the user keyconfig.

**HP_Check must know about extension paths.** `bpy.utils.script_paths()`
does not include `.../<version>/extensions/`, so on a normal extension
install the report said "0 files found" while everything worked. It now
also walks `user_resource('EXTENSIONS')` and the directories of loaded
`bl_ext.*.HEAVYPOLY_*` modules, and matches module names on the last dotted
part.

### Cleaning up duplicates

`Clean Up Duplicates` compares keymap items including their **properties**. An
earlier version ignored properties, decided every `wm.call_menu_pie` binding was
the same item, and deleted nearly every HEAVYPOLY shortcut. If you touch that
signature function, keep the properties in it.

---

## Design decisions and why

**Extension, not a config folder.** The old install meant copying folders into
`AppData` (hidden) or `Blender.app/Contents/Resources` (needs "Show Package
Contents"). That was where beginners gave up. One repository URL replaces it.

**Setup applies itself on first enable.** No dialog, no hunting through the
Add-ons tab. It opens a new file at the end, because the startup file is only
visible in a fresh scene — applying without reloading produced a half-applied
state that confused people.

**The startup file is copied on disk, not loaded.** `Set Up HEAVYPOLY` copies
`HP_Startup.blend` over `config/startup.blend`. The current scene is untouched;
`File > New` picks it up. Users can override with
`File > Defaults > Save Startup File` afterwards.

**Two keymap backups, deliberately separate.** `HP_keymap_backup.py` is the
user's manual save; `HP_keymap_autosave.py` is written automatically before any
destructive repair. Sharing one file meant a rescue could overwrite the good
copy.

**`Reset Keymap to HP Default` calls `restore_to_default()` per keymap.**
`bpy.ops.preferences.keyconfig_restore()` did nothing in 5.2. Without the
per-keymap reset, anything deleted from the stock keymap stayed deleted.

**No Japanese in the UI.** Deliberate — the students are learning Blender in
English so that tutorials and error messages are searchable.

---

## Open work

- **macOS verification.** Nothing here has been tested on a Mac yet. Most
  students are on macOS and historically that is where HEAVYPOLY broke.
- **macOS keymap adaptation.** Cmd (`oskey`) instead of Ctrl where it makes
  sense. Blanket replacement is unsafe — `Ctrl+S` and friends would collide.
  Needs a list of the chords that actually hurt on a Mac. **On hold by
  Azusa's request (July 2026): she wants to work through it together when
  she has time, since it needs her Mac for testing. Don't start it solo.**
- **Cut-out meshes.** Confirmed working by Azusa (1.20.x). Shipped as
  `Cut Out to Mesh` (`object.hp_cutout_mesh`): contour tracing, not the grid
  approximation originally planned — Azusa asked for the Leafig-style result.
  Written from scratch; the Leafig zip was deliberately never opened (paid
  add-on, GPL). 1.21.0 added Inset (mask erosion), Origin (Keep/Center/
  Bottom), Thickness (managed Solidify) and `Separate Islands`. 1.23.0 made
  the cutoff per-image (Otsu; fixed 0.5 shredded pale soft-brushed images),
  guessed the background from the image border, and added Min Size. 1.24.0
  added Fill = Grid (Quads): integral-image cell coverage, rim corners
  snapped to the traced outline (only within 1.5 cells, so filled pinholes
  don't yank verts to the silhouette) — for pieces that get animated.
- **N-panel tab.** Confirmed working (1.20.x): `HP Tools` sidebar tab
  (`HEAVYPOLY_panel_tools.py`). 1.21.0 added `Separate Islands` and
  `Copy Diagnostic Report` (runs HP_Check, clipboard) plus a What's New
  popup after updates — those still need verifying.
- **Tab conflict — fixed, confirmed.** The 1.20.0 idname-match disable did
  nothing on Azusa's machine; 1.20.1's `disable_stock_tab()` (match by key,
  both keyconfigs) works — she confirmed Tab toggles subdiv on the first
  press. Side effect: the disable reads as a user edit, see
  `INTENTIONAL_DISABLES` in `HEAVYPOLY_setup.py`.
- **Old Releases.** `v1.2.1` on the Releases page still has the pre-extension
  layout. Delete it or mark it deprecated so nobody installs it by hand.
- **UV workflow.** Unrelated to the add-on so far, but the reason several of
  these features exist: sphere projection mangles UVs on concave areas (lips,
  eyelids) of head meshes built from many spheres. Colour attributes and Grease
  Pencil sidestep UVs entirely, which is why `Draw with GP` and the clipboard
  paste exist.

---

## Working style that has been effective

Blender cannot be run from the assistant side, so **every fix is a hypothesis
until Azusa confirms it**. What has worked:

1. State the suspected cause explicitly before changing anything.
2. Prefer changes that report what they did — the symmetry operator prints
   `toggled Mesh.use_mirror_x -> True`, which is how the inert
   `tool_settings.sculpt` property was finally caught.
3. Ask for the system console output. `HP_Check.py` exists for the same reason.
4. Failing loudly beats failing silently. Guarded lookups print a `[HEAVYPOLY]`
   line rather than swallowing the error.

For feature requests Azusa prefers: list the interpretations, offer options with
a recommendation and the trade-offs, ask the open questions, then implement once
she confirms. She will say when to skip that and just build.
