from enumr import enumr


###############################################################################

class Devices1(enumr):
    PRIMARY = 1                     # value 1
    SECONDARY = 2
    USER_DEFINED = (3, 10)          # subrange 3..10
    RESERVED = (11, 14)
    INVALID = 15


print Devices1.PRIMARY
print Devices1.SECONDARY
print Devices1.USER_DEFINED
print Devices1.RESERVED
print Devices1.INVALID
print


class Devices2(enumr):
    _ant_spec = 'brief', 'ref'
    _str_spec = "{value} {brief!r}"
    PRIMARY = 1, "Primary device", "sub.10.2.1"
    USER_DEFINED = (3, 10), "User defined device", "sub.10.2.3"


print Devices2.PRIMARY
print Devices2.USER_DEFINED
print


###############################################################################

print Devices1.USER_DEFINED          # 3..10
print Devices1.USER_DEFINED.min      # 3
print Devices1.USER_DEFINED.max      # 10
print 7 in Devices1.USER_DEFINED     # True
print 11 > Devices1.USER_DEFINED     # True
print 2 in Devices1.SECONDARY        # True
print 2 == Devices1.SECONDARY        # True
print "0x{:02X}".format(Devices1.RESERVED)     # 0x0B..0E
print "{0.value} {0.name!r}".format(Devices1.INVALID)  # 15 'INVALID'
print

print Devices2.PRIMARY.brief     # Primary device
print Devices2.PRIMARY.ref       # sub.10.2.1
print

print "{0.value}: {0.brief!r}".format(Devices2.USER_DEFINED)
# 3..10: 'User defined device'
print

print Devices2(1)            # 1 'Primary device'
print Devices2(7)            # 3..10 'User defined device'
print Devices2(20, None)     # None
try:
    print Devices2(20)  # raises ValueError: 20 is not in Devices
except ValueError as e:
    print e
print


class Devices21(enumr):
    _ant_spec = 'brief', 'ref'
    _str_spec = "0x{value:02X}"             # 0x03..0A
    USER_DEFINED = (3, 10), "User defined device", "sub.10.2.3"


class Devices22(enumr):
    _ant_spec = 'brief', 'ref'
    _str_spec = "0x{min:02X}-{max:02X}"     # 0x03-0A
    USER_DEFINED = (3, 10), "User defined device", "sub.10.2.3"


class Devices23(enumr):
    _ant_spec = 'brief', 'ref'
    _str_spec = "{name} = {value}"          # USER_DEFINED = 3..10
    USER_DEFINED = (3, 10), "User defined device", "sub.10.2.3"


class Devices24(enumr):
    _ant_spec = 'brief', 'ref'
    _str_spec = "{brief!r}"                 # 'User defined device'
    USER_DEFINED = (3, 10), "User defined device", "sub.10.2.3"

print Devices21.USER_DEFINED          # 0x03..0A
print Devices22.USER_DEFINED          # 0x03-0A
print Devices23.USER_DEFINED          # USER_DEFINED = 3..10
print Devices24.USER_DEFINED          # 'User defined device'
print


###############################################################################

class Devices3(enumr):
    _str_spec = "{value} {name!r}"
    PRIMARY = 1
    SECONDARY = 2
    USER_DEFINED = (3, 10)
    RESERVED = (11, 14)
    INVALID = 15

print Devices3(2)            # 2 'SECONDARY'
print Devices3(7)            # 3..10 'USER_DEFINED'
print Devices3(20, None)     # None
try:
    print Devices3(20)  # raises ValueError: 20 is not in Devices
except ValueError as e:
    print e
