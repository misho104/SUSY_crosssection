"""Classes to describe annotations of general-purpose tables.

This module provides annotation classes for CSV-like table data. The data is a
two-dimensional table and represents functions over a parameter space. Some
columns represent parameters and others do values. Each row represents a single
data point and corresponding value.

Two structural annotations and two semantic annotations are defined.
`TableInfo` and `ColumnInfo` are structural, which respectively annotate the
whole table and each columns. For semantics, `ParameterInfo` collects the
information of parameters, each of which is a column, and `ValueInfo` is for a
value. A value may be given by multiple columns if, for example, the value has
uncertainties or the value is given by the average of two columns.
"""

from __future__ import absolute_import, division, print_function  # py2

import itertools
import json
import logging
import pathlib  # noqa: F401
import sys
from typing import Any, Dict, List, Mapping, MutableMapping, Optional, Sequence, Union

if sys.version_info[0] < 3:  # py2
    str = basestring  # noqa: A001, F821
    JSONDecodeError = Exception
else:
    JSONDecodeError = json.decoder.JSONDecodeError


logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


class ColumnInfo(object):
    """Stores information of a column.

    Instead of the :typ:`int` identifier `!index`, we use `!name` as the
    principal identifier for readability. We also annotate a column by `!unit`,
    which is :typ:`str` that is passed to `Unit()`.

    Attributes
    ----------
    index : int
        The zero-based index of column.

        The columns of a table should have valid `!index`, i.e., no overlap, no
        gap, and starting from zero.
    name : str
        The human-readable and machine-readable name of the column.

        As it is used as the identifier, it should be unique in one table.
    unit : str
        The unit of column, or empty string if the column has no unit.

        The default value is an empty str ``''``, which means the column has no
        unit. Internally this is passed to `Unit()`.

    Note
    ----
    As for now, `!unit` is restricted as a str object, but in future a float
    should be allowed to describe "x1000" etc.
    """

    def __init__(self, index, name, unit=""):
        # type: (int, str, str)->None
        self.index = index  # type: int
        self.name = name  # type: str
        self.unit = unit or ""  # type: str

    @classmethod
    def from_json(cls, json_obj):
        # type: (Any)->ColumnInfo
        """Initialize an instance from valid json data.

        Parameters
        ----------
        json_obj: Any
            a valid json object.

        Returns
        -------
        ColumnInfo
            Constructed instance.

        Raises
        ------
        ValueError
            If :ar:`json_obj` has invalid data.
        """
        try:
            obj = cls(
                index=json_obj["index"],
                name=json_obj["name"],
                unit=json_obj.get("unit", ""),
            )
        except (TypeError, AttributeError) as e:
            logger.error("ColumnInfo.from_json: %s", e)
            raise ValueError("Invalid data passed to ColumnInfo.from_json: %s")
        except KeyError as e:
            logger.error("ColumnInfo.from_json: %s", e)
            raise ValueError("ColumnInfo data missing: %s", e)

        for k in json_obj.keys():
            if k not in ["index", "name", "unit"]:
                logger.warn("Unknown data for ColumnInfo.from_json: %s", k)

        obj.validate()
        return obj

    def to_json(self):
        # type: ()->MutableMapping[str, Union[str, int]]
        """Serialize the object to a json data.

        Returns
        -------
        dict(str, str or int)
            The json data describing the object.
        """
        json_obj = {
            "index": self.index,
            "name": self.name,
        }  # type: MutableMapping[str, Union[str, int]]
        if self.unit:
            json_obj["unit"] = self.unit
        return json_obj

    def validate(self):
        # type: ()->None
        """Validate the content.

        Raises
        ------
        TypeError
            If any attributes are invalid type of instance.
        ValueError
            If any attributes have invalid content.
        """
        if not isinstance(self.index, int):
            raise TypeError("ColumnInfo.index must be int: %s", self.index)
        if not self.index >= 0:
            raise ValueError("ColumnInfo.index must be non-negative: %s", self.index)
        if not isinstance(self.name, str):
            raise TypeError("Col %d: `name` must be string: %s", self.index, self.name)
        if not self.name:
            raise ValueError("Column %d: `name` missing", self.index)
        if not isinstance(self.unit, str):
            raise TypeError("Col %d: `unit` must be string: %s", self.index, self.unit)


