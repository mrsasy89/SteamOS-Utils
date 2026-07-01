# Command-line tool for automating the customization and configuration of handhelds and PCs running SteamOS

> **Fork** of [InnoVision-Games/SteamOS-Utils](https://github.com/InnoVision-Games/SteamOS-Utils)  
> **Changes**: Removal of the static whitelist of kernel versions, replaced with dynamic detection, live verification and automatic discovery of the correct Valve repo.

---

## Differences from the original

The original implementation had two issues: a **static whitelist** of supported kernel versions, and a **hardcoded mirror URL** pointing to `jupiter-main` — a repo that Valve no longer updates with recent kernels.

This fork permanently resolves both issues:

| Behavior | Original | This fork |
|---|---|---|
| Supported versions | Hardcoded static whitelist | Any version with packages on the Valve mirror |
| Mirror repo | Hardcoded `jupiter-main` | Dynamically discovered (e.g. `jupiter-3.8.1x`) |
| Search order | N/A | Stable repo first, then others descending, then `jupiter-main` |
| Check package availability | No | Yes, live check on the mirror |
| Check if already installed | No | Yes, checks `lsmod` before proceeding |
| Error message | Generic "unsupported version" | Indicates the missing package and the reason |

---

## How dynamic repo discovery works

On every run the script:

1. **Detects the current stable repo** used by pacman on the running system — first by parsing `/etc/pacman.d/mirrorlist`, then by scanning `/var/lib/pacman/sync/jupiter-*.db` files (e.g. `jupiter-3.8.1x`)
2. **Scans the Valve mirror root** (`https://steamdeck-packages.steamos.cloud/archlinux-mirror/`) for all `jupiter-*` repos
3. **Searches in priority order**:
   - The detected stable repo first (fastest, hit rate ~100% for the running system)
   - Other versioned repos sorted descending (newest first)
   - `jupiter-main` as last fallback
4. **Returns the correct `base_url` and `remote_path`** so packages are always downloaded from the right repo

This means the script will continue to work automatically across future SteamOS updates without any code changes.

---

## Enabling Linux Dynamic Kernel Module Support (DKMS) ACPI calls

In order to enable custom fan curves and set the Legion Go charge limit, we need to enable
DKMS ACPI call support for SteamOS.

To enable ACPI calls, the following steps must be taken:

- Disable SteamOS read-only mode
- Automatically detect the current kernel version
- Discover the correct Valve repo and check in real-time if the required packages exist
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

os_version:
{'os_name': 'linux', 'kernel_type': 'neptune', 'kernel_short_version': '616', 'kernel_long_version': '6.16.12', 'vendor_version': 'valve24.1', 'sub_version': '1'}

Now generating kernel modules filename...
Generated kernel modules filename: linux-neptune-616-6.16.12.valve24.1-1-x86_64.pkg.tar.zst.

Now generating kernel headers filename...
Generated kernel headers filename: linux-neptune-616-headers-6.16.12.valve24.1-1-x86_64.pkg.tar.zst.

Step 3: Checking package availability on Valve mirror...

  -> Detected stable repo from mirrorlist: jupiter-3.8.1x
  -> Search order: ['jupiter-3.8.1x', 'jupiter-main']
  -> Package found in repo: jupiter-3.8.1x
  -> Package found on mirror!
  -> Package found in repo: jupiter-3.8.1x
  -> Package found on mirror!

All packages found on mirror! Proceeding with installation...
...
Congratulations! ACPI calls enabled. You can now use custom fan curves and charge limit!
Please reboot your device to complete the installation.
```

### If the packages are not yet available

If Valve has not yet released the packages for the current kernel version in any repo, the script will display:

```
ERROR: Kernel modules package not found on Valve mirror.
Package needed: linux-neptune-XXX-X.XX.XX.valveXX-X-x86_64.pkg.tar.zst
This SteamOS version may not yet be supported. Please check later or open an issue.
```

In this case, wait for Valve to release the packages on the mirror and try again.  
You can manually check availability at:  
`https://steamdeck-packages.steamos.cloud/archlinux-mirror/`

### Verify installation

After rebooting, verify that the module is active:

```bash
dkms status
```

Expected output:

```
acpi_call/1.2.2, 6.16.12-valve24.1-1-neptune-616, x86_64: installed
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
| 6.16.12 | valve24.1-1 | 3.8.1x | ✅ Tested |

---

## Notes

- The script is designed for the **Lenovo Legion Go** on SteamOS but can work on any handheld device with the Neptune kernel.
- After every SteamOS update, you must rerun the script because the filesystem is rewritten.
- The kernel packages are automatically removed after installation.
- The stable repo is detected automatically — no manual configuration needed after a SteamOS version update.
