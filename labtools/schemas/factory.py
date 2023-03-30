"""Factory for creating a metadata object."""

from typing import Any, Callable
from pydantic import BaseModel

metadata_creation_funcs: dict = {}


def register(schema_name: str, item_creator_fn: Callable[..., BaseModel], collection_creator_fn: Callable[..., BaseModel]) -> None:
    """Register a new metadata schema.

    eg: register('OMEGA_C_PROJ', ias.schemas.OMEGA_C_PROJ, ias.schemas.PSUP_Collection)
    """
    metadata_creation_funcs[schema_name] = {'item': item_creator_fn, 'collection': collection_creator_fn}


def unregister(schema_name: str) -> None:
    """Unregister a metadata schema."""
    metadata_creation_funcs.pop(schema_name, None)


def get_schema_names() -> list[str]:
    schema_names = []
    for name in metadata_creation_funcs.keys():
        name += ' ' + str(list(metadata_creation_funcs[name].keys()))
        schema_names.append(name)
    return schema_names


def get_schema_name(metadata: BaseModel):
    metadata_class_name = metadata.__class__.__name__
    for schema_name in metadata_creation_funcs.keys():
        for object_type in metadata_creation_funcs[schema_name].keys():
                if metadata_class_name == metadata_creation_funcs[schema_name][object_type].__name__:
                    return schema_name
    return None

def get_object_type(metadata: BaseModel):
    metadata_class_name = metadata.__class__.__name__
    for schema_name in metadata_creation_funcs.keys():
        for object_type in metadata_creation_funcs[schema_name].keys():
                if metadata_class_name == metadata_creation_funcs[schema_name][object_type].__name__:
                    return object_type
    return None

def create_metadata_object(metadata_dict: dict[str, Any], schema_name: str, object_type: str) -> BaseModel:
    """Create a metadata object of a specific schema, object type, given metadata JSON data."""
    # metadata_dict_copy = metadata_dict.copy()
    # character_type = metadata_dict_copy.pop("type")
    try:
        creator_func = metadata_creation_funcs[schema_name][object_type]
    except KeyError:
        raise ValueError(f'No schema defined for {schema_name!r} schema {object_type!r} object type.') from None
    return creator_func(**metadata_dict)