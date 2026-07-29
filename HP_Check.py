# HP_Check.py - HEAVYPOLY config diagnostic
#
# HOW TO USE
#   1. Open Blender.
#   2. Switch an area to the Text Editor.
#   3. New -> paste this file -> press "Run Script" (Alt+P).
#   4. A new text block called "HP_Check_Result" is created.
#      Pick it from the Text Editor's dropdown at the top.
#      Select all (Ctrl+A), copy (Ctrl+C), and paste it back in chat.
#      Do NOT press Run Script while that report is open - it is a
#      report, not a script, and Python will complain.
#
# It changes nothing. It only reads and reports.

LANG = "JA"   # "JA" or "EN"

import bpy
import os
import re
import sys
import platform


# ---------------------------------------------------------------- text

T = {
    "title":        {"EN": "HEAVYPOLY CONFIG CHECK", "JA": "HEAVYPOLY CONFIG 診断"},
    "environment":  {"EN": "ENVIRONMENT", "JA": "環境"},
    "files":        {"EN": "HEAVYPOLY FILES", "JA": "HEAVYPOLY ファイル"},
    "modules":      {"EN": "MODULE LOAD STATUS", "JA": "モジュール読み込み状況"},
    "missing_ops":  {"EN": "MISSING OPERATORS", "JA": "存在しないオペレーター"},
    "suggestions":  {"EN": "SUGGESTED REPLACEMENTS", "JA": "置換候補"},
    "keymaps":      {"EN": "KEYMAPS", "JA": "キーマップ"},
    "hp_ops":       {"EN": "HEAVYPOLY OPERATORS REGISTERED", "JA": "HEAVYPOLY オペレーター登録状況"},
    "gp_ops":       {"EN": "GREASE PENCIL OPERATORS AVAILABLE", "JA": "利用可能な Grease Pencil オペレーター"},
    "summary":      {"EN": "SUMMARY", "JA": "まとめ"},
    "not_found":    {"EN": "not found", "JA": "見つかりません"},
    "none":         {"EN": "(none)", "JA": "（なし）"},
    "no_files":     {"EN": "No HEAVYPOLY_*.py files found. Is the config installed?",
                     "JA": "HEAVYPOLY_*.py が見つかりません。config は導入されていますか？"},
    "ok":           {"EN": "All referenced operators exist.", "JA": "参照されているオペレーターはすべて存在します。"},
    "end":          {"EN": "Copy everything above and paste it back in chat.",
                     "JA": "上をすべてコピーして、チャットに貼り付けてください。"},
}


def t(key):
    return T[key][LANG if LANG in ("EN", "JA") else "EN"]


lines = []


def out(s=""):
    lines.append(str(s))


def header(s):
    out()
    out("=" * 66)
    out("  " + s)
    out("=" * 66)


# ---------------------------------------------------------------- environment

header(t("title"))
out()
out("[%s]" % t("environment"))
out("  Blender      : %s" % bpy.app.version_string)
out("  Build branch : %s" % bpy.app.build_branch.decode(errors="replace"))
out("  Python       : %s" % sys.version.split()[0])
out("  Platform     : %s %s" % (platform.system(), platform.release()))
out("  Config path  : %s" % bpy.utils.user_resource('CONFIG'))
out("  Scripts paths:")
for p in bpy.utils.script_paths():
    out("      %s" % p)


# ---------------------------------------------------------------- find files

def find_hp_files():
    found = {}
    roots = list(bpy.utils.script_paths())
    for extra in (bpy.utils.user_resource('SCRIPTS'), bpy.utils.resource_path('LOCAL')):
        if extra:
            roots.append(extra)
    seen_roots = set()
    for root in roots:
        if not root or root in seen_roots or not os.path.isdir(root):
            continue
        seen_roots.add(root)
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d != "__pycache__"]
            for fn in filenames:
                if fn.startswith("HEAVYPOLY") and fn.endswith(".py"):
                    full = os.path.join(dirpath, fn)
                    found.setdefault(fn, full)
    return found