class ParameterInfo(object):
    """Stores information of a parameter.

    A parameter set defines a data point for the functions described by the
    table. A parameter set has one or more parameters, each of which
    corresponds to a column of the table. The `!column` attribute has
    :attr:`ColumnInfo.name` of the column.

    Since the parameter value is read from an ASCII file, :typ:`float` values
    might have round-off errors, which might cause grid misalignments in grid-
    based interpolations. To have the same :typ:`float` expression on the
    numbers that should be on the same grid, `!granularity` should be provided.

    Attributes
    ----------
    column: str
        Name of the column that stores this parameter.
    granularity: int or float, optional
        Assumed presicion of the parameter.

        This is used to round the parameter so that a data point should be
        exactly on the grid. Internally, a parameter is rounded to::

            round(value / granularity) * granularity

        For example, for a grid ``[10, 20, 30, 50, 70]``, it should be set to
        10 (or 5, 1, 0.1, etc.), while for ``[33.3, 50, 90]``, it should be
        0.01.
    """

    def __init__(self, column="", granularity=None):
        # type: (str, float)->None
        self.column = column  # type: str
        self.granularity = granularity or None  # type: Optional[float]

    @classmethod
    def from_json(cls, json_obj):
        # type: (Any)->ParameterInfo
        """Initialize an instance from valid json data.

        Parameters
        ----------
        json_obj: Any
            a valid json object.

        Returns
        -------
        ParameterInfo
            Constructed instance.

        Raises
        ------
        ValueError
            If :ar:`json_obj` has invalid data.
        """
        try:
            obj = cls(
                column=json_obj["column"], granularity=json_obj.get("granularity")
            )
        except (TypeError, AttributeError) as e:
            logger.error("ParameterInfo.from_json: %s", e)
            raise ValueError("Invalid data passed to ParameterInfo.from_json: %s")
        except KeyError as e:
            logger.error("ParameterInfo.from_json: %s", e)
            raise ValueError("ColumnInfo data missing: %s", e)

        for k in json_obj.keys():
            if k not in ["column", "granularity"]:
                logger.warn("Unknown data for ParameterInfo.from_json: %s", k)

        obj.validate()
        return obj

    def to_json(self):
        # type: ()->MutableMapping[str, Union[str, float]]
        """Serialize the object to a json data.

        Returns
        -------
        dict(str, str or float)
            The json data describing the object.
        """
        json_obj = {"column": self.column}  # type: Dict[str, Union[str, float]]
        if self.granularity:
            json_obj["granularity"] = self.granularity
        return json_obj

    def validate(self):
        # type: ()->None
        """Validate the content.

        Raises
        ------
        TypeError
            If any attributes are invalid type of instance.
        ValueError
            If any attributes have invalid content.
        """
        if not isinstance(self.column, str):
            raise TypeError("ParameterInfo.column must be string: %s", self.column)
        if not self.column:
            raise ValueError("ParameterInfo.column is missing")
        if self.granularity is not None:
            try:
                if not float(self.granularity) > 0:
                    raise ValueError(
                        "ParameterInfo.granularity is not positive: %s",
                        self.granularity,
                    )
            except TypeError:
                raise TypeError(
                    "ParameterInfo.granularity is not a number: %s", self.granularity
                )


