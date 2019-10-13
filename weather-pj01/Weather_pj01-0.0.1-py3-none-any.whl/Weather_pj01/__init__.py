import requests

"""Daily Forecast Function"""
def current(lat,lon):
	newurl="https://api.weather.com/v2/turbo/vt1observation?apiKey=d522aa97197fd864d36b418f39ebb323&format=json&geocode="+lat+"%2C"+lon+"&language=en-US&units=m"

	newurlo=requests.get(newurl)

	jsonObject=newurlo.json()

	details={}
	for k,v in jsonObject['vt1observation'].items():
		details[k]=v 
	details['temperature']=str(details['temperature'])+' °C'
	details['feelsLike']=str(details['feelsLike'])+' °C'
	details['humidity']=str(details['humidity'])+' %'
	details['dewPoint']=str(details['dewPoint'])+' °'
	details['visibility']=str(details['visibility'])+' km'
	details['windSpeed']=str(details['windSpeed'])+' km/h'
	details['temperatureMaxSince7am']=str(details['temperatureMaxSince7am'])+' °C'
	details['uvIndex']=str(details['uvIndex'])+' out of 10'
	details['altimeter']=str(details['altimeter'])+' mb'
	print("temperature: "+details['temperature'])
	delete=['temperature','icon','observationTime','obsQualifierCode','obsQualifierSeverity','barometerCode','barometerChange']
	
	for i in delete:
		del details[i]
	
	for k,v in details.items():
		print(k,end=": ")
		print(v)
	
	print('\n')


"""5-Day Forecast Function"""
def day_5(lat,lon):
	url3="https://api.weather.com/v2/turbo/vt1dailyForecast?apiKey=d522aa97197fd864d36b418f39ebb323&format=json&geocode="+lat+"%2C"+lon+"&language=en-IN&units=m"
	url3o=requests.get(url3)
	final3=url3o.json()
	details={}
	
	for k,v in final3['vt1dailyForecast'].items():
		details[k]=v
	
	for i in range(1,6):
		print(details['day']['dayPartName'][i],end=": ")
		print(str(details['day']['temperature'][i])+'°C')
	
	print('\n')


"""10-Day Forecast Function"""
def day_10(lat,lon):
	url3="https://api.weather.com/v2/turbo/vt1dailyForecast?apiKey=d522aa97197fd864d36b418f39ebb323&format=json&geocode="+lat+"%2C"+lon+"&language=en-IN&units=m"
	url3o=requests.get(url3)
	final3=url3o.json()
	details={}
	
	for k,v in final3['vt1dailyForecast'].items():
		details[k]=v
	
	for i in range(1,11):
		print(details['day']['dayPartName'][i],end=": ")
		print(str(details['day']['temperature'][i])+'°C')
	
	print('\n')


"""Main Program"""

wholeflag=True
while(wholeflag):
	flag=True
	while(flag):
		print("Enter City Name or enter 'e' to exit. ")
		place=input().lower()
		if(place=='e'):
			wholeflag=False
			break
		url2="https://api.weather.com/v3/location/search"
		searchparams={'apiKey':'d522aa97197fd864d36b418f39ebb323','format':'json' ,'language':'en-IN','locationType':'locale','query':place}
		urlo2=requests.get(url2,params=searchparams)
		final2=urlo2.json()

		for i in final2.values():
			head,sep,end=(i['address'][0].partition(','))
		if(head.lower()==place):
			flag=False
			break
		else:
			print("City Not Found!")
	
	if(not wholeflag):
		break		
	
	print("\n")

	for i in final2.values():
		lat=(i['latitude'][0])
		lon=(i['longitude'][0])
	lat = str("{0:.2f}".format(lat))
	lon = str("{0:.2f}".format(lon))

	flag=True
	while(flag):
		print("Enter '1','2','3' for daily forecast,5-day forecast,10-day forecast respectively:-")
		try:
			forecast=int(input())
			flag=False
		except:
			print("Enter correct number.")

	if(forecast==1):
		current(lat,lon)
	elif(forecast==2):
		day_5(lat,lon)
	else:
		day_10(lat,lon)

