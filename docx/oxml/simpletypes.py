# encoding: utf-8

"""
Simple type classes, providing validation and format translation for values
stored in XML element attributes. Naming generally corresponds to the simple
type in the associated XML schema.
"""

from __future__ import (
    absolute_import, division, print_function, unicode_literals
)

from ..exceptions import InvalidXmlError
from ..shared import Length, Emu, Pt, RGBColor, Twips, EighthsOfPoint


class BaseSimpleType(object):

    @classmethod
    def from_xml(cls, str_value):
        return cls.convert_from_xml(str_value)

    @classmethod
    def to_xml(cls, value):
        cls.validate(value)
        str_value = cls.convert_to_xml(value)
        return str_value

    @classmethod
    def validate_int(cls, value):
        if not isinstance(value, int):
            raise TypeError(
                "value must be <type 'int'>, got %s" % type(value)
            )

    @classmethod
    def validate_int_in_range(cls, value, min_inclusive, max_inclusive):
        cls.validate_int(value)
        if value < min_inclusive or value > max_inclusive:
            raise ValueError(
                "value must be in range %d to %d inclusive, got %d" %
                (min_inclusive, max_inclusive, value)
            )

    @classmethod
    def validate_string(cls, value):
        if isinstance(value, str):
            return value
        try:
            if isinstance(value, basestring):
                return value
        except NameError:  # means we're on Python 3
            pass
        raise TypeError(
            "value must be a string, got %s" % type(value)
        )


class BaseIntType(BaseSimpleType):

    @classmethod
    def convert_from_xml(cls, str_value):
        return int(str_value)

    @classmethod
    def convert_to_xml(cls, value):
        return str(value)

    @classmethod
    def validate(cls, value):
        cls.validate_int(value)


class BaseStringType(BaseSimpleType):

    @classmethod
    def convert_from_xml(cls, str_value):
        return str_value

    @classmethod
    def convert_to_xml(cls, value):
        return value

    @classmethod
    def validate(cls, value):
        cls.validate_string(value)


class BaseStringEnumerationType(BaseStringType):

    @classmethod
    def validate(cls, value):
        cls.validate_string(value)
        if value not in cls._members:
            raise ValueError(
                "must be one of %s, got '%s'" % (cls._members, value)
            )


class XsdAnyUri(BaseStringType):
    """
    There's a regular expression this is supposed to meet but so far thinking
    spending cycles on validating wouldn't be worth it for the number of
    programming errors it would catch.
    """


class XsdBoolean(BaseSimpleType):

    @classmethod
    def convert_from_xml(cls, str_value):
        if str_value not in ('1', '0', 'true', 'false'):
            raise InvalidXmlError(
                "value must be one of '1', '0', 'true' or 'false', got '%s'"
                % str_value
            )
        return str_value in ('1', 'true')

    @classmethod
    def convert_to_xml(cls, value):
        return {True: '1', False: '0'}[value]

    @classmethod
    def validate(cls, value):
        if value not in (True, False):
            raise TypeError(
                "only True or False (and possibly None) may be assigned, got"
                " '%s'" % value
            )


class XsdId(BaseStringType):
    """
    String that must begin with a letter or underscore and cannot contain any
    colons. Not fully validated because not used in external API.
    """
    pass


class XsdInt(BaseIntType):

    @classmethod
    def validate(cls, value):
        cls.validate_int_in_range(value, -2147483648, 2147483647)


class XsdLong(BaseIntType):

    @classmethod
    def validate(cls, value):
        cls.validate_int_in_range(
            value, -9223372036854775808, 9223372036854775807
        )


class XsdString(BaseStringType):
    pass


class XsdStringEnumeration(BaseStringEnumerationType):
    """
    Set of enumerated xsd:string values.
    """


class XsdToken(BaseStringType):
    """
    xsd:string with whitespace collapsing, e.g. multiple spaces reduced to
    one, leading and trailing space stripped.
    """
    pass


class XsdUnsignedInt(BaseIntType):

    @classmethod
    def validate(cls, value):
        cls.validate_int_in_range(value, 0, 4294967295)


class XsdUnsignedLong(BaseIntType):

    @classmethod
    def validate(cls, value):
        cls.validate_int_in_range(value, 0, 18446744073709551615)


