#
# OrangeFox build-time variables for degas (Xiaomi 14T).
# vendor/recovery/OrangeFox_A16.sh reads FOX_* from the build environment
# (/tmp/<device>/fox_env.sh), so they must be exported here, not in BoardConfig.
#
FDEVICE="degas"

fox_get_target_device() {
local chkdev=$(echo "$BASH_SOURCE" | grep -w \"$FDEVICE\")
   if [ -n "$chkdev" ]; then
      FOX_BUILD_DEVICE="$FDEVICE"
   else
      chkdev=$(set | grep BASH_ARGV | grep -w \"$FDEVICE\")
      [ -n "$chkdev" ] && FOX_BUILD_DEVICE="$FDEVICE"
   fi
}

if [ -z "$1" -a -z "$FOX_BUILD_DEVICE" ]; then
   fox_get_target_device
fi

if [ "$1" = "$FDEVICE" -o "$FOX_BUILD_DEVICE" = "$FDEVICE" ]; then
	# A/B, virtual A/B, recovery in vendor_boot
	export FOX_AB_DEVICE=1
	export FOX_VIRTUAL_AB_DEVICE=1
	export FOX_VENDOR_BOOT_RECOVERY=1

	# size: vendor_boot is 64 MiB and also carries ~20 MiB of kernel modules
	export FOX_DRASTIC_SIZE_REDUCTION=1
	export FOX_REMOVE_BASH=1
	export FOX_EXCLUDE_NANO_EDITOR=1
	export FOX_DELETE_AROMAFM=1
	export FOX_DELETE_INITD_ADDON=1
else
	if [ -z "$FOX_BUILD_DEVICE" -a -z "$BASH_SOURCE" ]; then
		echo "I: This script requires bash. Not processing the $FDEVICE $(basename $0)"
	fi
fi
