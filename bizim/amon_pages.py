"""Amon page edits: a quieter About screen and a File Transfer screen."""
import re

from amon_theme import LANGUAGE, THEME, read_text, write_text

SETTINGS = THEME / "pages/settings.xml"
MOUNT = THEME / "pages/mount.xml"
ADVANCED = THEME / "pages/advanced.xml"
VARIABLES = THEME / "resources/vars.xml"
TURKISH = LANGUAGE.parent / "tr_TR.xml"

CARDS_START = "<!-- Yan's Card -->"
CARD_END = "<!-- Card -->"
PAGE_END = "</page>"
MORE_BUTTON = re.compile(r'\s*<button style="btn_about_credits">.*?</button>', re.S)
BASED_ON_TEXT = "Based on OrangeFox Recovery Project and TWRP"
TRANSFER_TEXT = "File Transfer (PC / USB / SD)"
COPY_TEXT = "Copy files (File Manager)"
PULL_TEXT = "Phone to PC: adb pull /sdcard/file"
PUSH_TEXT = "PC to phone: adb push file /sdcard/"

ABOUT_FOOTER = f"""<text style="caption">
				<placement x="%center_x%" y="%amon_credit_y1%" placement="5"/>
				<text>{{@amon_based_on={BASED_ON_TEXT}}}</text>
			</text>

			<text style="caption">
				<placement x="%center_x%" y="%amon_credit_y2%" placement="5"/>
				<text>orangefox.download | gitlab.com/OrangeFox | twrp.me</text>
			</text>"""
CREDIT_VARIABLES = """		<variable name="amon_credit_y1" value="%screen_h%-480"/>
		<variable name="amon_credit_y2" value="%screen_h%-430"/>
"""
MENU_ANCHOR = '<listitem name="{@mount_btn}">'
MENU_ITEM = f"""<listitem name="{{@amon_transfer_btn={TRANSFER_TEXT}}}">
					<icon res="usb"/>
					<action function="page">amon_transfer</action>
				</listitem>
				"""
TRANSFER_ANCHOR = '<page name="usb_mount">'
TRANSFER_PAGE = f"""<page name="amon_transfer">
			<template name="base"/>

			<text style="text_ab_title">
				<placement x="%col1_x_indent%" y="%ab_bc_y%"/>
				<text>{{@amon_transfer_btn={TRANSFER_TEXT}}}</text>
			</text>

			<listbox style="group_list">
				<placement x="0" y="%row1_1a_y%" w="%screen_w%" h="%part_list_mount_h%"/>
				<listitem name="{{@enable_mtp_btn}}">
					<icon res="devices"/>
					<condition var1="tw_has_mtp" var2="1"/>
					<condition var1="tw_mtp_enabled" op="!=" var2="1"/>
					<action function="startmtp"/>
				</listitem>
				<listitem name="{{@disable_mtp_btn}}">
					<icon res="devices"/>
					<condition var1="tw_has_mtp" var2="1"/>
					<condition var1="tw_mtp_enabled" var2="1"/>
					<action function="stopmtp"/>
				</listitem>
				<listitem name="{{@mount_btn}}">
					<icon res="sd_card"/>
					<action function="page">mount</action>
				</listitem>
				<listitem name="{{@amon_transfer_copy={COPY_TEXT}}}">
					<icon res="files"/>
					<action function="page">filemanagerlist</action>
				</listitem>
			</listbox>

			<text style="caption">
				<placement x="%gl_text_x%" y="%row5_3_y%"/>
				<text>{{@amon_adb_pull={PULL_TEXT}}}</text>
			</text>

			<text style="caption">
				<placement x="%gl_text_x%" y="%row6_1_y%"/>
				<text>{{@amon_adb_push={PUSH_TEXT}}}</text>
			</text>

			<template name="gestures"/>

			<action>
				<touch key="home"/>
				<action function="page">main</action>
			</action>

			<action>
				<touch key="back"/>
				<action function="page">advanced</action>
			</action>
		</page>

		"""
ENGLISH_STRINGS = (
    ("amon_based_on", BASED_ON_TEXT),
    ("amon_transfer_btn", TRANSFER_TEXT),
    ("amon_transfer_copy", COPY_TEXT),
    ("amon_adb_pull", PULL_TEXT),
    ("amon_adb_push", PUSH_TEXT),
)
TURKISH_STRINGS = (
    ("amon_based_on", "OrangeFox Recovery Project ve TWRP tabanlıdır"),
    ("amon_transfer_btn", "Dosya Aktarımı (PC / USB / SD)"),
    ("amon_transfer_copy", "Dosya kopyala (Dosya Yöneticisi)"),
    ("amon_adb_pull", "Telefondan PC'ye: adb pull /sdcard/dosya"),
    ("amon_adb_push", "PC'den telefona: adb push dosya /sdcard/"),
)


def insert_once(path, anchor, addition, before=True):
    text = read_text(path)
    count = text.count(anchor)
    if count != 1:
        raise SystemExit(f"{path}: expected one anchor, found {count}: {anchor!r}")
    joined = addition + anchor if before else anchor + addition
    write_text(path, text.replace(anchor, joined))


def simplify_about(root):
    path = root / SETTINGS
    text = read_text(path)
    start = text.index(CARDS_START)
    page_end = text.index(PAGE_END, start)
    end = text.rfind(CARD_END, start, page_end)
    if end < 0:
        raise SystemExit("About cards end marker not found")
    trimmed = text[:start] + ABOUT_FOOTER + text[end + len(CARD_END):]
    without_more, removed = MORE_BUTTON.subn("", trimmed, count=1)
    if removed != 1:
        raise SystemExit("About credits button not found")
    write_text(path, without_more)
    insert_once(root / VARIABLES, "\t</variables>", CREDIT_VARIABLES)


def add_strings(path, strings):
    lines = "".join(f'\t\t<string name="{name}">{value}</string>\n' for name, value in strings)
    insert_once(path, "\t</resources>", lines)


def add_transfer_screen(root):
    insert_once(root / MOUNT, TRANSFER_ANCHOR, TRANSFER_PAGE)
    insert_once(root / ADVANCED, MENU_ANCHOR, MENU_ITEM)
    add_strings(root / LANGUAGE, ENGLISH_STRINGS)
    add_strings(root / TURKISH, TURKISH_STRINGS)


def apply_pages(root):
    simplify_about(root)
    add_transfer_screen(root)
    print("Amon pages applied")
