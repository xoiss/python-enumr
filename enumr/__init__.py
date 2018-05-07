"""This package provides a base class `enumr` for ranged enumerations
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
"""


from subrange import subrangef


class _MetaEnumr(type):
    """Metaclass for subclasses of `enumr`.

    When a custom ranged enum class is defined, user populates it with
    item descriptors. This metaclass accepts the set of descriptors and
    creates actual ranged items after them. Then original descriptors
    are substituted one-by-one with created items preserving item names.

    For example, given a custom ranged enum class description::

        class Devices(enumr):
            PRIMARY = 1
            SECONDARY = 2
            USER_DEFINED = (3, 10)
            RESERVED = (11, 14)
            INVALID = 15

    this metaclass produces the following class (some details are not
    shown here for simplicity of illustration)::

        class Devices(enumr):
            PRIMARY = subrangef(1, 1)
            SECONDARY = subrangef(2, 2)
            USER_DEFINED = subrangef(3, 10)
            RESERVED = subrangef(11, 14)
            INVALID = subrangef(15, 15)

    If user also defined an annotation attributes list and/or a format
    string, such specifications are used to create annotated ranged
    items with reach default formatting.

    For example, given a class description::

        class Devices(enumr):
            _ant_spec = 'brief', 'ref'
            _str_spec = "{value} {brief!r}"
            PRIMARY = 1, "Primary device", "sub.10.2.1"
            USER_DEFINED = (3, 10), "User defined device", "sub.10.2.3"

    this metaclass produces the following class (some details are not
    shown here for simplicity of illustration)::

        class Devices(enumr):
            PRIMARY = subrangef(1, 1,
                    brief="Primary device",
                    ref="sub.10.2.1",
                    str_spec="{value} {brief!r}")
            USER_DEFINED = subrangef(3, 10,
                    brief="User defined device",
                    ref="sub.10.2.3"
                    str_spec="{value} {brief!r}")

    During its work, metaclass checks the given set of items if they all
    have valid descriptors and define nonoverlapping subranges. Finally,
    some private implementation specific data structures are attached to
    the new class that are used further for resolving integers to items.

    See documentation to `enumr` for more details on how to define a
    custom `enumr` subclass prototype, how to define items, annotation
    attributes list ``ant_spec`` and a format string ``str_spec``.

    See documentation to `subrangef` for more details on how to use
    ranged items that are instances of `subrangef` and how to describe a
    format string ``str_spec``. Note also that this metaclass adds
    ``name`` custom attribute to each ranged item. This attribute may be
    referenced in ``str_spec``.
    """

    def __new__(cls, name, bases, dict_):
        """Create a new subclass of `enumr`.

        :arg str name: subclass name
        :arg tuple bases: base classes
        :arg dict dict_: items of the subclass prototype as they are
            defined by user
        :returns: newly created subclass of `enumr`

        Note that bases should contain only the `enumr` class. However,
        this is not checked and other bases are not prohibited formally.
        """

        ant_spec = dict_.get('_ant_spec', ())
        if not (isinstance(ant_spec, tuple) or isinstance(ant_spec, list)):
            ant_spec = (ant_spec,)

        str_spec = dict_.get('_str_spec', "")

        def items_factory(name, descr):
            """Create a `subrangef` instance given name and descriptor.

            :arg str name: name of the constructed enum item
            :arg descr: descriptor providing an initializer for the item
                and values of all the annotation attributes
            :returns: newly created and fully initialized instance of
                `subrangef`, an item of constructed ranged enum

            This function uses ``ant_spec`` and ``str_spec`` local
            variables of the nested parent function. They specify an
            annotation attributes list and a format string.
            """

            if ant_spec:
                if not (isinstance(descr, tuple) or isinstance(descr, list)):
                    type_error = TypeError(
                        "item %r descriptor is %s, must be tuple or list"
                        % (name, type(descr).__name__))
                    raise type_error
                if len(descr) != 1 + len(ant_spec):
                    value_error = ValueError(
                        "item %r descriptor contains %d fields, %d required"
                        % (name, len(descr), 1 + len(ant_spec)))
                    raise value_error

                args = descr[0]
                kwargs = dict(zip(ant_spec, descr[1:]))

            else:
                args = descr
                kwargs = {}

            if not (isinstance(args, tuple) or isinstance(args, list)):
                args = (args,)

            if str_spec:
                kwargs['str_spec'] = str_spec

            kwargs['name'] = name

            return subrangef(*args, **kwargs)

        items = sorted(list(items_factory(name, descr)
                            for name, descr in dict_.items()
                            if not name.startswith("_")),
                       key=lambda item: item.min)

        for item, prev in zip(items[1:], items[:-1]):
            if not item > prev:
                value_error = ValueError(
                    "overlapping ranges {0.value} and {1.value} "
                    "in items {0.name!r} and {1.name!r}".format(prev, item))
                raise value_error

        dict_.update({item.name: item for item in items})

        dict_['_lookup_dict'] = {item.min: item for item in items}
        dict_['_ranges_list'] = [item for item in items if len(item) > 1]

        return type.__new__(cls, name, bases, dict_)