hp_files = find_hp_files()

out()
out("[%s]" % t("files"))
if not hp_files:
    out("  " + t("no_files"))
else:
    folders = sorted({os.path.dirname(p) for p in hp_files.values()})
    for f in folders:
        out("  %s" % f)
    out("  -> %d file(s)" % len(hp_files))


# ---------------------------------------------------------------- module status

out()
out("[%s]" % t("modules"))
loaded = sorted(m for m in sys.modules if m.startswith("HEAVYPOLY") or m == "jmQuickPipe")
if loaded:
    for m in loaded:
        out("  loaded : %s" % m)
else:
    out("  " + t("none"))

not_loaded = sorted(
    os.path.splitext(f)[0] for f in hp_files
    if os.path.splitext(f)[0] not in sys.modules
)
for m in not_loaded:
    out("  FAILED : %s   <-- did not import" % m)


# ---------------------------------------------------------------- collect operators

OP_PATTERNS = (
    r'bpy\.ops\.([a-z_]+)\.([a-z_0-9]+)',
    r'\.operator\(\s*["\']([a-z_]+\.[a-z_0-9]+)["\']',
    r'\.operator_menu_enum\(\s*["\']([a-z_]+\.[a-z_0-9]+)["\']',
    r'keymap_items\.new\(\s*["\']([a-z_]+\.[a-z_0-9]+)["\']',
)

referenced = {}          # idname -> set("file:line")
hp_defined = set()
keymaps_used = set()

for fn, path in sorted(hp_files.items()):
    try:
        src = open(path, encoding="utf-8").read()
    except Exception as e:
        out("  ! could not read %s: %r" % (fn, e))
        continue

    for m in re.finditer(r'bl_idname\s*=\s*["\']([a-z_]+\.[a-z_0-9]+)["\']', src):
        hp_defined.add(m.group(1))

    for m in re.finditer(r'keymaps\.new\(\s*(?:name\s*=\s*)?["\']([^"\']+)["\']', src):
        keymaps_used.add(m.group(1))
    for m in re.finditer(r'(?:disable_default_kmi|disable_specific_kmi|get_active_kmi|deactivate_kmi)\(\s*["\']([^"\']+)["\']', src):
        keymaps_used.add(m.group(1))

    for line_no, line in enumerate(src.splitlines(), 1):
        if line.lstrip().startswith("#"):
            continue
        for pat in OP_PATTERNS:
            for m in re.finditer(pat, line):
                idname = ".".join(m.groups()) if len(m.groups()) == 2 else m.group(1)
                referenced.setdefault(idname, set()).add("%s:%d" % (fn, line_no))


# ---------------------------------------------------------------- available operators

available = set()
for mod_name in dir(bpy.ops):
    if mod_name.startswith("_"):
        continue
    mod = getattr(bpy.ops, mod_name, None)
    if mod is None:
        continue
    try:
        for op_name in dir(mod):
            if not op_name.startswith("_"):
                available.add("%s.%s" % (mod_name, op_name))
    except Exception:
        pass


def op_exists(idname):
    if idname in available:
        return True
    mod_name, _, op_name = idname.partition(".")
    mod = getattr(bpy.ops, mod_name, None)
    return mod is not None and hasattr(mod, op_name)


external = {k: v for k, v in referenced.items() if k not in hp_defined}
missing = sorted(k for k in external if not op_exists(k))

out()
out("[%s]  %d" % (t("missing_ops"), len(missing)))
if not missing:
    out("  " + t("ok"))
else:
    for idname in missing:
        where = ", ".join(sorted(external[idname])[:3])
        out("  %-34s %s" % (idname, where))


# ---------------------------------------------------------------- suggestions

