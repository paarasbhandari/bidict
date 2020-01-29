# -*- coding: utf-8 -*-
# Copyright 2009-2020 Joshua Bronson. All Rights Reserved.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""Provides :func:`bidict.namedbidict`."""

from typing import cast

from ._abc import BidirectionalMapping, KT, VT
from ._bidict import bidict


# TODO: Provide a statically-typed NamedBidict à la typing.NamedTuple.

def namedbidict(
    typename: str,
    keyname: str,
    valname: str,
    base_type: BidirectionalMapping[KT, VT] = bidict,  # type: ignore
) -> BidirectionalMapping[KT, VT]:
    r"""Create a new subclass of *base_type* with custom accessors.

    Analagous to :func:`collections.namedtuple`.

    The new class's ``__name__`` and ``__qualname__``
    will be set based on *typename*.

    Instances of it will provide access to their
    :attr:`inverse <BidirectionalMapping.inverse>`\s
    via the custom *keyname*\_for property,
    and access to themselves
    via the custom *valname*\_for property.

    *See also* the :ref:`namedbidict usage documentation
    <other-bidict-types:\:func\:\`~bidict.namedbidict\`>`

    :raises ValueError: if any of the *typename*, *keyname*, or *valname*
        strings is not a valid Python identifier, or if *keyname == valname*.

    :raises TypeError: if *base_type* is not a subclass of
        :class:`BidirectionalMapping`.
        (This function requires slightly more of *base_type*,
        e.g. the availability of an ``_isinv`` attribute,
        but all the :ref:`concrete bidict types
        <other-bidict-types:Bidict Types Diagram>`
        that the :mod:`bidict` module provides can be passed in.
        Check out the code if you actually need to pass in something else.)
    """
    # Re the `base_type` docs above:
    # The additional requirements (providing _isinv and __getstate__) do not belong in the
    # BidirectionalMapping interface, and it's overkill to create additional interface(s) for this.
    # On the other hand, it's overkill to require that base_type be a subclass of BidictBase, since
    # that's too specific. The BidirectionalMapping check along with the docs above should suffice.
    if not issubclass(base_type, BidirectionalMapping):  # type: ignore
        raise TypeError(base_type)
    names = (typename, keyname, valname)
    if not all(map(str.isidentifier, names)) or keyname == valname:
        raise ValueError(names)

    class _Named(base_type):  # type: ignore

        __slots__ = ()

        def _getfwd(self) -> BidirectionalMapping:
            return self.inverse if self._isinv else self

        def _getinv(self) -> BidirectionalMapping:
            return self if self._isinv else self.inverse

        @property
        def _keyname(self) -> str:
            return valname if self._isinv else keyname

        @property
        def _valname(self) -> str:
            return keyname if self._isinv else valname

        def __reduce__(self):
            return (_make_empty, (typename, keyname, valname, base_type), self.__getstate__())

    bname = base_type.__name__  # type: ignore
    fname = valname + '_for'
    iname = keyname + '_for'
    namedict = dict(typename=typename, bname=bname, keyname=keyname, valname=valname)
    fdoc = '{typename} forward {bname}: {keyname} → {valname}'.format(**namedict)
    idoc = '{typename} inverse {bname}: {valname} → {keyname}'.format(**namedict)
    setattr(_Named, fname, property(_Named._getfwd, doc=fdoc))
    setattr(_Named, iname, property(_Named._getinv, doc=idoc))

    _Named.__qualname__ = _Named.__qualname__[:-len(_Named.__name__)] + typename
    _Named.__name__ = typename
    return cast(BidirectionalMapping[KT, VT], _Named)


def _make_empty(
    typename: str,
    keyname: str,
    valname: str,
    base_type: BidirectionalMapping[KT, VT],
) -> BidirectionalMapping[KT, VT]:
    """Create a named bidict with the indicated arguments and return an empty instance.
    Used to make :func:`bidict.namedbidict` instances picklable.
    """
    cls = namedbidict(typename, keyname, valname, base_type=base_type)
    return cls()  # type: ignore