class enumr(object):
    """Base class for ranged enumerations.

    Define your custom ranged enum as a subclass of this class. Provide
    item descriptors as described below. Then use class items freely as
    separate instances of `subrangef` class.

    Example::

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

        print "0x{:02X}".format(Devices.RESERVED)     # 0x0B..0E

        print "{0.value} {0.name!r}".format(Devices.INVALID)
        # 15 'INVALID'

    In the example above, a ranged enum with five items is defined.
    Formally all five items are subranges of integers (three of them are
    single-value subranges) and provide the full set of methods as
    instances of `subrangef` class. See documentation to `subrangef` for
    description of supported methods and examples of use.

    The root idea is that items definitions do not reference `subrangef`
    class directly. You have to give only descriptors, and the actual
    subclass with `subrangef` instances is constructed by the metaclass
    of the `enumr` class. In the given examples, descriptors contain
    range initializers for items. Single-value items may be initialized
    with integer values, and ranged items require a couple of integers.

    The class actually created for this example is the following. See
    documentation to `_MetaEnumr` metaclass for more details::

        class Devices(enumr):
            PRIMARY = subrangef(1, 1)
            SECONDARY = subrangef(2, 2)
            USER_DEFINED = subrangef(3, 10)
            RESERVED = subrangef(11, 14)
            INVALID = subrangef(15, 15)

    .. note::

        Do not start item identifiers with ``'_'`` (underscore). Such
        identifiers are considered private and not converted to enum
        items (`subrangef` instances).

        You may use lower or mixed case identifiers, but we recommend
        using upper case to emphasize the immutability of enum items.

    The ranged enum also provide reach annotation and formatting
    capabilities. Both of them relate to enum items. You may define a
    default formatting for enum's items, choose a different base, add
    description, etc. See documentation to `subrangef` class for more
    details and consider the following example::

        class Devices(enumr):
            _ant_spec = 'brief', 'ref'
            _str_spec = "{value} {brief!r}"
            PRIMARY = 1, "Primary device", "sub.10.2.1"
            USER_DEFINED = (3, 10), "User defined device", "sub.10.2.3"

        print Devices.PRIMARY           # 1 'Primary device'
        print Devices.USER_DEFINED      # 3..10 'User defined device'

    In the example above, ``_ant_spec`` specifies the annotation
    attributes list and ``_str_spec`` defines the format string. Both
    are optional fields. Note that these identifiers are reserved by
    `enumr` and recognized by it as defined here.

    The ``_ant_spec``, if given, must be a single string, or a tuple or
    list of strings. Each string element must be a valid identifier. The
    leading symbol of such identifier should be a latter. There are some
    reserved identifiers: ``min``, ``max``, ``value``, ``name``. Do not
    use them in ``_ant_spec`` as soon as they are already defined for
    you: ``min`` and ``max`` correspond to subrange limits, ``value``
    represent the whole subrange (as an instance of `subrange` class),
    and ``name`` equals to the item identifier as a string.

    If ``_ant_spec`` is given then each item descriptor must be a tuple
    or a list of exactly (1 + N) elements, where N is the number of
    custom annotation attributes declared in the ``_ant_spec``. The
    first element in descriptor is the subrange initializer. It must be
    either a single integer or a couple of integers. The following N
    elements are values of custom annotation attributes of the described
    item. See also `subrangef` for more details on how to initialize it.

    In the given example, each item will get custom attributes ``brief``
    and ``ref``::

        print Devices.PRIMARY.brief     # Primary device
        print Devices.PRIMARY.ref       # sub.10.2.1

    The ``_str_spec``, if given, must be a string conforming to Format
    String Syntax. Format strings may contain Replacement Fields (parts
    surrounded by curly braces) and Literal Text (symbols outside all
    pairs of curly braces). All the Replacement Fields must contain the
    Field Name that is either a built-in or a custom attribute. The
    built-in attributes are ``min``, ``max``, ``value``, ``name``. The
    custom attributes are those declared in ``_ant_spec``. Replacement
    Field may contain Conversion Specification (``!r`` or ``!s``),
    Format Specification (this is mostly for ``min``, ``max`` and
    ``value`` attributes) and further levels of Field Name for complex
    attributes if needed.

    Here are some more examples. Call to ``print Devices.USER_DEFINED``
    will produce different output depending on ``_str_spec``::

        _str_spec = "0x{value:02X}"             # 0x03..0A
        _str_spec = "0x{min:02X}-{max:02X}"     # 0x03-0A
        _str_spec = "{name} = {value}"          # USER_DEFINED = 3..10
        _str_spec = "{brief!r}"                 # 'User defined device'

    Surely you may use ad hoc formatting::

        print "{0.value}: {0.brief!r}".format(Devices.USER_DEFINED)
        # 3..10: 'User defined device'

    A custom ranged enum class may be used to find which ranged item
    contains a given integer value. To resolve an integer value to item
    call the class with such value as argument (i.e., like making an
    instance of the class). The ranged enum class will return reference
    to one of its items or raise `ValueError` if the given value is
    included in neither item. If desired, a different exception may be
    raised or default value (for example, `None`) may be returned in
    such case. See `__new__` method for more details::

        print Devices(1)            # 1 'Primary device'
        print Devices(7)            # 3..10 'User defined device'
        print Devices(20, None)     # None
        print Devices(20)  # raises ValueError: 20 is not in Devices

    Integer values are resolved in O(lb(m)) in the worst case, where m
    is the number of ranged items (i.e., items containing more than one
    value), lb(n) is the binary logarithm. If all items in the enum are
    single-value ranges, the given integer is resolved in O(1).
    """

    __metaclass__ = _MetaEnumr

    def __new__(cls, value, default=ValueError):
        """Resolve integer value to ranged enum item.

        :arg int value: value to resolve
        :arg default: instance to return if failed to resolve ``value``;
            if default is a subclass of BaseException then exception
            instance of such subclass is raised
        :returns: reference to one of this enum items that is equal or
            contains the given value (instance of `subrangef` class)

        Foe example, given a class::

            class Devices(enumr):
                _str_spec = "{value} {name!r}"
                PRIMARY = 1
                SECONDARY = 2
                USER_DEFINED = (3, 10)
                RESERVED = (11, 14)
                INVALID = 15

        the following will return::

            print Devices(1)            # 1 'PRIMARY'
            print Devices(7)            # 3..10 'USER_DEFINED'
            print Devices(20, None)     # None
            print Devices(20)  # raises ValueError: 20 is not in Devices

        """

        if not isinstance(value, int):
            type_error = TypeError("invalid initializer %r" % value)
            raise type_error

        try:
            return cls._lookup_dict[value]
        except KeyError:
            pass

        ranges_list = cls._ranges_list
        (left, right) = (0, len(ranges_list) - 1)
        while left <= right:
            mid = (left + right) / 2
            item = ranges_list[mid]
            if value in item:
                return item
            if value < item:
                right = mid - 1
            else:
                left = mid + 1

        if isinstance(default, type) and issubclass(default, BaseException):
            error = default("%s is not in %s" % (value, cls.__name__))
            raise error
        else:
            return default
