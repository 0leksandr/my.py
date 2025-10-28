from __future__ import annotations
from pathlib import Path
import json

import my


def json_to_csv(from_filename: str, to_filename: str) -> None:
    my.csv_write_dicts(to_filename,
                       json.loads(open(from_filename).read()))

HOME = Path.home()

# with open(f"{HOME}/Downloads/companies-1.txt") as file1:
#     content: list[dict] = my.json_decode(file1.read())
#     for i, row in enumerate(content):
#         if row["nr_vacancies"] is None:
#             content[i]["nr_vacancies"] = 0
#     with open(f"{HOME}/Downloads/companies-2.txt", "w") as file2:
#         file2.write(json.dumps(content, ensure_ascii=False))

# filename = f"{HOME}/Downloads/feedly-vacancies"
# json_to_csv(f"{filename}.json", f"{filename}.csv")