class ST_BrClear(XsdString):

    @classmethod
    def validate(cls, value):
        cls.validate_string(value)
        valid_values = ('none', 'left', 'right', 'all')
        if value not in valid_values:
            raise ValueError(
                "must be one of %s, got '%s'" % (valid_values, value)
            )


class ST_BrType(XsdString):

    @classmethod
    def validate(cls, value):
        cls.validate_string(value)
        valid_values = ('page', 'column', 'textWrapping')
        if value not in valid_values:
            raise ValueError(
                "must be one of %s, got '%s'" % (valid_values, value)
            )


class ST_Coordinate(BaseIntType):

    @classmethod
    def convert_from_xml(cls, str_value):
        if 'i' in str_value or 'm' in str_value or 'p' in str_value:
            return ST_UniversalMeasure.convert_from_xml(str_value)
        return Emu(int(str_value))

    @classmethod
    def validate(cls, value):
        ST_CoordinateUnqualified.validate(value)


class ST_CoordinateUnqualified(XsdLong):

    @classmethod
    def validate(cls, value):
        cls.validate_int_in_range(value, -27273042329600, 27273042316900)


class ST_DecimalNumber(XsdInt):
    pass


class ST_DrawingElementId(XsdUnsignedInt):
    pass


class ST_HexColor(BaseStringType):

    @classmethod
    def convert_from_xml(cls, str_value):
        if str_value == 'auto':
            return ST_HexColorAuto.AUTO
        return RGBColor.from_string(str_value)

    @classmethod
    def convert_to_xml(cls, value):
        """
        Keep alpha hex numerals all uppercase just for consistency.
        """
        # expecting 3-tuple of ints in range 0-255
        return '%02X%02X%02X' % value

    @classmethod
    def validate(cls, value):
        # must be an RGBColor object ---
        if not isinstance(value, RGBColor):
            raise ValueError(
                "rgb color value must be RGBColor object, got %s %s"
                % (type(value), value)
            )


class ST_HexColorAuto(XsdStringEnumeration):
    """
    Value for `w:color/[@val="auto"] attribute setting
    """
    AUTO = 'auto'

    _members = (AUTO,)


class ST_HpsMeasure(XsdUnsignedLong):
    """
    Half-point measure, e.g. 24.0 represents 12.0 points.
    """
    @classmethod
    def convert_from_xml(cls, str_value):
        if 'm' in str_value or 'n' in str_value or 'p' in str_value:
            return ST_UniversalMeasure.convert_from_xml(str_value)
        return Pt(int(str_value)/2.0)

    @classmethod
    def convert_to_xml(cls, value):
        emu = Emu(value)
        half_points = int(emu.pt * 2)
        return str(half_points)

class ST_PtsMeasure(XsdUnsignedLong):
    """
    Point measure.
    """
    @classmethod
    def convert_from_xml(cls, str_value):
        if 'm' in str_value or 'n' in str_value or 'p' in str_value:
            return ST_UniversalMeasure.convert_from_xml(str_value)
        return Pt(int(str_value))

    @classmethod
    def convert_to_xml(cls, value):
        emu = Emu(value)
        points = int(emu.pt)
        return str(points)


class ST_Merge(XsdStringEnumeration):
    """
    Valid values for <w:xMerge val=""> attribute
    """
    CONTINUE = 'continue'
    RESTART = 'restart'

    _members = (CONTINUE, RESTART)


class ST_OnOff(XsdBoolean):

    @classmethod
    def convert_from_xml(cls, str_value):
        if str_value not in ('1', '0', 'true', 'false', 'on', 'off'):
            raise InvalidXmlError(
                "value must be one of '1', '0', 'true', 'false', 'on', or 'o"
                "ff', got '%s'" % str_value
            )
        return str_value in ('1', 'true', 'on')


class ST_PositiveCoordinate(XsdLong):

    @classmethod
    def convert_from_xml(cls, str_value):
        return Emu(int(str_value))

    @classmethod
    def validate(cls, value):
        cls.validate_int_in_range(value, 0, 27273042316900)


class ST_RelationshipId(XsdString):
    pass


class ST_SignedTwipsMeasure(XsdInt):

    @classmethod
    def convert_from_xml(cls, str_value):
        if 'i' in str_value or 'm' in str_value or 'p' in str_value:
            return ST_UniversalMeasure.convert_from_xml(str_value)
        return Twips(int(str_value))

    @classmethod
    def convert_to_xml(cls, value):
        emu = Emu(value)
        twips = emu.twips
        return str(twips)


