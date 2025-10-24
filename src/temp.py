from __future__ import annotations

import my


def json_to_csv(from_filename: str, to_filename: str) -> None:
    with open(from_filename) as json_file:
        json_decoded: list[dict] = my.json_decode(json_file.read())
        header = list(json_decoded[0].keys())
        my.csv_write(to_filename,
                     [[row[key] for key in header] for row in json_decoded],
                     header)
