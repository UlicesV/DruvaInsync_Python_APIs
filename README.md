# DruvaInsync_Python_APIs
Use Druva Insync Cloud APIs to automate tasks. Here I am using APIs to download user data from Druva onto an external hard drive. 


Prerequisites:
WindowsOS Computer to install the eDiscovery Download Client

Follow this guide

Create and Manage API Credentials: https://help.druva.com/en/articles/8580838-create-and-manage-api-credentials#h_0d43dc0f06

PLEASE MAKE SURE eDiscovery Download Client is running and is 'Successfully Registered' - application must remain running at all times.
To Register the download client: https://help.druva.com/en/articles/8513274-register-ediscovery-download-client

OS Environment Variables need to be created. 
client_id = os.environ.get('Client_ID')
secret_key = os.environ.get('Secret_Key')
domain = os.environ.get('domain')
Script assumes there is a Profile in Druva Insync already created named "Offboarded"
Script assumes there is a Legal Hold in Druva Insync named "Offboarded"

Re-naming user format is inside of the function def updateUsername(user_id,endDate) - defined in payload variable

Python Libraries:
pip install oauthlib
python -m pip install requests
pip install requests requests-oauthlib

Run the program with arguments from command line: 
Open Command Prompt
Copy/Paste: C:/Users/sa-druvabackup/AppData/Local/Programs/Python/Python312/python.exe c:/Users/sa-druvabackup/Desktop/DruvaOffboard/Main.py
You can enter the parameter -h or --help to prompt the help menu

Example Usage: 
C:/Users/sa-druvabackup/AppData/Local/Programs/Python/Python312/python.exe c:/Users/sa-druvabackup/Desktop/DruvaOffboard/Main.py -u ulicestest -d 2024-06-28 -o 5

Running the above example will complete all offboarding steps and then prompt you if you'd like to download user data. 
User Data is downloaded locally into: C:\DruvaDownloads 
This can be changed in the function def initiateDownload() with the payload variable. Change the value of 'downloadLocation'
Unfortunately Druva Inync Download Client does not support downloading to external drives that are NAS drives. They mentioned they will add to feature requests. 
