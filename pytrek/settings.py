import os

from pydantic import BaseModel, field_serializer
from pydantic_extra_types.color import Color
from yaml import safe_dump, safe_load


class _SettingsModel(BaseModel):
    klingon_color: Color = Color('green')

    @field_serializer('klingon_color', mode='plain')
    def hex_encode(self, value: Color) -> str:
        return value.as_hex()


def _load_settings():
    # Create the settings file if necessary.
    if not os.path.exists('settings.yaml'):
        with open('settings.yaml', 'w') as _:
            pass
    # Load settings from the file.
    with open('settings.yaml', 'r') as file:
        data = safe_load(file)
        if isinstance(data, dict):
            settings = _SettingsModel.model_validate(data)
        else:
            settings = _SettingsModel()
    # Write any default values to the file.
    with open('settings.yaml', 'w') as file:
        safe_dump(settings.model_dump(), file)
    # Return the loaded settings.
    return settings


settings = _load_settings()
print(settings)