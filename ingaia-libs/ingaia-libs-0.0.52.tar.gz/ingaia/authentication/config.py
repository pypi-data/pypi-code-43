from ingaia.gcloud import ProjectReference

RSA_PROJECT_ID = 'ingaia-authentication-api'
RSA_BUCKET_LOCATION = 'southamerica-east1'
RSA_BUCKET = 'ingaia-authentication-public-rsa'
RSA_PUBLIC_KEY = 'jwt-key.pub'
RSA_PROJECT_REF = ProjectReference(RSA_PROJECT_ID, RSA_BUCKET_LOCATION)
