#!/usr/bin/env python3

import msal,json,sys,logging,requests,pprint

# Pass the parameters.json file as an argument to this Python script. E.g.: python your_py_file.py parameters.json
config = json.load(open(sys.argv[1]))



# Create a preferably long-lived app instance that maintains a token cache.
app = msal.ConfidentialClientApplication(
    config["client_id"], authority=config["authority"],
    client_credential=config["secret"],
    # token_cache=...  # Default cache is in memory only.
                       # You can learn how to use SerializableTokenCache from
                       # https://msal-python.rtfd.io/en/latest/#msal.SerializableTokenCache
    )

result = app.acquire_token_silent(config["scope"], account=None)

if not result:
    logging.info("No suitable token exists in cache, get a new one from AAD")
    result = app.acquire_token_for_client(scopes=config["scope"])


if "access_token" in result:
    print("Access token: " + result["token_type"], file=sys.stderr)

else:
    print(result.get("error"))
    print(result.get("error_description"))
    print(result.get("correlation_id")) #used for bug reporting if necessary

http_headers = {'Authorization': 'Bearer ' + result['access_token'],
                'Accept': 'application/json',
                'Content-Type': 'application/json'}


#set up a dict for the users and the licenses that the tenant has
users = {}
licenses = {}

#while there's a license_endpoint key in the config dict
while config["license_endpoint"] is not None:

    #query the endpoint in the licenses_endpoint key
    data = requests.get(config["license_endpoint"], headers=http_headers).json()
    
    #At this point there may be a @odata.nextLink key in the response - this will be the link to the next set of data
    if '@odata.nextLink' in data:
        config["license_endpoint"] = data['@odata.nextLink']

    #if there's no more data, set the endpoint to None (to break the while loop)
    else:
        config["license_endpoint"] = None
   
    #if the data includes a value key, read the licenses out of it into the license dict 
    if 'value' in data:
        for license in data['value']:
            licenses[license['skuId']] = license['skuPartNumber']

    #commented out, only used for debugging
    #pprint.pprint(data)

   
#Basically the same as above, but for users
while config["endpoint"] is not None:
    #get the first set of responses from the API
    data = requests.get(config["endpoint"], headers=http_headers).json()
    
    #At this point there may be a @odata.nextLink key in the response - this will be the link to the next set of data
    if '@odata.nextLink' in data:
        config["endpoint"] = data['@odata.nextLink']

    else:
        config["endpoint"] = None
    
    if 'value' in data:
        for user in data['value']:
            users[user['userPrincipalName']] = []
            for license in user['assignedLicenses']:
                users[user['userPrincipalName']].append(licenses[license['skuId']])

    #pprint.pprint(data)
    #print("\n\n")

    #print out some info to stderr so we can pipe the actual output somewhere and not have to worry about seeing it
    #if we dont, the script seems to just sit there for a while as it works
    print("Number of results so far: " + str(len(users)), file=sys.stderr)

#print out a csv in the following format:
#userprincipalname,LICENSE|LICENSE|LICENSE|etc
for user in users:
    print(user + "," + "|".join(users[user]))



