# Quick Install: SysIDE Modeler for Cursor

## 🚀 Fast Installation (5 minutes)

### Step 1: Install Extension (2 min)
1. Open **Cursor**
2. Press **`Ctrl+Shift+X`** (Extensions view)
3. Search: **"SysIDE Modeler"**
4. Click **Install** (by Sensmetry)

### Step 2: Install Tools (2 min)
1. Press **`Ctrl+Shift+P`** (Command Palette)
2. Type: **"SysIDE Modeler: Install SysIDE Tools"**
3. Select it → Follow prompts
4. Choose **"Trial/Evaluation"** if asked for license

### Step 3: Reload (30 sec)
1. Press **`Ctrl+Shift+P`**
2. Type: **"Reload Window"**
3. Press Enter

### Step 4: Verify (30 sec)
1. Open **`OpsCon.sysml`**
2. Check for **syntax highlighting** (colored text)
3. Press **`Ctrl+Shift+P`** → Type **"SysIDE"**
4. Should see: **"SysIDE: Open Diagram"**

## ✅ Success Checklist

- [ ] Extension installed (check Extensions view)
- [ ] Tools installed (Command Palette shows SysIDE commands)
- [ ] Window reloaded
- [ ] `.sysml` files have syntax highlighting
- [ ] Can run "SysIDE: Open Diagram" command

## 🔧 Troubleshooting

**Extension not found?**
- Search for "Sensmetry" (publisher name)
- Or visit: https://marketplace.visualstudio.com/

**Commands not appearing?**
- Reload window again
- Check extension is enabled (not disabled)
- Restart Cursor completely

**Syntax highlighting not working?**
- Right-click `.sysml` file → "Open With" → "SysML"
- Or check file association in settings

## 📝 Integration Notes

Your existing slides generator (`main.py`) works alongside SysIDE:

```bash
# SysIDE: Visual diagrams in Cursor
# Your tool: Automated slides
python main.py OpsCon.sysml --format pptx
```

Both use the same `.sysml` files! 🎉







