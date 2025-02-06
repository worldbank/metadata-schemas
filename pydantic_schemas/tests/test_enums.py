from typing import List, Optional

import pytest
from pydantic import BaseModel

from ..utils.enum_with_value_or_key import EnumWithValueOrKey


def test_enum_with_value_or_key():
    class IndicatorType(EnumWithValueOrKey):
        Concept = "concept"
        Disaggregation = "disaggregation"
        Derivation = "derivation"

    # This will work
    assert IndicatorType("concept") == IndicatorType.Concept
    assert IndicatorType("Concept") == IndicatorType.Concept

    # This will raise a ValidationError
    with pytest.raises(ValueError):
        IndicatorType("Invalid")


def test_pydantic_with_enum():
    class IndicatorType(EnumWithValueOrKey):
        Concept = "concept"
        Disaggregation = "disaggregation"
        Derivation = "derivation"

    class Indicator(BaseModel):
        type: IndicatorType

    indicator = Indicator(type="concept")
    assert indicator.type == IndicatorType.Concept

    indicator = Indicator(type="Concept")
    assert indicator.type == IndicatorType.Concept

    with pytest.raises(ValueError):
        Indicator(type="Invalid")

    # now with optional type
    class Indicator(BaseModel):
        type: Optional[IndicatorType] = None

    indicator = Indicator(type="concept")
    assert indicator.type == IndicatorType.Concept

    indicator = Indicator(type="Concept")
    assert indicator.type == IndicatorType.Concept

    with pytest.raises(ValueError):
        Indicator(type="Invalid")

    Indicator.model_validate({"type": "concept"})
    Indicator.model_validate({"type": "Concept"})

    # now with a list of types
    class Indicator(BaseModel):
        types: List[IndicatorType]

    indicator = Indicator(types=["concept", "disaggregation"])
    assert indicator.types == [IndicatorType.Concept, IndicatorType.Disaggregation]

    indicator = Indicator(types=["Concept", "Disaggregation"])
    assert indicator.types == [IndicatorType.Concept, IndicatorType.Disaggregation]

    with pytest.raises(ValueError):
        Indicator(types=["Invalid"])

    with pytest.raises(ValueError):
        Indicator(types=["Concept", "Invalid"])

    Indicator.model_validate({"types": ["concept", "Disaggregation"]})

    # now with optional list of types
    class Indicator(BaseModel):
        types: Optional[List[IndicatorType]] = None

    indicator = Indicator()
    assert indicator.types is None

    indicator = Indicator(types=[])
    assert indicator.types == []

    indicator = Indicator(types=["concept", "disaggregation"])
    assert indicator.types == [IndicatorType.Concept, IndicatorType.Disaggregation]

    indicator = Indicator(types=["Concept", "Disaggregation"])
    assert indicator.types == [IndicatorType.Concept, IndicatorType.Disaggregation]

    with pytest.raises(ValueError):
        Indicator(types=["Invalid"])

    Indicator.model_validate({"types": ["concept", "Disaggregation"]})

    # now where the enum is a subfield
    class Indicator(BaseModel):
        type: IndicatorType

    class Parent(BaseModel):
        indicator: Indicator

    parent = Parent(indicator={"type": "concept"})
    assert parent.indicator.type == IndicatorType.Concept

    parent = Parent(indicator={"type": "Concept"})
    assert parent.indicator.type == IndicatorType.Concept

    with pytest.raises(ValueError):
        Parent(indicator={"type": "Invalid"})

    Parent.model_validate({"indicator": {"type": "concept"}})


def test_mixed_types():
    class IndicatorType(EnumWithValueOrKey):
        One = 1
        Two = 2

    IndicatorType(1)
    IndicatorType(2)

    IndicatorType("One")
    IndicatorType("Two")

    with pytest.raises(ValueError):
        IndicatorType(3)

    with pytest.raises(ValueError):
        IndicatorType("Three")

    class Indicator(BaseModel):
        type: IndicatorType

    indicator = Indicator(type=1)
    assert indicator.type == IndicatorType.One

    indicator = Indicator(type=2)
    assert indicator.type == IndicatorType.Two

    indicator = Indicator(type="One")
    assert indicator.type == IndicatorType.One

    indicator = Indicator(type="Two")
    assert indicator.type == IndicatorType.Two

    with pytest.raises(ValueError):
        Indicator(type=3)

    with pytest.raises(ValueError):
        Indicator(type="Three")
