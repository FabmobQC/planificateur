import os
import shutil
import subprocess

from .config_handler import BorderBox, ConfigOsmData
from .downloader import download_file_if_newer
from .update_status import UpdateStatus


def getmtime(path: str) -> float:
    if os.path.exists(path):
        return os.path.getmtime(path)
    else:
        return 0


def generate_osm_data(
    config_osm_data: ConfigOsmData, osm_data_folder: str, otp_input_folder: str
) -> UpdateStatus:
    osm_base_path = os.path.join(osm_data_folder, config_osm_data["base_filename"])
    print("Download OSM data:", osm_base_path)
    update_status = download_file_if_newer(config_osm_data["url"], osm_base_path)
    print("OSM data update status:", update_status)

    osm_base_mtime = os.path.getmtime(osm_base_path)

    print("Extract bbox from OSM data")
    osm_bbox_path = os.path.join(osm_data_folder, f"bbox-{config_osm_data["filename"]}")
    osm_bbox_exists = os.path.exists(osm_bbox_path)
    osm_bbox_mtime = getmtime(osm_bbox_path)
    if not osm_bbox_exists or osm_base_mtime > osm_bbox_mtime:
        extract_osm_bbox(osm_base_path, osm_bbox_path, config_osm_data["bbox"])
        update_status = UpdateStatus.UPDATED
    else:
        print("Skip")

    if update_status == UpdateStatus.UPDATED:
        print("Copy OSM data to OTP input folder")
        osm_final_path = os.path.join(otp_input_folder, config_osm_data["filename"])
        shutil.copy(osm_bbox_path, osm_final_path)
    return update_status


def extract_osm_bbox(input_osm_path: str, output_path: str, bbox: BorderBox) -> None:
    command = [
        "osmium",
        "extract",
        "--strategy",
        "complete_ways",
        "--bbox",
        f"{bbox["min_lon"]},{bbox["min_lat"]},{bbox["max_lon"]},{bbox["max_lat"]}",
        input_osm_path,
        "-o",
        output_path,
        "--overwrite",
    ]
    subprocess.run(command, check=True)


# This breaks walking, cycling and car trips
def filter_osm(input_osm_path: str, output_path: str) -> None:
    command = [
        "osmium",
        "tags-filter",
        input_osm_path,
        "w/highway",
        "wa/public_transport=platform",
        "wa/railway=platform",
        "w/park_ride=yes",
        "r/type=restriction",
        "r/type=route",
        "-o",
        output_path,
        "-f",
        "pbf",
        "add_metadata=false",
        "--overwrite",
    ]
    print(command)
    subprocess.run(command, check=True)
