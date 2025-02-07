import sys
from importlib import import_module, util
from types import ModuleType
from importlib.abc import MetaPathFinder, Loader
from importlib.machinery import ModuleSpec


from wrapper.shared import get_only_item_in_dict


class ModuleLoader(Loader):
    def __init__(self, original_spec, replace: dict[str, list[str | dict[str, str]]]):
        self.original_spec = original_spec
        self.replace = replace

    def create_module(self, spec):
        return None  # Use default module creation

    def exec_module(self, module):
        # Execute the original module
        if self.original_spec.loader:
            self.original_spec.loader.exec_module(module)

        # Apply our patches after module is loaded
        module_name = module.__name__

        # Check both the full module name and potential parent module
        if module_name in self.replace:
            replace_list = self.replace[module_name]
        else:
            return

        def create_unallowed_call(error_message: str):
            def unallowed_call(*args, **kwargs):
                raise PermissionError(error_message)

            # Burn the error message directly into the function
            unallowed_call.__closure__[0].cell_contents = error_message  # type: ignore
            return unallowed_call

        for attr_name in replace_list:
            if isinstance(attr_name, str):
                error = "This function has been disabled for security purposes"
            elif isinstance(attr_name, dict):
                attr_name, error = get_only_item_in_dict(attr_name)

            if "." in attr_name:
                obj_path, final_attr = attr_name.rsplit(".", 1)
                obj = module
                for part in obj_path.split("."):
                    obj = getattr(obj, part)
                setattr(obj, final_attr, create_unallowed_call(error))
            else:
                setattr(module, attr_name, create_unallowed_call(error))


class ModulePatch(MetaPathFinder):
    def __init__(self, replace):
        self._importing = set()
        self.replace = replace

    def find_spec(self, fullname, path, target=None):
        if fullname in self._importing:
            # print(f">Skipped {fullname}")
            return None

        # print(f"Finding spec for: {fullname}")

        # Check both the full module name and the parent module
        should_handle = fullname in self.replace

        if should_handle:
            try:
                self._importing.add(fullname)
                original_spec = util.find_spec(fullname)
                if original_spec is None:
                    return None

                spec = ModuleSpec(
                    name=fullname,
                    loader=ModuleLoader(original_spec, self.replace),
                    origin=original_spec.origin,
                    loader_state=original_spec.loader_state,
                    is_package=(original_spec.submodule_search_locations is not None),
                )

                spec.has_location = original_spec.has_location
                if hasattr(original_spec, "cached"):
                    spec.cached = original_spec.cached

                return spec
            finally:
                self._importing.remove(fullname)

        return None


def block_modules(module: dict[str, list[str]]):
    sys.meta_path.insert(0, ModulePatch(module))


# {"PIL.Image": ["open", "save", "show"]}
