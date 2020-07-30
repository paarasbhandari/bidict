from hypothesis import given, example
import pytest_mutagen as mg
from bidict import (
    BidictException,
    DROP_OLD, RAISE, OnDup, ON_DUP_RAISE,
    OrderedBidictBase, OrderedBidict, BidictBase, MutableBidict, bidict, namedbidict,
    inverted,
)
from . import _strategies as st

# mutants

@mg.mutant_of("BidictBase._isinv", "NO_MUTATION")

@mg.mutant_of("BidictBase.inverse", "INVERSE_IS_NONE")
def inverse():
    return None

@mg.mutant_of("BidictBase.inverse", "INVERSE_IS_SELF")
def inverse(self):
    return self

@mg.mutant_of("MutableBidict.pop", "POP_RETURNS_NONE")
def pop():
    return None

@mg.mutant_of("MutableBidict.put", "PUT_NOOP")
def put():
    return

@mg.mutant_of("OrderedBidictBase._already_have", "ALREADY_HAVE_FALSE")
def _already_have():
    return False

@mg.mutant_of("OrderedBidictBase._already_have", "ALREADY_HAVE_TRUE")
def _already_have():
    return True

@mg.mutant_of("BidictBase.copy", "COPY_RETURNS_SELF")
def copy(self):
    return self

@mg.mutant_of("MutableBidict.putall", "PUTALL_NOOP")
def putall():
    return

# test properties

@given(st.MUTABLE_BIDICTS, st.L_PAIRS, st.ON_DUP)
# These test cases ensure coverage of all branches in [Ordered]BidictBase._undo_write
# (Hypothesis doesn't always generate examples that cover all the branches otherwise).
@example(bidict({1: 1, 2: 2}), [(1, 3), (1, 2)], OnDup(key=DROP_OLD, val=RAISE))
@example(bidict({1: 1, 2: 2}), [(3, 1), (2, 4)], OnDup(key=RAISE, val=DROP_OLD))
@example(bidict({1: 1, 2: 2}), [(1, 2), (1, 1)], OnDup(key=RAISE, val=RAISE, kv=DROP_OLD))
@example(OrderedBidict({1: 1, 2: 2}), [(1, 3), (1, 2)], OnDup(key=DROP_OLD, val=RAISE))
@example(OrderedBidict({1: 1, 2: 2}), [(3, 1), (2, 4)], OnDup(key=RAISE, val=DROP_OLD))
@example(OrderedBidict({1: 1, 2: 2}), [(1, 2), (1, 1)], OnDup(key=RAISE, val=RAISE, kv=DROP_OLD))
def test_putall_same_as_put_for_each_item(bi, items, on_dup):
    """*bi.putall(items) <==> for i in items: bi.put(i)* for all values of OnDup."""
    check = bi.copy()
    expect = bi.copy()
    checkexc = None
    expectexc = None
    for (key, val) in items:
        try:
            expect.put(key, val, on_dup)
        except BidictException as exc:
            expectexc = type(exc)
            expect = bi  # Bulk updates fail clean -> roll back to original state.
            break
    try:
        check.putall(items, on_dup)
    except BidictException as exc:
        checkexc = type(exc)
    assert checkexc == expectexc
    assert check == expect
    assert check.inv == expect.inv
