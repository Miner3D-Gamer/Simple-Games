import os

def get_config_file(path: str, name: str) -> str:
    """Find configuration file with supported extensions in the given path.
    Returns empty string if no config file is found."""
    extensions = [
        "json",
        "json5",
        "yaml",
        "yml",
        "toml",
        "ini",
        "tf",
        "hcl",
        "xml",
        "conf",
        "properties",
        "hjson",
    ]

    for extension in extensions:
        file_path = os.path.join(path, f"{name}.{extension}")
        if os.path.exists(file_path):
            return file_path
    return ""


def load_config(path: str):
    ext = path.split(".")[-1]
    if ext == "json":
        import json

        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    elif ext == "json5":
        import json5

        with open(path, "r", encoding="utf-8") as f:
            return json5.load(f)
    elif ext == "hjson":
        import hjson

        with open(path, "r", encoding="utf-8") as f:
            return hjson.load(f)
    elif ext in ["yml", "yaml"]:
        import yaml

        with open(path, "r", encoding="utf-8") as f:
            return yaml.load(f, Loader=yaml.Loader)
    elif ext == "toml":
        import tomli

        with open(path, "r", encoding="utf-8") as f:
            return tomli.load(f)
    elif ext == "ini":
        import configparser

        config = configparser.ConfigParser()
        config.read(path, encoding="utf-8")
        return {section: dict(config.items(section)) for section in config.sections()}
    elif ext in ["tf", "hcl"]:
        import hcl2

        with open(path, "r", encoding="utf-8") as f:
            return hcl2.load(f)
    elif ext == "xml":
        import xml.etree.ElementTree as ET

        tree = ET.parse(path)
        root = tree.getroot()

        def xml_to_dict(element):
            result = {}
            for child in element:
                if len(child) > 0:
                    result[child.tag] = xml_to_dict(child)
                else:
                    result[child.tag] = child.text
            return result

        return xml_to_dict(root)
    elif ext in ["conf", "hocon"]:
        from pyhocon import ConfigFactory

        return ConfigFactory.parse_file(path)
    elif ext == "properties":
        with open(path, "r", encoding="utf-8") as f:
            props = {}
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    key, value = line.split("=", 1)
                    props[key.strip()] = value.strip()
            return props


def file_config_content(path: str, name: str):
    p = get_config_file(path, name)
    if p == "":
        return None
    try:
        return load_config(p)
    except:
        return None