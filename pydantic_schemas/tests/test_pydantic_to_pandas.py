from typing import Any, Dict, List, Optional, Union

import pandas as pd
from pydantic import BaseModel, Field
from utils.pydantic_to_excel import pydantic_to_dataframe
from utils.quick_start import make_skeleton


def test_simple():
    class Simple(BaseModel):
        idno: str
        title: Optional[str] = None
        author: str

    simple_original = Simple(idno="AVal", author="CVal")

    expected = pd.DataFrame([["AVal"], [None], ["CVal"]], index=["idno", "title", "author"])
    outp = pydantic_to_dataframe(simple_original)
    actual = outp[0]
    list_indices = outp[1]
    enums = outp[2]
    assert expected.equals(actual), actual
    assert list_indices == [], list_indices
    assert enums == {}, enums


def test_simple_list():
    class Simple(BaseModel):
        idno: str
        title: str
        authors: List[str]

    simple_original = Simple(idno="AVal", title="BVal", authors=["CVal"])

    expected = pd.DataFrame([["AVal"], ["BVal"], ["CVal"]], index=["idno", "title", "authors"])
    outp = pydantic_to_dataframe(simple_original, debug=True)
    actual = outp[0]
    list_indices = outp[1]
    enums = outp[2]
    print("actual", actual)
    assert expected.equals(actual), actual
    assert list_indices == [2], list_indices
    assert enums == {}, enums

    class SimpleOptional(BaseModel):
        idno: str
        title: str
        authors: Optional[List[str]]

    simple_original_optional = SimpleOptional(idno="AVal", title="BVal", authors=None)

    expected = pd.DataFrame([["AVal"], ["BVal"], [None]], index=["idno", "title", "authors"])
    outp = pydantic_to_dataframe(simple_original_optional)
    actual = outp[0]
    list_indices = outp[1]
    enums = outp[2]
    assert expected.equals(actual), actual
    assert list_indices == [2], list_indices
    assert enums == {}, enums

    simple_original_empty = SimpleOptional(idno="AVal", title="BVal", authors=[])

    expected = pd.DataFrame([["AVal"], ["BVal"], [None]], index=["idno", "title", "authors"])
    outp = pydantic_to_dataframe(simple_original_empty)
    actual = outp[0]
    list_indices = outp[1]
    enums = outp[2]
    assert expected.equals(actual), actual
    assert list_indices == [2], list_indices
    assert enums == {}, enums


def test_subfield():
    class Production(BaseModel):
        idno: str
        title: str
        author: str

    class Country(BaseModel):
        name: str
        initials: str

    class ProductionAndCountries(BaseModel):
        production: Production
        countries: Country

    inp = ProductionAndCountries(
        production=Production(idno="AVal", title="BVal", author="CVal"),
        countries=Country(name="MyCountry", initials="MC"),
    )

    index = pd.MultiIndex.from_tuples(
        [
            ("production", "idno"),
            ("production", "title"),
            ("production", "author"),
            ("countries", "name"),
            ("countries", "initials"),
        ]
    )
    expected = pd.DataFrame([["AVal"], ["BVal"], ["CVal"], ["MyCountry"], ["MC"]], index=index)
    outp = pydantic_to_dataframe(inp, debug=True)
    actual = outp[0]
    list_indices = outp[1]
    enums = outp[2]
    assert expected.equals(actual), actual
    assert list_indices == []
    assert enums == {}, enums


