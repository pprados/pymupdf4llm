"""Helpers used across multiple partitioners to compute metadata."""

from __future__ import annotations

import datetime as dt
import os
from typing import Optional, Sequence

from unstructured.documents.elements import Element


def get_last_modified_date(filename: str) -> Optional[str]:
    """Modification time of file at path `filename`, if it exists.

    Returns `None` when `filename` is not a path to a file on the local filesystem.

    Otherwise returns date and time in ISO 8601 string format (YYYY-MM-DDTHH:MM:SS) like
    "2024-03-05T17:02:53".
    """
    if not os.path.isfile(filename):
        return None

    modify_date = dt.datetime.fromtimestamp(os.path.getmtime(filename))
    return modify_date.strftime("%Y-%m-%dT%H:%M:%S%z")


HIERARCHY_RULE_SET = {
    "Title": [
        "Text",
        "UncategorizedText",
        "NarrativeText",
        "ListItem",
        "BulletedText",
        "Table",
        "FigureCaption",
        "CheckBox",
        "Table",
    ],
    "Header": [
        "Title",
        "Text",
        "UncategorizedText",
        "NarrativeText",
        "ListItem",
        "BulletedText",
        "Table",
        "FigureCaption",
        "CheckBox",
        "Table",
    ],
}


def set_element_hierarchy(
    elements: Sequence[Element], ruleset: dict[str, list[str]] = HIERARCHY_RULE_SET
) -> list[Element]:
    """Sets the parent_id for each element in the list of elements
    based on the element's category, depth and a ruleset

    """
    stack: list[Element] = []
    for element in elements:
        if element.metadata.parent_id is not None:
            continue
        parent_id = None
        element_category = getattr(element, "category", None)
        element_category_depth = getattr(element.metadata, "category_depth", 0) or 0

        if not element_category:
            continue

        while stack:
            top_element: Element = stack[-1]
            top_element_category = getattr(top_element, "category")
            top_element_category_depth = (
                getattr(
                    top_element.metadata,
                    "category_depth",
                    0,
                )
                or 0
            )

            if (
                top_element_category == element_category
                and top_element_category_depth < element_category_depth
            ) or (
                top_element_category != element_category
                and element_category in ruleset.get(top_element_category, [])
            ):
                parent_id = top_element.id
                break

            stack.pop()

        element.metadata.parent_id = parent_id
        stack.append(element)

    return list(elements)
