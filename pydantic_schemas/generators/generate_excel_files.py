import os

from pydantic_schemas.metadata_manager import MetadataManager

metadata_manager = MetadataManager()

for metadata_name in metadata_manager.metadata_type_names:
    if metadata_name in ["image", "geospatial"]:
        continue
    filename = f"excel_sheets/{metadata_name.capitalize()}_metadata.xlsx"
    print(f"Writing {metadata_name} outline to {filename}")
    if os.path.exists(filename):
        os.remove(filename)
    metadata_manager.write_metadata_outline_to_excel(metadata_name_or_class=metadata_name, filename=filename)