def test_sublists():
    class Citation(BaseModel):
        """
        A set of elements to describe a resource citation
        """

        title: Optional[str] = Field(None, description="Resource title", title="Title")
        alternateTitle: Optional[List[str]] = Field(
            None, description="Resource alternate title", title="Alternate Title"
        )

    class IdentificationInfo(BaseModel):
        """
        Identification(s) of the resource
        """

        citation: Optional[Citation] = Field(None, description="Dataset citation", title="Citation")

    class MetaDataOfVariousHierarchies(BaseModel):
        citation: Optional[Citation] = None
        identification_info: Optional[IdentificationInfo] = None
        lst: Optional[List[str]] = None

    inp = MetaDataOfVariousHierarchies(
        citation=Citation(title="topleveltitle", alternateTitle=[]),
        identification_info=IdentificationInfo(
            citation=Citation(title="citation_title", alternateTitle=["alt_title_1", "alt_title_2"])
        ),
        lst=["a", "b", "c"],
    )

    index = pd.MultiIndex.from_tuples(
        [
            ("lst",),
            ("citation", "title"),
            ("citation", "alternateTitle"),
            ("identification_info", "citation", "title"),
            ("identification_info", "citation", "alternateTitle"),
        ]
    )
    expected = pd.DataFrame(
        [["a", "b", "c"], ["topleveltitle"], [], ["citation_title"], ["alt_title_1", "alt_title_2"]], index=index
    )
    outp = pydantic_to_dataframe(inp, debug=True)
    actual = outp[0]
    list_indices = outp[1]
    enums = outp[2]
    assert "lst" in actual.index
    assert "citation" in actual.index
    assert "identification_info" in actual.index
    print("Gordon", expected.loc["lst"])
    print(actual.loc["lst"])
    assert expected.loc["lst"].equals(actual.loc["lst"]), actual.loc["lst"]
    assert expected.equals(actual), actual
    assert list_indices == [0, 2, 4], list_indices
    assert enums == {}, enums


def test_list_of_lists():
    class Citation(BaseModel):
        """
        A set of elements to describe a resource citation
        """

        title: Optional[str] = Field(None, description="Resource title", title="Title")
        alternateTitle: Optional[List[str]] = Field(
            None, description="Resource alternate title", title="Alternate Title"
        )

    class IdentificationInfo(BaseModel):
        """
        Identification(s) of the resource
        """

        citation: Optional[Citation] = Field(None, description="Dataset citation", title="Citation")

    class LegalConstraints(BaseModel):
        """
        Legal constraints associated to the resource
        """

        useLimitation: Optional[List[str]] = None
        accessConstraints: Optional[List[str]] = Field(
            None,
            description=(
                "A restriction to access/use a resource. e.g. 'dataset'. Recommended code following the [ISO/TS"
                " 19139](http://standards.iso.org/iso/19139/resources/gmxCodelists.xml#MD_RestrictionCode) Restriction"
                " codelist. Suggested values: {`copyright`, `patent`, `patentPending`, `trademark`, `license`,"
                " `intellectualPropertyRights`, `restricted`, `otherRestrictions`, `unrestricted`, `licenceUnrestricted`,"
                " `licenceEndUser`, `licenceDistributor`, `private`, `statutory`, `confidential`, `SBU`, `in-confidence`}"
            ),
            title="Access constraints",
        )

    class Constraints(BaseModel):
        """
        Constraints associated to the resource
        """

        legalConstraints: Optional[LegalConstraints] = Field(
            None, description="Legal constraints associated to the resource", title="Legal constraints"
        )

    class ServiceIdentification(BaseModel):
        """
        Service identification
        """

        restrictions: Optional[List[Constraints]] = Field(
            None, description="Constraints associated to the service", title="Service constraints"
        )

    class MetaDataOfVariousHierarchies(BaseModel):
        # citation: Optional[Citation] = None
        identification_info: Optional[IdentificationInfo] = None
        # lst: Optional[List[str]] = None,
        service_identification: Optional[ServiceIdentification] = None

    inp = MetaDataOfVariousHierarchies(
        # citation = Citation(title="topleveltitle", alternateTitle=[]),
        identification_info=IdentificationInfo(
            citation=Citation(title="citation_title", alternateTitle=["alt_title_1", "alt_title_2"])
        ),
        # lst = ["a", 'b', 'c'],
        service_identification=ServiceIdentification(
            restrictions=[Constraints(legalConstraints=LegalConstraints(useLimitation=[], accessConstraints=[]))]
        ),
    )

    index = pd.MultiIndex.from_tuples(
        [
            ("identification_info", "citation", "title"),
            ("identification_info", "citation", "alternateTitle"),
            ("service_identification", "restrictions", "legalConstraints", "useLimitation"),
            ("service_identification", "restrictions", "legalConstraints", "accessConstraints"),
        ]
    )

    expected = pd.DataFrame(
        [["citation_title", None], ["alt_title_1", "alt_title_2"], [[], None], [[], None]], index=index
    )

    outp = pydantic_to_dataframe(inp)
    actual = outp[0]
    list_indices = outp[1]
    enums = outp[2]
    assert expected.loc["identification_info"].equals(actual.loc["identification_info"]), actual.loc[
        "identification_info"
    ]
    assert expected.loc["service_identification"].equals(actual.loc["service_identification"]), actual.loc[
        "service_identification"
    ]
    assert expected.equals(actual), actual
    assert list_indices == [1, 2, 3], list_indices
    assert enums == {}, enums


