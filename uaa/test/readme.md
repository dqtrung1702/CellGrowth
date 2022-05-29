OS: Ubuntu-20.04
```
# upgrade 
sudo apt-get update # được sử dụng để tải xuống thông tin gói từ tất cả các nguồn được cấu hình
sudo apt-get upgrade # để cài đặt các bản nâng cấp có sẵn của tất cả các gói hiện được cài đặt trên hệ thống từ các nguồn được cấu hình thông qua tệp sources.list

sudo apt install python3-pip # bản phân phối Linux của bạn đã đi kèm với Python, có thể cài đặt PIP bằng trình quản lý gói (package manager) của hệ thống
sudo apt install python3-virtualenv # Do đặc thù của mỗi dự án lại sử dụng các package khác nhau nên mỗi dự án sẽ tạo cho nó một venv. Tại mỗi venv, thoải mái cài đặt các thư viện cần dùng mà không phải lo nghĩ đến việc cài thư viện này sẽ làm ảnh hưởng đến việc khởi chạy các dự án khác vì mỗi VE là một môi trường ảo hoàn toàn độc lập.

sudo apt install git # version control system
git --version
git init
git clone https://github.com/dqtrung1702/UAA.git
```

cd UAA/uaa/test

