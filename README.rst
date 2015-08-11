Introduction
============

In Plone it's often necessary to track *relations* between
content items; that is, a connection between two items that are
in arbitrary locations in the content hierarchy.

Achieving this within a non-relational object database relies on
the use of a *relation catalog*; that is, a place to keep track
of which content item relates to which other. Solutions in Plone
have traditionally relied on a relation catalog that is separate
from the main portal_catalog. This is the case with Archetypes'
reference_catalog and with the zc.relation catalog used by
plone.app.relationfield for Dexterity content.

That approach is non-ideal for several reasons:

* The separate catalog must track metadata for the indexed
  items, such as title and provided interfaces. This ends up
  duplicating data that's already in portal_catalog.
* If a developer needs to query for items that are related
  in a particular way *and also* meet some other criteria,
  two queries must be done and the resultsets manually merged.

``Products.RelationIndex`` attempts to solve these problems
by implementing a relation catalog *as an index within portal_catalog*.

The goals are:

* If you store references on a content item (Archetypes or Dexterity),
  they will get indexed without need for any additional configuration.
* Relations can be queried as part of a normal catalog query.
  For example, in an application where Persons can be related to
  Committees as members, this query finds all Persons who are
  members of a particular committee::

   catalog.searchResults({
   	   'portal_type': 'Person',
   	   'relations': ('is_member_of', review_committee),
   })

   And this one finds all committees of which a given Person is
   a member::

   catalog.searchResults({
       'portal_type': 'Committee',
       'relations': ('contains_person', david_glick),
   })

   (This assumes relations have different names for forward and
   backward lookups. If that's not practical, we could do:
   'relation_target': ('membership', review_committee)
   ...but that doesn't read nearly as nicely.)
   Or maybe return both forward and backward if it's a
   non-directional relation.

   ** or maybe (if possible) **

   catalog.searchResults({
   	   'portal_type': 'Person',
   	   'is_member_of': committee,
   })


To think about
--------------

- Indexing attributes of relation objects
- Ordered relations
