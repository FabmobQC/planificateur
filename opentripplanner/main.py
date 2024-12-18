import os
import sys

from src.config_handler import open_config
from src.otp_data_generator import generate_otp_data


def main():
    config_path = sys.argv[1]
    otp_path = os.path.abspath(sys.argv[2])
    config = open_config(config_path)
    current_dir = os.path.dirname(os.path.realpath(__file__))
    work_folder = os.path.abspath(os.path.join(current_dir, "work_folder"))
    generate_otp_data(config, otp_path, work_folder)


if __name__ == "__main__":
    main()
