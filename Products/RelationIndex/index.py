from App.special_dtml import DTMLFile
from BTrees.OOBTree import OOBTree
from BTrees.IOBTree import IOBTree
from BTrees.IIBTree import IISet
from BTrees.IIBTree import IITreeSet
from BTrees.OIBTree import OISet
from BTrees.IIBTree import multiunion
from BTrees.IIBTree import intersection
from BTrees.Length import Length
from OFS.SimpleItem import SimpleItem
from Products.PluginIndexes.interfaces import ILimitedResultIndex
from zope.interface import implements
from plone.uuid.interfaces import IUUID


class RelationIndex(SimpleItem):
    """Index of relationships between objects."""
    implements(ILimitedResultIndex)

    meta_type = 'RelationIndex'

    manage_options = (
        {'label': 'Settings', 'action': 'manage_main'},
        {'label': 'Browse', 'action': 'manage_browse'},
    )

    manage = manage_main = DTMLFile('dtml/manageRelationIndex', globals())
    manage_main._setName('manage_main')
    manage_browse = DTMLFile('dtml/browseIndex', globals())

    def __init__(self, id, *args, **kw):
        self.id = id
        self.clear()

    def clear(self):
        self._length = Length()
        self._index = OOBTree()
        self._unindex = IOBTree()

    def getId(self):
        return self.id

    def getEntryForObject(self, documentId, default=None):
        return dict(self._unindex.get(documentId, default))

    def getIndexSourceNames(self):
        return self._index.keys()

    def getIndexQueryNames(self):
        return self._index.keys()

    def index_object(self, documentId, obj, threshold=None):
        # XXX should move to adapter
        at_refs = getattr(obj, 'at_references', None)
        if at_refs is None:
            return False

        unindex = OOBTree()
        found_refs = False
        for ref in at_refs.objectValues():
            found_refs = True
            reftype = ref.relationship
            target = ref.targetUID

            reftype_index = self._index.setdefault(reftype, OOBTree())
            target_index = reftype_index.setdefault(target, IITreeSet())
            target_index.add(documentId)

            reftype_unindex = unindex.setdefault(reftype, OISet())
            reftype_unindex.add(target)

        self._unindex[documentId] = unindex
        if found_refs:
            self._length.change(1)
        return True

    def unindex_object(self, documentId):
        entries = self._unindex.get(documentId, {})
        for reftype, targets in entries.items():
            # remove index -> reftype -> source
            reftype_index = self._index.get(reftype)
            if reftype_index is None:
                continue

            for target in targets:
                entry = reftype_index.get(target)
                if entry is None:
                    continue
                entry.remove(documentId)
        self._length.change(-1)
        del self._unindex[documentId]

    def _apply_index(self, request, resultset=None):
        setlist = []
        indices_used = []
        for reltype in self.getIndexSourceNames():
            query = request.get(reltype)
            if query is None:
                continue

            if isinstance(query, str):
                target = query
            else:
                target = IUUID(query)

            indices_used.append(reltype)
            index = self._index[reltype]
            s = index.get(target)
            if s is None:
                continue
            else:
                setlist.append(s)

        if not indices_used:
            return

        if len(setlist) == 1:
            return setlist[0], tuple(indices_used)

        # If we already get a small result set passed in, intersecting
        # the various indexes with it and doing the union later is
        # faster than creating a multiunion first.
        if resultset is not None and len(resultset) < 200:
            smalllist = []
            for s in setlist:
                smalllist.append(intersection(resultset, s))
            r = multiunion(smalllist)
        else:
            r = multiunion(setlist)

        if r is None:
            r = IISet()
        return r, tuple(indices_used)

    def numObjects(self):
        return self._length()
    indexSize = numObjects

    def items(self):
        items = []
        for k, v in self._index.items():
            items.append((k, dict(v.items())))
        return items


manage_addRelationIndexForm = DTMLFile('dtml/addRelationIndex', globals())


def manage_addRelationIndex(self, id, extra=None,
                            REQUEST=None, RESPONSE=None, URL3=None):
    """Add a relation index"""
    return self.manage_addIndex(
        id, 'RelationIndex', extra=extra,
        REQUEST=REQUEST, RESPONSE=RESPONSE, URL1=URL3)
