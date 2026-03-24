# Command-line tool for automating the customization and configuration of handhelds and PCs running SteamOS

> **Fork** of [InnoVision-Games/SteamOS-Utils](https://github.com/InnoVision-Games/SteamOS-Utils) 
> **Changes**: Removal of the static whitelist of kernel versions, replaced with dynamic detection and live verification on the official Valve mirror.

---

## Differences from the original

The main issue with the original implementation was a **static whitelist** of supported kernel versions.
After every SteamOS update, the kernel would be updated and the script would exit with:

```
Attempting to install on an unsupported SteamOS version, now exiting!
```

This fork permanently resolves the issue:

| Behavior | Original | This fork |
|---|---|---|
| Supported versions | Hardcoded static whitelist | Any version with packages on the Valve mirror |
| Check package availability | No | Yes, live check on the mirror |
| Check if already installed | No | Yes, checks `lsmod` before proceeding |
| Error message | Generic “unsupported version” | Indicates the missing package and the reason |

---

## Enabling Linux Dynamic Kernel Module Support (DKMS) ACPI calls

In order to enable custom fan curves and set the Legion Go charge limit, we need to enable
DKMS ACPI call support for SteamOS.

To enable ACPI calls, the following steps must be taken:

- Disable SteamOS read-only mode
- Automatically detect the current kernel version
- Check in real-time on the official Valve mirror if the required packages exist
- Download and install the required kernel modules and kernel header packages
- Install the packages that enable the various daemons required for ACPI calls
- Re-enable SteamOS read-only mode

This script automates all of the above with a single command.

### Installation

```bash
git clone https://github.com/mrsasy89/SteamOS-Utils.git
cd SteamOS-Utils
./SteamOsUtils.py --enable_acpi_calls
```

The command will take several minutes to run depending on your internet connection.

### Expected Output

The script will display the following steps:

```
Step 1: Checking if acpi_call is already active...
Step 2: Detecting current kernel version...
Step 3: Checking package availability on Valve mirror...
  -> Package found on mirror!
  -> Package found on mirror!
All packages found on mirror! Proceeding with installation...
...
Congratulations! ACPI calls enabled. You can now use custom fan curves and charge limit!
Please reboot your device to complete the installation.
```

### If the packages are not yet available

If Valve has not yet released the packages for the current kernel, the script will display:

```
ERROR: Kernel modules package not found on Valve mirror.
Package needed: linux-neptune-XXX-X.XX.XX.valveXX-X-x86_64.pkg.tar.zst
This SteamOS version may not yet be supported. Please check later or open an issue.
```

In this case, wait for Valve to release the packages on the mirror and try again.

### Verify installation

After rebooting, verify that the module is active:

```bash
dkms status
```

Expected output:

```
acpi_call/1.2.2, 6.16.12-valve13-1-neptune-616-g324b4c971758, x86_64: installed
```

```bash
lsmod | grep acpi_call
```

### Check ACPI calls status

```bash
./SteamOsUtils.py --check_dkms_acpi_calls_enabled
```

---

## Tested compatibility

| Kernel | Valve Version | SteamOS | Status |
|---|---|---|---|
| 6.11.11 | valve27-1 | 3.7.x | ✅ Tested |
| 6.16.12 | valve13-1 | 3.8.x | ✅ Tested |

---

## Notes

- The script is designed for the **Lenovo Legion Go** on SteamOS but can work on any handheld device with the Neptune kernel.
- After every SteamOS update, you must rerun the script because the filesystem is rewritten.
- The kernel packages are automatically removed after installation.
