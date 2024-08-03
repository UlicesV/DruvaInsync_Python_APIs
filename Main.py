import requests
import json
import os
import time
import sys
import argparse

# Import Libs required for Bearer Token OAuth2.0
from oauthlib.oauth2 import BackendApplicationClient
from requests.auth import HTTPBasicAuth
from requests_oauthlib import OAuth2Session

# https://developer.druva.com/docs/get-bearer-token
client_id = os.environ.get('Client_ID')
secret_key = os.environ.get('Secret_Key') 
domain = os.environ.get('domain')  # Domain is just email address example: @ulices.org but with %40 instead of @ 

headers = {
    "accept": "application/json",
    "content-type": "application/x-www-form-urlencoded"
    }

# https://developer.druva.com/reference#reference-getting-started
def get_token(client_id, secret_key):
	global token
	auth = HTTPBasicAuth(client_id, secret_key)
	client = BackendApplicationClient(client_id=client_id)
	oauth = OAuth2Session(client=client)
	response = oauth.fetch_token(token_url='https://apis.druva.com/token', auth=auth)
	token = response['access_token']

def updateUser(offUser,domain):
    get_token(client_id, secret_key)
    offUser = str(offUser)
    url = "https://apis.druva.com/insync/usermanagement/v1/users?emailID=" + offUser + domain #Username input placed into URL for single User
    headers['Authorization'] = 'Bearer ' + str(token)
    response = requests.get(url, headers=headers)
    # Check if the request was successful
    if response.status_code == 200:
        #Write JSON data to file with indentation
        data = response.json()
        with open('User_info.json', 'w') as file: 
            json.dump(data, file, indent=4)
        # Parse the JSON response
        json_data = response.json()
        # Extract the variables
        global user_id
        global preserve_status
        global emailID
        global userName
        global profileID
        profileID = json_data["users"][0]["profileID"]
        userName = json_data["users"][0]["userName"]
        emailID = json_data["users"][0]["emailID"]
        user_id = json_data["users"][0]["userID"]
        preserve_status = json_data["users"][0]["status"]
        getProfiles(profileID)
        print( 'User_info.json updated')
    else:
        print("Error:", response.text)

#https://developer.druva.com/reference/get_profilemanagement-v1-profiles
def getProfiles(profileID):
    url = "https://apis.druva.com/insync/profilemanagement/v1/profiles"
    headers['Authorization'] = 'Bearer ' + str(token)
    response = requests.get(url, headers=headers)
    data = response.json()
    with open('Profiles_list.json','w') as file:
        json.dump(data, file, indent=4)
 
    #Find the profileID for "offboarded" so that I can assign it to a variable
    for profile in data.get("profiles", []):
        if profile.get("profileName") == "Offboarded":
            global offboardedProfileID
            offboardedProfileID = profile.get("profileID")

    #Find the profileID match so that we can return the profile's name and description
    for profile in data.get("profiles", []):
        if profile.get("profileID") == profileID:
            global currentProfile
            global currentProfileDescription
            currentProfile = profile.get("profileName")
            currentProfileDescription = profile.get("profileDescription")

#https://developer.druva.com/reference/post_usermanagement-v1-users-userid-preserve
def preserveUser(user_id):
    if preserve_status == "preserved":
        print(f'{userName} is already preserved')
    else:
        user_id = str(user_id)
        url = "https://apis.druva.com/insync/usermanagement/v1/users/"+ user_id + "/preserve"
        headers['Authorization'] = 'Bearer ' + str(token)
        response = requests.post(url, headers=headers)
        updateUser(offUser,domain)
        print(f"{userName} is now " + preserve_status)

#https://developer.druva.com/reference/patch_usermanagement-v1-users-userid
def updateUsername(user_id,endDate):
    url = "https://apis.druva.com/insync/usermanagement/v1/users/"+ str(user_id)
    payload = { "userName":"z_"+endDate+"_"+offUser}
    headers['content-type'] = "application/json"
    headers['Authorization'] = 'Bearer ' + str(token)
    response = requests.patch(url, json=payload, headers=headers)
    updateUser(offUser,domain)
    print("Username is now " + userName)

#https://developer.druva.com/reference/patch_usermanagement-v1-users-userid
def updateProfile(user_id,offboardedProfileID):
    if str(profileID) != str(offboardedProfileID): 
        url = "https://apis.druva.com/insync/usermanagement/v1/users/"+ str(user_id)
        payload = { "profileID": offboardedProfileID }
        headers['content-type'] = "application/json"
        headers['Authorization'] = 'Bearer ' + str(token)
        response = requests.patch(url, json=payload, headers=headers)
        updateUser(offUser,domain)
        getProfiles(profileID)
        print(f"{userName}\'s profile is now " + str(currentProfile)+ ": " + str(currentProfileDescription))
    else:
        print(f'{userName}\'s profile is already {currentProfile}')

