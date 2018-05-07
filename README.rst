This package provides a base class `enumr` for ranged enumerations
with reach annotation and formatting capabilities.

If you are new to this package, study also the `subrange` package as it
is used here as the class for ranged item instances. Reach annotation
and formatting capabilities are strongly based on the `subrange` class.

Define your custom ranged enum as a subclass of `enumr`. Provide item
descriptors as described below. Then use class items freely as separate
instances of `subrangef` class. Here is a basic example of ranged enum
(this one does not use reach annotation and formatting)::

    from enumr import enumr

    class Devices(enumr):
        PRIMARY = 1                     # value 1
        SECONDARY = 2
        USER_DEFINED = (3, 10)          # subrange 3..10
        RESERVED = (11, 14)
        INVALID = 15

    print Devices.USER_DEFINED          # 3..10
    print Devices.USER_DEFINED.min      # 3
    print Devices.USER_DEFINED.max      # 10
    print 7 in Devices.USER_DEFINED     # True
    print 11 > Devices.USER_DEFINED     # True
    print 2 in Devices.SECONDARY        # True
    print 2 == Devices.SECONDARY        # True
    print "0x{:02X}".format(Devices.RESERVED)             # 0x0B..0E
    print "{0.value} {0.name!r}".format(Devices.INVALID)  # 15 'INVALID'

See documentation to `subrange` package on which operations are
supported by ranged items (that are instances of `subrangef` class).

To use reach annotation and formatting capabilities add ``_ant_spec``
and ``_str_spec`` to your subclass definition. This will change the
default formatting of items::

    class Devices(enumr):
        _ant_spec = 'brief', 'ref'
        _str_spec = "{value} {brief!r}"
        PRIMARY = 1, "Primary device", "sub.10.2.1"
        USER_DEFINED = (3, 10), "User defined device", "sub.10.2.3"

    print Devices.PRIMARY           # 1 'Primary device'
    print Devices.USER_DEFINED      # 3..10 'User defined device'

    print Devices.PRIMARY.brief     # Primary device
    print Devices.PRIMARY.ref       # sub.10.2.1

    print "{0.value}: {0.brief!r}".format(Devices.USER_DEFINED)
    # 3..10: 'User defined device'

Here are some more examples. Call to ``print Devices.USER_DEFINED`` will
produce different output depending on ``_str_spec``::

    _str_spec = "0x{value:02X}"             # 0x03..0A
    _str_spec = "0x{min:02X}-{max:02X}"     # 0x03-0A
    _str_spec = "{name} = {value}"          # USER_DEFINED = 3..10
    _str_spec = "{brief!r}"                 # 'User defined device'

See documentation to `enumr` class for more details on how to use reach
annotation and formatting capabilities.

Enumeration class also provides a facility to resolve arbitrary integer
values to enumeration items::

    print Devices(1)            # 1 'Primary device'
    print Devices(7)            # 3..10 'User defined device'
    print Devices(20, None)     # None
    print Devices(20)       # raises ValueError: 20 is not in Devices

Integer values are resolved in O(lb(m)) in the worst case, where m is
the number of ranged items (i.e., items containing more than one
value), lb(n) is the binary logarithm. If all items in the enum are
single-value ranges, the given integer is resolved in O(1).

There are different implementations of enum data type in Python. Some of
them provide one-to-one relation between items and their values (and
values must be integers), some allow multiple items to have the same
value. Yet they support only one value per an item, but not a range (or
set) of values.

However, in some cases it might be very useful to consolidate a whole
subrange of integer values under the same identifier, define a number of
such subranges if needed, and be able to resolve the correct subrange (a
ranged enum item) given an integer value. Such things may be met if we
talk about classifiers, decoding tasks, etc. Covering a wide range of
integer codes they may have very limited sets of fully defined items and
a number of huge continuous ranges of values under names like
'user_defined' or 'reserved'. Obviously, if it's not a tiny set of 8-bit
codes, it would not be a good idea to put all the 'reserved' codes into
a dictionary to be able to resolve arbitrary code. On the other hand
constructing long if-else matchers is error-prone and not elegant (and
also they consume O(n) to find the match, where n is the number of
items). So, a ready-to-use data structure able to keep ranged enums and
resolve codes to items might help. And now you have it.
