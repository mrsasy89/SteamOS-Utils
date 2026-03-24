'''
    MIT License

    Copyright (c) 2025 InnoVision Games
    Modifications (c) 2026 mrsasy89

    file: AcpiEnabler.py

    CHANGES: replaced static whitelist check with dynamic Valve mirror check.
    Now supports any kernel version as long as packages exist on the mirror.
'''

import sys

from FileDownloader import download_kernel_packages
from ShellUtils import run_command
from DkmsSupportedVersions import dkms_acpi_enabled_strings
from DkmsSupportedVersions import get_os_version
from DkmsSupportedVersions import get_remote_kernel_modules_path
from DkmsSupportedVersions import get_remote_kernel_headers_path
from DkmsSupportedVersions import get_kernel_modules_filename
from DkmsSupportedVersions import get_kernel_headers_filename
from DkmsSupportedVersions import check_package_exists_on_mirror

def check_acpi_call_active():
    """
    Check if acpi_call module is currently loaded.
    """
    result = run_command(['lsmod'])
    if result and 'acpi_call' in result.stdout:
        return True
    return False

def prep_steamos(dry_run=True):
    print('\nDisabling SteamOS read-only mode.')
    run_command(['sudo', 'steamos-readonly', 'disable'], dry_run)

    print('\nClearing Pacman keys')
    run_command(['sudo', 'rm', '-r', '/etc/pacman.d/gnupg'], dry_run)

    print('\nInitializing Pacman keys')
    run_command(['sudo', 'pacman-key', '--init'], dry_run)

    print('\nPopulating Pacman Arch Linux keys')
    run_command(['sudo', 'pacman-key', '--populate', 'archlinux'], dry_run)

    print('\nPopulating Pacman SteamOS holo keys')
    run_command(['sudo', 'pacman-key', '--populate', 'holo'], dry_run)

    print('\nUpdating packages.')
    run_command(['sudo', 'pacman', '-Sy'], dry_run)

def install_kernel_packages(kernel_modules_filename, kernel_headers_filename, dry_run=True):
    print('\nInstalling required kernel modules')
    run_command(['sudo', 'pacman', '-U', kernel_modules_filename, '--noconfirm'], dry_run)

    print('\nInstalling required kernel headers')
    run_command(['sudo', 'pacman', '-U', kernel_headers_filename, '--noconfirm'], dry_run)

def finalize_steamos(dry_run=True):
    print('\nInstalling DKMS and build tools')
    run_command(['sudo', 'pacman', '-Sy', 'dkms', 'git', 'base-devel', '--noconfirm'], dry_run)

    print('\nEnabling Linux Dynamic Kernel Module Support ACPI calls')
    run_command(['sudo', 'pacman', '-Sy', 'acpi_call-dkms', '--noconfirm'], dry_run)

    print('\nRe-enabling SteamOS read-only mode.')
    run_command(['sudo', 'steamos-readonly', 'enable'], dry_run)

def cleanup(kernel_modules_filename, kernel_headers_filename, dry_run=True):
    print('\nCleaning up: %s.' % kernel_modules_filename)
    run_command(['rm', '-f', kernel_modules_filename], dry_run)

    print('Cleaning up: %s.' % kernel_headers_filename)
    run_command(['rm', '-f', kernel_headers_filename], dry_run)

def check_dkms_acpi_calls_enabled(dry_run):
    print('\nChecking if acpi_call DKMS module is active...')
    result = run_command(['lsmod'])
    if result and 'acpi_call' in result.stdout:
        print('  -> acpi_call module is LOADED and active.')
        return True
    print('  -> acpi_call module is NOT loaded.')
    return False

def enable_acpi_calls(dry_run):
    # 1. Check if already active
    print('\nStep 1: Checking if acpi_call is already active...')
    if check_acpi_call_active():
        print('acpi_call is already loaded! Nothing to do.')
        sys.exit(0)

    # 2. Detect current kernel version
    print('\nStep 2: Detecting current kernel version...')
    os_version = get_os_version()
    kernel_modules_filename = get_kernel_modules_filename(os_version)
    kernel_headers_filename = get_kernel_headers_filename(os_version)

    # 3. Check if packages exist on Valve mirror
    print('\nStep 3: Checking package availability on Valve mirror...')
    if not check_package_exists_on_mirror(kernel_modules_filename):
        print('\nERROR: Kernel modules package not found on Valve mirror.')
        print('Package needed: %s' % kernel_modules_filename)
        print('This SteamOS version may not yet be supported. Please check later or open an issue.')
        sys.exit(-1)

    if not check_package_exists_on_mirror(kernel_headers_filename):
        print('\nERROR: Kernel headers package not found on Valve mirror.')
        print('Package needed: %s' % kernel_headers_filename)
        print('This SteamOS version may not yet be supported. Please check later or open an issue.')
        sys.exit(-1)

    print('\nAll packages found on mirror! Proceeding with installation...')

    # 4. Download required kernel packages
    remote_kernel_modules_filename = get_remote_kernel_modules_path(kernel_modules_filename)
    remote_kernel_headers_filename = get_remote_kernel_headers_path(kernel_headers_filename)
    download_kernel_packages(remote_kernel_modules_filename, remote_kernel_headers_filename, dry_run)

    # 5. Prepare SteamOS and package manager
    prep_steamos(dry_run)

    # 6. Install kernel packages
    install_kernel_packages(kernel_modules_filename, kernel_headers_filename, dry_run)

    # 7. Enable required services
    finalize_steamos(dry_run)

    # 8. Cleanup
    cleanup(kernel_modules_filename, kernel_headers_filename, dry_run)

    print('\nCongratulations! ACPI calls enabled. You can now use custom fan curves and charge limit!')
    print('Please reboot your device to complete the installation.')
