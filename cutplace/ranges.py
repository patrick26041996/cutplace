"""
Ranges check if certain values are within it. This is used in several places of the ICD, in
particular to specify the length limits for field values and the characters allowed for a data
format.
"""
# Copyright (C) 2009-2013 Thomas Aglassinger
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License
# for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import io
import token
import tokenize

from cutplace import errors
from cutplace import _tools
from cutplace._compat import python_2_unicode_compatible

ELLIPSIS = '\u2026'  # '...' as single character.


@python_2_unicode_compatible
class Range(object):
    """
    A range that can be used to validate that a value is within it.
    """

    def __init__(self, text, default=None):
        """
        Setup a range as specified by ``text``.

        ``text`` must be of the form "lower:upper" or "limit". In case ``text`` is empty (""), any
        value will be accepted by `validate()`. For example, "1...40" accepts values between 1
        and 40.

        ``default`` is an alternative text to use in case ``text`` is ``None`` or empty.
        """
        assert default is None or default.strip(), "default=%r" % default

        if text is not None:
            text = text.replace('...', ELLIPSIS)
        # Find out if a `text` has been specified and if not, use optional `default` instead.
        has_text = (text is not None) and text.strip()
        if not has_text and default is not None:
            text = default
            has_text = True

        if not has_text:
            # Use empty ranges.
            self._description = None
            self._items = None
        else:
            self._description = text
            self._items = []

            # TODO: Consolidate code with `DelimitedDataFormat._validatedCharacter()`.
            tokens = tokenize.generate_tokens(io.StringIO(text).readline)
            end_reached = False
            while not end_reached:
                lower = None
                upper = None
                ellipsis_found = False
                after_hyphen = False
                next_token = next(tokens)
                while not _tools.is_eof_token(next_token) and not _tools.is_comma_token(next_token):
                    next_type = next_token[0]
                    next_value = next_token[1]
                    if next_type in (token.NAME, token.NUMBER, token.STRING):
                        if next_type == token.NUMBER:
                            try:
                                if next_value[:2].lower() == "0x":
                                    next_value = next_value[2:]
                                    base = 16
                                else:
                                    base = 10

                                long_value = int(next_value, base)
                            except ValueError:
                                raise errors.InterfaceError("number must be an integer but is: %r" % next_value)
                            if after_hyphen:
                                long_value = - 1 * long_value
                                after_hyphen = False
                        elif next_type == token.NAME:
                            try:
                                long_value = errors.NAME_TO_ASCII_CODE_MAP[next_value.lower()]
                            except KeyError:
                                valid_symbols = _tools.human_readable_list(sorted(errors.NAME_TO_ASCII_CODE_MAP.keys()))
                                raise errors.InterfaceError("symbolic name %r must be one of: %s"
                                                              % (next_value, valid_symbols))
                        elif next_type == token.STRING:
                            if len(next_value) != 3:
                                raise errors.InterfaceError("text for range must contain a single character "
                                                              "but is: %r" % next_value)
                            left_quote = next_value[0]
                            right_quote = next_value[2]
                            assert left_quote in "\"\'", "leftQuote=%r" % left_quote
                            assert right_quote in "\"\'", "rightQuote=%r" % right_quote
                            long_value = ord(next_value[1])
                        if ellipsis_found:
                            if upper is None:
                                upper = long_value
                            else:
                                raise errors.InterfaceError("range must have at most lower and upper limit "
                                                              "but found another number: %r" % next_value)
                        elif lower is None:
                            lower = long_value
                        else:
                            raise errors.InterfaceError("number must be followed by ellipsis (...) but found: %r" % next_value)
                    elif after_hyphen:
                        raise errors.InterfaceError("hyphen (-) must be followed by number but found: %r" % next_value)
                    elif (next_type == token.OP) and (next_value == "-"):
                        after_hyphen = True
                    elif next_value in (ELLIPSIS, ':'):
                        ellipsis_found = True
                    else:
                        message = "range must be specified using integer numbers, text, " \
                                  "symbols and ellipsis (...) but found: %r [token type: %r]" % (next_value, next_type)
                        raise errors.InterfaceError(message)
                    next_token = next(tokens)

                if after_hyphen:
                    raise errors.InterfaceError("hyphen (-) at end must be followed by number")

                # Decide upon the result.
                if (lower is None):
                    if (upper is None):
                        if ellipsis_found:
                            # Handle "...".
                            # TODO: Handle "..." same as ""?
                            raise errors.InterfaceError("ellipsis (...) must be preceded and/or succeeded by number")
                        else:
                            # Handle "".
                            result = None
                    else:
                        assert ellipsis_found
                        # Handle "...y".
                        result = (None, upper)
                elif ellipsis_found:
                    # Handle "x..." and "x...y".
                    if (upper is not None) and (lower > upper):
                        raise errors.InterfaceError("lower range %d must be greater or equal "
                                                      "to upper range %d" % (lower, upper))
                    result = (lower, upper)
                else:
                    # Handle "x".
                    result = (lower, lower)
                if result is not None:
                    for item in self._items:
                        if self._items_overlap(item, result):
                            # TODO: use _repr_item() or something to display item in error message.
                            raise errors.InterfaceError("range items must not overlap: %r and %r"
                                                   % (self._repr_item(item), self._repr_item(result)))
                    self._items.append(result)
                if _tools.is_eof_token(next_token):
                    end_reached = True

    @property
    def description(self):
        """
        The original human readable description of the range used to construct it.
        """
        return self._description

    @property
    def items(self):
        """
        A list compiled from `description` for fast processing. Each item is represented by a
        tuple ``(lower, upper)`` where either ``lower``or ``upper`` can be ``None``. For example,
        "2...20" turns ``(2, 20)``, "...20" turns to ``(None, 20)`` and "2..." becomes ``(2, None)``.
        """
        return self._items

    def _repr_item(self, item):
        """
        Human readable description of a range item.
        """
        if item is not None:
            result = ""
            (lower, upper) = item
            if lower is None:
                assert upper is not None
                result += ":%s" % upper
            elif upper is None:
                result += "%s:" % lower
            elif lower == upper:
                result += "%s" % lower
            else:
                result += "%s:%s" % (lower, upper)
        else:
            result = str(None)
        return result

    def __repr__(self):
        """
        Human readable description of the range similar to a Python tuple.
        """
        if self.items:
            result = "'%s'" % self
        else:
            result = str(None)
        return result

    def __str__(self):
        """
        Human readable description of the range similar to a Python tuple.
        """
        if self.items:
            result = ""
            is_first = True
            for item in self._items:
                if is_first:
                    is_first = False
                else:
                    result += ", "
                result += self._repr_item(item)
        else:
            result = str(None)
        return result

    def _items_overlap(self, some, other):
        assert some is not None
        assert other is not None
        lower = other[0]
        upper = other[1]
        result = self._item_contains(some, lower) or self._item_contains(some, upper)
        return result

    def _item_contains(self, item, value):
        assert item is not None
        result = False
        if value is not None:
            lower = item[0]
            upper = item[1]
            if lower is None:
                if upper is None:
                    # Handle ""
                    result = True
                else:
                    # Handle "...y"
                    result = (value <= upper)
            elif upper is None:
                # Handle "x..."
                result = (value >= lower)
            else:
                # Handle "x...y"
                result = (value >= lower) and (value <= upper)
        return result

    def validate(self, name, value, location=None):
        """
        Validate that value is within the specified range and in case it is not, raise a `RangeValueError`.
        """
        assert name is not None
        assert name
        assert value is not None

        if self._items is not None:
            is_valid = False
            item_index = 0
            while not is_valid and item_index < len(self._items):
                lower, upper = self._items[item_index]
                if lower is None:
                    assert upper is not None
                    if value <= upper:
                        is_valid = True
                elif upper is None:
                    if value >= lower:
                        is_valid = True
                elif (value >= lower) and (value <= upper):
                    is_valid = True
                item_index += 1
            if not is_valid:
                raise errors.RangeValueError(
                    "%s is %r but must be within range: %r" % (name, value, self), location)
