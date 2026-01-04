from pathlib import Path
from tools.toolbi import update_mobile_from_json

library_path = Path("library")

for json_file in library_path.glob("mobile_app*.json"):
    update_mobile_from_json(
        json_app=str(json_file),
        dest_table_app="translations"
    )