import DKConnection

conn = DKConnection.DKConnection('cloud.datakitchen.io', 'armand+hm@datakitchen.io', '%Gun8D9M' )
results = conn.TestsFromOrderRun('hemonc_prod', '23c6ac22-6088-11e9-8dda-12d21ed7aa80')
print results