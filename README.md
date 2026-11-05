# OrangeFox for Xiaomi 14T (degas)

OrangeFox recovery device tree for the **Xiaomi 14T**, codenamed **degas**.

**Port creator and maintainer:** `sigmapro555eshkere`

The tree targets OrangeFox `fox_16.0` on Android 16 / BP2A and builds a
recovery that runs from the device's A/B `vendor_boot` partition.

![Platform](https://img.shields.io/badge/platform-MediaTek%20MT6897-green)
![Android](https://img.shields.io/badge/Android-16-blue)
![Recovery](https://img.shields.io/badge/recovery-OrangeFox-orange)
![License](https://img.shields.io/badge/license-Apache--2.0-lightgrey)

## Device

| Property | Value |
| --- | --- |
| Device | Xiaomi 14T |
| Codename | `degas` |
| SoC | MediaTek Dimensity 8300-Ultra |
| Platform | `mt6897` |
| Architecture | arm64 |
| Display | 1220 × 2712 |
| Partitions | A/B, virtual A/B, dynamic partitions |
| Recovery location | `vendor_boot` |
| Boot image format | GKI v4 |
| Userdata | F2FS with FBE v2 and metadata encryption |
| Touchscreen | Goodix |

## Included functionality

- OrangeFox recovery with the portrait HDPI theme.
- Display, touch, brightness and battery support for the 14T.
- Goodix firmware and a patched `xiaomi_touch_common.ko` driver.
- Stock MT6897 vendor-ramdisk kernel modules, including display, UFS, USB and
  TEE dependencies.
- Dynamic-partition mounting with EROFS and ext4 fallbacks.
- Fastbootd and A/B OTA support.
- Backup and restore entries for `boot`, `init_boot`, `vendor_boot`, `dtbo`,
  `super`, `vbmeta`, `vbmeta_system` and `vbmeta_vendor`.
- ADB, ADB sideload, MTP over ConfigFS and USB OTG.
- Direct A/B slot switching through the `misc` partition.
- File-based encryption and metadata-decryption integration.
- MiTEE KeyMint and Gatekeeper services, NXP Weaver, the Xiaomi secure-element
  HAL and a native recovery OMAPI service.
- AVB recovery image configuration and recovery-specific SELinux policy.

## Source tree

```
BoardConfig.mk                    Board, partition, AVB and OrangeFox settings
device.mk                         Packages and vendor-ramdisk files
ofox_degas.mk                     Product definition
vendorsetup.sh                    OrangeFox target setup
prebuilt/                         Stock boot, DTBO and device tree blob
vendor_ramdisk/                   Stock MT6897 vendor modules and first-stage fstab
recovery/root/                    Recovery ramdisk, fstab, firmware and TEE stack
recovery/tee-blobs.sha256         Checksums for bundled TEE/eSE binaries
omapi/                            Native recovery OMAPI service
sepolicy/                         Recovery SELinux policy
patches/                          Upstream recovery patches
rom-blobs/                        Optional ROM-specific blob overlay
patch_touch_clean.sh              vendor_boot repack helper
tools/slot_switch.py              Host-side A/B slot utility
xiaomi_touch_common_patched.ko    Patched Goodix touch module
```

The tree contains source files and device-specific prebuilts. Built recovery
images are not committed.

## Build requirements

Use an OrangeFox source tree with the Android 16 / `fox_16.0` build system and
a synced `bootable/recovery` checkout. Place this repository at:

```
device/xiaomi/degas
```

Then run:

```bash
source build/envsetup.sh
lunch ofox_degas-bp2a-eng
mka vendorbootimage
```

The product name remains `ofox_degas` because it is the product definition
used by the OrangeFox build system.

### Applying the recovery patches

The `patches/` directory contains:

1. A direct `misc/bootloader_control` A/B slot switch implementation. It
   avoids the boot-control HAL, which is unavailable in standalone recovery.
2. An OrangeFox splash-screen attribution line.

Apply them before building:

```bash
./patches/apply_patches.sh
```

The helper is idempotent. It expects the target recovery checkout at
`bootable/recovery` relative to the directory containing `patches/`. If the
device tree is nested under another Android checkout, apply the patches from
that checkout with `git apply` or adapt the paths to your layout.

## Building the final vendor_boot image

This is a `TARGET_NO_KERNEL` device tree. The normal build produces the
OrangeFox recovery ramdisk, but the stock vendor kernel modules must be carried
into the final image. `patch_touch_clean.sh` combines:

- a base `vendor_boot` containing the stock module ramdisk;
- the freshly built OrangeFox `vendor_boot`;
- the patched touch module and Goodix firmware.

The script requires `unpack_bootimg.py`, `mkbootimg`, `lz4` and `cpio`.
It expects these inputs in its working directory:

```
ofox_degas-vendor_boot.img
out/target/product/degas/vendor_boot.img
xiaomi_touch_common_patched.ko
goodix_cfg_group_degas.bin
goodix_firmware_degas.bin
```

The Goodix files are also kept in the recovery tree under
`recovery/root/lib/firmware/` and `recovery/root/vendor/firmware/`.

Run the repack step after `vendorbootimage`:

```bash
bash patch_touch_clean.sh
```

The output is:

```
ofox_degas-vendor_boot-clean.img
```

Before flashing, make sure the image fits the 64 MiB `vendor_boot` partition.
The script prints the final size and the partition limit.

## GitHub Actions builds

The repository includes a manual workflow at
`.github/workflows/build-ofox.yml`. After forking the repository, open
**Actions → Build OrangeFox → Run workflow**. The workflow syncs the OrangeFox
source, applies the device patches, builds `ofox_degas`, repacks `vendor_boot`
and uploads the images and `SHA256SUMS` as an artifact.

The workflow is intended for ROM-specific builds. Add files under `rom-blobs/`
using paths relative to `device/xiaomi/degas` to override firmware, TEE files
or kernel modules. The matching base `vendor_boot` can be committed as
`rom-blobs/ofox_degas-vendor_boot.img`, or supplied through the
`vendor_boot_url` input. A blob archive can be supplied through
`blob_archive_url`; it is extracted over the device tree before the build.
SHA-256 inputs are available for both downloads.

Keep proprietary blobs in a private fork or provide them from a private,
short-lived download URL. GitHub's regular Git limit is 100 MiB per file;
large `vendor_boot` images should be passed as workflow inputs or stored with
Git LFS.

## Flashing

Unlock the bootloader and keep a backup of the original images before flashing.
With the phone in fastboot mode:

```bash
fastboot flash vendor_boot ofox_degas-vendor_boot-clean.img
fastboot reboot recovery
```

Use the image produced for the same firmware base as the device. The bundled
vendor modules and TEE binaries come from HyperOS
`OS3.0.306.0.WNEEUXM`.

## A/B slot utility

`tools/slot_switch.py` runs on the host and controls a connected device over
ADB. It reads the standard 32-byte `bootloader_control` structure at offset
2048 in `/dev/block/by-name/misc`.

```bash
python3 tools/slot_switch.py status
python3 tools/slot_switch.py set a --dry-run
python3 tools/slot_switch.py set a
python3 tools/slot_switch.py set b
```

The device must be booted into a recovery with working ADB and sufficient
privileges to read and write `misc`.

## Verifying bundled TEE files

The hashes in `recovery/tee-blobs.sha256` are relative to
`recovery/root`:

```bash
cd recovery/root
sha256sum -c ../tee-blobs.sha256
```

## License

The device-tree files are provided under the Apache License 2.0; see
[LICENSE](LICENSE). Components inherited from OrangeFox, TWRP, AOSP and the
Linux kernel retain their respective upstream licenses.

## Credits

- [Advnirr](https://github.com/Advnirr) — original Xiaomi 14T `degas` tree:
  [twrp_device_xiaomi_degas](https://github.com/Advnirr/twrp_device_xiaomi_degas).
- [Dip184](https://github.com/Dip184) — decryption method and reference work:
  [android_device_xiaomi_duchamp](https://github.com/Dip184/android_device_xiaomi_duchamp/tree/orangefox-14.1).
