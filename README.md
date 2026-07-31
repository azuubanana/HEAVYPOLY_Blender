# HEAVYPOLY for Blender 5.2

Custom pie menus and hotkeys that make Blender faster to work in — built for pen
tablets and mice alike, and fine for both left- and right-handed artists.

This is a fork of [HEAVYPOLY](https://github.com/HEAVYPOLY/HEAVYPOLY_Blender) by
Vaughan Ling, updated for Blender 5.2 and repackaged as an extension.
MIT licensed — see [LICENSE.md](LICENSE.md).

Blender 5.2 用の HEAVYPOLY です。パイメニューとショートカットで Blender の作業を
速くします。ペンタブでもマウスでも、左利き・右利きどちらでも使えます。

Vaughan Ling 氏の HEAVYPOLY を 5.2 対応にし、拡張機能として再パッケージした
フォークです。MIT ライセンスです。

---

## Installation / インストール

### Recommended: add the repository / おすすめ：リポジトリ登録

Do this once and Blender handles updates for you.

一度登録すれば、以降は Blender が更新を扱ってくれます。

1. **Edit > Preferences > Get Extensions**
2. Click **Repositories** (top right dropdown) / 右上の **Repositories** をクリック
3. **＋ > Add Remote Repository**
4. Paste this URL / このURLを貼り付け:

   ```
   https://azuubanana.github.io/HEAVYPOLY_Blender/index.json
   ```

5. Tick **Check for Updates on Startup** / チェックを入れる
6. **Create**
7. Search for `HEAVYPOLY`, press **Install** / 検索して **Install**

That's it. The first time it's enabled, HEAVYPOLY sets up the keymap, the
preferences and the startup file, then opens a new file so you land straight in
the HP Modeling workspace.

以上です。初回有効化時に、キーマップ・設定・スタートアップファイルが自動で適用され、
新しいファイルが開いて HP Modeling ワークスペースの状態になります。

> Install it on a fresh Blender session. If you have unsaved work open you'll be
> asked to confirm first, since the setup opens a new file.
>
> 起動直後の状態でインストールしてください。作業中のファイルがある場合は確認が出ます。

### Manual download / 手動ダウンロード

Drag this zip onto the Blender window / このzipを Blender のウィンドウにドラッグ:

**https://azuubanana.github.io/HEAVYPOLY_Blender/heavypoly-1.26.0.zip**

> ⚠️ **Do not use the green Code > Download ZIP button.** It wraps everything in
> an extra folder and Blender won't recognise it.
>
> ⚠️ **緑の Code > Download ZIP は使わないでください。** 余計なフォルダが付くため、
> Blender が拡張機能として認識できません。

> ⚠️ **macOS / Safari:** with "Open safe files after downloading" on, Safari
> unzips the file and there's nothing left to drag. Turn it off, or use Chrome.
>
> ⚠️ **macOS / Safari:** 「ダウンロード後、"安全な"ファイルを開く」がオンだと zip が
> 自動解凍されます。設定をオフにするか、Chrome を使ってください。

---

## Updating / 更新

**Edit > Preferences > Get Extensions > Check for Updates**

If a new version exists an **Update** button appears. After a feature update a
dialog asks you to apply the new settings.

新しいバージョンがあれば **Update** ボタンが出ます。機能追加を含む更新のあとは、
設定を適用するかどうかのダイアログが出ます。

Bug-fix releases (1.3.0 → 1.3.1) install quietly and need no action.

バグ修正だけの更新（1.3.0 → 1.3.1）は静かに入り、操作は不要です。

---

## The setup panel / セットアップパネル

**Edit > Preferences > Add-ons > HEAVYPOLY**

**Apply All** does everything. Individual steps live under **Manual Setup**.

**Apply All** ですべて設定されます。個別の操作は **Manual Setup** の中です。

| Button | What it does / 内容 |
|---|---|
| Apply Keymap | Re-registers the shortcuts / ショートカットを再登録 |
| Apply Preferences | Pie animation off, Node Wrangler on / パイのアニメをオフ、Node Wrangler をオン |
| Install Startup File | Makes File > New open the HP layout / File > New を HP の状態に |
| Load Workspaces | Adds the HP workspaces, keeps yours / HP のワークスペースを追加 |
| Replace Workspaces | Adds them and removes the rest / 追加して他を削除 |
| Save My Keymap | Writes your shortcuts to a file / 現在のショートカットを保存 |
| Load My Keymap | Reads them back / 保存したものを読み込み |
| Restore My Settings | Rolls back to before you first applied / 適用前に戻す |

Your preferences and startup file are backed up automatically the first time you
press Apply, so **Restore My Settings** can always take you back.

初回の Apply 時に設定とスタートアップファイルが自動バックアップされるので、
**Restore My Settings** でいつでも戻せます。

If you customise shortcuts, press **Save My Keymap** so an update can't lose them.

ショートカットを変えたら **Save My Keymap** を押しておいてください。更新で消える
心配がなくなります。

You can set your own default scene afterwards with **File > Defaults > Save
Startup File** — that overwrites ours, which is fine.

**File > Defaults > Save Startup File** で自分好みのスタートアップに上書きすることも
できます。

---

## When something doesn't work / うまくいかないとき

**The quick way:** press **N** in the 3D View, open the **HP Tools** tab, and
click **Copy Diagnostic Report**. The report is now on your clipboard — paste
it (Ctrl+V) into a message to your teacher. Done.

**いちばん簡単な方法：** 3Dビューで **N** キー → **HP Tools** タブ →
**Copy Diagnostic Report** をクリック。レポートがコピーされるので、そのまま
講師へのメッセージに貼り付け（Ctrl+V）てください。

If the HP Tools tab itself is missing (the add-on failed to load), use the
manual way below.

HP Tools タブ自体が出ていない（アドオンが読み込めていない）場合は、以下の
手動の方法を使ってください。

`HP_Check.py` ships inside the add-on and reports what is and isn't working. It
only reads — it changes nothing.

アドオンに `HP_Check.py` が同梱されています。何が動いていないかを診断します。
**環境を書き換えることはありません。**

1. Switch an area to the **Text Editor** / エリアを **Text Editor** に切り替える
2. **Open** → `HP_Check.py`
3. **Run Script** (Alt+P)
4. Pick `HP_Check_Result` from the dropdown at the top
   上部のドロップダウンから `HP_Check_Result` を選ぶ
5. Ctrl+A, Ctrl+C, and send it over / コピーして講師に送ってください

> ⚠️ Don't press Run Script while the report is open. It's a report, not a
> script, so Python will complain.
>
> ⚠️ レポートを開いた状態で Run Script を押さないでください。エラーになります。

Set `LANG = "EN"` at the top of the file for an English report.
冒頭の `LANG` を `"EN"` にすると英語で出力されます。

---

## What changed for 5.2 / 5.2 対応の変更点

### Fixed

- **Removed `import bgl`** (`draw_primitives`, `select_through_border`). BGL was
  deleted in Blender 5.0, so both files failed to import and every operator in
  them vanished. That also scrambled the Specials pie — the missing *Draw
  Primitives* entry shifted every later slot by one position.
- **`blf.size()`** no longer takes a DPI argument (changed in 4.0).
- **Auto Smooth** calls `bpy.ops.object.shade_auto_smooth()` instead of
  hard-coding the Essentials asset path and the node group's socket identifiers.
- **`Mesh.use_auto_smooth` / `auto_smooth_angle`** removed (gone since 4.1).
- **Keymap registration hardened.** A missing keymap used to raise and abort
  `register()` part-way, leaving Blender's conflicting defaults active.
- **`unregister()` actually unregisters.** It used to call the registration
  function again, stacking a second copy of every shortcut on each reload.
- **`unified_paint_settings`** moved onto the mode-specific `Paint` struct in 5.0.
- **`paint.brush_select`**: `sculpt_tool` → `sculpt_brush_type`.
- **OBJ and STL** importers/exporters are now `wm.obj_import`, `wm.stl_import`
  and friends.
- **`object.gpencil_modifier_add`** merged into `object.modifier_add` in 4.3.
- **Camera DOF panel** in `_menu_master` was still on the 2.79 `gpu_dof` API.
- **GP Canvas** (Front / Top / Side) assigned to a local variable and did nothing.
- **`mesh.smart_bevel`** → `view3d.smart_bevel` (a long-standing typo).
- *Keys Viewer* commented out — it needs the external Screencast Keys add-on.

### Added

- **Draw with GP** — Ctrl+Space, bottom-right column. Creates a Grease Pencil
  object and drops straight into draw mode.
  - Nothing selected → placed at the 3D cursor, stroke placement **Origin**
  - Object selected → placed at that object and **parented** to it, stroke
    placement **Surface** with a 0.015 m offset so strokes don't sink in
  - Drawing plane locked to **View**, depth order set to **3D**
  - Materials `Pencil`, `Halftone`, `Fill` attached, brush set to vertex colour
- **Double click selects a whole stroke** in Grease Pencil edit mode, the way it
  works on meshes. Shift+double click adds to the selection.
- **Alt+Left Click = Transfer Mode** — hop to whatever object is under the cursor
  without leaving sculpt or paint mode.
- **Setup panel** with backup and restore.
- **`HP_Check.py`** diagnostics.

---

## Other Blender versions / 他のバージョン

- **Blender 4.3 and 4.5** — [Renart84's config](https://github.com/Renart84/HEAVYPOLY_Blender)
- **Blender 4.1 and 4.2** — [v1.0.0](https://github.com/Renart84/HEAVYPOLY_Blender/releases/tag/v1.0.0)
- **Blender 3.6 and 4.0** — [older releases](https://github.com/HEAVYPOLY/HEAVYPOLY_Blender/releases)

---

## For maintainers / メンテナ向け

`build_release.py` handles releases. From the repository root:

```
python build_release.py 1.4.0
```

It rewrites the version in `blender_manifest.toml`, zips the add-on into
`docs/`, hashes it, and regenerates `docs/index.json`. Then commit and push.

`docs/` and `build_release.py` are repository infrastructure. They are not part
of the add-on and are excluded from the zip.
