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
    CHANGES: dynamic repo discovery across all jupiter-* repos.
    CHANGES: search starts from the current stable repo (detected from
    pacman mirrorlist or DB files), then other versioned repos sorted
    descending, then jupiter-main as last fallback.
'''

import os
import platform
import sys
import urllib.request
import re
import glob

VALVE_MIRROR_ROOT = 'https://steamdeck-packages.steamos.cloud/archlinux-mirror/'

dkms_acpi_enabled_strings = [
    'acpi_call',
]

def detect_current_stable_repo():
    """
    Detects the current stable repo name used by pacman.
    Strategy 1: parse /etc/pacman.d/mirrorlist for a jupiter-* entry.
    Strategy 2: scan /var/lib/pacman/sync/ for jupiter-*.db files.
    Returns a repo name like 'jupiter-3.8.1x' or None if not detected.
    """
    # Strategy 1: mirrorlist
    mirrorlist_path = '/etc/pacman.d/mirrorlist'
    try:
        with open(mirrorlist_path, 'r') as f:
            content = f.read()
        matches = re.findall(r'archlinux-mirror/(jupiter-[^/]+)/os/', content)
        for m in matches:
            if m != 'jupiter-main':
                print('  -> Detected stable repo from mirrorlist: %s' % m)
                return m
    except Exception:
        pass

    # Strategy 2: pacman sync db files
    try:
        db_files = glob.glob('/var/lib/pacman/sync/jupiter-*.db')
        for db in db_files:
            name = os.path.basename(db).replace('.db', '')
            if name != 'jupiter-main':
                print('  -> Detected stable repo from pacman db: %s' % name)
                return name
    except Exception:
        pass

    print('  -> Could not detect stable repo, will scan all.')
    return None

def discover_valve_repo(filename):
    """
    Searches for the package across Valve repos in this order:
      1. Current stable repo (detected from the running system)
      2. Other versioned jupiter-* repos, sorted descending (newest first)
      3. jupiter-main as last fallback
    Returns (base_url, remote_path) if found, (None, None) otherwise.
    """
    print('\nDiscovering Valve repos for package: %s ...' % filename)

    # Detect the stable repo first
    stable_repo = detect_current_stable_repo()

    # Fetch all available repos from the mirror root
    try:
        req = urllib.request.urlopen(VALVE_MIRROR_ROOT, timeout=10)
        html = req.read().decode('utf-8')
        all_repos = re.findall(r'href="(jupiter-[^/"]+)/?"', html)
        all_repos = list(dict.fromkeys(all_repos))  # deduplicate, preserve order
    except Exception as e:
        print('  -> Error scanning mirror root: %s' % str(e))
        all_repos = []

    # Build ordered search list:
    # 1. stable repo first (if detected and present)
    # 2. other versioned repos sorted descending (newest first), excluding main
    # 3. jupiter-main last
    versioned = sorted(
        [r for r in all_repos if r != 'jupiter-main' and r != stable_repo],
        reverse=True
    )
    ordered_repos = []
    if stable_repo:
        ordered_repos.append(stable_repo)
    ordered_repos.extend(versioned)
    if 'jupiter-main' in all_repos:
        ordered_repos.append('jupiter-main')
    elif not ordered_repos:
        ordered_repos = ['jupiter-main']

    print('  -> Search order: %s' % ordered_repos)

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
    package exists.
    Returns (True, base_url, remote_path) if found,
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
