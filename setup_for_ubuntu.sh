
echo '[+] Script runned'

sudo apt-get update
sudo apt-get install python3.7
sudo apt-get install git
sudo apt install snap
sudo apt-get install python3-venv
sudo apt-get update

cd backend
python3 -m venv venv
activate () {
    . ./venv/bin/activate
}
activate
pip install -r requirements.txt
python3 manage.py createsuperuser

# pip freeze > requirements.txt

echo "[+] Script completed"