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
    CHANGES: replaced hardcoded jupiter-main repo with dynamic discovery
    of all jupiter-* repos on the Valve mirror root, so the correct
    versioned repo (e.g. jupiter-3.8.1x) is always found automatically.
'''

import os
import platform
import sys
import urllib.request
import re

VALVE_MIRROR_ROOT = 'https://steamdeck-packages.steamos.cloud/archlinux-mirror/'

dkms_acpi_enabled_strings = [
    'acpi_call',
]

def discover_valve_repo(filename):
    """
    Scans the Valve mirror root for all jupiter-* repos and returns
    the base URL and remote path of the first repo that contains the
    requested package filename. Falls back to jupiter-main if none found.
    """
    print('\nDiscovering Valve repos for package: %s ...' % filename)
    try:
        req = urllib.request.urlopen(VALVE_MIRROR_ROOT, timeout=10)
        html = req.read().decode('utf-8')
        # Find all jupiter-* repo directory names
        repos = re.findall(r'href="(jupiter-[^/"]+)/?"', html)
        # Deduplicate while preserving order, prefer versioned repos over jupiter-main
        seen = set()
        ordered_repos = []
        for r in repos:
            if r not in seen:
                seen.add(r)
                if r != 'jupiter-main':
                    ordered_repos.append(r)
        # Append jupiter-main as last fallback
        if 'jupiter-main' in seen:
            ordered_repos.append('jupiter-main')
        print('  -> Found repos: %s' % ordered_repos)
    except Exception as e:
        print('  -> Error scanning mirror root: %s' % str(e))
        ordered_repos = ['jupiter-main']

    for repo in ordered_repos:
        base_url = '%s%s/os/x86_64/' % (VALVE_MIRROR_ROOT, repo)
        remote_path = '%s/os/x86_64/' % repo
        try:
            req = urllib.request.urlopen(base_url, timeout=10)
            html = req.read().decode('utf-8')
            if filename in html:
                print('  -> Package found in repo: %s' % repo)
                return base_url, remote_path
            else:
                print('  -> Not in repo: %s' % repo)
        except Exception as e:
            print('  -> Error checking repo %s: %s' % (repo, str(e)))

    print('  -> Package not found in any repo.')
    return None, None

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
    Dynamically discovers the correct Valve repo and checks if the
    package exists. Returns (True, base_url, remote_path) if found,
    (False, None, None) otherwise.
    """
    print('\nChecking Valve mirror for package: %s ...' % filename)
    base_url, remote_path = discover_valve_repo(filename)
    if base_url is not None:
        print('  -> Package found on mirror!')
        return True, base_url, remote_path
    else:
        print('  -> Package NOT found on mirror.')
        return False, None, None

def get_remote_kernel_modules_path(kernel_modules_filename, remote_path=None):
    print('\nNow generating remote path for: %s ...' % kernel_modules_filename)
    rpath = remote_path if remote_path else 'jupiter-main/os/x86_64/'
    remote_filename = os.path.join(rpath, kernel_modules_filename)
    print('Generated remote filename: %s.' % remote_filename)
    return remote_filename

def get_remote_kernel_headers_path(kernel_headers_filename, remote_path=None):
    print('\nNow generating remote path for: %s ...' % kernel_headers_filename)
    rpath = remote_path if remote_path else 'jupiter-main/os/x86_64/'
    remote_filename = os.path.join(rpath, kernel_headers_filename)
    print('Generated remote filename: %s.' % remote_filename)
    return remote_filename

# Legacy static lists kept for backward compatibility
kernel_modules_packages = []
kernel_headers_packages = []
os_remote_kernel_modules_path = {}
os_remote_kernel_headers_path = {}
