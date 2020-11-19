#! /bin/bash
apt-get update
yes | apt-get install build-essential python3.6 cppreference-doc-en-html cgroup-lite libcap-dev zip python3.6-dev libpq-dev libcups2-dev libyaml-dev libffi-dev python3-pip

cd /home/nfssdq
git clone --branch v1.5.dev0-bdoi2021 --recursive https://github.com/RezwanArefin01/cms.git 
cd cms
echo "##################################################################################"
python3 ./prerequisites.py -y --as-root install
usermod -a -G cmsuser nfssdq
pip3 install -r ./requirements.txt
python3 ./setup.py install

gsutil cp gs://contestdata/cms.conf /usr/local/etc/cms.conf
gsutil cp gs://contestdata/cms.ranking.conf /usr/local/etc/cms.ranking.conf