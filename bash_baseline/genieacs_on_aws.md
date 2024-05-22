# GenieACS installation on AWS-EC2
Sequence of commands to install GenieACS on AWS-EC2 running latest Ubuntu AMI

Instructions are derived from the [official guide](https://docs.genieacs.com/en/latest/installation-guide.html#install-genieacs)
## Preparation
```shell
sudo apt update
sudo apt upgrade -y
sudo apt install gnupg curl wget -y
```
## Pre-requisites
### Node.js
```shell
sudo apt install nodejs npm -y
sudo shutdown -r now
```
### MangoDB
As of authoring this document, the following version of MangoDB is known to be working for GenieACS:
```shell
curl -fsSL https://www.mongodb.org/static/pgp/server-7.0.asc | sudo gpg -o /usr/share/keyrings/mongodb-server-7.0.gpg --dearmor
echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list
sudo apt update
sudo apt-get install -y mongodb-org
```
Prevent automatic update of MangoDB packages
```shell
echo "mongodb-org hold" | sudo dpkg --set-selections
echo "mongodb-org-database hold" | sudo dpkg --set-selections
echo "mongodb-org-server hold" | sudo dpkg --set-selections
echo "mongodb-mongosh hold" | sudo dpkg --set-selections
echo "mongodb-org-mongos hold" | sudo dpkg --set-selections
echo "mongodb-org-tools hold" | sudo dpkg --set-selections
```
_[**Optional step**] verify that systemd is use by issuing the command:_
```shell
ps --no-headers -o comm 1
```
Start the MangoBD service:
```shell
sudo systemctl start mongod
sudo systemctl status mongod
sudo systemctl enable mongod
```
## GenieACS
### Install from NPM
```shell
sudo npm install -g genieacs
```
### Configure systemd
#### Create a system user to run GenieACS daemons
```shell
sudo useradd --system --no-create-home --user-group genieacs
```
#### Create directory to save extensions and environment file
```shell
sudo mkdir -p /opt/genieacs/ext
sudo chown genieacs:genieacs /opt/genieacs/ext
```
#### Create an environment file to hold configuration options
```shell
sudo bash -c 'cat <<'EOF' >> /opt/genieacs/genieacs.env
GENIEACS_CWMP_ACCESS_LOG_FILE=/var/log/genieacs/genieacs-cwmp-access.log
GENIEACS_NBI_ACCESS_LOG_FILE=/var/log/genieacs/genieacs-nbi-access.log
GENIEACS_FS_ACCESS_LOG_FILE=/var/log/genieacs/genieacs-fs-access.log
GENIEACS_UI_ACCESS_LOG_FILE=/var/log/genieacs/genieacs-ui-access.log
GENIEACS_DEBUG_FILE=/var/log/genieacs/genieacs-debug.yaml
NODE_OPTIONS=--enable-source-maps
GENIEACS_EXT_DIR=/opt/genieacs/ext
EOF'
```
#### Generate a secure JWT secret and append to environment file
```shell
GENIEACS_UI_JWT_SECRET=$(node -e "console.log(require('crypto').randomBytes(128).toString('hex'))")
echo "GENIEACS_UI_JWT_SECRET=$GENIEACS_UI_JWT_SECRET" | sudo tee -a /opt/genieacs/genieacs.env
```
#### Set file ownership and permissions:
```shell
sudo chown genieacs:genieacs /opt/genieacs/genieacs.env
sudo chmod 600 /opt/genieacs/genieacs.env
```
#### Create logs directory
```shell
sudo mkdir -p /var/log/genieacs
sudo chown genieacs:genieacs /var/log/genieacs
```
#### Create systemd unit files
Create a systemd unit file for each of the four GenieACS services
1. Run the following command to create **genieacs-cwmp** service:
```shell
sudo bash -c 'cat <<'EOF' >> /etc/systemd/system/genieacs-cwmp.service
[Unit]
Description=GenieACS CWMP
After=network.target

[Service]
User=genieacs
EnvironmentFile=/opt/genieacs/genieacs.env
ExecStart=/usr/local/bin/genieacs-cwmp

[Install]
WantedBy=default.target
EOF'
```
2. Run the following command to create **genieacs-nbi** service:
```shell
sudo bash -c 'cat <<'EOF' >> /etc/systemd/system/genieacs-nbi.service
[Unit]
Description=GenieACS NBI
After=network.target

[Service]
User=genieacs
EnvironmentFile=/opt/genieacs/genieacs.env
ExecStart=/usr/local/bin/genieacs-nbi

[Install]
WantedBy=default.target
EOF'
```
3. Run the following command to create **genieacs-fs** service:
```shell
sudo bash -c 'cat <<'EOF' >> /etc/systemd/system/genieacs-fs.service
[Unit]
Description=GenieACS FS
After=network.target

[Service]
User=genieacs
EnvironmentFile=/opt/genieacs/genieacs.env
ExecStart=/usr/local/bin/genieacs-fs

[Install]
WantedBy=default.target
EOF'
```
4. Run the following command to create **genieacs-ui** service:
```shell
sudo bash -c 'cat <<'EOF' >> /etc/systemd/system/genieacs-ui.service
[Unit]
Description=GenieACS UI
After=network.target

[Service]
User=genieacs
EnvironmentFile=/opt/genieacs/genieacs.env
ExecStart=/usr/local/bin/genieacs-ui

[Install]
WantedBy=default.target
EOF'
```
#### Configure log file rotation using logrotate
Save the following as **/etc/logrotate.d/genieacs** file:
```shell
sudo bash -c 'cat <<'EOF' >> /etc/logrotate.d/genieacs
/var/log/genieacs/*.log /var/log/genieacs/*.yaml {
    daily
    rotate 30
    compress
    delaycompress
    dateext
}
EOF'
```
### Enable & Start Services
```shell
sudo systemctl enable genieacs-cwmp
sudo systemctl start genieacs-cwmp
sudo systemctl status genieacs-cwmp

sudo systemctl enable genieacs-nbi
sudo systemctl start genieacs-nbi
sudo systemctl status genieacs-nbi

sudo systemctl enable genieacs-fs
sudo systemctl start genieacs-fs
sudo systemctl status genieacs-fs

sudo systemctl enable genieacs-ui
sudo systemctl start genieacs-ui
sudo systemctl status genieacs-ui
```
## AWS Security Configurations
### EC2 Security Group - Inbound Rules - Allow Ports:
```text
TCP 3000 - for accessing GenieACS Web UI
TCP 7557 - for accessing GenieACS NB API
TCP 7547 - for device(s) to connect to CWMP service
```