def checkUserInfo():
    print("Username: " + str(userName))
    print("Email: " + str(emailID))
    print("Status: " + str(preserve_status))
    print("Profile: " + str(currentProfile) + ": " +str(currentProfileDescription))

#https://developer.druva.com/reference/getcustomerjobs
def downloadjobs():
    get_token(client_id,secret_key)
    url = f"https://apis.druva.com/insync/legalholds/v4/jobs?jobStatus=Queued&custodian={userName}" #Once the download is initiated - the status is set to 'Queued'
    headers['content-type'] = "application/json"
    headers['Authorization'] = 'Bearer ' + str(token)
    response = requests.get(url, headers=headers)
    data2 = response.json()
    with open('jobs_archive.json', 'w',) as file:
        json.dump(data2, file, indent =4)  #Create an archive of all jobIds so we can pass to checkjobs. Open download_jobs and you'll notice it is empty
    while True:
        get_token(client_id,secret_key)
        url = f"https://apis.druva.com/insync/legalholds/v4/jobs?jobStatus=Queued&custodian={userName}" #Once the download is initiated - the status is set to 'Queued'
        headers['content-type'] = "application/json"
        headers['Authorization'] = 'Bearer ' + str(token)
        response = requests.get(url, headers=headers)
        data = response.json()
        with open('download_jobs','w') as file:
            json.dump(data, file, indent=4)
        cycle = 1
        for job in data['jobs']:
            print(f"Job ID: {job['jobId']}")
            print(f"custodianEmail:{job['custodianEmail']}")
            print(f"DataSource: {job['dataSource']}")
            print(f"Job Status: {job['jobStatus']}")
            print(f"Waiting for Job status change - {cycle}") # Just to make sure the program isn't stuck in the loop
            print()

        all_jobs_completed = all(job['jobStatus'] != 'Queued' for job in data['jobs'])
    
        if all_jobs_completed:
            job_ids = [job['jobId'] for job in data2['jobs']]
            for job_id in job_ids: # Iterate through each job ID and call checkJob()
                checkJob(job_id)
            print('Please check download status in https://console.druva.com/admin/app/#/governance/legalhold/downloadjobs')
            break
        cycle += 1
        time.sleep(30)
        

#https://developer.druva.com/reference/getdetailsofjob
def checkJob(job_id):
    get_token(client_id,secret_key)
    url = f"https://apis.druva.com/insync/legalholds/v4/job/{job_id}" # insert Job ID into link to check Job Status and other info
    headers['content-type'] = "application/json"
    headers['Authorization'] = 'Bearer ' + str(token)
    response = requests.get(url, headers=headers)
    data = response.json()
    with open('Job_Status','w') as file:
        json.dump(data, file, indent=4)
    job_id = data['jobId']
    download_location = data['downloadLocation']
    job_status = data['jobStatus']
    custodian = data['custodian']
    datasource = data['dataSource']

    print(f"Job ID: {job_id}")
    print(f"Datasource: {datasource}")
    print(f"Download Location: {download_location}")
    print(f"Job Status: {job_status}")
    print(f"Custodian: {custodian}")

#https://developer.druva.com/reference/get_legalholds-v3-policies
def getLegalHolds():
    url = "https://apis.druva.com/insync/legalholds/v3/policies"
    headers['Authorization'] = 'Bearer ' + str(token)
    response = requests.get(url, headers=headers)
    data = response.json()
    with open('LegalHolds_list','w') as file:
        json.dump(data, file, indent=4)
    #Now let's parse the file and find the legal hold policyID so we can use it in def initiateDownload()
    for legalHold in data.get("legalholdList", []):
        if legalHold.get("name") == "Offboarded":
            global legalHoldID
            legalHoldID = legalHold.get("policyId")

#https://developer.druva.com/reference/createnewjob
def initiateDownload():
    url = "https://apis.druva.com/insync/legalholds/v4/job"
    payload = {
        "downloadOption": 2,
        "enable_data_integrity": True,
        "clientName": "CORP-WIN10-Druva",
        "legalholdId": legalHoldID,
        "downloadLocation": r"C:\DruvaDownloads",
        "createdBy": "Ulices Ventura Perez",
        "custodianEmails": [emailID]
    }
    headers['content-type'] = "application/json"
    headers['Authorization'] = 'Bearer ' + str(token)
    response = requests.post(url, json=payload, headers=headers)

