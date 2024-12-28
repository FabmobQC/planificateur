# Launch
## Install dependencies
We assume osmium-tools and OpenOpenTripPlanner dependencies are already installed.
``` shell
pip install -r requirements.txt
```

## Launch
Launch `main.py` and specify the paths to the config and the OpenTripPlanner jar.
``` shell
python main.py configs/general.json work_folder/otp.jar
```

# Lint
## Install dependencies
``` shell
pip install -r requirements-dev.txt
```
## Launch
``` shell
sh ./lint
```

