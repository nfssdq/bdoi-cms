#! /bin/bash
apt-get update
yes | apt-get install build-essential python3.10 cppreference-doc-en-html cgroup-lite libcap-dev zip python3-dev libpq-dev libcups2-dev libyaml-dev libffi-dev python3-pip

pip3 install --upgrade pip google-cloud-storage google-cloud-secret-manager google-api-python-client pyopenssl

cd ~
gsutil cp gs://contestdata/config_updater.py .

git clone --branch v1.5.dev0-bdoi --recursive https://github.com/RezwanArefin01/cms.git 
cd cms
echo "##################################################################################"
python3 ./prerequisites.py -y --as-root install
usermod -a -G cmsuser root
pip3 install -r ./requirements.txt
python3 ./setup.py install

gsutil cp gs://contestdata/cms.conf /usr/local/etc/cms.conf
gsutil cp gs://contestdata/cms.ranking.conf /usr/local/etc/cms.ranking.conf