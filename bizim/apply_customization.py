#!/usr/bin/env python3
"""Apply the Amon look and the degas slot fix to an OrangeFox source tree.

Usage: apply_customization.py BOOTABLE_RECOVERY_DIR

Every edit requires its anchor to exist, so an upstream change stops the build
here instead of silently producing a partly branded recovery.
"""
import shutil
import sys
from pathlib import Path

import amon_pages
import amon_theme

ASSETS = Path(__file__).resolve().parent / "assets"
THEME = amon_theme.THEME
LOGOS = THEME / "images/SVG/Logos"
LOGO_FILES = ("logo_o.svg", "logo_d.svg", "logo_w.svg")
FOX_ICON = THEME / "images/SVG/Icons/fox.svg"
SPLASH = THEME / "splash.xml"
PARTITION_MANAGER = Path("partitionmanager.cpp")
LIBBLKID_MAKEFILE = Path("libblkid/Android.mk")
LIBBLKID_MODULE = "LOCAL_MODULE := libblkid\n"
CLEAR_VARS = "include $(CLEAR_VARS)"

SLOT_METHOD = "void TWPartitionManager::Set_Active_Slot(const string& Slot) {"
SLOT_BLOCK_START = "\t\tconst auto module = BootControlClient::WaitForService();\n"
SLOT_BLOCK_END = '\t\tDataManager::SetValue("tw_active_slot", Slot);'
SLOT_CALL = (
    '\t\tif (!Write_Active_Slot_To_Misc(Slot == "B" ? 1 : 0))\n'
    '\t\t\tgui_msg(Msg(msg::kError, "unable_set_boot_slot='
    'Error changing bootloader boot slot to {1}")(Slot));\n'
)
SLOT_HELPER = """// The boot control HAL is unavailable in standalone recovery, so waiting for it
// never returns. Update the bootloader_control struct in misc directly instead.
static bool Write_Active_Slot_To_Misc(int slot_number) {
\tconst off_t control_offset = 2048;
\tconst uint32_t control_magic = 0x42414342;
\tconst int fd = open("/dev/block/by-name/misc", O_RDWR);
\tif (fd < 0) {
\t\tLOGERR("Set_Active_Slot: cannot open misc\\n");
\t\treturn false;
\t}
\tunsigned char control[32];
\tbool written = pread(fd, control, sizeof(control), control_offset) == (ssize_t)sizeof(control);
\tif (written) {
\t\tuint32_t magic;
\t\tmemcpy(&magic, control + 4, sizeof(magic));
\t\tif (magic != control_magic) {
\t\t\tmemset(control, 0, sizeof(control));
\t\t\tmemcpy(control + 4, &control_magic, sizeof(control_magic));
\t\t\tcontrol[8] = 1;
\t\t\tcontrol[9] = 2;
\t\t}
\t\tmemcpy(control, slot_number == 0 ? "_a\\0\\0" : "_b\\0\\0", 4);
\t\tcontrol[12] = slot_number == 0 ? 0x7f : 0x7e;
\t\tcontrol[14] = slot_number == 1 ? 0x7f : 0x7e;
\t\tconst uint32_t checksum = crc32(0, control, 28);
\t\tmemcpy(control + 28, &checksum, sizeof(checksum));
\t\twritten = pwrite(fd, control, sizeof(control), control_offset) == (ssize_t)sizeof(control);
\t\tif (written)
\t\t\tfsync(fd);
\t}
\tclose(fd);
\tif (!written)
\t\tLOGERR("Set_Active_Slot: failed to update misc\\n");
\treturn written;
}

"""


def require_once(text, anchor, label):
    count = text.count(anchor)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}: {anchor!r}")


def copy_assets(root):
    for name in LOGO_FILES:
        target = root / LOGOS / name
        if not target.is_file():
            raise SystemExit(f"missing upstream logo: {target}")
        shutil.copyfile(ASSETS / "logo.svg", target)
    if not (root / FOX_ICON).is_file():
        raise SystemExit(f"missing upstream icon: {root / FOX_ICON}")
    shutil.copyfile(ASSETS / "fox.svg", root / FOX_ICON)


def apply_splash_name(root):
    path = root / SPLASH
    text = amon_theme.read_text(path)
    require_once(text, "<text>OrangeFox</text>", str(path))
    amon_theme.write_text(path, text.replace("<text>OrangeFox</text>", "<text>AMON</text>"))


def apply_slot_fix(root):
    path = root / PARTITION_MANAGER
    text = amon_theme.read_text(path)
    for anchor, label in ((SLOT_METHOD, "method"), (SLOT_BLOCK_START, "block start"), (SLOT_BLOCK_END, "block end")):
        require_once(text, anchor, f"slot fix {label}")
    start = text.index(SLOT_BLOCK_START)
    end = text.index(SLOT_BLOCK_END)
    if start >= end:
        raise SystemExit("slot fix: block markers are out of order")
    patched = text[:start] + SLOT_CALL + text[end:]
    amon_theme.write_text(path, patched.replace(SLOT_METHOD, SLOT_HELPER + SLOT_METHOD))


def remove_duplicate_libblkid(root):
    """Use the Soong libblkid from external/util-linux instead of the Make copy."""
    path = root / LIBBLKID_MAKEFILE
    text = amon_theme.read_text(path)
    require_once(text, LIBBLKID_MODULE, str(path))
    start = text.rfind(CLEAR_VARS, 0, text.index(LIBBLKID_MODULE))
    if start < 0:
        raise SystemExit("libblkid module start not found")
    amon_theme.write_text(path, text[:start].rstrip() + "\n")


def main():
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    root = Path(sys.argv[1])
    remove_duplicate_libblkid(root)
    amon_theme.apply_theme(root)
    amon_pages.apply_pages(root)
    copy_assets(root)
    apply_splash_name(root)
    apply_slot_fix(root)
    print("Amon customization applied")


if __name__ == "__main__":
    main()
