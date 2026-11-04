# Copyright (C) 2024 The Android Open Source Project
# SPDX-License-Identifier: Apache-2.0

# Literal path: PRODUCT_MANUFACTURER/PRODUCT_DEVICE are set in twrp_degas.mk
# only after this file is inherited, so they are empty here.
LOCAL_PATH := device/xiaomi/degas

# A/B
AB_OTA_POSTINSTALL_CONFIG += \
    RUN_POSTINSTALL_system=true \
    POSTINSTALL_PATH_system=system/bin/otapreopt_script \
    FILESYSTEM_TYPE_system=ext4 \
    POSTINSTALL_OPTIONAL_system=true

PRODUCT_PACKAGES += \
    otapreopt_script 

# API
PRODUCT_SHIPPING_API_LEVEL := 32

# Boot Control HAL
PRODUCT_PACKAGES += \
    android.hardware.boot@1.2-mtkimpl \
    android.hardware.boot@1.2-mtkimpl.recovery \
    bootctrl.mt6897 \
    bootctrl.mt6897.recovery

# Dynamic Partitions
PRODUCT_USE_DYNAMIC_PARTITIONS := true

# Fastbootd
PRODUCT_PACKAGES += \
    android.hardware.fastboot@1.0-impl-mock \
    fastbootd

# VNDK
PRODUCT_TARGET_VNDK_VERSION := 34

# Update Engine
PRODUCT_PACKAGES += \
    update_engine \
    update_verifier \
    update_engine_sideload

# NOTE: FBE decrypt is parked (TEE RoT-bound, unreachable from recovery), so the
# vold / keymaster / gatekeeper packages were removed — they only bloated the
# ramdisk. The health@2.0 HAL was also dropped: battery now reads sysfs directly
# (TW_USE_LEGACY_BATTERY_SERVICES), so the HAL is no longer needed.

# ── vendor_boot ramdisk00 (platform, used for normal boot AND recovery) ──────
# This is a TARGET_NO_KERNEL build: the vendor kernel modules are not built, so
# the stock ones are shipped verbatim (incl. modules.load / .recovery / .dep).
# Source: stock vendor_boot of HyperOS OS3.0.306.0.WNEEUXM (vermagic
# 6.1.157-android14-11), unmodified. The recovery-only patched touch driver
# lives in recovery/root/lib/modules/ (ramdisk01 overrides it in recovery).
PRODUCT_COPY_FILES += \
    $(call find-copy-subdir-files,*,$(LOCAL_PATH)/vendor_ramdisk/lib/modules,$(TARGET_COPY_OUT_VENDOR_RAMDISK)/lib/modules)

# First-stage fstab. The generated vendor ramdisk has none, and first-stage init
# needs it to mount system/vendor/... (and the ColorOS-port my_* partitions).
PRODUCT_COPY_FILES += \
    $(LOCAL_PATH)/vendor_ramdisk/first_stage_ramdisk/fstab.mt6897:$(TARGET_COPY_OUT_VENDOR_RAMDISK)/first_stage_ramdisk/fstab.mt6897
