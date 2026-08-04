import pandas
import shutil,os
import time

currentUsers = pandas.read_csv('users.csv')
currentRegUsers = pandas.read_csv('users_adder.csv')

#EDIT THIS HERE IF YOU NEED
manualApproval = True
#^ ^ ^ ^ ^ this thing

print(len(currentRegUsers), 'Users in Registration Queue! owo')

if manualApproval == False:
    if input("Press enter to add ALL USERS in queue (anything else to cancel)") == "":
        print("Making backup...")
        shutil.copy('users.csv', 'users.csv.backup')
        shutil.copy('users_adder.csv', 'users_adder.csv.backup')
        print("wiping csv file and keeping backup...")
        shutil.copy('templates/users_adder.csv', 'users_adder.csv')

        currentRegUsers.to_csv('users.csv', mode='a', index=False, header=False)


if manualApproval == True:
    print("wiping csv file and keeping backup...")
    shutil.copy('users.csv', 'users.csv.backup')
    shutil.copy('users_adder.csv', 'users_adder.csv.backup')
    shutil.copy('templates/users_adder.csv', 'users_adder.csv')

    for i in currentRegUsers.itertuples(name=None):
        print('\nusername :', i[1])
        if input("Enter Y to add user, N to skip ").lower() == 'y':
            continue
        else:
            currentRegUsers.drop([i[0]], inplace=True)

    print("\nConfirm Adding users:\n",currentRegUsers)
    if input("Enter Y to confirm ").lower() == 'y':
        currentRegUsers.to_csv('users.csv', mode='a', index=False, header=False)


print("Done! Closing... :3")
time.sleep(3)