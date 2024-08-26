import os

from pydantic_schemas.schema_interface import SchemaInterface

ei = SchemaInterface()

for metadata_type in ei.get_metadata_types():
    filename = f"excel_sheets/{metadata_type.capitalize()}_metadata.xlsx"
    print(f"Writing {metadata_type} outline to {filename}")
    if os.path.exists(filename):
        os.remove(filename)
    ei.write_outline_metadata_to_excel(metadata_type=metadata_type, filename=filename)
