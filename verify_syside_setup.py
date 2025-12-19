#!/usr/bin/env python3
"""
SysIDE Setup Verification Script

This script checks if SysIDE Modeler is properly installed and configured
in Cursor/VS Code for SysML file visualization.
"""

import os
import subprocess
import sys
from pathlib import Path


def check_cursor_cli():
    """Check if Cursor CLI is available."""
    try:
        result = subprocess.run(
            ['cursor', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            version = result.stdout.strip().split('\n')[0]
            print(f"✓ Cursor CLI found: {version}")
            return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    
    print("⚠️  Cursor CLI not found in PATH")
    print("   (This is okay - you can still install via UI)")
    return False


def check_syside_extension():
    """Check if SysIDE extension is installed."""
    try:
        result = subprocess.run(
            ['cursor', '--list-extensions'],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            extensions = result.stdout.lower()
            if 'syside' in extensions or 'sensmetry' in extensions:
                print("✓ SysIDE extension appears to be installed")
                # Show matching extensions
                for line in result.stdout.split('\n'):
                    if 'syside' in line.lower() or 'sensmetry' in line.lower():
                        print(f"  - {line.strip()}")
                return True
            else:
                print("❌ SysIDE extension not found in installed extensions")
                print("   Installed extensions (sample):")
                for line in result.stdout.split('\n')[:5]:
                    if line.strip():
                        print(f"     {line.strip()}")
                return False
    except (FileNotFoundError, subprocess.TimeoutExpired):
        print("⚠️  Could not check extensions (CLI may not work in this environment)")
        print("   Please check manually in Cursor: Extensions view")
        return None


def check_sysml_files():
    """Check if .sysml files exist in the project."""
    sysml_files = list(Path('.').glob('*.sysml'))
    if sysml_files:
        print(f"✓ Found {len(sysml_files)} .sysml file(s):")
        for f in sysml_files:
            print(f"  - {f}")
        return True
    else:
        print("⚠️  No .sysml files found in current directory")
        return False


def print_manual_verification_steps():
    """Print manual verification steps."""
    print("\n" + "="*60)
    print("MANUAL VERIFICATION STEPS")
    print("="*60)
    print("\n1. Open Cursor")
    print("2. Press Ctrl+Shift+X to open Extensions view")
    print("3. Search for 'SysIDE Modeler'")
    print("4. Verify it's installed and enabled")
    print("\n5. Open a .sysml file (e.g., OpsCon.sysml)")
    print("6. Check for syntax highlighting (colored text)")
    print("\n7. Press Ctrl+Shift+P to open Command Palette")
    print("8. Type 'SysIDE' and verify commands appear:")
    print("   - SysIDE: Open Diagram")
    print("   - SysIDE Modeler: Install SysIDE Tools")
    print("\n9. If commands don't appear:")
    print("   - Reload window: Ctrl+Shift+P → 'Reload Window'")
    print("   - Check extension is enabled (not disabled)")
    print("   - Restart Cursor completely")


def main():
    """Main verification function."""
    print("="*60)
    print("SysIDE Modeler Setup Verification")
    print("="*60)
    print()
    
    # Check 1: Cursor CLI
    print("Checking Cursor CLI...")
    cli_available = check_cursor_cli()
    print()
    
    # Check 2: SysIDE Extension
    print("Checking SysIDE Extension...")
    extension_status = check_syside_extension()
    print()
    
    # Check 3: .sysml files
    print("Checking .sysml files...")
    has_sysml = check_sysml_files()
    print()
    
    # Summary
    print("="*60)
    print("VERIFICATION SUMMARY")
    print("="*60)
    
    if extension_status is True:
        print("✓ SysIDE extension appears to be installed")
        print("\nNext steps:")
        print("1. Open Cursor and verify extension is enabled")
        print("2. Run 'SysIDE Modeler: Install SysIDE Tools' command")
        print("3. Reload window")
        print("4. Test with: Ctrl+Shift+P → 'SysIDE: Open Diagram'")
    elif extension_status is False:
        print("❌ SysIDE extension not found")
        print("\nPlease install:")
        print("1. Open Cursor → Ctrl+Shift+X")
        print("2. Search 'SysIDE Modeler'")
        print("3. Click Install")
        print("\nSee QUICK_INSTALL_SYSIDE.md for detailed steps")
    else:
        print("⚠️  Could not verify extension status automatically")
        print_manual_verification_steps()
    
    if has_sysml:
        print("\n✓ .sysml files found - ready for testing")
    
    print("\n" + "="*60)
    print("For detailed setup instructions, see:")
    print("  - QUICK_INSTALL_SYSIDE.md (quick guide)")
    print("  - SYSIDE_SETUP.md (detailed guide)")
    print("="*60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nVerification cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error during verification: {e}")
        print("\nPlease verify manually using the steps in QUICK_INSTALL_SYSIDE.md")
        sys.exit(1)







