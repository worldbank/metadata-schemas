from enum import Enum


class EnumWithValueOrKey(Enum):
    """A custom Enum that allows input values to be either the key or the value.

    Users of the Metadata Editor tend to put either the key or the value of an Enum.

    For example I was seeing errors like:

    series_description.related_indicators.1.type
      Input should be 'concept', 'disaggregation' or 'derivation' [type=enum, input_value='Derivation', input_type=str]
        For further information visit https://errors.pydantic.dev/2.10/v/enum/

    This custom Enum class allows the input to be either the key or the value of the Enum.

    Example:
    ```python
    class IndicatorType(EnumWithValueOrKey):
        Concept = "concept"
        Disaggregation = "disaggregation"
        Derivation = "derivation"

    # Example usage:

    # This will work
    IndicatorType("concept")  # gives IndicatorType.Concept
    IndicatorType("Concept")  # gives IndicatorType.Concept

    # This will raise a ValidationError
    IndicatorType("Invalid")
    ```
    """

    @classmethod
    def _missing_(cls, value):
        """Handle both keys (names) and values for Enum."""
        # Check if the value is a valid key (name)
        if isinstance(value, str):
            # Try to map the string value to the Enum's key
            for item in cls:
                if item.name == value or item.value == value:  # case-insensitive check
                    return item
            raise ValueError(f"{value} is not a valid {cls.__name__}")  # Raise if input is neither key nor value
        # proceed as usual
        return super()._missing_(value)