class ValueInfo(object):
    """Stores information of value accompanied by uncertainties.

    A value is generally composed from several columns. In current
    implementation, the central value must be given by one column, whose name
    is specified by :attr:`column`. The positive- and negative-direction
    uncertainties are specified by `!unc_p` and `!unc_m`, respectively, which
    are :typ:`dict(str, str)`.

    Attributes
    ----------
    column: str
        Name of the column that stores this value.

        This must be match one of the :attr:`ColumnInfo.name` in the table.
    unc_p : dict (str, str)
        The sources of "plus" uncertainties.

        Multiple uncertainty sources can be specified. Each key corresponds
        :attr:`ColumnInfo.name` of the source column, and each value denotes
        the "type" of the source. Currently, two types are implementend:

        - ``"relative"`` for relative uncertainty, where the unit of the column
          must be dimension-less.

        - ``"absolute"`` for absolute uncertainty, where the unit of the column
          must be the same as that of the value column up to a factor.

        The unit of the uncertainty column should be consistent with the unit
        of the value column.
    unc_m : dict(str, str)
        The sources of "minus" uncertainties.

        Details are the same as `!unc_p`.
    """

    _valid_uncertainty_types = ["relative", "absolute"]  # type: List[str]

    def __init__(self, column="", unc_p=None, unc_m=None, **kw):
        # type: (str, MutableMapping[str, str], MutableMapping[str, str], Any)->None
        self.column = column
        self.unc_p = unc_p or {}  # type: MutableMapping[str, str]
        self.unc_m = unc_m or {}  # type: MutableMapping[str, str]

    def validate(self):
        # type: ()->None
        """Validate the content."""
        if not isinstance(self.column, str):
            raise TypeError("ValueInfo.column must be string: %s", self.column)
        if not self.column:
            raise ValueError("ValueInfo.column is missing")
        for title, unc in [("unc+", self.unc_p), ("unc-", self.unc_m)]:
            if not isinstance(unc, MutableMapping):
                raise TypeError("Value %s: %s must be dict", self.column, title)
            for k, v in unc.items():
                if not isinstance(k, str):
                    raise TypeError(
                        "Value %s: %s has invalid column name: %s",
                        self.column,
                        title,
                        k,
                    )
                if v not in self._valid_uncertainty_types:
                    raise ValueError(
                        "Value %s: %s has wrong value: %s", self.column, title, v
                    )

    @classmethod
    def from_json(cls, json_obj):
        # type: (Any)->ValueInfo
        """Initialize an instance from valid json data.

        Parameters
        ----------
        json_obj: typing.Any
            a valid json object.

        Returns
        -------
        ValueInfo
            Constructed instance.

        Raises
        ------
        ValueError
            If :ar:`json_obj` has invalid data.
        """
        if not isinstance(json_obj, Mapping):
            raise TypeError('Entry of "values" must be a dict: %s', json_obj)
        if "column" not in json_obj:
            raise KeyError('Entry of "values" must have a key "column": %s', json_obj)

        obj = cls()
        obj.column = json_obj["column"]
        if ("unc" in json_obj) and ("unc+" in json_obj or "unc-" in json_obj):
            raise ValueError("Uncertainty duplicates: %s", obj.column)
        for attr_name, key_name in [("unc_p", "unc+"), ("unc_m", "unc-")]:
            unc_def = json_obj.get(key_name) or json_obj.get("unc") or None
            if unc_def is None:
                logger.warning("Uncertainty (%s) missing for %s.", key_name, obj.column)
                continue
            if not (
                isinstance(unc_def, Sequence)
                and all(isinstance(source, Mapping) for source in unc_def)
            ):
                raise TypeError("%s (%s) is not a list of dicts.", key_name, obj.column)
            try:
                unc_dict = {source["column"]: source["type"] for source in unc_def}
                setattr(obj, attr_name, unc_dict)
            except KeyError as e:
                raise ValueError("%s missing in %s (%s)", key_name, obj.column, *e.args)

        if not (obj.unc_p and obj.unc_m):
            logger.warning("Value %s lacks uncertainties.", obj.column)

        return obj

    def to_json(self):
        # type: ()->MutableMapping[str, Union[str, List[MutableMapping[str, str]]]]
        """Serialize the object to a json data.

        Returns
        -------
        dict(str, str or float)
            The json data describing the object.
        """
        return {
            "column": self.column,
            "unc+": [{"column": k, "type": v} for k, v in self.unc_p.items()],
            "unc-": [{"column": k, "type": v} for k, v in self.unc_m.items()],
        }