def test_dictionary():
    class Embedding(BaseModel):
        id: str = Field(..., title="Vector Model ID")
        description: Optional[str] = Field(None, title="Vector Model Description")
        date: Optional[str] = Field(None, title="Date (YYYY-MM-DD)")
        vector: Union[Dict[str, Any], List[Any]] = Field(..., title="Vector")

    emb = make_skeleton(Embedding)
    df, _, _ = pydantic_to_dataframe(emb, debug=True)

    emb = Embedding(id="sjc", description="ekjrv", date="2024-01-01", vector={"1": "a", "2": "b"})
    df, _, _ = pydantic_to_dataframe(emb, debug=True)
    assert df.loc["id"].values[0][0] == "sjc", df.loc["id"]
    assert df.loc["description"].values[0][0] == "ekjrv", df.loc["description"]
    assert df.loc["date"].values[0][0] == "2024-01-01", df.loc["date"]
    assert df.loc["vector"].loc["key"].values[0] == "1", df.loc["vector"].loc["key"]
    assert df.loc["vector"].loc["key"].values[1] == "2", df.loc["vector"].loc["key"]
    assert df.loc["vector"].loc["value"].values[0] == "a", df.loc["vector"].loc["value"]
    assert df.loc["vector"].loc["value"].values[1] == "b", df.loc["vector"].loc["value"]

    emb = Embedding(id="sjc", description="ekjrv", date="2024-01-01", vector=[1, 2, 3])
    df, _, _ = pydantic_to_dataframe(emb, debug=True)
    assert df.loc["id"].values[0] == "sjc", df.loc["id"]
    assert df.loc["description"].values[0] == "ekjrv", df.loc["description"]
    assert df.loc["date"].values[0] == "2024-01-01", df.loc["date"]
    assert df.loc["vector"].values[0] == 1, df.loc["vector"]
    assert df.loc["vector"].values[1] == 2, df.loc["vector"]
    assert df.loc["vector"].values[2] == 3, df.loc["vector"]

    # lists of embeddings
    class Parent(BaseModel):
        embeddings: Optional[List[Embedding]] = Field(None, description="Word embeddings", title="Word embeddings")

    emb = make_skeleton(Parent)
    df, _, _ = pydantic_to_dataframe(emb, debug=True)

    emb = Parent(embeddings=[Embedding(id="sjc", description="ekjrv", date="2024-01-01", vector={"1": "a", "2": "b"})])
    df, _, _ = pydantic_to_dataframe(emb, debug=True)
    assert df.loc["embeddings"].loc["id"].values[0][0] == "sjc", df.loc["embeddings"].loc["id"]
    assert df.loc["embeddings"].loc["description"].values[0][0] == "ekjrv", df.loc["embeddings"].loc["description"]
    assert df.loc["embeddings"].loc["date"].values[0][0] == "2024-01-01", df.loc["embeddings"].loc["date"]
    assert False, df.loc["embeddings"]
    assert df.loc["embeddings"].loc["vector"].loc["key"].values[0] == "1", df.loc["embeddings"].loc["vector"].loc["key"]
    assert df.loc["embeddings"].loc["vector"].loc["key"].values[1] == "2", df.loc["embeddings"].loc["vector"].loc["key"]
    assert df.loc["embeddings"].loc["vector"].loc["value"].values[0] == "a", (
        df.loc["embeddings"].loc["vector"].loc["value"]
    )
    assert df.loc["embeddings"].loc["vector"].loc["value"].values[1] == "b", (
        df.loc["embeddings"].loc["vector"].loc["value"]
    )
