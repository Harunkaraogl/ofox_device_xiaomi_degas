# Inherit from those products. Most specific first.
$(call inherit-product, $(SRC_TARGET_DIR)/product/base.mk)
$(call inherit-product, $(SRC_TARGET_DIR)/product/core_64_bit.mk)

# Inherit some common TWRP stuff.
$(call inherit-product, vendor/twrp/config/common.mk)

$(call inherit-product, device/xiaomi/degas/device.mk)

# Virtual A/B OTA (recovery lives in vendor_boot)
$(call inherit-product, $(SRC_TARGET_DIR)/product/virtual_ab_ota/launch_with_vendor_ramdisk.mk)
$(call inherit-product, $(SRC_TARGET_DIR)/product/virtual_ab_ota/compression.mk)
PRODUCT_USE_DYNAMIC_PARTITIONS := true

# Emulated (FUSE) internal storage
$(call inherit-product, $(SRC_TARGET_DIR)/product/emulated_storage.mk)

# Device
PRODUCT_DEVICE := degas
PRODUCT_NAME := ofox_degas
PRODUCT_BRAND := Xiaomi
PRODUCT_MODEL := Xiaomi 14T
PRODUCT_MANUFACTURER := Xiaomi

# Platform
PRODUCT_PLATFORM := mt6897

# Recovery is in vendor_boot: hide "reflash recovery" for a non-recovery partition
PRODUCT_PROPERTY_OVERRIDES += \
    ro.twrp.vendor_boot=true
