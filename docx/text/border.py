from ..shared import ElementProxy, lazyproperty

class BorderSide(ElementProxy):

    def __init__(self, element, side, parent=None):
        super(BorderSide, self).__init__(element, parent)
        self._side = side

    def _get_side_element_from_pBdr(self, pBdr):
        return getattr(pBdr, self._side)

    def _get_or_add_side_element_from_pBdr(self, pBdr):
        return getattr(pBdr, "get_or_add_%s" % self._side)()

    def _get_side_element(self):
        pPr = self._element.pPr
        if pPr is None:
            return None
        pBdr = pPr.pBdr
        if pBdr is None:
            return None
        side = self._get_side_element_from_pBdr(pBdr)
        return side

    def _get_or_add_side_element(self):
        pPr = self._element.get_or_add_pPr()
        if pPr is None:
            return None
        pBdr = pPr.get_or_add_pBdr()
        if pBdr is None:
            return None
        side = self._get_or_add_side_element_from_pBdr(pBdr)
        return side

    @property
    def side(self):
        """
        Returns a string representing the side to whichthis |BorderSide|
        object belongs.
        """
        return self._side

    @property
    def val(self):
        """
        An |ST_BorderValue| object representing the style of the border.
        """
        side = self._get_side_element()
        if side is None:
            return None
        return side.val

    @val.setter
    def val(self,val):
        side = self._get_or_add_side_element()
        side.val = val

    @property
    def sz(self):
        """
        An |ST_EighthsOfPointMeasure| object representing the size of the
        border in eighths of a point.
        """
        side = self._get_side_element()
        if side is None:
            return None
        return side.sz

    @sz.setter
    def sz(self,sz):
        side = self._get_or_add_side_element()
        side.sz = sz

    @property
    def space(self):
        """
        An |ST_PtsMeasure| object representing the spacing offset for the
        border, in Points.
        """
        side = self._get_side_element()
        if side is None:
            return None
        return side.space

    @space.setter
    def space(self,space):
        side = self._get_or_add_side_element()
        side.space = space

    @property
    def color(self):
        """
        An |ST_HexColor| object representing the color of the border.
        """
        side = self._get_side_element()
        if side is None:
            return None
        return side.color

    @color.setter
    def color(self,color):
        side = self._get_or_add_side_element()
        side.color = color

    @property
    def shadow(self):
        """
        An |XsdBoolean| object representing specifying whether a shadow is
        displayed on the border.
        """
        side = self._get_side_element()
        if side is None:
            return None
        return side.shadow

    @shadow.setter
    def shadow(self,shadow):
        side = self._get_or_add_side_element()
        side.shadow = shadow


class ParagraphBorder(ElementProxy):
    __slots__ = ('_top','_left','_bottom','_right',)

    @property
    def top(self):
        """
        The |BorderSide| object representing the top border of the
        paragraph.
        """
        try:
            return self._top
        except AttributeError:
            pPr = self._element.pPr
            if pPr is None:
                return None
            pBdr = self._element.pPr.pBdr
            if pBdr is None:
                return None
            top = pBdr.top
            if top is None:
                return None
            self._top = BorderSide(self._element, "top")
        return self._top

    @top.setter
    def top(self, side):
        if self.top is None:
            self._top = BorderSide(self._element, "top")
        top = self.top
        top.val = side.val
        top.sz = side.sz
        top.space = side.space
        top.color = side.color
        top.shadow = side.shadow

    @property
    def left(self):
        """
        The |BorderSide| object representing the left border of the
        paragraph.
        """
        try:
            return self._left
        except AttributeError:
            pPr = self._element.pPr
            if pPr is None:
                return None
            pBdr = self._element.pPr.pBdr
            if pBdr is None:
                return None
            left = pBdr.left
            if left is None:
                return None
            self._left = BorderSide(self._element, "left")
            return self._left

    @left.setter
    def left(self, side):
        if self.left is None:
            self._left = BorderSide(self._element, "left")
            left = self.left
            left.val = side.val
            left.sz = side.sz
            left.space = side.space
            left.color = side.color
            left.shadow = side.shadow

    @property
    def bottom(self):
        """
        The |BorderSide| object representing the bottom border of the
        paragraph.
        """
        try:
            return self._bottom
        except AttributeError:
            pPr = self._element.pPr
            if pPr is None:
                return None
            pBdr = self._element.pPr.pBdr
            if pBdr is None:
                return None
            bottom = pBdr.bottom
            if bottom is None:
                return None
            self._bottom = BorderSide(self._element, "bottom")
            return self._bottom

    @bottom.setter
    def bottom(self, side):
        if self.bottom is None:
            self._bottom = BorderSide(self._element, "bottom")
        bottom = self.bottom
        bottom.val = side.val
        bottom.sz = side.sz
        bottom.space = side.space
        bottom.color = side.color
        bottom.shadow = side.shadow

    @property
    def right(self):
        """
        The |BorderSide| object representing the right border of the
        paragraph.
        """
        try:
            return self._right
        except AttributeError:
            pPr = self._element.pPr
            if pPr is None:
                return None
            pBdr = self._element.pPr.pBdr
            if pBdr is None:
                return None
            right = pBdr.right
            if right is None:
                return None
            self._right = BorderSide(self._element, "right")
            return self._right

    @right.setter
    def right(self, side):
        if self.right is None:
            self._right = BorderSide(self._element, "right")
            right = self.right
            right.val = side.val
            right.sz = side.sz
            right.space = side.space
            right.color = side.color
            right.shadow = side.shadow
