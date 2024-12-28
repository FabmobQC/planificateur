import csv
import io
import os
import zipfile
from datetime import datetime
from io import TextIOWrapper

from .config_handler import ConfigGtfsData, GtfsInfos
from .downloader import download_file_if_newer
from .update_status import UpdateStatus


def handle_gtfs_data(
    config_gtfs_data: ConfigGtfsData, otp_input_folder: str
) -> UpdateStatus:
    print("Handle GTFS data")
    update_status = UpdateStatus.NOT_UPDATED
    for gtfs_infos in config_gtfs_data["infos"]:
        destination = f"{otp_input_folder}/{gtfs_infos["filename"]}"
        print("File URL:", gtfs_infos["url"])
        print("Local destination:", destination)
        if gtfs_infos.get("is_manual_download", False):
            print("Manual download")
            file_update_status = handle_manual_download(destination)
        else:
            file_update_status = download_file_if_newer(gtfs_infos["url"], destination)
        if gtfs_infos.get("is_timezone_incorrect", False):
            # We always fix timezone to avoid mistakes in case of crash.
            print("Fix timezone")
            handle_fix_timezone(destination, config_gtfs_data["timezone"])
        print("File update status: ", file_update_status)
        if file_update_status == UpdateStatus.ERROR:
            return UpdateStatus.ERROR
        if file_update_status == UpdateStatus.UPDATED:
            update_status = UpdateStatus.UPDATED
    return update_status


def handle_manual_download(destination: str) -> UpdateStatus:
    if os.path.exists(destination):
        if check_is_gtfs_expired(destination):
            print("The current GTFS data is expired.")
            return UpdateStatus.ERROR
        return UpdateStatus.NOT_UPDATED
    else:
        print("The file must be manually downloaded and put into its destination.")
        return UpdateStatus.ERROR


def handle_fix_timezone(gtfs_path: str, timezone: str) -> None:
    temp_gtfs_path = gtfs_path + "-tmp"
    with zipfile.ZipFile(gtfs_path, "r") as zip_ref:
        with zipfile.ZipFile(temp_gtfs_path, "w") as temp_zip_ref:
            for filename in zip_ref.namelist():
                with zip_ref.open(filename) as file:
                    if filename == "agency.txt":
                        text_file = TextIOWrapper(file, encoding="utf-8")
                        csv_reader = csv.DictReader(text_file)
                        rows = list(csv_reader)
                        for row in rows:
                            row["agency_timezone"] = timezone
                        new_file = io.StringIO()
                        fieldnames = (
                            csv_reader.fieldnames
                            if csv_reader.fieldnames is not None
                            else []
                        )
                        csv_writer = csv.DictWriter(new_file, fieldnames=fieldnames)
                        csv_writer.writeheader()
                        csv_writer.writerows(rows)

                        temp_zip_ref.writestr(filename, new_file.getvalue())
                    else:
                        temp_zip_ref.writestr(filename, file.read())
    os.replace(temp_gtfs_path, gtfs_path)


def check_is_gtfs_expired(gtfs_path: str) -> bool:
    current_date = datetime.now()
    formatted_current_date = current_date.strftime("%Y%m%d")
    with zipfile.ZipFile(gtfs_path, "r") as zip_ref:
        if "feed_info.txt" in zip_ref.namelist():
            with zip_ref.open("feed_info.txt") as file:
                text_file = TextIOWrapper(file, encoding="utf-8")
                csv_reader = csv.DictReader(text_file)
                earliest_feed_end_date = ""
                for row in csv_reader:
                    feed_end_date = row["feed_end_date"]
                    if feed_end_date > earliest_feed_end_date:
                        earliest_feed_end_date = feed_end_date
                print(
                    f"Earliest feed_end_date: {earliest_feed_end_date} (current: {formatted_current_date})"
                )
                return earliest_feed_end_date < formatted_current_date
        elif "calendar.txt" in zip_ref.namelist():
            with zip_ref.open("calendar.txt") as file:
                text_file = TextIOWrapper(file, encoding="utf-8")
                csv_reader = csv.DictReader(text_file)
                last_end_date = ""
                for row in csv_reader:
                    end_date = row["end_date"]
                    if end_date > last_end_date:
                        last_end_date = end_date
                print(
                    f"Last end_date: {last_end_date} (current: {formatted_current_date})"
                )
                return last_end_date < formatted_current_date
    raise Exception("Unhandled case for GTFS expiration check")