def suggest(idname):
    mod_name, _, op_name = idname.partition(".")
    hits = []
    # same function name in any module
    for cand in available:
        if cand.split(".", 1)[1] == op_name:
            hits.append(cand)
    # token overlap
    tokens = [w for w in op_name.split("_") if len(w) > 2]
    if tokens:
        for cand in available:
            c_mod, c_op = cand.split(".", 1)
            if cand in hits:
                continue
            score = sum(1 for w in tokens if w in c_op)
            if score >= max(2, len(tokens) - 1):
                if mod_name.replace("_", "") in cand.replace("_", "") or c_mod in ("wm", mod_name):
                    hits.append(cand)
    return hits[:4]


if missing:
    out()
    out("[%s]" % t("suggestions"))
    for idname in missing:
        hits = suggest(idname)
        out("  %-34s -> %s" % (idname, ", ".join(hits) if hits else t("not_found")))


# ---------------------------------------------------------------- keymaps

wm = bpy.context.window_manager
kc_default = wm.keyconfigs.get("Blender")
kc_active = wm.keyconfigs.active

out()
out("[%s]" % t("keymaps"))
missing_km = []
for name in sorted(keymaps_used):
    in_default = bool(kc_default and kc_default.keymaps.get(name))
    in_active = bool(kc_active and kc_active.keymaps.get(name))
    if not (in_default or in_active):
        missing_km.append(name)
out("  referenced: %d   missing: %d" % (len(keymaps_used), len(missing_km)))
for name in missing_km:
    out("  MISSING : '%s'" % name)

if missing_km and kc_default:
    out()
    out("  -- keymaps that DO exist (filtered) --")
    words = set()
    for name in missing_km:
        words.update(w.lower() for w in name.split() if len(w) > 3)
    for km in kc_default.keymaps:
        low = km.name.lower()
        if any(w in low for w in words):
            out("      '%s'" % km.name)


# ---------------------------------------------------------------- HP operators

out()
out("[%s]" % t("hp_ops"))
hp_missing = sorted(o for o in hp_defined if not op_exists(o))
out("  defined in source: %d   NOT registered: %d" % (len(hp_defined), len(hp_missing)))
for o in hp_missing:
    out("  NOT REGISTERED : %s" % o)


# ---------------------------------------------------------------- GP operators

out()
out("[%s]" % t("gp_ops"))
for mod_name in ("grease_pencil", "gpencil"):
    mod = getattr(bpy.ops, mod_name, None)
    if mod is None:
        out("  bpy.ops.%s : %s" % (mod_name, t("not_found")))
        continue
    ops = sorted(o for o in dir(mod) if not o.startswith("_"))
    out("  bpy.ops.%s : %d operators" % (mod_name, len(ops)))
    for i in range(0, len(ops), 4):
        out("      " + "  ".join("%-24s" % o for o in ops[i:i + 4]).rstrip())


# ---------------------------------------------------------------- summary

out()
out("[%s]" % t("summary"))
out("  HEAVYPOLY files found      : %d" % len(hp_files))
out("  Modules that failed to load: %d" % len(not_loaded))
out("  Missing operators          : %d" % len(missing))
out("  Missing keymaps            : %d" % len(missing_km))
out("  HP operators not registered: %d" % len(hp_missing))
out()
out(t("end"))
out()


# ---------------------------------------------------------------- emit

report = "\n".join(lines)
print(report)

name = "HP_Check_Result"
text = bpy.data.texts.get(name)
if text is None:
    text = bpy.data.texts.new(name)
text.clear()
text.write(report)

# NOTE: deliberately does NOT switch the Text Editor to the report.
# Doing so meant a second Alt+P would try to *run* the report as Python.
print("\n" + "=" * 66)
print(">>> Report written to the text block '%s'." % name)
print(">>> Pick it from the Text Editor dropdown, then Ctrl+A / Ctrl+C.")
print(">>> Do NOT press Run Script while the report is open.")
print("=" * 66)
