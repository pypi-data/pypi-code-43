#QB Error codes
#https://help.quickbase.com/api-guide/errorcodes.html
codes = {
  0: {
    "message": "No error",
    "response_code": 200
  },
  1: {
    "message": "Unknown error",
    "response_code": 500
  },
  2: {
    "message": "Invalid input",
    "response_code": 400
  },
  3: {
    "message":"Insufficient permissions",
    "response_code": 401
  },
  4: {
    "message": "Bad ticket",
    "response_code": 401,
  },
  5: {
    "message": "Unimplemented operation",
    "response_code": 501
  },
  6: {
    "message": "Syntax error",
    "response_code": 400
  },
  7: {
    "message": "API not allowed on this application table",
    "response_code": 400
  },
  8: {
    "message": "SSL required for this application table",
    "response_code": 401
  },
  9: {
    "message": "Invalid choice",
    "response_code": 400
  },
  10: {
    "message": "Invalid field type",
    "response_code": 400
  },
  11: {
    "message": "Could not parse XML input",
    "response_code": 400
  },
  12: {
    "message": "Invalid source DBID",
    "response_code": 400
  },
  13: {
    "message": "Invalid account ID",
    "response_code": 400
  },
  14: {
    "message": "Missing DBID or DBID of wrong type",
    "response_code": 400
  },
  15: {
    "message": "Invalid hostname",
    "response_code": 400
  },
  19: {
    "message": "Unauthorized IP address",
    "response_code": 401
  },
  20: {
    "message": "Unknown username/password",
    "response_code": 401
  },
  21: {
    "message": "Unknown user",
    "response_code": 401
  },
  22: {
    "message": "Sign-in required",
    "response_code": 401
  },
  23: {
    "message": "Feature not supported",
    "response_code": 501
  },
  24: {
    "message": "Invalid application token",
    "response_code": 401
  },
  25: {
    "message": "Duplicate application token",
    "response_code": 401
  },
  26: {
    "message": "Max count",
    "response_code": 400
  },
  27: {
    "message": "Registration required",
    "response_code": 403
  },
  28: {
    "message": "Managed by LDAP",
    "response_code": 400
  },
  29: {
    "message": "User on Deny list",
    "response_code": 403
  },
  30: {
    "message": "No such record",
    "response_code": 400
  },
  31: {
    "message": "No such field",
    "response_code": 400
  },
  32: {
    "message": "The application does not exist or was deleted",
    "response_code": 410
  },
  33: {
    "message": "No such query",
    "response_code": 400
  },
  34: {
    "message": "You cannot change the value of this field",
    "response_code": 403
  },
  35: {
    "message": "No data returned",
    "response_code": 400
  },
  36: {
    "message": "Cloning error",
    "response_code": 500
  },
  37: {
    "message": "No such report",
    "response_code": 400
  },
  38: {
    "message": "Periodic report contains a restricted field",
    "response_code": 400
  },
  50: {
    "message": "Missing required field",
    "response_code": 400
  },
  51: {
    "message": "Attempting to add a non-unique value to a field marked unique",
    "response_code": 400
  },
  52: {
    "message": "Duplicate field",
    "response_code": 400
  },
  53: {
    "message": "Fields missing from your import data",
    "response_code": 400
  },
  54: {
    "message": "Cached list of records not found",
    "response_code": 400
  },
  60: {
    "message": "Update conflict detected",
    "response_code": 409
  },
  61: {
    "message": "Schema is locked",
    "response_code": 409
  },
  70: {
    "message": "Account size limit exceeded",
    "response_code": 403
  },
  71: {
    "message": "Database size limit exceeded",
    "response_code": 403
  },
  73: {
    "message": "Your account has been suspended",
    "response_code": 403
  },
  74: {
    "message": "You are not allowed to create applications",
    "response_code": 403
  },
  75: {
    "message": "View too large",
    "response_code": 400
  },
  76: {
    "message": "Too many criteria",
    "response_code": 400
  },
  77: {
    "message": "API request limit exceeded",
    "response_code": 400
  },
  78: {
    "message": "Data limit exceeded",
    "response_code": 403
  },
  80: {
    "message": "Overflow",
    "response_code": 403
  },
  81: {
    "message": "Item not found",
    "response_code": 400
  },
  82: {
    "message": "Operation took too long",
    "response_code": 408
  },
  83: {
    "message": "Access denied",
    "response_code": 403
  },
  84: {
    "message": "Database error",
    "response_code": 500
  },
  85: {
    "message": "Schema update error",
    "response_code": 500
  },
  87: {
    "message": "Invalid group",
    "response_code": 400
  },
  100: {
    "message": "Technical Difficulties -- try again later",
    "response_code": 500
  },
  101: {
    "message": "Quick Base is temporarily unavailable due to technical difficulties",
    "response_code": 500
  },
  102: {
    "message": "Invalid request - we cannot understand the URL you specified",
    "response_code": 400
  },
  103: {
    "message": "The Quick Base URL you specified contained an invalid srvr parameter",
    "response_code": 400
  },
  104: {
    "message": "Your Quick Base app is experiencing unusually heavy traffic. Please wait a few minutes and re-try this command.",
    "response_code": 408
  },
  105: {
    "message": "Quick Base is experiencing technical difficulties",
    "response_code": 500
  },
  110: {
    "message": "Invalid role",
    "response_code": 400
  },
  111: {
    "message": "User exists",
    "response_code": 400
  },
  112: {
    "message": "No user in role",
    "response_code": 400
  },
  113: {
    "message": "User already in role",
    "response_code": 400
  },
  114: {
    "message": "Must be admin user",
    "response_code": 401
  },
  150: {
    "message": "Upgrade plan",
    "response_code": 403
  },
  151: {
    "message": "Expired plan",
    "response_code": 403
  },
  152: {
    "message": "App suspended",
    "response_code": 403
  }
}