class TableInfo(object):
    """Stores table-wide annotations for general-purpose table data.

    A table structure is given by `!columns`, while in semantics a table
    consists of `!parameters` and `!values`. The information about them is
    stored as lists of `ColumnInfo`, `ParameterInfo`, and `ValueInfo` objects.
    In addition, `!reader_options` can be specified, which is directly passed
    to :func:`pandas.read_csv`.

    The attribute `!document` is provided just for documentation. The
    information is guaranteed not to modify any functionality of codes or
    packages, and thus can be anything.

    Developers must not use `!document` information except for displaying them.
    If one needs to interpret some information, one should extend this class to
    provide other data-storage for such information, as is done in
    `CrossSectionInfo` class.

    Attributes
    ----------
    document : dict(Any, Any)
        Any information for documentation without physical meanings. meanings.
    columns : list of ColumnInfo
        The list of columns.
    parameters: list of ParameterInfo
        The list of parameters to define a data point.
    values: list of ValueInfo
        The list of values described in the table.
    reader_options: dict(str, Any)
        Options to read the CSV

        The values are directly passed to :func:`pandas.read_csv` as keyword
        arguments, so all the options of :func:`pandas.read_csv` are available.
    """

    def __init__(
        self,
        document=None,  # type: Mapping[Any, Any]
        columns=None,  # type: List[ColumnInfo]
        parameters=None,  # type: List[ParameterInfo]
        values=None,  # type: List[ValueInfo]
        reader_options=None,  # type: Mapping[str, Any]
    ):
        # type: (...)->None
        self.document = document or {}
        self.columns = columns or []
        self.parameters = parameters or []
        self.values = values or []
        self.reader_options = reader_options or {}

    def validate(self):  # noqa: C901
        # type: ()->None
        """Validate the content."""
        if not isinstance(self.document, MutableMapping):
            raise TypeError("document must be a dict.")
        for name in ["columns", "parameters", "values"]:
            if not isinstance(getattr(self, name), List):
                raise TypeError("TableInfo.%s must be a list", name)
            for obj in getattr(self, name):
                obj.validate()
        if not isinstance(self.reader_options, MutableMapping):
            raise TypeError("reader_options must be a dict(str, Any).")
        if not all(isinstance(k, str) for k in self.reader_options.keys()):
            raise TypeError("reader_options must be a dict(str, Any).")

        # validate columns (`index` matches actual index, names are unique)
        names_dict = {}  # type: MutableMapping[str, bool]
        for i, column in enumerate(self.columns):
            if column.index != i:
                raise ValueError("Mismatched column index: %d has %d", i, column.index)
            if names_dict.get(column.name):
                raise ValueError("Duplicated column name: %s", column.name)
            names_dict[column.name] = True

        # validate params and values
        for p in self.parameters:
            if p.column not in names_dict:
                raise ValueError("Unknown column name: %s", p.column)
        for v in self.values:
            for col in itertools.chain([v.column], v.unc_p.keys(), v.unc_m.keys()):
                if col not in names_dict:
                    raise ValueError("Unknown column name: %s", v.column)

    @classmethod
    def load(cls, source):
        # type: (Union[pathlib.Path, str])->TableInfo
        """Load and construct TableInfo from a json file.

        Parameters
        ----------
        source: pathlib.Path or str
            Path to the json file.

        Returns
        -------
        TableInfo
            Constructed instance.
        """
        obj = cls()
        with open(source.__str__()) as f:  # py2
            obj._load(**(json.load(f)))
        obj.validate()
        return obj

    def _load(self, **kw):
        # type: (Any)->None
        """Load and construct TableInfo from keyword arguments."""
        self.document = kw.get("document") or {}
        self.columns = [
            ColumnInfo(index=i, name=c.get("name"), unit=c.get("unit"))
            for i, c in enumerate(kw.get("columns") or [])
        ]
        self.parameters = [
            ParameterInfo.from_json(p) for p in kw.get("parameters") or []
        ]
        self.values = [ValueInfo.from_json(p) for p in kw.get("values") or []]
        self.reader_options = kw.get("reader_options") or {}

        # emit warnings
        if not self.document:
            logger.warning("No document is given.")
        for key in kw:
            if key not in [
                "document",
                "columns",
                "parameters",
                "values",
                "reader_options",
            ]:
                logger.warning('Unrecognized attribute "%s"', key)

    def get_column(self, name):
        # type: (str)->ColumnInfo
        """Return a column with specified name.

        Return `ColumnInfo` of a column with name :ar:`name`.

        Arguments
        ---------
        name
            The name of column to get.

        Returns
        -------
        ColumnInfo
            The column with name :ar:`name`.

        Raises
        ------
        KeyError
            If no column is found.
        """
        for c in self.columns:
            if c.name == name:
                return c
        raise KeyError(name)

    def dump(self):
        # type: ()->str
        """Return the formatted string.

        Returns
        -------
        str
            Dumped data.
        """
        results = ["[Document]"]
        for k, v in self.document.items():
            results.append("  {}: {}".format(k, v))
        return "\n".join(results)
