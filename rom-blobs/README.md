# ROM-specific blobs

Place files here when building this fork for a ROM whose firmware or TEE files
differ from the files committed in the device tree. Paths are relative to
`device/xiaomi/degas`, so for example:

```
rom-blobs/recovery/root/vendor/lib64/libkeymint.so
rom-blobs/vendor_ramdisk/lib/modules/mtk-some-driver.ko
rom-blobs/ofox_degas-vendor_boot.img
```

The GitHub Actions workflow overlays this directory on the device tree before
building. Keep proprietary files in a private fork or use the workflow's
`blob_archive_url` input instead of committing them to a public repository.
