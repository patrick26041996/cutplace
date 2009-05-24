=====================================
Writing an Interface Control Document
=====================================

This chapter describes how to ... TODO: introduction overview.

Parts of an ICD
===============

ICD's for cutplace focus on the data specific parts and hence only describe:

1. The Data format: The general format for data files, such as line separator,
   character encoding, quote character and so on. These properties concern the
   whole file and each data item in it.

2. Fields:

3. Optional Checks, which are rules that have to be met across the whole
   document or several fields. For example, a customer ID is supposed to be
   unique and therefor must occur only once within a file.

4. Comments are intended for human readers. Cutplace does not process them.
   Typically they describing the meaning of things or the motivation for
   certain decisions. Another use is the description the source of certain data
   items to simplify error analysis.

This means that for cutplace to be applicable, the data of your interface have
to fit in a table with each column always containing the same kind of value.

TODO: elaborate

Data formats
============

The data format describes general properties of the input. Here is an example:

Example data format

==  ==============  ==========
..  Property        Value
==  ==============  ==========
D   Format          CSV
D   Encoding        ISO-8859-1
D   Line delimiter  LF
D   Item delimiter  ,
==  ==============  ==========

This basically says that the data are provided as comma separated values (CSV)
and the character encoding is ISO-8859-1 (also known as Latin-1). Rows are
separated using linefeed characters (ASCII code 10) and columns are separated
using a comma (,).

The remainder of this section describes the supported formats and available
properties for them.

Delimited data
--------------

For data, both lines and columns are delimited by certain characters.

Example for delimited data using visible ASCII characters and Cyrillic (Unicode
0x0400-0x4ff)

==  ==================  =================
..  Property            Value
==  ==================  =================
D   Format              Delimited
D   Encoding            UTF-8
D   Line delimiter      CRLF
D   Item delimiter      ,
D   Quote character     "
D   Escape character    "
D   Allowed characters  32:128, 1024:1280
==  ==================  =================

In case Format is Delimited, the following properties have to be specified:

Encoding
    The character encoding. The most common values will be ASCII, ISO-8859-1
    (for many western countries), UTF-8 (for Unicode), CP-850 (used by MS DOS
    in many western countries).

Line delimiter
    Thus describes which character or character sequence is used to mark the
    end of a line. Possible values are:

    * CR - "carriage return", ASCII code 13, used by Mac OS Classic.

    * LF - "line feed", ASCII code 10, used by Unix based platforms and others,
      for example Mac OS X, Linux, Solaris BSD-variants and Amiga OS.
    
    * CRLF - "carriage return linefeed", two characters with ASCII code 13 and
      10, used for example by Windows and MS DOS.
    
    * Any - Do an analysis of the input and automatically choose the line
      delimiter from it based on the one used most often with the first few
      lines. Note that this still requires that the line delimiter is used
      consistently, using for example CR for some lines and LF for others is
      not allowed.

Item delimiter
    The character used to separated data items from each other, for example:
    comma (,), semicolon (;), colon (:).

    TODO: How to specify tab?

