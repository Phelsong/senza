import os
import tomllib
from tomli_w import dump
from pathlib import Path


def load_config(path: str) -> dict:
    """loads the config from disk"""
    with open(path, "rb") as f:
        return tomllib.load(f)


def write_config(path: str, config: dict) -> None:
    """writes the config back to disk"""
    with open(path, "wb") as f:
        dump(config, f)


def push_revision_task(config: dict) -> dict:
    """updates the revision number"""
    ov = config["version"]
    current_version = config["version"].split(".")
    pushed_version = int(current_version[2]) + 1
    config["version"] = f"{current_version[0]}.{current_version[1]}.{pushed_version}"
    print(f"pushing version {ov} --> {config['version']}")
    return config


def push_revision() -> None:
    """takes command line args for the env"""
    from utils import project_root
    import sys

    p_env = sys.argv[1] if len(sys.argv) > 1 else "dev"
    config_dir = Path(f"{project_root}/config/web_config")

    match p_env:
        case "qa":
            config_path = Path(f"{config_dir}/{p_env}.toml")
            config = load_config(config_path)
            config = push_revision_task(config)
            write_config(config_path, config)
        case "prod":
            config_path = Path(f"{config_dir}/{p_env}.toml")
            config = load_config(config_path)
            config = push_revision_task(config)
            write_config(config_path, config)
        case "dev":
            config_path = Path(f"{config_dir}/dev.toml")
            config = load_config(config_path)
            config = push_revision_task(config)
            write_config(config_path, config)
        case "all":
            for config_file in os.listdir(config_dir):
                config_path = Path(f"{config_dir}/{config_file}")
                config = load_config(config_path)
                config = push_revision_task(config)
                write_config(config_path, config)
        case _:
            print(f"{p_env} is an invalid arg")


def push_minor_version_task():
    pass


def push_minor_version() -> None:
    """takes command line args for the env"""
    from utils import project_root
    import sys

    p_env = sys.argv[1]
    config_dir = Path(f"{project_root}/config/web_config")

    match p_env:
        case "qa":
            config_path = Path(f"{config_dir}/{p_env}.toml")
            config = load_config(config_path)
            config = push_minor_version_task(config)
            write_config(config_path, config)
        case "prod":
            config_path = Path(f"{config_dir}/{p_env}.toml")
            config = load_config(config_path)
            config = push_minor_version_task(config)
            write_config(config_path, config)
        case "dev":
            config_path = Path(f"{config_dir}/dev.toml")
            config = load_config(config_path)
            config = push_minor_version_task(config)
            write_config(config_path, config)
        case "all":
            for config_file in os.listdir(config_dir):
                config_path = Path(f"{config_dir}/{config_file}")
                config = load_config(config_path)
                config = push_minor_version_task(config)
                write_config(config_path, config)
        case _:
            print(f"{p_env} is an invalid arg")


def push_major_version_task():
    pass


def push_major_version() -> None:
    """takes command line args for the env"""
    from utils import project_root
    import sys

    p_env = sys.argv[1]
    config_dir = Path(f"{project_root}/config/web_config")

    match p_env:
        case "qa":
            config_path = Path(f"{config_dir}/{p_env}.toml")
            config = load_config(config_path)
            config = push_major_version_task(config)
            write_config(config_path, config)
        case "prod":
            config_path = Path(f"{config_dir}/{p_env}.toml")
            config = load_config(config_path)
            config = push_major_version_task(config)
            write_config(config_path, config)
        case "dev":
            config_path = Path(f"{config_dir}/dev.toml")
            config = load_config(config_path)
            config = push_major_version_task(config)
            write_config(config_path, config)
        case "all":
            for config_file in os.listdir(config_dir):
                config_path = Path(f"{config_dir}/{config_file}")
                config = load_config(config_path)
                config = push_major_version_task(config)
                write_config(config_path, config)
        case _:
            print(f"{p_env} is an invalid arg")
