"""A simple metadata schema loader."""
import importlib


class ModuleInterface:
    """Represents a schema module interface. A schema module has a single register function."""

    @staticmethod
    def register() -> None:
        """Register the necessary items in the game character factory."""

    @staticmethod
    def get_transformer_module() -> str:
        """Returns transformer module associated to schema."""
        return ''


def import_module(name: str) -> ModuleInterface:
    """Imports a module given a name."""
    return importlib.import_module(name)  # type: ignore


def load_schemas(schemas: list[str]) -> None:
    """Loads the schemas defined in the schemas list, as well as associated transformer module associated to each schema."""
    for schema_module in schemas:
        schema = import_module(schema_module)
        schema.register()
        transformer_module = schema.get_transformer_module()
        try:
            transformer = import_module(transformer_module)
            try:
                transformer.register()
            except Exception as e:
                print(e)
                print(f'Transformer module could not be registered: schema={schema_module!r}, transformer={transformer_module!r}.')
                print()
        except Exception as e:
            print(e)
            print(f'Transformer module could not be loaded: schema={schema_module!r}, transformer={transformer_module!r}.')
            print()
