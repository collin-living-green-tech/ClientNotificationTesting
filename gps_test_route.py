import requests
import time


# a test for one route based on a single pickup day and artificially generated gps info
# OPERATES IN DEBUG OR REGULAR MODE
# DEBUG MODE POSTS TO THE LOCAL DEVELOPMENT REST API ENDPOINTS
# REGULAR MODE REST CALLS ARE MADE TO PRODUCTION

# CREDENTIALS NEED TO REQUESTED FROM THE DEVELOPMENT TEAM

"""
steps:
    1)  set up the gps array
    2)  at an interval of once / 5 secs
        post update to api endpoint
"""

# put the gps data into array

gps_coords = []

with open('gps_short.txt', 'r') as fp:

    for line in fp:
        coords = line.split(',')[0:2]
        gps_coords.append(coords)

partial_gps_coords =[]
for i in range(0,len(gps_coords)):
    partial_gps_coords.append(gps_coords[i])

# now just make api call at 15 second intervals:
# maybe just take every 5th index

debug = True

# set all the urls to dev environment
if debug == True:
    login_url = 'http://localhost:8000/token/'
    test_setup_url = 'http://localhost:8000/apis/test/setup/'
    newday_url = 'http://localhost:8000/apis/routes/newday/'
    route_update_url = 'http://localhost:8000/apis/routeupdate/create/'
else:
    login_url = 'https://lgtpickup.net/token/'
    test_setup_url = 'https://lgtpickup.net/apis/test/setup'
    newday_url = 'https://lgtpickup.net/apis/routes/newday/'
    route_update_url = 'https://lgtpickup.net/apis/routeupdate/create/'


# setup get token etc.

# data
# input the credentials for testing
auth_data = {"username":"", "password":""}
if auth_data["username"]=="":
    raise Exception("please request credentials")

resp = requests.request("POST", login_url, data=auth_data).json()

token = resp['access']
headers = { "Authorization": "Bearer {}".format(token)}
# do testing setup
res = requests.request('GET',test_setup_url, headers=headers)

time.sleep(5)
# make call to startday endpoint
resp = requests.request('GET', newday_url, headers=headers)

total_updates = len(partial_gps_coords)
idx = 0
time.sleep(10)

err_no = 0
for update in partial_gps_coords:

    coords_data = {'lat':float(update[1]),'lng':float(update[0])}
    try:
        resp = requests.request('POST', route_update_url, data=coords_data, headers=headers)
        res_content = resp.text
        if resp.status_code != 200:
            err_no+= 1
            with open("Error.html","w") as fp:
                fp.write(res_content)

            raise Exception(resp.status_code)



        #print(str(res_content,'UTF-8'))
        res = int(res_content)
    except Exception as error:

        print("Error last call returned {}\nSee Error.html in the project directory for more info.".format(error))

        break

    print("{} out of {} routes remaining:{}\tresp code:{}".format(idx,total_updates,res,resp.status_code))
    idx+=1
    if res == 0:
        break
    time.sleep(5)


