# SysIDE Modeler Setup Guide

This guide will help you install and configure SysIDE Modeler in Cursor for SysML diagram visualization.

## Prerequisites

- Cursor (or VS Code) installed
- Internet connection for downloading extensions and tools
- `.sysml` files to work with

## Installation Steps

### Step 1: Install SysIDE Modeler Extension

**Option A: Via Extension Marketplace (Recommended)**

1. Open Cursor
2. Press `Ctrl+Shift+X` (or `Cmd+Shift+X` on macOS) to open Extensions view
3. Search for **"SysIDE Modeler"** in the search bar
4. Look for the extension published by **Sensmetry**
5. Click **"Install"**
6. Wait for installation to complete

**Option B: Via Command Line**

```bash
# Try these extension IDs (one should work)
cursor --install-extension sensmetry.syside-modeler
# OR
cursor --install-extension SysIDE.syside-modeler
```

**Option C: Via Extension ID**

1. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on macOS)
2. Type: `Extensions: Install Extensions`
3. Enter extension ID: `sensmetry.syside-modeler`
4. Press Enter

### Step 2: Install SysIDE Tools Backend

After the extension is installed:

1. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on macOS) to open Command Palette
2. Type: **"SysIDE Modeler: Install SysIDE Tools"**
3. Select the command
4. Follow the prompts to download and install backend tools
5. If prompted for a license:
   - Select **"Trial"** or **"Evaluation"** mode
   - You can use the extension in trial mode for evaluation

### Step 3: Reload Window

1. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on macOS)
2. Type: **"Reload Window"**
3. Press Enter
4. Wait for Cursor to reload

### Step 4: Verify Installation

1. **Open a `.sysml` file** (e.g., `OpsCon.sysml`)
2. **Check syntax highlighting:**
   - The file should have colored syntax
   - Keywords like `package`, `part def`, `connect` should be highlighted
3. **Check Command Palette:**
   - Press `Ctrl+Shift+P`
   - Type "SysIDE"
   - You should see commands like:
     - `SysIDE: Open Diagram`
     - `SysIDE Modeler: Install SysIDE Tools`
     - `SysIDE: Generate Documentation`
4. **Test Diagram Visualization:**
   - Right-click on a `.sysml` file
   - Look for "SysIDE" context menu options
   - Or use Command Palette: `SysIDE: Open Diagram`

## Troubleshooting

### Extension Not Found

If you can't find "SysIDE Modeler" in the marketplace:

1. **Check publisher name:** Look for extensions by **"Sensmetry"**
2. **Alternative search terms:** Try searching for:
   - "SysIDE"
   - "SysML"
   - "Sensmetry"
3. **Manual installation:** Visit [VS Code Marketplace](https://marketplace.visualstudio.com/) and search for "SysIDE Modeler"

### Installation Fails

1. **Check Cursor version:** Ensure you're using a recent version
2. **Check internet connection:** Extension download requires internet
3. **Try manual installation:** Use the Extensions view instead of CLI
4. **Check permissions:** Ensure you have write permissions for extension directory

### Tools Installation Fails

1. **Check disk space:** Ensure sufficient space for backend tools
2. **Check permissions:** May need admin/sudo permissions
3. **Manual download:** Visit [SysIDE Documentation](https://docs.sensmetry.com/latest/modeler/install.html)
4. **Firewall/Proxy:** Ensure network access for downloading tools

### Syntax Highlighting Not Working

1. **Reload window:** Press `Ctrl+Shift+P` → "Reload Window"
2. **Check file association:** Ensure `.sysml` files are associated with SysML language
3. **Check extension status:** Verify extension is enabled in Extensions view
4. **Reinstall extension:** Try disabling and re-enabling the extension

### Commands Not Appearing

1. **Verify extension is active:** Check Extensions view for enabled status
2. **Reload window:** This is often required after installation
3. **Check extension output:** View → Output → Select "SysIDE Modeler" from dropdown
4. **Restart Cursor:** Fully close and reopen Cursor

## Integration with Existing Slides Generator

Your existing slides generation system (`main.py`) will continue to work alongside SysIDE:

- **SysIDE Modeler:** For interactive diagram visualization and editing
- **Your Python tool:** For automated slide generation (Google Slides/PowerPoint)

Both can work with the same `.sysml` files:

```bash
# Use SysIDE for visualization
# (Open .sysml file in Cursor and use SysIDE commands)

# Use your tool for slide generation
python main.py OpsCon.sysml --format pptx
```

## Verification Checklist

- [ ] SysIDE Modeler extension installed
- [ ] SysIDE Tools backend installed
- [ ] Window reloaded after installation
- [ ] `.sysml` files show syntax highlighting
- [ ] Command Palette shows SysIDE commands
- [ ] Can open diagrams from `.sysml` files
- [ ] Existing slides generator still works

## Next Steps

After successful installation:

1. **Test diagram visualization:**
   - Open `OpsCon.sysml`
   - Use `SysIDE: Open Diagram` command
   - Verify diagram renders correctly

2. **Test slides generation:**
   ```bash
   python main.py OpsCon.sysml --format pptx
   ```

3. **Explore SysIDE features:**
   - Try different diagram types
   - Explore editing capabilities
   - Check documentation generation

## Resources

- **SysIDE Documentation:** https://docs.sensmetry.com/latest/modeler/install.html
- **VS Code Marketplace:** https://marketplace.visualstudio.com/
- **Your Project README:** See `README.md` for slides generation usage

## Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review extension output logs (View → Output → SysIDE Modeler)
3. Check SysIDE documentation
4. Verify Cursor/VS Code is up to date







