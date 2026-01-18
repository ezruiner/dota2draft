#!/usr/bin/env python3
"""
Automated release builder for Synergy.OS
Handles versioning, building, and GitHub integration
"""

import subprocess
import sys
import json
import re
from pathlib import Path

def update_version(version: str):
    """Update version in all config files"""
    
    # Update Cargo.toml (root)
    p = Path('Cargo.toml')
    if p.exists():
        content = p.read_text()
        # Only update version in [package] section
        new_content = re.sub(
            r'(\[package\][^\[]*?version\s*=\s*)"[^"]*"',
            rf'\1"{version}"',
            content,
            flags=re.DOTALL
        )
        p.write_text(new_content)
        print(f"✓ Updated {p}")
    
    # Update src-tauri/Cargo.toml
    p = Path('src-tauri/Cargo.toml')
    if p.exists():
        content = p.read_text()
        # Only update version in [package] section
        new_content = re.sub(
            r'(\[package\][^\[]*?version\s*=\s*)"[^"]*"',
            rf'\1"{version}"',
            content,
            flags=re.DOTALL
        )
        p.write_text(new_content)
        print(f"✓ Updated {p}")
    
    # Update tauri.conf.json
    p = Path('src-tauri/tauri.conf.json')
    if p.exists():
        content = p.read_text()
        data = json.loads(content)
        data['version'] = version
        p.write_text(json.dumps(data, indent=2))
        print(f"✓ Updated {p}")
    
    # Update package.json
    p = Path('package.json')
    if p.exists():
        content = p.read_text()
        data = json.loads(content)
        data['version'] = version
        p.write_text(json.dumps(data, indent=2))
        print(f"✓ Updated {p}")

def build():
    """Build the release"""
    print("\n📦 Building release...")
    result = subprocess.run(['cargo', 'tauri', 'build'], capture_output=True, text=True)
    
    if result.returncode != 0:
        print("✗ Build failed!")
        print(result.stderr)
        return False
    
    print("✓ Build completed!")
    return True

def create_tag(version: str):
    """Create and push git tag"""
    print(f"\n🏷️  Creating tag v{version}...")
    
    try:
        subprocess.run(['git', 'add', '.'], check=True)
        subprocess.run(['git', 'commit', '-m', f'Release v{version}'], check=True)
        subprocess.run(['git', 'tag', f'v{version}'], check=True)
        subprocess.run(['git', 'push', 'origin', f'v{version}'], check=True)
        print(f"✓ Tag v{version} pushed!")
        print(f"✓ GitHub Actions will automatically build the release")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Git operation failed: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python build-release.py VERSION")
        print("Example: python build-release.py 0.2.0")
        sys.exit(1)
    
    version = sys.argv[1]
    
    print("=" * 50)
    print(f"Synergy.OS - Release Builder v{version}")
    print("=" * 50)
    
    # Validate version format
    if not re.match(r'^\d+\.\d+\.\d+$', version):
        print("✗ Invalid version format. Use: X.Y.Z")
        sys.exit(1)
    
    # Update versions
    update_version(version)
    
    # Build
    if not build():
        sys.exit(1)
    
    # Get paths
    release_dir = Path(f'src-tauri/target/release/bundle/msi')
    exe_file = release_dir / f'Synergy.OS_{version}_x64.exe'
    msi_file = release_dir / f'Synergy.OS_{version}_x64.msi'
    
    if exe_file.exists() and msi_file.exists():
        print(f"\n✓ Release artifacts ready:")
        print(f"  - {exe_file}")
        print(f"  - {msi_file}")
    else:
        print("\n⚠️  Some artifacts not found:")
        print(f"  EXE exists: {exe_file.exists()}")
        print(f"  MSI exists: {msi_file.exists()}")
    
    # Offer to create tag
    response = input(f"\n📤 Create GitHub tag and push v{version}? (y/n): ")
    if response.lower() == 'y':
        if create_tag(version):
            print("\n" + "=" * 50)
            print("✓ Release process completed!")
            print("=" * 50)
            print(f"\nCheck GitHub: https://github.com/ezruiner/dota2draft/releases/tag/v{version}")
        else:
            print("\n✗ Tag creation failed")
            sys.exit(1)

if __name__ == '__main__':
    main()
