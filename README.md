
# HEAVYPOLY for Blender

Custom scripts and pie menus to make Blender faster and easier to use — designed for pen tablet or mouse. Works well for both left- and right-handed artists.

---

## 🔧 Blender 5.2 Update (fork)

This copy targets **Blender 5.2 LTS only**. Legacy 2.79 / 4.x code paths have been removed.
Original work © 2022 Vaughan Ling, MIT licensed — see `LICENSE.md`.

### Fixed

- **Removed `import bgl`** (`draw_primitives`, `select_through_border`). The BGL module was
  deleted in Blender 5.0, so both files failed to import and every operator inside them
  vanished. This also restores the Specials pie layout — the missing *Draw Primitives*
  entry was shifting all later slots by one position.
- **`blf.size()`** no longer takes a DPI argument (changed in 4.0).
- **Auto Smooth** now uses `bpy.ops.object.shade_auto_smooth()` instead of hard-coding the
  Essentials asset path and the node group's socket identifiers.
- **`Mesh.use_auto_smooth` / `auto_smooth_angle`** removed (gone since 4.1).
- **Keymap registration hardened.** Missing keymaps used to raise and abort `register()`
  part-way, leaving Blender's conflicting default shortcuts active. Lookups now warn and
  continue.
- **`unified_paint_settings`** moved to the mode-specific `Paint` struct in 5.0.
- **`paint.brush_select`**: `sculpt_tool` renamed to `sculpt_brush_type`.
- **Camera DOF panel** in `_menu_master` was still on the 2.79 `gpu_dof` API.
- **GP Canvas** (Front / Top / Side) assigned to a local variable and did nothing.
- *Keys Viewer* commented out — it needs the external Screencast Keys add-on.

### Added

- **Draw with GP** — Ctrl+Space → bottom-right column. Creates a new Grease Pencil object
  and drops straight into draw mode.
  - Nothing selected → placed at the 3D cursor, stroke placement **Origin**
  - Object selected → placed at that object and **parented** to it, stroke placement
    **Surface** with a 0.015 m offset (stops strokes sinking into the mesh)
  - Drawing plane is locked to **View** in both cases
  - Materials `Pencil`, `Halftone` and `Fill` are attached (reused if already present) and
    the brush is switched to vertex colour

### Note

`config/startup.blend` and `config/userpref.blend` are still the 4.5 / 4.3 files.
Open them in 5.2 and re-save if you want them fully converted.

---

## 💾 Installation (Blender 5.2)

**Drag `HEAVYPOLY_5.2.zip` onto the Blender window.** That's it.

Blender will ask you to confirm, then install it as an extension.

Then open **Edit > Preferences > Add-ons > HEAVYPOLY** and press **Apply All**.
That installs the HEAVYPOLY startup file (so **File > New** opens in the
HEAVYPOLY layout, with the HP Modeling workspace), turns off the pie menu
unfold animation, and adds the workspaces to whatever file you have open right
now. The keymap is already active as soon as the add-on is enabled.

Your previous `startup.blend` is backed up first. If you later want your own
default scene, just set it up and use **File > Defaults > Save Startup File** —
that overwrites ours, which is fine.

If you'd rather do it piece by piece, expand **Manual Setup** in the same panel.
It also holds **Restore My Settings**, which puts back both the preferences and
the startup file you had before you first pressed Apply.

> ⚠️ **macOS / Safari:** if "Open safe files after downloading" is enabled,
> Safari unzips the file automatically and there is nothing left to drag.
> Turn that setting off, or use Chrome or Firefox.

### Uninstalling

Preferences > Add-ons > HEAVYPOLY > the dropdown > Uninstall. Your own settings
are untouched; use **Restore My Settings** first if you want the theme and
workspaces reverted too.

### Diagnostics

`HP_Check.py` ships inside the add-on folder. Open it in the Text Editor and
press Run Script to get a report on what is and isn't working in your Blender.
It only reads; it changes nothing.

---

## 📦 Older manual installation (Blender 4.x)

### Download Instructions

#### Blender Versions

- **Blender 5.2** — this fork
  Grab the zip from [Releases](https://github.com/azuubanana/HEAVYPOLY_Blender/releases)
  and drag it onto Blender. See **Installation** above; the folder-copying steps
  below do **not** apply.

- **Blender 4.3 and 4.5**
  [Renart84's config](https://github.com/Renart84/HEAVYPOLY_Blender)

- **Blender 4.1 and 4.2**
  [Download v1.0.0](https://github.com/Renart84/HEAVYPOLY_Blender/releases/tag/v1.0.0)

- **Blender 3.6 and 4.0**
  [Download older release](https://github.com/HEAVYPOLY/HEAVYPOLY_Blender/releases)

---

The instructions below are for **4.x only**.

### 🔹 Windows

#### For the **portable version** of Blender:
1. Open the folder where `blender.exe` is located.
2. Create a new folder named:
   ```
   portable
   ```
3. Unzip the `HEAVYPOLY Config` and copy the folders ( Config and Scripts) into the "portable" folder you just created — you should now have:
   ```
   blender-folder/
     └─ portable/
         ├─ config/
         └─ scripts/
   ```
   
#### For the **installed version** of Blender:
1. Unzip the downloaded `HEAVYPOLY Config`.
2. Copy the folders named `config` and `scripts` into:  
   ```
   C:\Users\YOURUSERNAME\AppData\Roaming\Blender Foundation\Blender\5.2\
   ```
   > ⚠️ Replace `5.2` with your actual Blender version.  
   > ⚠️ The `AppData` folder is hidden. Enable **"Show hidden files"** in your File Explorer settings to see it.




### 🔹 macOS

1. In the **Applications** folder, right-click on the Blender app and choose **"Show Package Contents"**.
2. Go to:
   ```
   Contents/Resources
   ```
3. Create a folder named:
   ```
   portable
   ```
4. Unzip the `HEAVYPOLY Config` and copy the folders ( Config and Scripts) into the "portable" folder you just created — you should now have:
   ```
   Blender.app/
     └─ Contents/
         └─ Resources/
             └─ portable/
                 ├─ config/
                 └─ scripts/
   ```

---

## 🎥 Setup Video (for Blender 3.6 – 4.1)

[Watch the installation tutorial on YouTube](https://www.youtube.com/watch?v=TRESMUenxa8)
