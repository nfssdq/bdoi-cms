from google.cloud import storage
from googleapiclient import discovery
import json
import sys
import subprocess

compute = discovery.build('compute', 'v1')
bucket = storage.Client().bucket('bdoi')
zones = ['asia-southeast1-a', 'asia-southeast1-b',
         'asia-southeast1-c', 'asia-south1-a']


def list_servers(servertype=None):
    servers = []
    for zone in zones:
        instances = compute.instances().list(project='bdoi2020', zone=zone).execute()
        if 'items' not in instances:
            continue
        for item in instances['items']:
            has_servertype = False
            for kv in item['metadata']['items']:
                if kv['key'] == 'servertype':
                    has_servertype = True
                    if servertype is not None and kv['value'] == servertype:
                        servers.append([
                            item['networkInterfaces'][0]['networkIP'],
                            item['name'], zone])
            if has_servertype is False and servertype is None:
                servers.append([
                    item['networkInterfaces'][0]['networkIP'],
                    item['name'], zone])
    return servers


def load_conf():
    blob = bucket.get_blob('cms.conf')
    data = blob.download_as_string()
    return json.loads(data)


def save_conf(conf):
    bucket.blob('cms.conf').upload_from_string(json.dumps(conf))


def process_workers(conf, admin, worker, ranking):
    services = conf['core_services']
    other_services = conf['other_services']
    services['LogService'] = [[admin[0], 29000]]
    services['AdminWebServer'] = [[admin[0], 21100]]
    services['ProxyService'] = [[admin[0], 28600]]
    services['EvaluationService'] = [[admin[0], 25000]]
    services['ResourceService'] = []
    services['ScoringService'] = []
    services['Checker'] = []
    services['Worker'] = []
    services['ContestWebServer'] = []
    conf['rankings'] = []
    other_services['TestFileCacher'] = []
    conf['contest_listen_address'] = []
    conf['contest_listen_port'] = []

    services['ResourceService'].append([admin[0], 28000])
    conf['admin_listen_address'] = admin[0]

    for server in worker:
        services['ResourceService'].append([server[0], 28000])
        services['ScoringService'].append([server[0], 28500])
        services['Checker'].append([server[0], 22000])
        services['Worker'].append([server[0], 26000])
        services['Worker'].append([server[0], 26001])
        services['Worker'].append([server[0], 26002])
        services['Worker'].append([server[0], 26003])
        services['ContestWebServer'].append([server[0], 21000])
        conf['contest_listen_address'].append(server[0])
        conf['contest_listen_port'].append(8888)
        other_services['TestFileCacher'].append([server[0], 27501])

    for server in ranking:
        conf['rankings'].append(
            "http://bdoi2020:jdmnpn@{}:8890/".format(server[0]))


def make_commands(cid):
    return [
        'sudo gsutil cp gs://bdoi/cms.conf /usr/local/etc/cms.conf',
        'sudo screen -XS cmsResourceService quit',
        'sudo screen -S cmsResourceService -d -m cmsResourceService -a {}'.format(cid)]


def reload(instance, zone, cid):
    for cmd in make_commands(cid):
        print(subprocess.run(
            ["gcloud compute ssh {} --zone={} --command=\"{}\"".format(
                instance, zone, cmd)], stdout=subprocess.PIPE, shell=True))


def controller(cid):
    admin = list_servers()
    worker = list_servers('contestworker')
    ranking = list_servers('rankingworker')
    conf = load_conf()
    process_workers(conf, admin[0], worker, ranking)
    print(json.dumps(conf))
    save_conf(conf)
    for server in worker:
        reload(server[1], server[2], cid)
    for cmd in make_commands(cid):
        print(subprocess.run([cmd], stdout=subprocess.PIPE, shell=True))


if __name__ == "__main__":
    controller(sys.argv[1])
