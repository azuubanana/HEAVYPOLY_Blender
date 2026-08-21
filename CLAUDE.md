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

A correct build reports **34 files, 0.6 MB** (was 33 before
`HEAVYPOLY_screencast_keys.py`, 32 before `HEAVYPOLY_panel_tools.py` in
1.20.0). If the count or size jumps, something that should be excluded got
swept in.

Students install by adding this repository URL once:

```
https://azuubanana.github.io/HEAVYPOLY_Blender/index.json
```

Blender then handles updates. On first enable the add-on applies itself
automatically (keymap, preferences, startup file) and opens a new file.

### Beta channel

`python build_release.py 1.20.0 --beta` writes to `docs/beta/` instead —
`https://azuubanana.github.io/HEAVYPOLY_Blender/beta/index.json`. It never
touches `blender_manifest.toml`, `README.md` or `docs/index.json` on disk
(only the copy of the manifest packed inside the beta zip gets the version
bump), so pushing a beta build can't affect students on the real repository.
That means a beta push doesn't need the same caution an official release
does.

```
python build_release.py 1.20.1 --beta
git add docs/beta && git commit -m "Beta 1.20.1" && git push
```

Add the beta URL once in Preferences > Get Extensions > Repositories and
Blender's normal "Check for Updates" picks up new beta builds — no manual
zip handling. Bump the version on every beta rebuild, even a small fix, or
Blender won't see it as an update (it compares version strings, not
content). Whichever version was last approved on the beta channel is the
one to build again without `--beta` to promote it to the real release.

