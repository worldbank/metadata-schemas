from enum import Enum
from typing import Any, Dict, List, Optional, Union

import pytest
from pydantic import BaseModel

from ..quick_start import create_empty_schema_from_path, make_skeleton, metadata_types_file_map


def test_simple_strings():
    class Simple(BaseModel):
        a: str
        b: str

    expected = Simple(a="", b="")
    actual = make_skeleton(Simple)
    assert expected == actual


def test_simple_optional_string():
    class SimpleOptional(BaseModel):
        a: Optional[str]
        b: str

    expected = SimpleOptional(a=None, b="")
    actual = make_skeleton(SimpleOptional)
    assert expected == actual, actual


def test_simple_enum():
    class Color(Enum):
        RED = 1
        GREEN = 2
        BLUE = 3

    class SimpleEnum(BaseModel):
        a: Color

    expected = SimpleEnum(a=Color.RED)
    actual = make_skeleton(SimpleEnum)
    assert actual == expected, actual


def test_optional_enum():
    class Color(Enum):
        RED = 1
        GREEN = 2
        BLUE = 3

    class SimpleEnum(BaseModel):
        a: Optional[Color] = None

    expected = SimpleEnum(a=None)
    actual = make_skeleton(SimpleEnum)
    assert actual == expected, actual


def test_one_level():
    class Simple(BaseModel):
        a: str
        b: str

    class OneLevel(BaseModel):
        c: Simple

    expected = OneLevel(c=Simple(a="", b=""))
    actual = make_skeleton(OneLevel)
    assert actual == expected


def test_one_level_optional():
    class Simple(BaseModel):
        a: str
        b: str

    class OneLevel(BaseModel):
        c: Optional[Simple]

    expected = OneLevel(c=Simple(a="", b=""))
    actual = make_skeleton(OneLevel)
    assert actual == expected, actual


def test_two_levels():
    class Simple(BaseModel):
        a: str
        b: str

    class OneLevel(BaseModel):
        c: Optional[Simple] = None
        c1: Optional[str] = None
        c2: str

    class TwoLevel(BaseModel):
        d: OneLevel
        e: Optional[OneLevel] = None
        f: Optional[str]

    expected = TwoLevel(
        d=OneLevel(c=Simple(a="", b=""), c1=None, c2=""), e=OneLevel(c=Simple(a="", b=""), c1=None, c2=""), f=None
    )
    actual = make_skeleton(TwoLevel)
    assert actual == expected, actual


def test_list_of_builtin():
    class Simple(BaseModel):
        a: List[str]
        b: str

    expected = Simple(a=[""], b="")
    actual = make_skeleton(Simple)
    assert actual == expected, actual


def test_list_of_enum():
    class Color(Enum):
        RED = 1
        GREEN = 2
        BLUE = 3

    class Simple(BaseModel):
        a: List[Color]
        b: str

    expected = Simple(a=[Color.RED], b="")
    actual = make_skeleton(Simple)
    assert actual == expected, actual


def test_list_of_pydantic():
    class Simple(BaseModel):
        a: str
        b: str

    class OneLevel(BaseModel):
        c: List[Simple]

    expected = OneLevel(c=[Simple(a="", b="")])
    actual = make_skeleton(OneLevel)
    assert actual == expected, actual


def test_dict_of_strs():
    class Simple(BaseModel):
        a: Dict[str, str]
        b: str

    expected = Simple(a={"": ""}, b="")
    actual = make_skeleton(Simple)
    assert actual == expected, actual


def test_union_of_str_list_str():
    class Simple(BaseModel):
        a: Optional[Union[str, List[str]]] = None
        b: Any
        c: str

    expected = Simple(a=[""], b="", c="")
    actual = make_skeleton(Simple)
    assert actual == expected, actual

    class SimpleReversed(BaseModel):
        a: Optional[Union[List[str], str]] = None
        b: Any
        c: str

    expected = SimpleReversed(a=[""], b="", c="")
    actual = make_skeleton(SimpleReversed)
    assert actual == expected, actual


def test_union_of_List_Dict():
    class Simple(BaseModel):
        a: Union[Dict[str, str], List[Any]]

    expected = Simple(a={"": ""})
    actual = make_skeleton(Simple, debug=True)
    assert actual == expected, actual

    # because a dict is more complicated than a list, we should default to using the dict
    class Simple(BaseModel):
        a: Union[List[Any], Dict[str, str]]

    expected = Simple(a={"": ""})
    actual = make_skeleton(Simple, debug=True)
    assert actual == expected, actual


def test_union_of_many_builtins():
    class Simple(BaseModel):
        a: Union[int, float, str]

    expected = Simple(a="")
    actual = make_skeleton(Simple, debug=True)
    assert actual == expected, actual


@pytest.mark.parametrize("k, v", [(k, v) for k, v in metadata_types_file_map.items()])
def test_actual_schemas(k, v):
    base = "pydantic_schemas.definitions.{}"
    print(k)
    try:
        create_empty_schema_from_path(base.format(k), v)
    except TypeError as e:
        if str(e) == "To define root models, use `pydantic.RootModel` rather than a field called '__root__'":
            print("Caught the specific TypeError:", e)
        else:
            raise
