from .. import constants
import re

def checkPassword(user,newpassword):
  prevpasslist = user.passowrdhistory
  for i in prevpasslist[0:constants.Conf.passwordpreviousdifferent]:
    if newpassword == prevpasslist[i]:
      return False
  for reexp in constants.Conf.passwordrelist:
    myre = re.compile(reexp)
    if myre.search(newpassword) is None:
      return False
  return True



