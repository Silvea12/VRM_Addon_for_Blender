from typing import Callable, Optional

import bpy

addon_package_name_temp = ".".join(__name__.split(".")[:-3])
if not addon_package_name_temp:
    addon_package_name_temp = "VRM_Addon_for_Blender_fallback_key"
    print(f"VRM Add-on: Failed to detect add-on package name from __name__={__name__}")

if "addon_package_name" not in globals():
    addon_package_name = addon_package_name_temp
elif globals()["addon_package_name"] != addon_package_name_temp:
    print(
        "VRM Add-on: Accidentally package name is changed? addon_package_name: "
        + str(globals()["addon_package_name"])
        + f" => {addon_package_name_temp}, __name__: "
        + str(globals().get("previous_package_name"))
        + f" => {__name__}"
    )

previous_package_name = __name__


class VrmAddonPreferences(bpy.types.AddonPreferences):  # type: ignore[misc]
    bl_idname = addon_package_name

    set_use_experimental_vrm_component_ui_callback: Optional[
        Callable[[bool], None]
    ] = None

    @classmethod
    def register_set_use_experimental_vrm_component_ui_callback(
        cls, callback: Callable[[bool], None]
    ) -> None:
        if cls.set_use_experimental_vrm_component_ui_callback is not None:
            print(
                "WARNING: VrmAddonPreferences.set_use_experimental_vrm_component_ui_callback is already registered"
            )
        cls.set_use_experimental_vrm_component_ui_callback = callback

    def get_use_experimental_vrm_component_ui(self) -> bool:
        return bool(self.get("use_experimental_vrm_component_ui", False))

    def set_use_experimental_vrm_component_ui(self, value: bool) -> None:
        key = "use_experimental_vrm_component_ui"
        if self.get(key) == value:
            return
        self[key] = value
        callback = self.set_use_experimental_vrm_component_ui_callback
        if callable(callback):
            # pylint: disable=not-callable;
            callback(value)
        else:
            print(
                "WARNING: VrmAddonPreferences.set_use_experimental_vrm_component_ui_callback is not a callable"
            )

    export_invisibles: bpy.props.BoolProperty(  # type: ignore[valid-type]
        name="Export invisible objects",  # noqa: F722
        default=False,
    )
    export_only_selections: bpy.props.BoolProperty(  # type: ignore[valid-type]
        name="Export only selections",  # noqa: F722
        default=False,
    )
    use_experimental_vrm_component_ui: bpy.props.BoolProperty(  # type: ignore[valid-type]
        name="Try experimental VRM component UI",  # noqa: F722
        default=False,
        get=get_use_experimental_vrm_component_ui,
        set=set_use_experimental_vrm_component_ui,
    )

    def draw(self, _context: bpy.types.Context) -> None:
        layout = self.layout
        layout.prop(self, "export_invisibles")
        layout.prop(self, "export_only_selections")

        testing_box = layout.box()
        testing_box.label(text="Testing", icon="EXPERIMENTAL")
        testing_box.prop(self, "use_experimental_vrm_component_ui")


def use_legacy_importer_exporter() -> bool:
    return bool(bpy.app.version < (2, 83))


def get_preferences(context: bpy.types.Context) -> Optional[bpy.types.AddonPreferences]:
    addon = context.preferences.addons.get(addon_package_name)
    if addon:
        return addon.preferences
    print(f"WARNING: Failed to read add-on preferences for {addon_package_name}")
    return None


def use_experimental_vrm_component_ui(context: bpy.types.Context) -> bool:
    preferences = get_preferences(context)
    if not preferences:
        return False
    return bool(preferences.use_experimental_vrm_component_ui)