Quote character
    The character used to surround items with that contain delimiters or while
    space, for example double quote (") or single quote (').

    TODO: How to specify "no quoting"?

Escape character
    The escape character necessary to use the quote character in item values.
    Possible values are: double quote (").

    TODO: Consider supporting backslash (\) for C-like escapes

Allowed characters
    This range describing the characters allowed for data items. Each number
    represents the decimal Unicode value of a character that can be used. With
    the help of colons (:) you can easily specify several characters. For
    example, ``32:128`` means "between 32 and 128".

    You can find more information on how to specify ranges in :ref:`ranges`.

CSV data (comma separated values)
---------------------------------

CSV data are delimited data too, but most properties already have default
values you do not need to specify unless you want to use other values.

Minimal example for CSV data

==  ========  =====
..  Property  Value
==  ========  =====
F   Format    CSV
==  ========  =====

This is the same as:

Example for CSV data with default values spelled out

==  ==================  =====
..  Property            Value
==  ==================  =====
F   Format              CSV
F   Encoding            ASCII
F   Line delimiter      Any
F   Item delimiter      ,
F   Quote character     "
F   Escape character    "
F   Allowed characters  0:
==  ==================  =====

Many of these values will be fine for all practical purpose.  Most frequently
"Encoding" and "Item delimiter" might have to be adjusted.

Example for CSV data common in many European regions

==  ==============  ==========
..  Property        Value
==  ==============  ==========
F   Format          CSV
F   Encoding        ISO-8859-1
F   Item delimiter  ;
==  ==============  ==========

.. _format-excel:

Excel data
----------

Excel is a spreadsheet application and part of Microsoft Office.

Minimal example for Excel data

==  ========  =====
..  Property  Value
==  ========  =====
F   Format    Excel
==  ========  =====

Additionally there are a couple of optional properties.

A more advanced example for Excel data

==  ========  =====
..  Property  Value
==  ========  =====
F   Format    Excel
F   Header    2
F   Sheet     5
==  ========  =====

The property header describes how many rows should be skipped before the data
to validate start. It is optional and defaults to 0, meaning there is no header
and the first row already contains data.

The property sheet specifies from which sheet the data should be read. It is
only required in case a workbook contains more than one sheet and the data to
validate are located in the second or any later sheet. This property defaults
to 1 meaning the first sheet.

Fixed data
----------

Fixed data reserve a certain number of characters per field. No delimiters are
necessary.

Example for fixed data format

==  ==================  ==========
..  Property            Value
==  ==================  ==========
F   Format              Fixed
F   Encoding            ISO-8859-1
F   Line delimiter      LF
F   Allowed characters  0:
==  ==================  ==========

ODS data (open document spreadsheet)
------------------------------------

The Open Document Spreadsheet (ODS) file format is supported by several
application, for instance OpenOffice.org's Calc.

Minimal example for ODS data

==  ========  =====
..  Property  Value
==  ========  =====
F   Format    ODS
==  ========  =====

The properties header and sheet have the same meaning as described in
:ref:`format-excel`.

A more advanced example for ODS data

==  ========  =====
..  Property  Value
==  ========  =====
F   Format    ODS
F   Header    2
F   Sheet     5
==  ========  =====

Field formats
=============

This section describes the different field formats.

Overview
--------

The field format section of the ICD contains rows with the following columns:

* The letter "F" to indicate that the remaining columns describe a field
  format.
      
* The name of the field. It must start with an ASCII letter and continue with
  letters, numbers and underscores (_), for example
  ``customer_id``.

* An optional example value for the field. This is for documentation purpose
  only and can be omitted for fields where there is no meaningful example (such
  as a field containing a BLOB). In case a value is specified though, it must
  be a valid example conforming to all the rules for this field.

* The type of the field, for example ``Text``, ``Integer``, ``DateTime`` and
  others. Refer to the sections below for detailed descriptions of these types.

* A flag that indicates if the field is allowed to be empty.  "X" means that
  the field can be empty, no text means that the field always must contain at
  least some data.

* The length of the field in characters.  For separated formats, this is
  optional and takes the form ``lower_limit``:``upper_limit``.  For example,
  ``10:20`` means that values in this field must contains at least 10
  characters and at most 20. It is also possible to specify only a lower or
  upper limit, for example ``10:`` means at least 10 characters ans ``:20``
  means at least 20 characters.  Furthermore the length can be a single number
  with any colon (:), meaning that the length must match this number exactly.
  For fixed formats, this column takes a number that specifies the exact length
  of the field, for example ``50``.

* A rule depending on the type further describing the field.  For example, a
  field of type DateTime requires an exact date or time format such as
  DD.MM.YYYY.

* The remaining columns are not parsed by cutplace and can contain any text you
  like, for example a description of the meaning of the field or details about
  from where the data originate.

Simple examples for various field formats

==  =============  ==========  ========  ======  ==========  ====
..  Name           Example     Type      Empty   Length      Rule
==  =============  ==========  ========  ======  ==========  ====
F   customer_id    123456      Integer           1:999999
F   surname        Miller      Text              1:60
F   date_of_birth  1969-11-03  DateTime  X       YYYY-MM-DD
==  =============  ==========  ========  ======  ==========  ====

Text
----

The Text type describes a field that can contain any letters, digits and other
characters.

Examples for Text fields

==  =======  =======  ====  =====  ======  ====
..  Name     Example  Type  Empty  Length  Rule
==  =======  =======  ====  =====  ======  ====
F   surname  Miller   Text         1..60 
==  =======  =======  ====  =====  ======  ====

Integer
-------

The Integer type describes a field that can contain decimal numbers without any
fractional part.

Examples for Integer fields

==  ======  =======  =======  =====  ======  =======
..  Name    Example  Type     Empty  Length  Rule
==  ======  =======  =======  =====  ======  =======
F   height  3798     Integer         0:8848
F   weight  72       Integer         0:      0:
F   id      1337     Integer         5       1:99999
==  ======  =======  =======  =====  ======  =======

Choice
------

The Choice type describes a field that can contain on value out of a set of
possibly values.

Examples for Choice fields

==  ==========  =======  ======  =====  ======  ========================================
..  Name        Example  Type    Empty  Length  Rule
==  ==========  =======  ======  =====  ======  ========================================
F   color       red      Choice                 red, green, blue
F   iso_gender  male     Choice                 male, female, unknown, other
F   department  sales    Choice                 accounting, development, sales, shipping
==  ==========  =======  ======  =====  ======  ========================================

DateTime
--------

The DateTime type describes a field that can contain a date and/or time in a
specified format.

To describe a date, use the following place holders:

* DD: the day (a number between 1 and 31)

* MM: the numeric month (a number between 1 and 12)

* YYYY: the year including the century (a number between 1 and 9999)

* YY: the year without century

To describe a time, use the following place holders:

* hh: hours (a number between 0 and 23)

* mm: minutes (a number between 0 and 59)

* ss: seconds, a number between 0 and 61; note that 60 and 61 are valid values
  because of possible leap seconds.

Leading zeros are ignored. Any other characters will be interpreted as
separators and have to appear in the data as specified.

Examples for DateTime fields

==  ===============  ==========  ========  =====  ======  ==========
..  Name             Example     Type      Empty  Length  Rule
==  ===============  ==========  ========  =====  ======  ==========
F   date_of_birth    1969-11-03  DateTime                 YYYY-MM-DD
F   time_of_arrival  17:23       DateTime                 hh:mm
==  ===============  ==========  ========  =====  ======  ==========

Pattern
-------

The Pattern type is similar to the Text type but additionally allows to use
special characters as place holders:

* "?" mean "exactly 1 character".

* "*" means "none or any characters"

Examples for Pattern fields

==  ============  =======  =====  ======  ============
..  Name          Type     Empty  Length  Rule
==  ============  =======  =====  ======  ============
F   dos_filename  Pattern         1:12    ?*.*
F   branch_id     Pattern                 B???-????-?*
==  ============  =======  =====  ======  ============

RegEx
-----

The RegEx type is similar to the Pattern type but allows more sophisticated
place holders by describing a regular expression. The syntax available is
described in the chapter on "Regular expression operations" of the Python
documentation, available from http://docs.python.org/library/re.html.

Examples for RegEx fields

==  =====  ================  =====  =====  ======  ================================================
..  Name   Example           Type   Empty  Length  Rule
==  =====  ================  =====  =====  ======  ================================================
F   email  some@example.com  RegEx                 ^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}$ [#fn1]_
==  =====  ================  =====  =====  ======  ================================================

Checks
======

Checks are rules that cannot be expressed easily with the rules available for
data formats and field formats. In general checks validate conditions that can
be only be met by looking at several fields in a row or the whole document. In
the ICD, a row describing the check requires the following columns:

1.  A human readable description of the check that will be used in the error
    message in case the check fails. Most of the time this will be a short
    sentence of the template "something must/have something". For instance,
    "``customer must be unique``".

2.  The type of the check as described in one of the sections below, for
    example ``DistinctCount`` or ``IsUnique``.

3.  A rule describing the actual check to perform. The contents of this field
    highly depend on the check type specified in the previous column. For
    example, the IsUnique check requires the field(s) to be checked for
    uniqueness like "``branch_id, customer_id``"

The remainder of this section describes the available checks in detail and
gives specific examples.

DistinctCount
-------------

Purpose: Validate that the number of different values for a certain field is
within expected limits.

The rule column describes the field to check and the limit is must meet.
Example check for a limited number of different values within a field shows how
to make sure that the data contain at most 5 different branch_ids.

Example check for a limited number of different values within a field.

==  ======================================  =============  =============
..  Description                             Type           Rule
==  ======================================  =============  =============
C   distinct branches must be within limit  DistinctCount  branch_id < 5
==  ======================================  =============  =============

To describe the rule you can use any comparison operator or mathematical
expression available to the Python language.

IsUnique
--------

Purpose: Validate that values for a field or a combination of fields occurs
only once. This enables to detect duplicate or contradicting data.

The "Rule" column describes the field that must contain only unique values.
Example check for unique values within a single field shows how to specify that
two customers must not have the same ID numbers.

Example check for unique values within a single field.

==  =======================  ========  ===========
..  Description              Type      Rule
==  =======================  ========  ===========
C   customer must be unique  IsUnique  customer_id
==  =======================  ========  ===========

It could also be possible that customers actually may have the same ID number
as long as they are assigned to different branches. In this case, only the
combination of branch_id and customer_id must be unique.  Example check for
unique values within a combination of fields shows how to describe a check for
this: simply list all the necessary fields, separated by a comma (,) sign.

Example check for unique values within a combination of fields.

==  =======================  ========  ======================
..  Description              Type      Rule
==  =======================  ========  ======================
C   customer must be unique  IsUnique  branch_id, customer_id
==  =======================  ========  ======================

Comments
========

Comments can show up in the ICD at any line or column cutplace does not parse.
In particular this constitutes:

* Lines that have an empty first column. Remember that a D means details about
  the data format, F about the field format and C describes checks.

* Columns that are past the columns needed by cutplace. For example, in a line
  describing a data format property, cutplace parses only the first three (D,
  Property name, value). Because of that you can write any text starting with
  column number 4.

.. _ranges:

Ranges
======

At several locations in the ICD you can specify ranges. For example as value
for the "Allowed characters" property of a data format or as length of a field
format. Example ranges shows a couple of examples for ranges and explains their
meaning.

Example ranges.

============  =======================================================================================================================================
Example       Description
============  =======================================================================================================================================
5:20          Between 5 and 20
6:            At least 6
:7            At most 7. Sample accepted values are -5, 0, 4 or 7.  Sample rejected values would be 8, 17, or 723.
8             Exactly 8, which is the only accepted value. Anything else is rejected.
2, 4, 6, 8    One of the values specified, meaning 2, 4, 6 or 8.  Anything else is rejected, including 3, 5 and 7.
20:30, 40:50  Everything between 20 and 30 or between 40 and 50. Sample accepted values are 20, 27, 43 and 50. Sample rejected values are 19, 31, 55.
============  =======================================================================================================================================

Essentially ranges are one or more values (separated by a comma (,)) that are
either numeric constant or a lower and upper limit separated by a colon (:).
You can omit the lower or upper limit, in which case cutplace will use a
sensible default depending on the context. For instance, a length of ``:20``
will use 0 as lower limit, whereas a field format of type ``Integer`` with a
rule of ``:20`` will use the largest negative number possible on your computer
(which depends on the amount of memory available).

.. rubric:: Footnotes

.. [#fn1] Validate that field value is an email address as described in `how to find or validate an email address <http://www.regular-expressions.info/email.html>`_