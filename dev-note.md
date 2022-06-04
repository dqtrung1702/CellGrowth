# Git
* git clone https://github.com/dqtrung1702/UAA.git

# DEV Evironment
* Phát triển sử dung vscode,host trên máy ảo WSL bản Ubuntu 20.04(Focal Fossa).

    ## Enable the WSL, Install vm Ubuntu-20.04
    * Open PowerShell as Administrator and run:
        dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
        dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
    * Download the latest package:
        WSL2 Linux kernel update package for x64 machines: https://wslstorestorage.blob.core.windows.net/wslblob/wsl_update_x64.msi
    * Open PowerShell, Set WSL 2 as your default version ```wsl --set-default-version 2```
    * Download & Install Linux distribution [Ubuntu 20.04 LTS]
        * Check danh sách các máy ảo đang chạy và verion WSL đang sử dụng ```wsl --list --verbose```
        * Nếu máy ảo đang chạy trên version WSL v1 thì set lại version cho nó: ```wsl --set-version Ubuntu-20.04 2```
    ## Cài đặt trên máy vm Ubuntu
    ```
    sudo apt-get update 
    sudo apt-get upgrade 
    ```
    * TZ
    ```
    sudo timedatectl set-timezone Asia/Ho_Chi_Minh  
    ```
    * Python
    ```
    sudo apt install python3-pip 
    sudo apt install python3-virtualenv 
    ```
    * virtualenv
    ```
    virtualenv venv
    ```
    * activate env
    ```
    source venv/bin/activate
    ```
    * Install lib
    ```
    pip3 install -r reqirements.txt
    ```
# Installation  
## postgres
    
1. Installing PostgreSQL
    > To install PostgreSQL, first refresh your server’s local package index: 
    ```
    sudo apt update
    ```
    > Then, install the Postgres package along with a -contrib package that adds some additional utilities and functionality:
    ```
    sudo apt install postgresql postgresql-contrib
    ```
2. Using PostgreSQL Roles and Databases
    > Certify that postgresql service is running, using
    ```
    pg_lsclusters	# Hiển thị thông tin các clusters PostgreSQL
    ```
    ```
    sudo pg_ctlcluster {Ver} main start # start một cluster PostgreSQL
    ```
    > Start/Stop/Restart postgresql service  
    ```
    sudo service postgresql start
    sudo service postgresql stop
    sudo service postgresql restart
    ```
    > Switch over to the postgres account on your server by typing: 
    ```
    sudo -i -u postgres
    ```
    > Then you can access the Postgres prompt by typing: 
    ```
    psql
    ```
    > To exit out of the PostgreSQL prompt, run the following: ```\q```
    > To return to your regular system user, run the exit command:
    ```
    exit
    ```
3. Enable remote access to PostgreSQL server
    > Get location of postgresql.conf file by executing the command 
    ```
    psql -U postgres -c 'SHOW config_file' 
    # ex:========> /etc/postgresql/12/main/postgresql.conf
    ```
    * Open postgresql.conf file and add the following line to the end: 
        * ```listen_addresses = '*'``` (listen on all IP - not recomment)
        * ```5432 -> [5436]``` (change port) 
    >Get the location of pg_hba.conf file 
    ```
    grep pg_hba.conf /etc/postgresql/12/main/postgresql.conf
    ```
    * Add the following line to the end of /etc/postgresql/12/main/pg_hba.conf file: 
        * ```host    all             all             0.0.0.0/32              md5```
    > Restart PostgreSQL server to apply the changes 
    ```
    sudo service postgresql restart
    ```
4. Init database
    * CREATE USER admin;
    * CREATE DATABASE dev;
    * GRANT ALL PRIVILEGES ON DATABASE dev TO admin;
    * ALTER USER admin WITH ENCRYPTED PASSWORD 'admin';
    * \l #  list database 
    * \c <database>
    * CREATE SCHEMA uaa AUTHORIZATION admin;
    * \dn #  list SCHEMA 
    * \dt #  list tables 
        
## Installation of Node.js on Linux
> Node.js is a JavaScript runtime built on Chrome’s V8 JavaScript engine
```
sudo apt install nodejs
node -v or node –version
```
> NPM is an open source library of Node.js packages.
```
sudo apt install npm
npm -v or npm –version
```
## Install Angular
```
sudo npm uninstall -g angular-cli
sudo npm uninstall -g @angular/cli
sudo npm cache clear --force
sudo npm install -g @angular/cli@latest
```
* Tạo frontend - Angular-client

# Show PID/Program name - kill program running
* sudo apt install net-tools
* sudo netstat -tulpn
* pgrep python3
* kill -9 PID