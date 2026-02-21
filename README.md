# py-mailbox-viewer

A simple offline mail file viewer written in python

## Requirements

- Python 3.12 (recommended)
- Git (to clone the repository)

See `requirements.txt` for the Python dependencies used by the project.

## Quick setup

1. Clone the repository:

   ```bash
   git clone https://github.com/AlstonChan/py-mailbox-viewer.git
   cd py-mailbox-viewer
   ```

2. Create a virtual environment (recommended):

   ```bash
   # Using the system Python launcher
   py -3.12 -m venv .venv

   # Or using the active `python` executable
   python -m venv .venv
   ```

3. Activate the virtual environment:

   ```bash
   # PowerShell (recommended)
   .\.venv\Scripts\Activate.ps1

   # Command Prompt (cmd.exe)
   .\.venv\Scripts\activate.bat

   # Git Bash / MSYS / Unix
   source .venv/bin/activate
   ```

4. Upgrade pip and install dependencies:

   ```bash
   py -m pip install --upgrade pip
   py -m pip install -r requirements.txt
   ```

If you used `python -m venv` instead of `py -3.12`, replace the `py -3.12 -m pip` calls with the `python` from the activated venv.

Run the application with `py ./src/app.py`

### Updating the resources file

After a new resources has been added to the [resources](./resources/) directory, you have to update the [resources.qrc](./resources.qrc) file to include the new entry of resource or remove the delete resource entry. Then re-compile the [resources_rc](./src/resources_rc.py) file with:

```bash
pyside6-rcc resources.qrc -o src/resources_rc.py
```

## Building with PyInstaller (app.spec)

This repository includes an app.spec that can be used with PyInstaller to create a standalone application bundle on Windows and Linux.

General steps (Windows / Linux):

1. Create and activate a virtual environment and install dependencies:

   ```bash
   # Windows (PowerShell / cmd) or Linux/macOS (use the appropriate python launcher)
   python -m venv .venv
   # activate the venv (platform-specific)
   # PowerShell: .\.venv\Scripts\Activate.ps1
   # cmd.exe: .\.venv\Scripts\activate.bat
   # Linux/macOS: source .venv/bin/activate

   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt
   ```

2. (If resources changed) Compile Qt resources into Python:

   ```bash
   pyside6-rcc resources.qrc -o src/resources_rc.py
   ```

3. Build with `pyinstaller` using the included spec file:

   ```bash
   pyinstaller app.spec
   ```

`pyinstaller` will create the standard build artifacts and distributions (`build/`, `dist/`) in the repository root. The bundled application will be placed under `dist/py-mailbox-viewer`.

### Packaging as an AppImage (Linux)

If you want to produce a Linux AppImage for redistribution, the typical workflow is:

1. Build the application bundle with PyInstaller on a Linux host (use the same spec used earlier):

   ```bash
   pyinstaller app.spec
   ```

2. Install the `appimagetool` binary

   ```bash
   wget https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-x86_64.AppImage

   # Make it executable
   chmod +x appimagetool-x86_64.AppImage

   # move it into /usr/local/bin
   sudo mv appimagetool-x86_64.AppImage /usr/local/bin/appimagetool
   ```

3. Prepare the directory for packaging

   ```bash
   mkdir -p "packaging/AppImage/usr/bin"

   # Copy the PyInstaller dist output into usr/bin
   cp -r dist/py-mailbox-viewer/* "packaging/AppImage/usr/bin/"
   ```

4. Run the packaging

   ```bash
   appimagetool "packaging/AppImage"
   ```

This will produce a app image file - `Py_Mailbox_Viewer-x86_64.AppImage`

## References

- [RFC5322](https://datatracker.ietf.org/doc/html/rfc5322.html) - Defines how an email header should be

## License

[Apache 2.0](./LICENSE)
