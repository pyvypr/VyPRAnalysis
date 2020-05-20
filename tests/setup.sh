rm -rf VyPRServer/
git clone git@github.com:pyvypr/VyPRServer.git
cd VyPRServer
git clone git@github.com:pyvypr/VyPR.git
cd ..
cp verdicts.db VyPRServer/verdicts.db

python test_script.py
