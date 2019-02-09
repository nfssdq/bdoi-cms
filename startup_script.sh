yes "" | sudo add-apt-repository ppa:webupd8team/java
sudo apt-get update
yes "Y" | sudo apt install g++ gcc build-essential openjdk-8-jdk-headless postgresql postgresql-client python3.6 libcap-dev zip python3.6-dev libpq-dev libcups2-dev libyaml-dev libffi-dev python3-pip nginx-full python2.7 php7.2-cli php7.2-fpm phppgadmin texlive-latex-base a2ps
wget https://github.com/cms-dev/cms/releases/download/v1.4.rc1/v1.4.rc1.tar.gz
tar xvzf v1.4.rc1.tar.gz
cd cms
yes "Y" | sudo python3 prerequisites.py install
sudo pip3 install -r requirements.txt
python3 prerequisites.py build
export PATH=$PATH:./isolate/
export PYTHONPATH=./
cp config/cms.conf.sample config/cms.conf
cp config/cms.ranking.conf.sample config/cms.ranking.conf
sudo python3 setup.py install