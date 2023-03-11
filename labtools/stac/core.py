from abc import ABC, abstractmethod

def create_stac_object(metadata, schema, object_type):
    pass


def create_stac_item(metadata, schema):
    return create_stac_object(metadata, schema, 'item')


def create_stac_collection(metadata, schema):
    return create_stac_object(metadata, schema, 'collection')


def create_stac_catalog(metadata, schema):
    return create_stac_object(metadata, schema, 'catalog')


class STAC_Object_Factory(ABC):
    """Abstract STAC object factory"""

    @abstractmethod
    def get_object(self):
        pass

class STAC_Item_Factory(STAC_Object_Factory):
    pass

class STAC_Collection_Factory(STAC_Object_Factory):
    pass

class STAC_Catalogy_Factory(STAC_Object_Factory):
    pass