class ST_String(XsdString):
    pass


class ST_TblLayoutType(XsdString):

    @classmethod
    def validate(cls, value):
        cls.validate_string(value)
        valid_values = ('fixed', 'autofit')
        if value not in valid_values:
            raise ValueError(
                "must be one of %s, got '%s'" % (valid_values, value)
            )


class ST_TblWidth(XsdString):

    @classmethod
    def validate(cls, value):
        cls.validate_string(value)
        valid_values = ('auto', 'dxa', 'nil', 'pct')
        if value not in valid_values:
            raise ValueError(
                "must be one of %s, got '%s'" % (valid_values, value)
            )


class ST_TwipsMeasure(XsdUnsignedLong):

    @classmethod
    def convert_from_xml(cls, str_value):
        if 'i' in str_value or 'm' in str_value or 'p' in str_value:
            return ST_UniversalMeasure.convert_from_xml(str_value)
        return Twips(int(str_value))

    @classmethod
    def convert_to_xml(cls, value):
        emu = Emu(value)
        twips = emu.twips
        return str(twips)

class ST_EighthsOfPointMeasure(XsdUnsignedLong):

    @classmethod
    def convert_from_xml(cls, str_value):
        if 'i' in str_value or 'm' in str_value or 'p' in str_value:
            return ST_UniversalMeasure.convert_from_xml(str_value)
        return EighthsOfPoint(int(str_value))

    @classmethod
    def convert_to_xml(cls, value):
        emu = Emu(value)
        eop = emu.eighths_of_point
        return str(eop)


class ST_UniversalMeasure(BaseSimpleType):

    @classmethod
    def convert_from_xml(cls, str_value):
        float_part, units_part = str_value[:-2], str_value[-2:]
        quantity = float(float_part)
        multiplier = {
            'mm': Length._EMUS_PER_MM,
            'cm': Length._EMUS_PER_CM,
            'in': 914400,
            'pt': Length._EMUS_PER_PT,
            'pc': 152400,
            'pi': 152400
        }[units_part]
        emu_value = Emu(int(round(quantity * multiplier)))
        return emu_value


class ST_VerticalAlignRun(XsdStringEnumeration):
    """
    Valid values for `w:vertAlign/@val`.
    """
    BASELINE = 'baseline'
    SUPERSCRIPT = 'superscript'
    SUBSCRIPT = 'subscript'

    _members = (BASELINE, SUPERSCRIPT, SUBSCRIPT)

