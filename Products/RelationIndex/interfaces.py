from zope.interface import Attribute
from zope.interface import Interface


class IRelation(Interface):
    """Represents a relation between content items."""

    source = Attribute('UID of the source item')
    relation_name = Attribute('String identifying the type of relationship')
    target = Attribute('UID of the target item')


class IRelationCollector(Interface):
    """Responsible for finding relations from a content item.
    """

    def __init__(context):
        """Adapts a context."""

    def __iter__():
        """Iterates over the IRelations found on the content item."""
