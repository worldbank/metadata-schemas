import random
import string

from pydantic import BaseModel, ValidationError
from pydantic_core import Url


# Function to generate a random 4-character string
def random_string(length=4):
    return "".join(random.choices(string.ascii_letters, k=length))


# Recursive function to traverse and replace Nones or empty strings
def fill_in_pydantic_outline(model: BaseModel, debug=False):
    assert isinstance(model, BaseModel), model
    for field_name, field_value in model.__dict__.items():
        if debug:
            print(f"filling in {field_name} starting with {field_value}")
        if field_value is None or field_value == "":
            try:
                show = field_value is not None or random.random() < 0.7
                setattr(model, field_name, random_string() if show else None)
                if debug:
                    print(f"filled in {field_name} with {getattr(model, field_name)}")
            except ValidationError:
                continue
        elif isinstance(field_value, BaseModel):
            fill_in_pydantic_outline(field_value)
        elif isinstance(field_value, dict):
            for item in field_value.values():
                if isinstance(item, BaseModel):
                    fill_in_pydantic_outline(item)
        elif isinstance(field_value, list):
            if debug:
                print("found list")
            n_elements = random.choices([1, 4, 8])[0]

            if len(field_value) == 0:
                non_null_values = [random.random() < 0.7 for _ in range(n_elements)]
                if not any(non_null_values):
                    setattr(
                        model,
                        field_name,
                        [],
                    )
                try:
                    setattr(
                        model, field_name, [random_string() if non_null_values[i] else None for i in range(n_elements)]
                    )
                except ValidationError:
                    setattr(
                        model,
                        field_name,
                        [],
                    )
            elif isinstance(field_value[0], BaseModel):
                if debug:
                    print("found list of basemodels")
                try:
                    # make a deep copy of the skeleton pydantic object
                    new_vals = [field_value[0].model_copy(deep=True) for i in range(n_elements)]
                    if debug:
                        print(f"new_vals: {new_vals}")
                    for i in range(n_elements):
                        fill_in_pydantic_outline(new_vals[i])
                    if debug:
                        print(f"new_vals filled: {new_vals}")
                    # ignore list item if every value in the item is None or default
                    new_vals = [v for v in new_vals if is_empty(v) == False]
                    if debug:
                        print(f"new_vals filtered: {new_vals}")
                    setattr(
                        model,
                        field_name,
                        new_vals,
                    )
                    if len(new_vals) == 0:
                        assert (
                            getattr(model, field_name) == []
                        ), f"{field_name}, {new_vals}, {getattr(model, field_name)}"
                    assert getattr(model, field_name) != [[]], f"{field_name}, {new_vals}, {getattr(model, field_name)}"
                except ValidationError as e:
                    raise ValueError(f"{field_name}, {new_vals}") from e
            else:
                raise NotImplementedError(
                    f"fill_in_pydantic_outline list type not implemented for {field_name}: {field_value}"
                )
        elif isinstance(field_value, Url):
            continue
        else:
            raise NotImplementedError(
                f"fill_in_pydantic_outline not implemented for {field_name}: {field_value} of type {type(field_value)} from {model}"
            )


def is_empty(m):
    if isinstance(m, str):
        return m == ""
    if isinstance(m, BaseModel):
        iterabl = [v for _, v in m.model_dump().items()]
    elif isinstance(m, dict):
        if len(m) == 0:
            return True
        iterabl = [v for _, v in m.items()]
    elif isinstance(m, list):
        if len(m) == 0:
            return True
        iterabl = m
    else:
        return m is None

    for v in iterabl:
        if isinstance(v, (dict, BaseModel, list, str)):
            if is_empty(v) == False:
                return False
        elif v is not None:
            return False
    return True


# Recursive function to compare two Pydantic models
def assert_pydantic_models_equal(model1: BaseModel, model2: BaseModel) -> bool:
    # First, check if the two models are of the same type
    assert type(model1) == type(model2), f"{type(model1)}, {type(model2)}"

    if not hasattr(model1, "model_fields"):
        assert model1 == model2, f"{model1}, {model2}"

    # Traverse through the fields of the model
    for field_name in model1.model_fields:
        value1 = getattr(model1, field_name)
        value2 = getattr(model2, field_name)

        if value1 is None and value2 is None:
            continue

        # distinction without a difference
        if value1 is None and value2 == "":
            continue
        if value1 == "" and value2 is None:
            continue

        # If values are different, return False
        if value1 != value2:
            if isinstance(value1, str) and isinstance(value2, str):
                # sometimes new line is \r\n and sometimes \n but this is not a real difference
                normalize_newlines = lambda s: "\n".join(s.splitlines())
                assert normalize_newlines(value1).lower().replace("null", "") == normalize_newlines(
                    value2
                ).lower().replace("null", ""), field_name
            # If both are BaseModel instances, compare recursively
            elif isinstance(value1, BaseModel) and isinstance(value2, BaseModel):
                assert_pydantic_models_equal(value1, value2)
                # assert False, field_name
            # If both are lists, compare their elements
            elif isinstance(value1, list) or isinstance(value2, list):
                if value1 is None:
                    value1 = []
                else:
                    value1 = [v for v in value1 if is_empty(v) == False]
                if value2 is None:
                    value2 = []
                else:
                    value2 = [v for v in value2 if is_empty(v) == False]
                # remove empty basemodels

                assert len(value1) == len(value2), f"{field_name} mismatched len, {value1}, {value2}"
                for v1, v2 in zip(value1, value2):
                    if isinstance(v1, BaseModel) and isinstance(v2, BaseModel):
                        assert_pydantic_models_equal(v1, v2)
                    else:
                        assert v1 == v2, field_name
            elif isinstance(value1, dict) and isinstance(value2, dict):
                assert value1.keys() == value2.keys(), f"{field_name} mismatched keys, {value1.keys()}, {value2.keys()}"
                for key in value1:
                    if isinstance(value1[key], BaseModel) and isinstance(value2[key], BaseModel):
                        assert_pydantic_models_equal(value1[key], value2[key])
                    else:
                        assert value1[key] == value2[key], field_name
            else:
                assert value1 == value2, field_name  # For other types, if they are not equal, return False

    return True  # All fields are equal
