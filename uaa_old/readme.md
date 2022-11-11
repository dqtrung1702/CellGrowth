# OS: Ubuntu-20.04
```
sudo apt-get update # được sử dụng để tải xuống thông tin gói từ tất cả các nguồn được cấu hình
sudo apt-get upgrade # để cài đặt các bản nâng cấp có sẵn của tất cả các gói hiện được cài đặt trên hệ thống từ các nguồn được cấu hình thông qua tệp sources.list
sudo timedatectl set-timezone Asia/Ho_Chi_Minh  # set TZ

sudo apt install python3-pip # bản phân phối Linux của bạn đã đi kèm với Python, có thể cài đặt PIP bằng trình quản lý gói (package manager) của hệ thống
sudo apt install python3-virtualenv # Do đặc thù của mỗi dự án lại sử dụng các package khác nhau nên mỗi dự án sẽ tạo cho nó một venv. Tại mỗi venv, thoải mái cài đặt các thư viện cần dùng mà không phải lo nghĩ đến việc cài thư viện này sẽ làm ảnh hưởng đến việc khởi chạy các dự án khác vì mỗi VE là một môi trường ảo hoàn toàn độc lập.

sudo apt install git # version control system
git --version
git init
git clone https://github.com/dqtrung1702/UAA.git

sudo service postgresql restart
cd UAA
virtualenv venv
source venv/bin/activate
cd uaa
pip3 install -r requirements.txt
```
## DB-Postgres
1. Installation
> install the Postgres package along with a -contrib package that adds some additional utilities and functionality:
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