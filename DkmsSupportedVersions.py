'''
    MIT License

    Copyright (c) 2025 InnoVision Games

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.

    file: DkmsSupportedVersions.py

    Modifications (c) 2026 mrsasy89
    CHANGES: replaced static version whitelist with dynamic kernel detection
    and live package availability check against the official Valve mirror.
'''

import os
import platform
import sys
import urllib.request
import re

VALVE_MIRROR_BASE = 'https://steamdeck-packages.steamos.cloud/archlinux-mirror/jupiter-main/os/x86_64/'
REMOTE_PATH = 'jupiter-main/os/x86_64/'

dkms_acpi_enabled_strings = [
    'acpi_call',
]

def get_os_version():
    temp = platform.release()
    temp = temp.split('-')

    os_version = {
        'os_name'              : 'linux',
        'kernel_type'          : temp[3] if len(temp) > 3 else 'neptune',
        'kernel_short_version' : temp[4] if len(temp) > 4 else '',
        'kernel_long_version'  : temp[0],
        'vendor_version'       : temp[1],
        'sub_version'          : temp[2]
    }

    print('\nos_version: ')
    print(os_version)

    return os_version

def get_kernel_modules_filename(os_version):
    print('\nNow generating kernel modules filename...')
    filename = (
        f"{os_version['os_name']}-"
        f"{os_version['kernel_type']}-"
        f"{os_version['kernel_short_version']}-"
        f"{os_version['kernel_long_version']}."
        f"{os_version['vendor_version']}-"
        f"{os_version['sub_version']}-"
        f"x86_64.pkg.tar.zst"
    )
    print('Generated kernel modules filename: %s.' % filename)
    return filename

def get_kernel_headers_filename(os_version):
    print('\nNow generating kernel headers filename...')
    filename = (
        f"{os_version['os_name']}-"
        f"{os_version['kernel_type']}-"
        f"{os_version['kernel_short_version']}-headers-"
        f"{os_version['kernel_long_version']}."
        f"{os_version['vendor_version']}-"
        f"{os_version['sub_version']}-"
        f"x86_64.pkg.tar.zst"
    )
    print('Generated kernel headers filename: %s.' % filename)
    return filename

def check_package_exists_on_mirror(filename):
    """
    Dynamically checks if a package filename exists on the official Valve mirror.
    Returns True if found, False otherwise.
    """
    print('\nChecking Valve mirror for package: %s ...' % filename)
    try:
        url = VALVE_MIRROR_BASE
        req = urllib.request.urlopen(url, timeout=10)
        html = req.read().decode('utf-8')
        if filename in html:
            print('  -> Package found on mirror!')
            return True
        else:
            print('  -> Package NOT found on mirror.')
            return False
    except Exception as e:
        print('  -> Error checking mirror: %s' % str(e))
        return False

def get_remote_kernel_modules_path(kernel_modules_filename):
    print('\nNow generating remote path for: %s ...' % kernel_modules_filename)
    remote_filename = os.path.join(REMOTE_PATH, kernel_modules_filename)
    print('Generated remote filename: %s.' % remote_filename)
    return remote_filename

def get_remote_kernel_headers_path(kernel_headers_filename):
    print('\nNow generating remote path for: %s ...' % kernel_headers_filename)
    remote_filename = os.path.join(REMOTE_PATH, kernel_headers_filename)
    print('Generated remote filename: %s.' % remote_filename)
    return remote_filename

# Legacy static lists kept for backward compatibility
kernel_modules_packages = []
kernel_headers_packages = []
os_remote_kernel_modules_path = {}
os_remote_kernel_headers_path = {}
