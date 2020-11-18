import csv
import random
import string
import subprocess

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

counter_by_team = {}

def parse_and_generate_users():
    contestant_details = {}
    with open("contestants.csv") as f:
        reader = csv.DictReader(f)
        for row in reader:
            contestant_details[row['Email Address']] = {
                'First Name': row['First Name'],
                'Last Name': row['Last Name']
            }
    with open("national.csv", "r") as f:
        reader = csv.DictReader(f)
        w = open("contestants_creds.csv", "w")
        reader.fieldnames.extend(['First Name', 'Last Name', 'username', 'team', 'Day1 Password', 'Day2 Password'])
        writer = csv.DictWriter(w, fieldnames=reader.fieldnames)
        writer.writeheader()

        for row in reader:
            team = grade_code[ row['Class'] ]
            counter_by_team[team] = counter_by_team.get(team, 0) + 1
            username = team + "{0:0=3d}".format(counter_by_team[team])

            row['First Name'] = contestant_details[row['Email']]['First Name']
            row['Last Name'] = contestant_details[row['Email']]['Last Name']
            row['username'] = username
            row['team'] = team
            row['Day1 Password'] = ''.join(random.choice(string.ascii_uppercase) for i in range(7))
            row['Day2 Password'] = ''.join(random.choice(string.ascii_uppercase) for i in range(7))
            writer.writerow(row)
            
        for i in range(1, 6):
            username = 'TEST'+"{0:0=3d}".format(i)
            writer.writerow({
                'username': username, 
                'team': 'TEST',
                'Day1 Password': ''.join(random.choice(string.ascii_uppercase) for i in range(7)),
                'Day2 Password': ''.join(random.choice(string.ascii_uppercase) for i in range(7))})
        w.close()


parse_and_generate_users()