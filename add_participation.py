import csv
import subprocess
import random
import string

def execute(command):
    print(command)
    process = subprocess.run(command, stdout=subprocess.PIPE)
    if process.returncode != 0:
        print(process)
    # process.check_returncode()

def parse_and_generate_users(contest_id):
    with open("contestants.csv", "r") as f:
        reader = csv.DictReader(f)
        w = open("contestants_creds.csv", "w")
        reader.fieldnames.extend(['password'])
        writer = csv.DictWriter(w, fieldnames=reader.fieldnames)
        writer.writeheader()

        for row in reader:
            team = row['team']
            username = row['username']
            password = ''.join(random.choice(string.ascii_uppercase) for i in range(7))
            execute(['cmsAddParticipation', '-c', "{}".format(contest_id), '-t', team, '-p', password, '--bcrypt', username])
            row['password'] = password
            writer.writerow(row)
        w.close()

parse_and_generate_users(3)
