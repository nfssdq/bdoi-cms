#!python3

from google.cloud import storage
from google.cloud import secretmanager
from googleapiclient import discovery
import json
import sys
import subprocess


PROJECT_NAME = 'bdoi-cms'
SQL_INSTANCE_NAME = 'bdoi'
CONFIG_FILE_NAME = 'cms.conf'
CONTEST_DB_PASSWORD_SECRET_ID = 'cmsdb-password'
TELEGRAM_BOT_TOKEN_SECRET_ID = 'telegrambot-token'
TELEGRAM_BOT_CHAT_SECRET_ID = 'telegrambot-chat-id'

compute = discovery.build('compute', 'v1')
sqladmin = discovery.build('sqladmin', 'v1beta4')
secretmanagerclient = secretmanager.SecretManagerServiceClient()
bucket = storage.Client(project=PROJECT_NAME).bucket('contestdata')
zones = ['asia-southeast1-a', 'asia-southeast1-b',
         'asia-southeast1-c', 'asia-south1-a']


def list_servers(servertype):
    # returns a list of server
    # each server is a list of three items [ip, name, zone].
    servers = []
    for zone in zones:
        instances = compute.instances().list(
            project=PROJECT_NAME, zone=zone,
            filter='labels.type={}'.format(servertype)).execute()
        if 'items' not in instances:
            continue
        for item in instances['items']:
            has_servertype = False
            if item['labels']['type'] == servertype:
                servers.append([
                    item['networkInterfaces'][0]['networkIP'],
                    item['name'], zone])
    return servers


def load_conf():
    blob = bucket.get_blob(CONFIG_FILE_NAME)
    data = blob.download_as_string()
    return json.loads(data)


def save_conf(conf):
    bucket.blob(CONFIG_FILE_NAME).upload_from_string(
        json.dumps(conf, indent=4))


def get_secret(secret_id):
    secret = secretmanagerclient.access_secret_version(
        name='projects/{}/secrets/{}/versions/latest'.format(
            PROJECT_NAME, secret_id))
    return secret.payload.data.decode('utf-8')


def populate_workers(conf, admin, workers, rankingservers):
    services = conf['core_services']
    other_services = conf['other_services']

    # admin server
    services['LogService'] = [[admin[0], 29000]]
    services['AdminWebServer'] = [[admin[0], 21100]]
    services['ProxyService'] = [[admin[0], 28600]]
    services['EvaluationService'] = [[admin[0], 25000]]
    services['ResourceService'] = [[admin[0], 28000]]
    conf['admin_listen_address'] = admin[0]

    # contest server workers
    services['ResourceService'].extend(
        [[server[0], 28000] for server in workers])
    services['ScoringService'] = [[server[0], 28500] for server in workers]
    services['Checker'] = [[server[0], 22000] for server in workers]
    services['Worker'] = [[server[0], 26000] for server in workers]
    services['Worker'].extend([[server[0], 26001] for server in workers])
    services['Worker'].extend([[server[0], 26002] for server in workers])
    services['Worker'].extend([[server[0], 26003] for server in workers])
    other_services['TestFileCacher'] = [[server[0], 27501]
                                        for server in workers]

    # contest web service
    services['ContestWebServer'] = [[server[0], 21000] for server in workers]
    conf['contest_listen_address'] = [server[0] for server in workers]
    conf['contest_listen_port'] = [8888 for server in workers]

    # ranking servers
    conf['rankings'] = []
    for server in rankingservers:
        conf['rankings'].append(
            "http://ranking:jdmnpn@{}:8890/".format(server[0]))

    # telegram config
    conf['telegram_bot_token'] = get_secret(TELEGRAM_BOT_TOKEN_SECRET_ID)
    conf['telegram_bot_chat_id'] = int(get_secret(TELEGRAM_BOT_CHAT_SECRET_ID))


def make_commands(cid):
    return [
        'sudo gsutil cp gs://contestdata/cms.conf /usr/local/etc/cms.conf',
        'sudo screen -XS cmsResourceService quit',
        'sudo screen -S cmsResourceService -d -m cmsResourceService -a {}'
        .format(cid)]


def reload(instance, zone, commands):
    print("reloading {} in zone {}".format(instance, zone))
    for cmd in commands:
        result = subprocess.run(
            ["gcloud compute ssh {} --zone={} --command=\"{}\"".format(
                instance, zone, cmd)], stdout=subprocess.PIPE, shell=True)
        if result.returncode != 0:
            print("error running {}, stdout: {}".format(
                result.args, result.stdout))


def populate_db(conf):
    instance = sqladmin.instances().get(
        project=PROJECT_NAME, instance=SQL_INSTANCE_NAME).execute()
    ip = instance['ipAddresses'][0]['ipAddress']
    conf['database'] = \
        'postgresql+psycopg2://cmsuser:{}@{}:5432/cmsdb'.format(
            get_secret(CONTEST_DB_PASSWORD_SECRET_ID), ip)


def controller(cid=None):
    admin = list_servers('adminserver')[0]
    workers = list_servers('contestserver')
    ranking = list_servers('rankingserver')

    conf = load_conf()
    populate_db(conf)
    populate_workers(conf, admin, workers, ranking)
    print(json.dumps(conf, indent=4))
    save_conf(conf)

    if cid is None:
        return

    commands = make_commands(cid)
    [reload(server[1], server[2], commands) for server in workers]
    [reload(server[1], server[2], commands) for server in ranking]

    commands = [
        'sudo screen -XS cmsLogService quit',
        'sudo screen -S cmsLogService -d -m cmsLogService'] + commands
    reload(admin[1], admin[2], commands)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        controller(cid=sys.argv[1])
    else:
        controller()
