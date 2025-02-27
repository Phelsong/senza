import os
import urllib.request
import tarfile

from utils import project_dir, package_dir


version = "0.27.3"
version_entry = f"pyodide-{version}.tar.bz2"

def sync_pyodide():
    print(
        f"Current Version is {version} ... Make sure to check for updated releases: https://github.com/pyodide/pyodide/releases/"
    )

    os.chdir(package_dir)
    try:
        os.rename("pyodide", "pyodide_old")
    except Exception:
        pass
    os.makedirs(f"pyodide/{version}/full/", exist_ok=True)
    os.chdir(os.path.join(package_dir, "pyodide", version, "full"))

    url = f"https://github.com/pyodide/pyodide/releases/download/{version}/{version_entry}"
    urllib.request.urlretrieve(url, version_entry)

    with tarfile.open(version_entry, "r:bz2") as tar:
        tar.extractall()

    os.remove(version_entry)

    os.chdir(project_dir)
