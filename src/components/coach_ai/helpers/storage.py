# Import standard library modules
from typing import Dict, List, Union

# Import local modules
from src.components.coach_ai.helpers.logging import log
from src.components.coach_ai.helpers.utils import get_filename_and_page_from_path_list
from src.components.coach_ai.services.az_storage import (
    generate_blob_url,
    storage_container_client,
    storage_container_name,
)


def find_match_file_from_azure_storage(
    source_list: List[Dict[str, Union[int, str]]],
    source_image_path: str,
) -> List[str]:
    if not source_list:
        return []

    blob_names_list = storage_container_client.list_blob_names(
        name_starts_with=source_image_path
    )

    matched_data = []
    for blob_name in blob_names_list:
        for source in source_list:
            if f"{source['filename']}.page-{source['page']}." in blob_name:
                matched_data.append(blob_name)
                break
            # image in page after
            elif f"{source['filename']}.page-{int(source['page'])+1}." in blob_name:
                matched_data.append(blob_name)
                break
            # image in page before
            elif (
                f"{source['filename']}.page-{max(int(source['page'])-1, 0)}."
                in blob_name
            ):
                matched_data.append(blob_name)
                break

    return matched_data


def generate_blob_urls_from_matched_data(matched_data: List[str]) -> List[str]:
    log.info("Generating blob urls from matched data...")

    if not matched_data:
        log.warning("No matched data found")
        return []

    blob_urls = []
    for blob_name in matched_data:
        url = generate_blob_url(blob_name, storage_container_name)
        blob_urls.append(url)

    return blob_urls


def find_and_return_source_images(
    source_files: List[Dict[str, Union[int, str]]],
    source_image_path: str,
    answer: str,
    filter_explicit_sources: bool = False,
):
    if filter_explicit_sources:
        filtered_source_files = []
        for source in source_files:
            source_str_unescaped = f"{source['source']}#page={source['page']}"
            if source_str_unescaped in answer:
                filtered_source_files.append(source)
        source_files = filtered_source_files

    matched_sources = find_match_file_from_azure_storage(
        source_list=get_filename_and_page_from_path_list(source_files),
        source_image_path=source_image_path,
    )

    if matched_sources:
        return format_source_image_links(matched_sources)

    log.info("No matches found for sources")
    return ""


def format_source_image_links(sources: List[str]):
    formatted_urls = []
    for source in sources:
        url_with_image_markdown = "![image](/" + source + ")"
        formatted_urls.append(url_with_image_markdown)
    return "".join(formatted_urls)
