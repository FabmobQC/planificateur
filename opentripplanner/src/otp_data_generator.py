import glob
import os
import shutil
import subprocess

from .config_handler import Config
from .gtfs_handler import handle_gtfs_data
from .osm_data_handler import generate_osm_data
from .update_status import UpdateStatus


def launch_otp_build(otp_path: str, otp_input_folder: str) -> None:
    command = [
        "java",
        "-Xmx8G",
        "-jar",
        otp_path,
        "--build",
        "--save",
        otp_input_folder,
    ]
    subprocess.run(command, check=True)


def launch_otp_build_street(otp_path: str, otp_input_folder: str) -> None:
    command = ["java", "-Xmx8G", "-jar", otp_path, "--buildStreet", otp_input_folder]
    subprocess.run(command, check=True)


def launch_otp_load_street(otp_path: str, otp_input_folder: str) -> None:
    command = [
        "java",
        "-Xmx8G",
        "-jar",
        otp_path,
        "--loadStreet",
        "--save",
        otp_input_folder,
    ]
    subprocess.run(command, check=True)


def generate_otp_data(
    config: Config, otp_path: str, work_folder: str, force=False
) -> None:
    project_name = config["project_name"]
    project_folder = os.path.join(work_folder, project_name)
    osm_data_folder = os.path.join(project_folder, "osm_data")
    otp_input_folder = os.path.join(project_folder, "otp_input")
    otp_output_folder = os.path.abspath(
        os.path.join(work_folder, config["output_folder"])
    )

    print("Project name:", project_name)
    print("OTP path:", otp_path)
    print("Project folder:", project_folder)
    print("Output folder:", otp_output_folder)

    osm_data_update_status = generate_osm_data(
        config["osm_data"], osm_data_folder, otp_input_folder
    )
    gtfs_data_update_status = handle_gtfs_data(config["gtfs_data"], otp_input_folder)
    statuses = [osm_data_update_status, gtfs_data_update_status]
    print("statuses:", statuses)
    if force or (
        UpdateStatus.ERROR not in statuses and UpdateStatus.UPDATED in statuses
    ):
        print("Building OTP graphes")
        launch_otp_build(otp_path, otp_input_folder)
        launch_otp_build_street(otp_path, otp_input_folder)
        launch_otp_load_street(otp_path, otp_input_folder)

        print("Move generated files to output folder")
        os.makedirs(otp_output_folder, exist_ok=True)
        obj_files = glob.glob(os.path.join(otp_input_folder, "*.obj"))
        for file in obj_files:
            filename = os.path.basename(file)
            # shutil.move overwrite pre-existing files only if we give it full destination path
            destination = os.path.join(otp_output_folder, filename)
            print(f"Move: {file} -> {destination}")
            shutil.move(file, destination)
