import subprocess
from utils import project_root


def compile_sass():
    subprocess.run(
        [
            "sass",
            f"{project_root}/sass/index.sass",
            f"{project_root}/static/index.css",
        ]
    )
