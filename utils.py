import importlib
from yaml import safe_load


class Config:

    def __init__(self, yaml_path):

        with open(yaml_path, "r") as stream:
            yaml_dict = safe_load(stream)

        self.initializing = True
        self.load(yaml_dict)
        self.initializing = False

    def load(self, yaml_dict):

        for target_module_name, params in yaml_dict.items():
            target_module_name = target_module_name.strip()

            if params is not dict:
                setattr(self, target_module_name, params)
                continue

            for param, value in params.items():
                param = param.strip()

                if not hasattr(self, target_module_name):
                    setattr(self, target_module_name, {})
                getattr(self, target_module_name)[param] = value

    def __getattr__(self, item):
        if self.initializing:
            return object.__getattribute__(self, item)
        return None


def load_module(path: str):
    module_name, class_name = path.rsplit('.', 1)
    module = importlib.import_module(module_name)
    return getattr(module, class_name)
