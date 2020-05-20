rm -rf VyPRServer/

git clone git@github.com:pyvypr/VyPRServer.git

cd VyPRServer
virtualenv venv --python=python2.7
source venv/bin/activate
pip install -r requirements.txt

git clone git@github.com:pyvypr/VyPR.git
cd ..

cp verdicts.db VyPRServer/verdicts.db

python test_script.py