class ST_BorderValue(XsdStringEnumeration):
    """
    Valid values for val attribute of children of ``<w:pBdr>`` elements.
    These values come from the .NET OpenXML documentation at
    https://docs.microsoft.com/en-us/dotnet/api/documentformat.openxml.wordprocessing.bordervalues?view=openxml-2.8.1
    """
    APPLES = "apples"
    ARCHEDSCALLOPS = "archedScallops"
    BABYPACIFIER = "babyPacifier"
    BABYRATTLE = "babyRattle"
    BALLOONS3COLORS = "balloons3Colors"
    BALLOONSHOTAIR = "balloonsHotAir"
    BASICBLACKDASHES = "basicBlackDashes"
    BASICBLACKDOTS = "basicBlackDots"
    BASICBLACKSQUARES = "basicBlackSquares"
    BASICTHINLINES = "basicThinLines"
    BASICWHITEDASHES = "basicWhiteDashes"
    BASICWHITEDOTS = "basicWhiteDots"
    BASICWHITESQUARES = "basicWhiteSquares"
    BASICWIDEINLINE = "basicWideInline"
    BASICWIDEMIDLINE = "basicWideMidline"
    BASICWIDEOUTLINE = "basicWideOutline"
    BATS = "bats"
    BIRDS = "birds"
    BIRDSFLIGHT = "birdsFlight"
    CABINS = "cabins"
    CAKESLICE = "cakeSlice"
    CANDYCORN = "candyCorn"
    CELTICKNOTWORK = "celticKnotwork"
    CERTIFICATEBANNER = "certificateBanner"
    CHAINLINK = "chainLink"
    CHAMPAGNEBOTTLE = "champagneBottle"
    CHECKEDBARBLACK = "checkedBarBlack"
    CHECKEDBARCOLOR = "checkedBarColor"
    CHECKERED = "checkered"
    CHRISTMASTREE = "christmasTree"
    CIRCLESLINES = "circlesLines"
    CIRCLESRECTANGLES = "circlesRectangles"
    CLASSICALWAVE = "classicalWave"
    CLOCKS = "clocks"
    COMPASS = "compass"
    CONFETTI = "confetti"
    CONFETTIGRAYS = "confettiGrays"
    CONFETTIOUTLINE = "confettiOutline"
    CONFETTISTREAMERS = "confettiStreamers"
    CONFETTIWHITE = "confettiWhite"
    CORNERTRIANGLES = "cornerTriangles"
    COUPONCUTOUTDASHES = "couponCutoutDashes"
    COUPONCUTOUTDOTS = "couponCutoutDots"
    CRAZYMAZE = "crazyMaze"
    CREATURESBUTTERFLY = "creaturesButterfly"
    CREATURESFISH = "creaturesFish"
    CREATURESINSECTS = "creaturesInsects"
    CREATURESLADYBUG = "creaturesLadyBug"
    CROSSSTITCH = "crossStitch"
    CUP = "cup"
    DASHDOTSTROKED = "dashDotStroked"
    DASHED = "dashed"
    DASHSMALLGAP = "dashSmallGap"
    DECOARCH = "decoArch"
    DECOARCHCOLOR = "decoArchColor"
    DECOBLOCKS = "decoBlocks"
    DIAMONDSGRAY = "diamondsGray"
    DOTDASH = "dotDash"
    DOTDOTDASH = "dotDotDash"
    DOTTED = "dotted"
    DOUBLE = "double"
    DOUBLED = "doubleD"
    DOUBLEDIAMONDS = "doubleDiamonds"
    DOUBLEWAVE = "doubleWave"
    EARTH1 = "earth1"
    EARTH2 = "earth2"
    ECLIPSINGSQUARES1 = "eclipsingSquares1"
    ECLIPSINGSQUARES2 = "eclipsingSquares2"
    EGGSBLACK = "eggsBlack"
    FANS = "fans"
    FILM = "film"
    FIRECRACKERS = "firecrackers"
    FLOWERSBLOCKPRINT = "flowersBlockPrint"
    FLOWERSDAISIES = "flowersDaisies"
    FLOWERSMODERN1 = "flowersModern1"
    FLOWERSMODERN2 = "flowersModern2"
    FLOWERSPANSY = "flowersPansy"
    FLOWERSREDROSE = "flowersRedRose"
    FLOWERSROSES = "flowersRoses"
    FLOWERSTEACUP = "flowersTeacup"
    FLOWERSTINY = "flowersTiny"
    GEMS = "gems"
    GINGERBREADMAN = "gingerbreadMan"
    GRADIENT = "gradient"
    HANDMADE1 = "handmade1"
    HANDMADE2 = "handmade2"
    HEARTBALLOON = "heartBalloon"
    HEARTGRAY = "heartGray"
    HEARTS = "hearts"
    HEEBIEJEEBIES = "heebieJeebies"
    HOLLY = "holly"
    HOUSEFUNKY = "houseFunky"
    HYPNOTIC = "hypnotic"
    ICECREAMCONES = "iceCreamCones"
    INSET = "inset"
    LIGHTBULB = "lightBulb"
    LIGHTNING1 = "lightning1"
    LIGHTNING2 = "lightning2"
    MAPLELEAF = "mapleLeaf"
    MAPLEMUFFINS = "mapleMuffins"
    MAPPINS = "mapPins"
    MARQUEE = "marquee"
    MARQUEETOOTHED = "marqueeToothed"
    MOONS = "moons"
    MOSAIC = "mosaic"
    MUSICNOTES = "musicNotes"
    NIL = "nil"
    NONE = "none"
    NORTHWEST = "northwest"
    OUTSET = "outset"
    OVALS = "ovals"
    PACKAGES = "packages"
    PALMSBLACK = "palmsBlack"
    PALMSCOLOR = "palmsColor"
    PAPERCLIPS = "paperClips"
    PAPYRUS = "papyrus"
    PARTYFAVOR = "partyFavor"
    PARTYGLASS = "partyGlass"
    PENCILS = "pencils"
    PEOPLE = "people"
    PEOPLEHATS = "peopleHats"
    PEOPLEWAVING = "peopleWaving"
    POINSETTIAS = "poinsettias"
    POSTAGESTAMP = "postageStamp"
    PUMPKIN1 = "pumpkin1"
    PUSHPINNOTE1 = "pushPinNote1"
    PUSHPINNOTE2 = "pushPinNote2"
    PYRAMIDS = "pyramids"
    PYRAMIDSABOVE = "pyramidsAbove"
    QUADRANTS = "quadrants"
    RINGS = "rings"
    SAFARI = "safari"
    SAWTOOTH = "sawtooth"
    SAWTOOTHGRAY = "sawtoothGray"
    SCAREDCAT = "scaredCat"
    SEATTLE = "seattle"
    SHADOWEDSQUARES = "shadowedSquares"
    SHAPES1 = "shapes1"
    SHAPES2 = "shapes2"
    SHARKSTEETH = "sharksTeeth"
    SHOREBIRDTRACKS = "shorebirdTracks"
    SINGLE = "single"
    SKYROCKET = "skyrocket"
    SNOWFLAKEFANCY = "snowflakeFancy"
    SNOWFLAKES = "snowflakes"
    SOMBRERO = "sombrero"
    SOUTHWEST = "southwest"
    STARS = "stars"
    STARS3D = "stars3d"
    STARSBLACK = "starsBlack"
    STARSSHADOWED = "starsShadowed"
    STARSTOP = "starsTop"
    SUN = "sun"
    SWIRLIGIG = "swirligig"
    THICK = "thick"
    THICKTHINLARGEGAP = "thickThinLargeGap"
    THICKTHINMEDIUMGAP = "thickThinMediumGap"
    THICKTHINSMALLGAP = "thickThinSmallGap"
    THINTHICKLARGEGAP = "thinThickLargeGap"
    THINTHICKMEDIUMGAP = "thinThickMediumGap"
    THINTHICKSMALLGAP = "thinThickSmallGap"
    THINTHICKTHINLARGEGAP = "thinThickThinLargeGap"
    THINTHICKTHINMEDIUMGAP = "thinThickThinMediumGap"
    THINTHICKTHINSMALLGAP = "thinThickThinSmallGap"
    THREEDEMBOSS = "threeDEmboss"
    THREEDENGRAVE = "threeDEngrave"
    TORNPAPER = "tornPaper"
    TORNPAPERBLACK = "tornPaperBlack"
    TREES = "trees"
    TRIANGLE1 = "triangle1"
    TRIANGLE2 = "triangle2"
    TRIANGLECIRCLE1 = "triangleCircle1"
    TRIANGLECIRCLE2 = "triangleCircle2"
    TRIANGLEPARTY = "triangleParty"
    TRIANGLES = "triangles"
    TRIBAL1 = "tribal1"
    TRIBAL2 = "tribal2"
    TRIBAL3 = "tribal3"
    TRIBAL4 = "tribal4"
    TRIBAL5 = "tribal5"
    TRIBAL6 = "tribal6"
    TRIPLE = "triple"
    TWISTEDLINES1 = "twistedLines1"
    TWISTEDLINES2 = "twistedLines2"
    VINE = "vine"
    WAVE = "wave"
    WAVELINE = "waveline"
    WEAVINGANGLES = "weavingAngles"
    WEAVINGBRAID = "weavingBraid"
    WEAVINGRIBBON = "weavingRibbon"
    WEAVINGSTRIPS = "weavingStrips"
    WHITEFLOWERS = "whiteFlowers"
    WOODWORK = "woodwork"
    XILLUSIONS = "xIllusions"
    ZANYTRIANGLES = "zanyTriangles"
    ZIGZAG = "zigZag"
    ZIGZAGSTITCH = "zigZagStitch"

    _members = (APPLES, ARCHEDSCALLOPS, BABYPACIFIER, BABYRATTLE, BALLOONS3COLORS, BALLOONSHOTAIR, BASICBLACKDASHES, BASICBLACKDOTS, BASICBLACKSQUARES, BASICTHINLINES, BASICWHITEDASHES, BASICWHITEDOTS, BASICWHITESQUARES, BASICWIDEINLINE, BASICWIDEMIDLINE, BASICWIDEOUTLINE, BATS, BIRDS, BIRDSFLIGHT, CABINS, CAKESLICE, CANDYCORN, CELTICKNOTWORK, CERTIFICATEBANNER, CHAINLINK, CHAMPAGNEBOTTLE, CHECKEDBARBLACK, CHECKEDBARCOLOR, CHECKERED, CHRISTMASTREE, CIRCLESLINES, CIRCLESRECTANGLES, CLASSICALWAVE, CLOCKS, COMPASS, CONFETTI, CONFETTIGRAYS, CONFETTIOUTLINE, CONFETTISTREAMERS, CONFETTIWHITE, CORNERTRIANGLES, COUPONCUTOUTDASHES, COUPONCUTOUTDOTS, CRAZYMAZE, CREATURESBUTTERFLY, CREATURESFISH, CREATURESINSECTS, CREATURESLADYBUG, CROSSSTITCH, CUP, DASHDOTSTROKED, DASHED, DASHSMALLGAP, DECOARCH, DECOARCHCOLOR, DECOBLOCKS, DIAMONDSGRAY, DOTDASH, DOTDOTDASH, DOTTED, DOUBLE, DOUBLED, DOUBLEDIAMONDS, DOUBLEWAVE, EARTH1, EARTH2, ECLIPSINGSQUARES1, ECLIPSINGSQUARES2, EGGSBLACK, FANS, FILM, FIRECRACKERS, FLOWERSBLOCKPRINT, FLOWERSDAISIES, FLOWERSMODERN1, FLOWERSMODERN2, FLOWERSPANSY, FLOWERSREDROSE, FLOWERSROSES, FLOWERSTEACUP, FLOWERSTINY, GEMS, GINGERBREADMAN, GRADIENT, HANDMADE1, HANDMADE2, HEARTBALLOON, HEARTGRAY, HEARTS, HEEBIEJEEBIES, HOLLY, HOUSEFUNKY, HYPNOTIC, ICECREAMCONES, INSET, LIGHTBULB, LIGHTNING1, LIGHTNING2, MAPLELEAF, MAPLEMUFFINS, MAPPINS, MARQUEE, MARQUEETOOTHED, MOONS, MOSAIC, MUSICNOTES, NIL, NONE, NORTHWEST, OUTSET, OVALS, PACKAGES, PALMSBLACK, PALMSCOLOR, PAPERCLIPS, PAPYRUS, PARTYFAVOR, PARTYGLASS, PENCILS, PEOPLE, PEOPLEHATS, PEOPLEWAVING, POINSETTIAS, POSTAGESTAMP, PUMPKIN1, PUSHPINNOTE1, PUSHPINNOTE2, PYRAMIDS, PYRAMIDSABOVE, QUADRANTS, RINGS, SAFARI, SAWTOOTH, SAWTOOTHGRAY, SCAREDCAT, SEATTLE, SHADOWEDSQUARES, SHAPES1, SHAPES2, SHARKSTEETH, SHOREBIRDTRACKS, SINGLE, SKYROCKET, SNOWFLAKEFANCY, SNOWFLAKES, SOMBRERO, SOUTHWEST, STARS, STARS3D, STARSBLACK, STARSSHADOWED, STARSTOP, SUN, SWIRLIGIG, THICK, THICKTHINLARGEGAP, THICKTHINMEDIUMGAP, THICKTHINSMALLGAP, THINTHICKLARGEGAP, THINTHICKMEDIUMGAP, THINTHICKSMALLGAP, THINTHICKTHINLARGEGAP, THINTHICKTHINMEDIUMGAP, THINTHICKTHINSMALLGAP, THREEDEMBOSS, THREEDENGRAVE, TORNPAPER, TORNPAPERBLACK, TREES, TRIANGLE1, TRIANGLE2, TRIANGLECIRCLE1, TRIANGLECIRCLE2, TRIANGLEPARTY, TRIANGLES, TRIBAL1, TRIBAL2, TRIBAL3, TRIBAL4, TRIBAL5, TRIBAL6, TRIPLE, TWISTEDLINES1, TWISTEDLINES2, VINE, WAVE, WAVELINE, WEAVINGANGLES, WEAVINGBRAID, WEAVINGRIBBON, WEAVINGSTRIPS, WHITEFLOWERS, WOODWORK, XILLUSIONS, ZANYTRIANGLES, ZIGZAG, ZIGZAGSTITCH)
