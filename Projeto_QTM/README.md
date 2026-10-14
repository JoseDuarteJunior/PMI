Just one single file
1 - Install bootstrap 
sudo apt install -y libjs-bootstrap4
dpkg -L libjs-bootstrap4 | grep -E "\.(css|js)$"


2 - Copy
cp /usr/share/javascript/bootstrap4/css/bootstrap.min.css static/bootstrap.min.css
