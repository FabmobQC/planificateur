# Planificateur
These are the steps for building and deploying the FabMob's trip planner locally or for production.

Ideally these steps should be automatized, but we're not there yet.

# Architecture
The trip planner has three parts: OpenTripPlanner (backend), and otp-react-redux and planificateur-otp-proxy

## OpenTripPlanner
We use it as it is, and we try to keep it up to date

# otp-react-redux
This is with some modifications.

## planificateur-otp-proxy
The frontend communicates directly to the proxy. The proxy modify and forwards the requests to the backend. It modifies the responses and forward them to the frontend.

Its goal is to avoid completely modifying OpenTripPlanner, which is a complex software, and to keep the modifications on for easing updates. 

# Build Data
These operations are expected to be executed locally.

## Prepare directories
``` shell
mkdir -p planificateur/otp
cd planificateur
# Define a variable for the working directory (facultative)
# This is used in the readme solely to make clearer where the commands have to be executed.
cwd=$(pwd)
```

## Install OpenTripPlanner
``` shell
cd "$cwd"
wget https://github.com/opentripplanner/OpenTripPlanner/releases/download/v2.5.0/otp-2.5.0-shaded.jar
apt install openjdk-21-jre
# Select version 21
sudo update-alternatives --config java
```
## Download GTFS
Everything must be put in the `planificateur/otp` folder we created earlier.

Some links might require a VPN if accessed outside of Quebec.
1. Download
``` shell
cd "$cwd/otp"
wget https://www.stm.info/sites/default/files/gtfs/gtfs_stm.zip
wget -O gtfs_rtc.zip https://cdn.rtcquebec.ca/Site_Internet/DonneesOuvertes/googletransit.zip
wget https://www.stlevis.ca/sites/default/files/public/assets/gtfs/transit/gtfs_stlevis.zip
wget -O gtfs_exo-sainte-julie.zip https://exo.quebec/xdata/omitsju/google_transit.zip
wget -O gtfs_exo-terrebonne-mascouche.zip https://exo.quebec/xdata/mrclm/google_transit.zip
wget -O gtfs_exo-assomption.zip https://exo.quebec/xdata/mrclasso/google_transit.zip
wget -O gtfs_exo-vallee-du-richelieu.zip https://exo.quebec/xdata/citvr/google_transit.zip
wget -O gtfs_exo-sud-ouest.zip https://exo.quebec/xdata/citso/google_transit.zip
wget -O gtfs_exo-sorel-varennes.zip https://exo.quebec/xdata/citsv/google_transit.zip
wget -O gtfs_exo-presquile.zip https://exo.quebec/xdata/citpi/google_transit.zip
wget -O gtfs_exo-laurentides.zip https://exo.quebec/xdata/citla/google_transit.zip
wget -O gtfs_exo-haut-saint-laurent.zip https://exo.quebec/xdata/cithsl/google_transit.zip
wget -O gtfs_exo-chambly-richelieu-carignan.zip http://www.exo.quebec/xdata/citcrc/google_transit.zip
wget -O gtfs_exo-trains.zip https://www.rtm.quebec/xdata/trains/google_transit.zip
wget -O gtfs_sts.zip https://gtfs.sts.qc.ca:8443/gtfs/client/GTFS_clients.zip # Optional
curl -L -o GTFS_STL.zip https://stlaval.ca/datas/opendata/GTF_STL.zip # gives trouble with wget
```

2. Download GTFS for RTL
Must be done manually: https://www.rtl-longueuil.qc.ca/fr-CA/donnees-ouvertes/fichiers-gtfs/. **The filename must be renamed to contain `gtfs`**

