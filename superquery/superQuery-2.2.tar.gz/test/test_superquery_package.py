from superQuery import SuperQuery

sq = SuperQuery()
mydata = sq.get_data("SELECT COUNT(*) as totalRows FROM `mydata-1470162410749.EVALUEX_PROD.projectsJobs`", get_stats=True, username="R14SnKpLY2", password="F4rY_Ovvsj")

print("Data:", mydata.data)
print("Cost:", mydata.stats["superQueryTotalCost"])
print("Savings %:", mydata.stats["saving"])

del sq

