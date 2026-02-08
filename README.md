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

   # Git Bash / MSYS
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

## References

- [RFC5322](https://datatracker.ietf.org/doc/html/rfc5322.html) - Defines how an email header should be

## License

[Apache 2.0](./LICENSE)