3. Build GTFS for Boischatel and Côte-de-Beaupré
[zenbus-to-gtfs](https://github.com/FabmobQC/zenbus-to-gtfs). You might need to ask for permissions to access the repository.

4. For gtfs_sts, change `agency_timezone` in agency.txt. It has to be replaced by `America/Montreal`.

## Prepare OpenStreetMap data
``` shell
cd "$cwd"
wget http://download.geofabrik.de/north-america/canada/quebec-latest.osm.pbf
sudo apt install osmium-tool
# The bbox includes the area comprising Montreal and Quebec city.
# It is done for performance.
osmium extract --strategy complete_ways --bbox -74.7776,45.0009,-70.84150184496582,47.144541002415956 quebec-latest.osm.pbf -o montreal-quebec.osm.pbf
mv montreal-quebec.osm.pbf otp
```

## Build
Note these operations require a lot of RAM. This is the reason we do it locally. If the processes get killed, you can try rebooting your computer or using a more powerfull machine.

```shell
cd "$cwd"
java -Xmx8G -jar otp-2.5.0-shaded.jar --build --save otp
java -Xmx8G -jar otp-2.5.0-shaded.jar --buildStreet otp
java -Xmx8G -jar otp-2.5.0-shaded.jar --loadStreet --save otp
```

# Deploy

## Launch OpenTripPlanner

### Locally
``` shell
cd "$cwd"
java -Xmx8G -jar otp-2.5.0-shaded.jar --load otp
```

### Production

1. Install OpenTripPlanner on the server. See [Install OpenTripPlanner](#install-opentripplanner)

2. Upload the data to the server.  **Don't forget to adapt the server's address**
``` shell
# Commands are executed locally
cd "$cwd"
# We use the FabMob's server as an example
scp otp/graph.obj root@146.190.248.76:~/planificateur/otp
scp otp/streetGraph.obj root@146.190.248.76:~/planificateur/otp
scp otp/montreal-quebec.osm.pbf root@146.190.248.76:~/planificateur/otp
```

3. Create a service  
``` shell
# Command is executed on the server
cat << EOF > `/etc/systemd/system/otp.service`
[Unit]
Description=Planificateur FabmobQC.ca OpenTripPlanner Grizzli server
After=network-online.target
 
[Service]
Type=simple
 
User=root
Group=root
UMask=007
 
ExecStart=java -Xmx2G -jar /root/planificateur/otp-2.5.0-shaded.jar --load /root/planificateur/otp
#ExecStart=/bin/docker run -it --rm -p 8080:8080 -v "/root/planificateur/otp:/var/opentripplanner" docker.io/opentripplanner/opentripplanner:2.4.0_2023-04-28T08-35 --load --serve 

Restart=on-failure
 
# Configures the time to wait before service is stopped forcefully.
TimeoutStopSec=300
 
[Install]
WantedBy=multi-user.target
EOF
```

4. Start the service
``` shell
# Command is executed on the server
service otp restart
```

## Launch Proxy

### Locally

1. Clone the repository
``` shell
git clone git@github.com:FabmobQC/planificateur-otp-proxy.git
```
2. Follow the instructions in the readme

### Production

1. Clone the repository
``` shell
cd ~
git clone git@github.com:FabmobQC/planificateur-otp-proxy.git
```

2. Build
```
npm run build
```

3. Create a service  
``` shell
cat << EOF > /etc/systemd/system/otp-proxy.service
[Unit]
Description=Proxy for OpenTripPlanner

[Service]
Type=simple

User=root
Group=root
UMask=007

WorkingDirectory=/root/planificateur-otp-proxy
ExecStart=/root/.nvm/versions/node/v16.19.0/bin/node dist/index.js
Restart=on-failure

# Configures the time to wait before service is stopped forcefully.
TimeoutStopSec=300
 
[Install]
WantedBy=multi-user.target
EOF
```

4. Start the service
``` shell
systemctl start otp-proxy
```

## Launch otp-react-redux

### Locally

1. Clone the repository
``` shell
# Install both otp-ui and otp-react-redux in the same folder
git clone git@github.com:FabmobQC/otp-ui.git
cd otp-ui
git checkout fabmob
yarn
cd ..
git clone git@github.com:FabmobQC/otp-react-redux.git
git checkout fabmob
```

2. Set proper host and port in config-fabmob.yml:
``` yaml
api:
  host: http://localhost
  path: /otp/routers/default
  basePath: /otp/routers/default
  port: 3000
  v2: true
```

3. Install dependencies
``` shell
yarn
```

4. Start
```shell
env YAML_CONFIG=/var/www/html/planificateur.fabmobqc.ca/otp-react-redux/config-fabmob.yml yarn start
```

### Production

1. Clone the repository
``` shell
mkdir -p /var/www/html/planificateur.fabmobqc.ca
cd /var/www/html/planificateur.fabmobqc.
# Install both otp-ui and otp-react-redux in the same folder
git clone git@github.com:FabmobQC/otp-ui.git
git checkout fabmob
yarn && yarn prepublish
cd .. 
git clone git@github.com:FabmobQC/otp-react-redux.git
git checkout fabmob
```


2. Set proper host and port in config-fabmob.yml:
``` yaml
api:
  host: https://www.api-otp.fabmobqc.ca
  path: /otp/routers/default
  basePath: /otp/routers/default
#  port: 3000
  v2: true
```

3. Install dependencies
``` shell
yarn
```

4. Build
```shell
env YAML_CONFIG=/var/www/html/planificateur.fabmobqc.ca/otp-react-redux/config-fabmob.yml yarn build
```

5. Start nginx
``` shell
systemctl start nginx
```