#https://developer.druva.com/reference/post_legalholds-v3-policies-policyid-users
#Place offUser into legal hold 'Offboarded'
def legalHoldUser():
    import requests
    url = f"https://apis.druva.com/insync/legalholds/v3/policies/{legalHoldID}/users" #legalHoldID pulled from legalHolds_list 
    payload = {
        "action": "add",
        "custodians": [{ "emailId": f"{emailID}" }]    #emailID pulled from User_info
    }
    headers['content-type'] = "application/json"
    headers['Authorization'] = 'Bearer ' + str(token)
    response = requests.post(url, json=payload, headers=headers)

offUser = None
endDate = None
option = None

    #Argument parsing setup
parser = argparse.ArgumentParser(description='Offboard users from Druva Insync.')
parser.add_argument('-u', '--username', metavar='USERNAME', type=str, help='Username to offboard ')
parser.add_argument('-d', '--enddate', metavar='END_DATE', type=str, help='End date for offboarding in YYYY-MM-DD format')
parser.add_argument(f'-o', '--option', metavar='OPTION', type=str, help='Option to choose (1-6)\n Please select an option for {userName}\n 1. Change username to z_{endDate}_{offUser} \n 2. Preserve user \n 3. Change profile to Offboarded \n 4. Check User info \n 5. All of the above \n 6. Download User Data\n 7. Quit\n')

    #Parse arguments
args = parser.parse_args()

    #Assign parsed arguments to global variables
offUser = args.username
endDate = args.enddate
option = args.option

def main():
    global offUser, endDate, option, parser

    #os.system('cls')
    print('Hello! This program is to offboard users from Druva Insync. Please enter one user at a time.')
  
    if offUser is None:
        offUser = input('Who will you be offboarding? Please enter only their username. \n')

    if endDate is None:
        endDate = input(f'Please enter {offUser}\'s end date in this format: YYYY-MM-DD \n')

    updateUser(offUser,domain) 
    #os.system('cls')

    while True:
        if option is None: 
         option = input(f'Please select an option for {userName}\n 1. Change username to z_{endDate}_{offUser} \n 2. Preserve user \n 3. Change profile to Offboarded \n 4. Check User info \n 5. All of the above \n 6. Download User Data\n 7. Quit\n')

        if option == '1':
                os.system('cls')
                print("Previous Username: " + userName)
                updateUsername(user_id, endDate)
                time.sleep(2)
                print()
                option = None
        elif option == '2':
                os.system('cls')
                print(f"{userName} status:" + preserve_status)
                preserveUser(user_id)
                time.sleep(2)
                print()
                option = None
        elif option == '3':
                os.system('cls')
                getProfiles(profileID)
                print("Previous User profile: " + currentProfile + ": " + currentProfileDescription)
                time.sleep(2)
                print()
                updateProfile(user_id, offboardedProfileID)
                print()
                option = None
        elif option == '4':
                os.system('cls')  # Clear screen (assuming Windows)
                checkUserInfo()
                time.sleep(5)
                print()
                option = None
        elif option == '5':
                os.system('cls')
                performAllActions()
                quit()
        elif option == '6':
                updateUsername(user_id, endDate)
                getLegalHolds()
                legalHoldUser()
                initiateDownload()
                downloadjobs()
                quit()
        elif option == '7':
                quit()
        else:
                print("Invalid option. Please choose a number between 1 and 7.")
                option = None

# Function for option 5
def performAllActions():
    updateUsername(user_id, endDate)
    preserveUser(user_id)
    updateProfile(user_id, offboardedProfileID)
    os.system('cls')
    print('Updated User info:\n')
    checkUserInfo()
    userInput = input('Ready to download? Yes or No ?\n')
    userInput = userInput.lower()
    if userInput == "yes":
        getLegalHolds()
        legalHoldUser()
        initiateDownload()
        downloadjobs()
        quit()
    elif userInput == "no":
        print('Goodbye.')
        quit()

if __name__ == "__main__":
  # Check if command-line arguments were provided
    if len(sys.argv) > 1:
        args = sys.argv[1:]
        if '-h' in args or '--help' in args:
            parser.print_help()    
            
            sys.exit()
        
        # Otherwise, assume user provided all required arguments
        parser = argparse.ArgumentParser()  # This is a dummy parser to ensure proper parsing
        main()
    else:
        main()