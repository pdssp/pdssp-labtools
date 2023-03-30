"""Factory for creating a transformer object."""

from typing import Any, Callable
from pydantic import BaseModel
from labtools.transformers.transformer import AbstractTransformer

transformer_creation_funcs: dict = {}


def register(schema_name: str, transformer_creator_fn: Callable[..., AbstractTransformer]) -> None:
    """Register a new transformer.
    """
    transformer_creation_funcs[schema_name] = transformer_creator_fn


def unregister(schema_name: str) -> None:
    """Unregister a metadata schema."""
    transformer_creation_funcs.pop(schema_name, None)


def create_transformer(schema_name: str) -> AbstractTransformer:
    """Create a transformer object given an input schema name."""
    try:
        creator_func = transformer_creation_funcs[schema_name]
    except KeyError:
        raise ValueError(f'No transformer defined for {schema_name!r} schema.') from None
    return creator_func()