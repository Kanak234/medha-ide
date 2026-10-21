# Snap Store Submission Guide for MEDHA IDE

This document contains the exact steps for Kanak Prabhakar (kanakprabhakar72@gmail.com, GitHub: Kanak234) to publish **medha-ide** to the Snap Store with classic confinement.

---

## Prerequisites

- [ ] Snapcraft installed: `sudo snap install snapcraft --classic`
- [ ] Snapcraft CLI authenticated: `snapcraft login` (uses Ubuntu One account)
- [ ] GitHub repository: https://github.com/Kanak234/medha-ide
- [ ] Snap name registered: `medha-ide`
- [ ] App ID: `io.github.Kanak234.Medha`

---

## Step 1: Register the Snap Name

```bash
# Register the snap name on snapcraft.io
snapcraft register medha-ide
```

**Expected output:**
```
We've registered the snap name `medha-ide` for you.
You can now use this name when you push your snap.
```

> **Note:** Do this first — snap names are first-come, first-served.

---

## Step 2: Build the Snap Locally (Optional Verification)

```bash
cd /home/kanak07/chromium-shift/medha-ide
snapcraft --destructive-mode
```

This builds the snap using Multipass (VM). For classic confinement, local builds work but **cannot be uploaded to stable channel**.

---

## Step 3: Remote Build on Launchpad (Recommended for Classic)

Classic confinement snaps **must** be built on Launchpad (remote-build) for store upload.

```bash
# Trigger remote build on Launchpad builders
snapcraft remote-build --build-on=amd64,arm64
```

**What this does:**
- Queues build on Launchpad for `amd64` and `arm64`
- Produces `.snap` files for each architecture
- Takes 10–30 minutes depending on queue

**Monitor progress:**
```bash
snapcraft remote-build --watch
# Or check at: https://launchpad.net/~kanak234/+snap/medha-ide
```

---

## Step 4: Upload to Edge Channel

Once remote-build completes, download the `.snap` files and upload:

```bash
# List completed builds
snapcraft remote-build --list

# Download the built snaps (they're attached to the build)
# Or use snapcraft CLI to release directly from the build
snapcraft release medha-ide <revision> edge
```

**Alternative: Manual upload**
```bash
# If you have the .snap file locally
snapcraft upload medha-ide_1.1.0_amd64.snap --release=edge
snapcraft upload medha-ide_1.1.0_arm64.snap --release=edge
```

**Expected output:**
```
Uploading medha-ide_1.1.0_amd64.snap... OK
Released to edge channel.
```

> **Critical:** Classic confinement snaps **cannot go to stable** until approved by Snap Store reviewers. They must start in `edge` → `beta` → `candidate` → then request stable.

---

## Step 5: Request Classic Confinement Approval

This is **mandatory** for classic snaps. Without approval, the snap stays in `edge`/`beta` only.

### 5.1 Prepare Justification Text

Copy the following justification and paste it into the forum request:

---

**Title:** Classic confinement request for medha-ide

**Category:** store-requests

**Body:**

