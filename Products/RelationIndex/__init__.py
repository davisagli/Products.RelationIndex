from .index import RelationIndex
from .index import manage_addRelationIndex
from .index import manage_addRelationIndexForm


def initialize(context):

    context.registerClass(
        RelationIndex,
        permission='Add Pluggable Index',
        constructors=(
            manage_addRelationIndexForm,
            manage_addRelationIndex),
        visibility=None,
        )
