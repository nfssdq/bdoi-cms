import csv
import subprocess
import random
import string

grade_code = {
    "Class 7": "C07",
    "Class 8": "C08",
    "Class 9": "C09",
    "Class 10": "C10",
    "Class 11": "C11",
    "Class 12": "C12",
    "SSC Candidates": "SSC",
    "HSC Candidates": "HSC",
    "Others": "OTH",
}

def execute(command):
    print(command)
    process = subprocess.run(command, stdout=subprocess.PIPE)
    if process.returncode != 0:
        print(process)
    process.check_returncode()

def add_users():
    with open("contestants_creds.csv", "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['Email'] == '':
                execute(['cmsAddUser', 'Test', row['team'], row['username']])
                continue
            execute(['cmsAddUser', 
                '--email', row['Email'],
                '--timezone', 'Asia/Dhaka',
                r"""{}""".format(row['First Name']),
                r"""{}""".format(row['Last Name']),
                row['username']])


def add_participation(contest_id, password_field):
    with open("contestants_creds.csv", "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            execute(['cmsAddParticipation', 
                '-c', "{}".format(contest_id), 
                '-t', row['team'], 
                '-p', row[password_field], '--bcrypt', 
                row['username']])

def add_teams():
    for name, team in grade_code.items():
        execute(['cmsAddTeam', team, name])

add_teams()
add_users()
add_participation(4, 'Day1 Password')
add_participation(5, 'Day2 Password')