Workflow in practice (Azusa's preference, August 2026): she lives on the
beta channel going forward, testing every iteration from there. Claude
builds and pushes beta freely, bumping the version each time — that part
never needs to wait for a go-ahead, since it can't reach students. Only the
final official push (no `--beta`) needs her explicit "this is legit, ship
it", since that's the one students actually receive. Source code for a
feature under beta testing stays on its own branch and is only merged into
`master` at that final promotion — so `master`'s tracked source doesn't
carry half-finished work while it's still being tried out.

### The `.git`-in-the-zip trap

`build_release.py` excludes a `.git` *directory*. In a normal clone that's
enough — but in a **git worktree**, `.git` is a plain text file (a `gitdir:
...` pointer), not a directory, so the directory-only filter didn't catch it
and it was silently getting zipped up as a top-level file when a beta build
was tried from a Claude Code worktree. Both `EXCLUDE_DIRS` and
`EXCLUDE_FILES` list it now. Found by actually inspecting a test build's
file list — a reminder that "the file count matches" is a cheaper check
than it looks, but "open the zip and read the file list" is the one that
actually catches this class of bug.

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

**An in-place extension update can leave a half-registered state.** After
updating 1.27→1.28 the preferences section vanished and Ctrl+Space went
dead; the code was fine — a restart fixed everything. The update reloads
modules in a live session, and sometimes that lands halfway. First response
to "something broke right after an update" is always: restart Blender,
then diagnose.

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
  1.25.0: the grid is built PER ISLAND (one shared grid webbed neighbouring
  leaves together — cells touching two islands bridged them), pixels are
  labelled by island via point-in-polygon against the raw outlines, and a
  Separate Islands checkbox in the redo panel splits pieces with per-piece
  origins. Cut Out cannot run on an already-separated piece — it always
  rebuilds from the whole image; that is why the option lives inside it.
  1.26.0–1.27.0 tried to tighten the grid rim (inside-corner snapping,
  outline midpoints, debris culling) and **made it worse**: more moving
  verts meant more crossings and flipped faces, and culling the debris
  disconnected the mesh, which Separate Islands then turned into a pile of
  objects. 1.28.0 rolled the rim back to the 1.25 behaviour Azusa preferred
  (outside-corner snap only). Lesson: on soft-brushed outlines, every extra
  vertex you move is a new chance to self-intersect — keep the snapping
  minimal and let the texture's alpha hide the rest. 1.27.0's Show
  Wireframe option survived the rollback. Pixel Error is Triangles-only
  since 1.28.0 (in grid mode it only degraded the snap targets), and the
  tuning props are SKIP_SAVE so experiments don't leak into the next run.

**Backspace-to-reset does not work in redo panels.** Azusa hit this tuning
the cut-out: hovering a value in the F9 panel and pressing Backspace does
nothing. Blender limitation, not ours — nothing to hook from an add-on.
Workaround: run the operator again from the panel button; invoke re-derives
the auto values (channel, background, cutoff) from the image.
- **N-panel tab.** Confirmed working (1.20.x): `HP Tools` sidebar tab
  (`HEAVYPOLY_panel_tools.py`). 1.21.0 added `Separate Islands` and
  `Copy Diagnostic Report` (runs HP_Check, clipboard) plus a What's New
  popup after updates — those still need verifying. Can be switched off
  entirely from Preferences (`enable_hp_tools_panel`, checked in the panel's
  `poll()`) — added August 2026 so a feature being tried out in the panel
  doesn't have to be visible to everyone while it's still unverified.
- **Tab conflict — fixed, confirmed.** The 1.20.0 idname-match disable did
  nothing on Azusa's machine; 1.20.1's `disable_stock_tab()` (match by key,
  both keyconfigs) works — she confirmed Tab toggles subdiv on the first
  press. Side effect: the disable reads as a user edit, see
  `INTENTIONAL_DISABLES` in `HEAVYPOLY_setup.py`.
- **Tutorial-recording mode.** Azusa's idea (July 2026): one toggle that
  preps Blender for recording a tutorial — big visible mouse pointer, keys
  on screen. 1.29.0 shipped the ingredients (Screencast Keys helper button,
  save reminder); the giant-pointer part is NOT solved: Blender cannot
  resize the OS cursor, so the honest options are the OS accessibility
  setting (recommended to her) or a custom modal overlay that follows the
  mouse (fragile, only draws inside its own area — do not attempt casually,
  see the 1.26/1.27 lesson). Never bundle Screencast Keys itself: GPL — that
  is a licensing mechanic (GPL requires anything it's mixed into to become
  GPL too), not a call Azusa made personally; don't attribute the reasoning
  to her in future notes, just state the constraint.
  **August 2026 — confirmed broken, not just "not yet tried":** Azusa
  dragged the real Screencast Keys zip onto Blender 5.2.0/windows-x64 and
  got "The extension dropped was not found in the remote repository" from
  the `extensions.blender.org` install dialog. The add-on's own
  `blender_manifest.toml` declares `blender_version_min = "4.2.0"` with no
  upper bound, so this is `extensions.blender.org`'s own listing rejecting
  5.2 (an upstream indexing gap), not a bug in HEAVYPOLY or user error.
  Added `HEAVYPOLY_screencast_keys.py` as a from-scratch, MIT, in-add-on
  key/mouse overlay (blf-only draw handler + a background modal operator
  that PASS_THROUGHs every event, so it can't eat a shortcut) as a stopgap
  next to the existing helper button in the "Recording / Teaching" section —
  never read the GPL source, see the module's own docstring. Switch back to
  recommending the real extension once its listing installs cleanly on 5.2
  again. Unverified in Blender; test via the beta channel before promoting.
- **Random Island Colors.** Beta 1.31.4 (August 2026). 1.31.2 confirmed
  working by Azusa (bake + auto material on bare objects); she then asked
  for the node to appear in the Shader Editor by itself. 1.31.3 auto-
  connected it into Base Color; she preferred it merely *placed*, so
  1.31.4 made it an enum, In Materials: Place Node (default — drop the
  Color Attribute node next to the Principled BSDF, unconnected, material
  look unchanged) / Connect (also replace Base Color's input) / Nothing.
  Idempotent — re-runs reuse the node instead of stacking copies. EEVEE
  still does not support the shader Geometry node's Random Per Island
  output (Cycles only, confirmed against the 5.2 manual), so
  `object.hp_random_island_colors` (HP Tools > Color) bakes a finished
  random color per connected island into a `POINT`/`FLOAT_COLOR` color
  attribute named `Island Colors` — union-find over the edges, hues walked
  by golden ratio from a seeded start so few-island meshes still get
  well-separated colors. Redo panel: Seed, Saturation, Brightness, Show in
  Solid View (flips the viewport to Attribute coloring), Add Material If
  Missing (shared `HP Island Colors` material: Color Attribute node →
  Principled Base Color — only added when the object has zero materials).
  Re-running overwrites only that attribute; hand-painted attributes are
  untouched. Source lives on `claude/eevee-random-color-per-island-8bcb09`
  until promotion.
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
