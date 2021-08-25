**backgrou**
You'll need to create a json file that includes a few properties that scripts will use for connecting to your tenant:
```
{
  "authority": "https://login.microsoftonline.com/YOUR_TENANT_ID",
  "client_id": "CLIEN_ID_OF_YOUR_INTEGRATION_IN_AZURE",
  "scope": [ "https://graph.microsoft.com/.default" ],
  "secret": "SUPER_SECRET_FROM_YOUR_INTEGRATION_IN_AZURE",
  "endpoint": "https://graph.microsoft.com/beta/users?$select=userprincipalname,assignedlicenses",
  "license_endpoint": "https://graph.microsoft.com/v1.0/subscribedSkus?$select=skupartnumber,skuid"
}
```

save it as `parameters.json`

[licensing.py]
This is used for connecting to the tenant to pull the whole list of users and get their licesnes. 

Run this with `licensing.py parameters.json`