```
Snap name: medha-ide
App ID: io.github.Kanak234.Medha
Publisher: Kanak Prabhakar (kanakprabhakar72@gmail.com, GitHub: Kanak234)

MEDHA IDE is a native desktop IDE for C/C++/Python development (similar to VS Code, PyCharm, Qt Creator). It requires classic confinement because:

1. **Host toolchain execution**: The IDE spawns gcc, g++, gdb, python3, clangd, pylsp, cmake, git, ollama via QProcess. These are user-installed system binaries in /usr/bin, /usr/local/bin, etc. Strict confinement blocks access to arbitrary host binaries.

2. **Real terminal (PTY)**: The integrated terminal allocates a PTY and runs the user's shell (bash, zsh, fish). Strict confinement denies PTY allocation and shell access.

3. **Debugger (ptrace)**: GDB debugging requires ptrace syscall to attach to processes. Strict confinement blocks ptrace.

4. **Project directories anywhere**: Users open projects in /opt, /mnt, /media, /srv, etc. Strict confinement only allows $HOME and removable-media.

5. **LSP servers**: clangd and pylsp are external language servers installed by the user. The IDE connects to them via stdio/sockets. Strict confinement blocks arbitrary executable execution.

6. **Build systems**: CMake, Make, Ninja invoked in project directories. Strict confinement blocks build tool execution.

This is the same requirement as:
- code (VS Code) — classic
- pycharm-community, pycharm-professional — classic
- qtcreator — classic
- kdevelop — classic
- clangd — classic

The snap uses the `python` plugin + `dump` part to ship the MEDHA source tree ($SNAP/app/medha) and assets. The launcher sets PYTHONPATH, QT_PLUGIN_PATH, LD_LIBRARY_PATH for Qt6 plugins (xcb, wayland) and system libraries.

Source: https://github.com/Kanak234/medha-ide
Snapcraft.yaml: https://github.com/Kanak234/medha-ide/blob/main/snap/snapcraft.yaml
```

---

### 5.2 Post on Snapcraft Forum

1. Go to: https://forum.snapcraft.io/c/store-requests/18
2. Click **New Topic**
3. Category: **store-requests**
4. Title: **Classic confinement request for medha-ide**
5. Paste the justification body above
6. Submit

**Expected timeline:** 3–10 business days for review.

---

## Step 6: Promote Through Channels

Once classic confinement is **approved** (you'll get an email/forum notification):

```bash
# Promote from edge to beta
snapcraft release medha-ide <revision> beta

# Promote from beta to candidate (after testing)
snapcraft release medha-ide <revision> candidate

# Promote from candidate to stable (final)
snapcraft release medha-ide <revision> stable
```

---

## Step 7: Verify Store Listing

After stable release, verify at:
- https://snapcraft.io/medha-ide
- `snap info medha-ide`

Check:
- [ ] Name: `medha-ide`
- [ ] Summary/Description matches README
- [ ] Icon appears (512px)
- [ ] Screenshots appear (after adding via dashboard)
- [ ] License: GPL-3.0-or-later
- [ ] Confinement: classic
- [ ] Channels: stable, candidate, beta, edge all present

---

## Adding Screenshots (Post-Release)

1. Go to https://snapcraft.io/medha-ide/publish
2. Click **Media** tab
3. Upload `docs/screenshots/editor.png` and `docs/screenshots/disassembly.png`
4. Save

---

## Updating the Snap

For future versions:

```bash
# 1. Update version in medha/__init__.py and snapcraft.yaml (via craftctl)
# 2. Commit and push to GitHub
# 3. Trigger remote build
snapcraft remote-build --build-on=amd64,arm64

# 4. Release to edge for testing
snapcraft release medha-ide <new-revision> edge

# 5. Promote through channels after testing
snapcraft release medha-ide <new-revision> beta
snapcraft release medha-ide <new-revision> candidate
snapcraft release medha-ide <new-revision> stable
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `snapcraft register` fails: name taken | Contact Snapcraft support if you own the trademark |
| Remote build fails on arm64 | Check PySide6 wheel availability; arm64 wheels exist for 6.12+ |
| Classic request denied | Ensure justification matches VS Code/PyCharm precedent; add more detail |
| Qt plugins not found in snap | Verify `QT_PLUGIN_PATH` in snapcraft.yaml includes `$SNAP/usr/lib/$ARCH/qt6/plugins` |
| Desktop file not showing | Ensure `desktop: gui/io.github.Kanak234.Medha.desktop` in apps section |
| Icon not showing | Verify icon installed to `usr/share/icons/hicolor/*/apps/io.github.Kanak234.Medha.png` |

---

## Contact

- **Owner:** Kanak Prabhakar
- **Email:** kanakprabhakar72@gmail.com
- **GitHub:** https://github.com/Kanak234
- **Snapcraft Forum:** https://forum.snapcraft.io/u/Kanak234

---

**Last updated:** 2026-10-21
**Snap version:** 1.1.0