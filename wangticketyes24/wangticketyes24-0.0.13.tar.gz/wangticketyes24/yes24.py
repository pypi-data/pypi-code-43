
import sys
import requests
import datetime
import time
import traceback
from threading import Thread

from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import urllib
import re

from .selenium_yes24 import Selenium_yes24

class PerfDate(object):
	def __init__(self, date):
		mydatetime = datetime.datetime.strptime(date, "%Y-%m-%d")
		self.weekday = mydatetime.weekday()
		self.date = mydatetime.strftime("%Y%m%d")
		self.perftimes = None

	def setPerfTimes(self, perftimes):
		self.perftimes = perftimes

	def getPerfTimes(self):
		return self.perftimes

	def isPrefered(self, arr):
		if arr is None:
			return True

		for datestr in arr:
			d = datetime.datetime.strptime(datestr, "%Y-%m-%d %H:%M")
			if self.date == d.strftime("%Y%m%d"):
				return True
		return False

	def __repr__(self):
		whatday = ['MON','TUE','WED','THU','FRI','SAT','SUN'][self.weekday]
		return "---{}({})---".format(self.date, whatday)

class PerfTime(object):
	def __init__(self, timeid, date, timeinfo, idhall):
		self.timeid = timeid
		self.date = date
		mydatetime = datetime.datetime.strptime(timeinfo, "%H시 %M분")
		self.timeinfo = mydatetime.strftime("%H:%M")
		self.idhall = idhall
		self.seatdata = None

	def __repr__(self):
		return "[{}] {} {}".format(self.timeid, self.date, self.timeinfo)

	def isPrefered(self, arr):
		if arr is None:
			return True

		for datestr in arr:
			d = datetime.datetime.strptime(datestr, "%Y-%m-%d %H:%M")
			if self.date == d.strftime("%Y%m%d") and self.timeinfo == d.strftime("%H:%M"):
				return True
		return False

	def setSeatData(self, seatdata):
		self.seatdata = seatdata

	def getPreferedSeat(self, count=2, prefer=None, serial=True, strict=True, sort='left'):
		myseatdata = self.seatdata
		#myseatdata = self.seatdata[::-1]
		#seatcount = len(self.seatdata)
		#myseatdata = self.seatdata[seatcount//2:]

		"""
		#print start
		seatlen = min(len(myseatdata), 5)
		for seat in myseatdata[:seatlen]:
			print(seat)
		extralen = len(myseatdata) - seatlen
		if extralen > 0:
			print('......({} more)'.format(extralen))
		#print end
		"""
		print("Totally...{} seats...".format(len(myseatdata)))

		if prefer is not None:
			print("prefer is not None")
			myseatdata = [seat for seat in myseatdata if seat.isSeatPrefered(prefer)]

		if serial:
			#serial check
			while len(myseatdata) > 1:
				seat1 = myseatdata[0]
				seat2 = myseatdata[1]
				if not seat1.isSeatSerial(seat2):
					myseatdata.remove(seat1)
				else:
					break

		if len(myseatdata) == 0:
			print(self.timeid, ":seatdata is 0")
			return []
		elif len(myseatdata) < count:
			if strict:
				print(self.timeid, ":seatdata is less than", count, "(abort buying)")
				return []
			else:
				print(self.timeid, ":seatdata is less than", count, "(but buying)")
		else:
			if count == 1 and (sort == 'center' or sort == 'right'):
				print("You changed sort as {}..".format(sort))
				first = myseatdata[0]
				firstrow = []
				for s in myseatdata:
					if s.seat_row != first.seat_row:
						break
					firstrow.append(s)
				print(firstrow)
				if sort == 'center':
					myseatdata = [firstrow[len(firstrow)//2]]
				else:
					myseatdata = [firstrow[-1]]
			else: # left or invalid param
				myseatdata = myseatdata[0:count]

		return myseatdata

class Yes24(object):
	def __init__(self, idperf, idtime, idhall):
		self.session = requests.Session()
		self.idperf = idperf
		self.idtime = idtime
		self.idhall = idhall
		self.triedSeats = []
		#self.customerid = None
		#self.ipmanager = IPManager()

	def login(self, loginid, loginpw):
		self.loginid = loginid
		self.loginpw = loginpw
		URL = "http://ticket.yes24.com/Pages/Login/Ajax/AxLoginEnt.aspx"
		headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36'}
		payload = {'PLoginID':loginid, 'PPassword':loginpw}
		r = self.session.post(URL, headers=headers, data=payload)
		print("[login]", r.status_code, r.reason, r.headers['Date'])
		print(r.text)
		#age = self.session.cookies['Mallinmall_CKMAG']
		#print('age:', age)
		#self.customerid = self.session.cookies['Mallinmall_CKMN']
		#print('customerid:',self.customerid)

	def login2(self, loginid, loginpw):
		self.loginid = loginid
		self.loginpw = loginpw
		#URL = "http://ticket.yes24.com/Pages/Login/Ajax/AxLoginEnt.aspx"
		URL = "https://www.yes24.com/Templates/FTLogin.aspx?ReturnURL=http://ticket.yes24.com/"
		headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36'}
		headers['origin'] = 'https://www.yes24.com'
		headers['referer'] = 'https://www.yes24.com/Templates/FTLogin.aspx'

		payload = {'SMemberID':loginid, 'SMemberPassword':loginpw}
		payload['LoginType'] = ''
		payload['RefererUrl'] = 'http://ticket.yes24.com'
		payload['AutoLogin'] = 1
		payload['LoginIDSave'] = 'Y'
		r = self.session.post(URL, headers=headers, data=payload, verify=False)
		print("[login]", r.status_code, r.reason, r.headers['Date'])
		#print(r.text)
		#age = self.session.cookies['Mallinmall_CKMAG']
		#print('age:', age)
		#self.customerid = self.session.cookies['Mallinmall_CKMN']
		#print('customerid:',self.customerid)

		if "yesPop('loginFailPop'" in r.text:
			print("Wrong id or password..")
			exit()
		elif "FBLoginSub_panLoginCaptcha" in r.text:
			print("Captcha required...")
			return False

		return True

	# To parse IdCustomer
	def getPerfSaleHtmlSeat(self, idtime, idhall):
		#1029754 6538
		URL = "http://ticket.yes24.com/Pages/Perf/Sale/PerfSaleHtmlSeat.aspx?idTime={}&idHall={}&block=0&stMax=10&pHCardAppOpt=0".format(idtime, idhall)
		r = self.session.get(URL)
		print('[PerfSaleHtmlSeat]',r.status_code, r.reason, r.headers['Date'])
		#print(r.text)
		regex = re.compile("var IdCustomer = '([0-9]+)'")
		mo = regex.search(r.text)
		if mo != None:
			self.customerid = mo.group(1)
			print('customerid:',self.customerid)
		else:
			print("no customerid... abort")
			exit()

	#URL = "http://ticket.yes24.com/Pages/Perf/Sale/Ajax/Perf/TimeSaleState.aspx"
	#URL = "http://ticket.yes24.com/Pages/Perf/Sale/Ajax/Perf/TimeSeatRemain.aspx"
	#URL = "http://ticket.yes24.com/Pages/Perf/Sale/Ajax/Perf/TimeNoSeatClass.aspx"
	#URL = "http://ticket.yes24.com/Pages/Perf/Sale/Ajax/Perf/PerfSaleInfo.aspx"
	#URL = "http://ticket.yes24.com/Pages/Perf/Sale/Ajax/Perf/PerfGuideView.aspx"

	def getGuideView(self):
		URL = "http://ticket.yes24.com/Pages/Perf/Sale/Ajax/Perf/PerfGuideView.aspx"
		payload = {'pIdPerf':self.idperf}
		r = self.session.post(URL, data=payload)
		print('[GuideView]',r.status_code, r.reason, r.headers['Date'])
		print(r.text)

	def getPerfTime(self, date, filter_array=None):
		URL = "http://ticket.yes24.com/Pages/Perf/Sale/Ajax/Perf/PerfTime.aspx"
		#URL = "http://m.ticket.yes24.com/Perf/Sale/Ajax/Perf/AxPerfTime.aspx"
		headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36'}
		payload = {'pDay':date,'pIdPerf':self.idperf,'pIdCode':0,'pIsMania':0}
		r = self.session.post(URL, headers=headers, data=payload)
		print("[Time All]", r.status_code, r.reason, r.headers['Date'])
		#print(r.text)

		perftimes = []
		soup = BeautifulSoup(r.text, "html.parser")
		for li in soup.findAll('li'):
			timeid = li['value']
			timeinfo = li['timeinfo']
			idhall = li['idhall']
			myPerfTime = PerfTime(timeid, date, timeinfo, idhall)
			if myPerfTime.isPrefered(filter_array):
				print(myPerfTime)
				perftimes.append(myPerfTime)

		return perftimes


	def getHallMapRemain(self, idhall, idtime):
		URL = "http://ticket.yes24.com/OSIF/Book.asmx/GetHallMapRemain"
		headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36'}
		payload = {'idHall':idhall, 'idTime':idtime}
		r = self.session.post(URL, headers=headers, data=payload)
		print('[HallMap]', r.status_code, r.reason, r.headers['Date'])
		print(r.text)

		root = ET.fromstring(r.text)
		ns = "{http://tempuri.org/}"

		blockremain = root.findtext('{}BlockRemain'.format(ns))
		for block in blockremain.split('^'):
			if block == '':
				continue
			(block_num,remain) = block.split('@')
			if int(remain) > 0:
				print(block_num, remain)
				return block_num
		return -1

	def getSaleState(self):
		URL = "http://ticket.yes24.com/Pages/Perf/Sale/Ajax/Perf/TimeSaleState.aspx"
		payload = {'pIdTime':self.idtime}
		r = self.session.post(URL, data=payload)
		print('[HallMap]', r.status_code, r.reason, r.headers['Date'])
		#print(r.text)

	def getSeatData(self, block, idhall, idtime, idcustomer):
		URL = "http://ticket.yes24.com/OSIF/Book.asmx/GetBookWhole"
		#URL = "http://m.ticket.yes24.com/OSIF/Book.asmx/GetBookWhole"
		payload = {'idHall':idhall,'idTime':idtime,'block':block,'channel':1,'idCustomer':idcustomer,'idOrg':1}
		headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36'}
		r = self.session.post(URL, headers=headers, data=payload)
		print("[Seat]", r.status_code, r.reason, r.headers['Date'], end='\r')
		#print(r.text)

		root = ET.fromstring(r.text)
		ns = "{http://tempuri.org/}"
		#print(root.findtext('{}IdTime'.format(ns)))
		#print(root.findtext('{}Block'.format(ns)))
		blockseat = root.findtext('{}BlockSeat'.format(ns))
		seatdata = []
		for seat in blockseat.split('^'):
			if seat == '':
				continue
			mySeat = Seat(seat)
			if mySeat.idlock != '0': #if already bought
				continue
			if mySeat in self.triedSeats: #if already tried
				print("already tried...", mySeat)
				continue
			seatdata.append(mySeat)

		seatdata.sort()

		return seatdata

	def lockSeat(self, block, date, idtime, seats):
		if len(seats) == 0:
			return False

		self.triedSeats.extend(seats)

		mytoken = ",".join([seat.seatid for seat in seats])
		print(date, idtime, mytoken)
		[print(seat) for seat in seats]
		#myptags = "".join([seat.getPTag() for seat in seats])
		#print(myptags)

		URL = "http://ticket.yes24.com/OSIF/Book.asmx/Lock"
		payload = {'name':self.customerid,'idTime':idtime,'token':mytoken,'Block':block}
		headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36'}
		r = self.session.post(URL, headers=headers, data=payload)
		print("[Lock]", r.status_code, r.reason, r.headers['Date'])
		print(r.text)

		root = ET.fromstring(r.text)
		if int(root.text) != 0:
			print("Lock failed")
			return False

		print("Lock succeed.....Expires in 5min(NOW:{})".format(datetime.datetime.now()))

		params = urllib.parse.urlencode(payload)
		getURL = URL + "?" + params
		print(getURL)
		print("")
		return True

	def setLastPage(self, date, idtime, seats):
		self.classes = "-".join([seat.grade for seat in seats])
		seatend = self.seatEnd(idtime, self.classes)
		self.sel.change_element_html_by_id('ulSeatSpace', seatend)

		self.idseats = "-".join([seat.seatid for seat in seats])
		etcfee = self.getEtcFee(idtime, len(seats))
		self.sel.change_element_html_by_id('divBookingFee', etcfee)

		method = self.getDeliveryMethod(idtime, date, self.idperf, "")
		self.sel.change_element_html_by_id('deliveryPos', method)
		self.sel.driver.execute_script("var rdos = document.getElementsByName('rdoDelivery');if(rdos.length>0)rdos[0].click();")

		seats_desc = "".join(["<span>{}</span>".format(seat.desc) for seat in seats])
		self.sel.change_element_html_by_id('tk_seat', seats_desc)

		self.sel.change_value_by_id(self.idperf)
		self.sel.change_element_value_by_id('IdTime', idtime)
		self.sel.change_element_value_by_id('IdSeatClassPrice', self.idseatclassprice)
		self.sel.change_element_value_by_id('IdSeatClass', self.idseatclass)
		self.sel.change_element_value_by_id('IdSeat', self.idseats)
		print("READY!!!!!!!!!!!!!!!!!!! BOOK FAST!!!!!")

	def setDefaultDeliveryMethod(self, date, idtime, seats, rows):
		WillCallOK = False
		for seat in seats:
			if seat.seat_row in rows:
				WillCallOK = True

		if not WillCallOK:
			print("no need to change delivery method by default")
			return
		else:
			print("need to change delivery method by default")

		method = "<input type='radio' name='rdoDelivery' id='rdoDeliveryBase' value='-1' price='0' datedifference='' onclick='fdc_DeliveryMethodChange(this);' /><label for='rdoDeliveryBase'>현장수령</label>"
		self.sel.change_element_html_by_id('deliveryPos', method)
		self.sel.driver.execute_script("var rdos = document.getElementsByName('rdoDelivery');if(rdos.length>0)rdos[0].click();")

	def checkout(self):
		self.sel.checkout()
		print("Finding another seat!!!!!!!!")

	def browser_login(self, x=0, y=0, headless=False):
		self.sel = Selenium_yes24(idperf=self.idperf, x=x, y=y, headless=headless)
		self.sel.login(userid=self.loginid, userpw=self.loginpw)
		self.sel.openBlank()

	def browser_openSample(self, idperf, idtime):
		self.sel.openPerf(idperf, idtime)

	def browser_wait_last_page(self, payment_method=1, deposit=0, captcha_self=False):
		self.sel.goLastPage()
		self.sel.prepare_lastpage(payment_method=payment_method, deposit=deposit, captcha_self=captcha_self)

	def seatEnd(self, idtime, classes):
		URL = "http://ticket.yes24.com/Pages/Perf/Sale/Ajax/Perf/TimeSeatFlashEnd.aspx"
		#URL = "http://m.ticket.yes24.com/Perf/Sale/Ajax/Perf/AxTimeSeatFlashEnd.aspx"
		headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36'}
		payload = {'pIdTime': idtime, 'PCntClass':classes}
		r = self.session.post(URL, headers=headers, data=payload)
		print("[seatEnd]", r.status_code, r.reason, r.headers['Date'])
		#print(r.text)
		#<li class='grade'><div classbyte='T82$188$174'><strong class='c_name'>R석</strong> <span class='c_price'>130,000원</span><select id='selSeatClass' price='130000'><option selected value='2'>2매</option></select></div></li>

		soup = BeautifulSoup(r.text, "html.parser")
		self.classbyte = soup.find('div')['classbyte']
		self.price = int(soup.find('select', {"id":"selSeatClass"})['price'] )
		self.ticketcnt = soup.find('option')['value']
		self.idseatclassprice = "{}-{}-{},".format(self.classbyte, self.ticketcnt, self.price)
		self.idseatclass = "{}-{},".format(self.classbyte, self.ticketcnt)
		#print('IdSeatClassPrice:', self.idseatclassprice)
		#print('IdSeatClass:', self.idseatclass)
		return r.text

	def getEtcFee(self, idtime, count):
		#URL = "http://m.ticket.yes24.com/Perf/Sale/Ajax/Perf/AxEtcFee.aspx"
		URL = "http://ticket.yes24.com/Pages/Perf/Sale/Ajax/Perf/EtcFee.aspx"
		headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36'}
		payload = {'pIdTime': idtime, 'pSeatCnt': count, 'pFreeCountOfCoupon': 0, 'pFreeCountOfGiftTicket': 0}
		r = self.session.post(URL, headers=headers, data=payload)
		print("[EtcFee]", r.status_code, r.reason, r.headers['Date'])
		#print(r.text)
		#<input type=hidden id=EtcFees value='69#2000^' /><input type=hidden id=EtcFeeAmount value='2000' /><input type=hidden id=EtcValidTicketCnt value='2' />

		soup = BeautifulSoup(r.text, "html.parser")
		self.feetype = soup.find('input', {"id": "EtcFees"})['value']
		self.feeamount = soup.find('input', {"id": "EtcFeeAmount"})['value']
		#print(self.feetype)
		#print(self.feeamount)
		return r.text

	## http://ticket.yes24.com/Pages/Perf/Sale/Scripts/ps_divControls.js?v3=75
	## fdc_CheckWillCall()
	def getDeliveryMethod(self, idtime, date, idperf, idclass):
		URL = "http://ticket.yes24.com/Pages/Perf/Sale/Ajax/Perf/DeliveryMethod.aspx"
		headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36'}
		payload = {'pIdTime':idtime, 'pBaseDate':date, 'pIdPerf':idperf, 'pIdClass':idclass}
		r = self.session.post(URL, headers=headers, data=payload)
		print('[DeliveryMethod]',r.status_code, r.reason, r.headers['Date'])
		print(r.text)
		return r.text

	def getDeliveryInfo(self):
		URL = "http://ticket.yes24.com/Pages/Perf/Sale/Ajax/Perf/DeliveryUserInfo.aspx"
		headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36'}
		r = self.session.post(URL, headers=headers)
		print('[Delivery]',r.status_code, r.reason, r.headers['Date'])
		#print(r.text)

		soup = BeautifulSoup(r.text, "html.parser")
		username = soup.find('input', {'id':'LUAddr_UserName'})['value']
		mobile1 = soup.find('input', {'id':'LUAddr_Mobile1'})['value']
		mobile2 = soup.find('input', {'id':'LUAddr_Mobile2'})['value']
		mobile3 = soup.find('input', {'id':'LUAddr_Mobile3'})['value']
		mailh = soup.find('input', {'id':'LUAddr_MailH'})['value']
		maild = soup.find('input', {'id':'LUAddr_MailD'})['value']
		zipcode = soup.find('input', {'id':'LUAddr_ZipCode1'})['value']
		address1 = soup.find('input', {'id':'LUAddr_Address1'})['value']
		address2 = soup.find('input', {'id':'LUAddr_Address2'})['value']

		mobile = "{}-{}-{}".format(mobile1, mobile2, mobile3)
		email = "{}@{}".format(mailh, maild)
		print("[{}] [{}] [{}]".format(username, mobile, email))
		print("[{}] [{}] [{}]".format(zipcode, address1, address2))

		if mobile1 == '' or mobile2 == '' or mobile3 == '':
			print("no mobile number... abort")
			exit()
		if mailh == '' or maild == '':
			print("no email... abort")
			exit()
		if zipcode == '' or address1 == '' or address2 == '':
			print("no address... abort")
			exit()

	def getPayMethod(self, idtime, date):
		URL = "http://ticket.yes24.com/Pages/Perf/Sale/Ajax/Perf/PayMethod.aspx"
		headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36'}
		payload = {'pIdTime':idtime, 'pBaseDate':date, 'pIsMPoint':0}
		r = self.session.post(URL, headers=headers, data=payload)
		print('[PayMethod]',r.status_code, r.reason, r.headers['Date'])
		print(r.text)

	def getMyOrders(self, date=None):
		URL = "http://ticket.yes24.com/Pages/MyPage/Ajax/MyOrder/MyOrderList.aspx"
		payload = {'pDispGubun': 1, 'pStartDT':'2018-10-14', 'pEndDT':'2018-11-14', 'pCurPage':1, 'pPageSize':20}
		r = self.session.post(URL, data=payload)
		print("[MyOrders]", r.status_code, r.reason, r.headers['Date'])
		#print(r.text)

		orderlist = []
		soup = BeautifulSoup(r.text, "html.parser")
		for a in soup.findAll('a', {"class": "orderticketview"}):
			idorder = a['idorder']
			if idorder not in orderlist:
				orderlist.append(idorder)

		for order in orderlist:
			print(order)
			self.getMyOrderTicket(orderid=order)

	def getMyOrderTicket(self, orderid):
		URL = "http://ticket.yes24.com/Pages/MyPage/MyOrderTicketPrint.aspx?IdOrder={}&IdPackOrd=".format(orderid)
		r = self.session.post(URL)
		print("[Ticket]", r.status_code, r.reason, r.headers['Date'])
		#print(r.text)
		soup = BeautifulSoup(r.text, "html.parser")
		info = str( soup.find('div', {"class": "blu_list"}) )
		print(info)

class Seat(object):
	def __init__(self, seat):
		ticket = seat.split('@')
		self.seatid = ticket[0]
		self.seat_row = int(self.seatid)//100000
		self.seat_col = int(self.seatid)%100000
		self.idlock = ticket[2]
		self.desc = ticket[3]
		self.price = ticket[4]
		self.grade = ticket[5]

	def __repr__(self):
		return "{} / lock:{} / {} / {} / {}".format(self.seatid, self.idlock, self.desc, self.price, self.grade)

	def getPTag(self):
		return '<p id="C{}" class="txt2" name="cseat" grade="{}">{}</p>'.format(self.seatid, self.grade, self.desc)

	def __eq__(self, other):
		return self.seatid == other.seatid

	def __lt__(self, other):
		return int(self.seatid) < int(other.seatid)

	def isSeatPrefered(self, prefer):
		(row1, col1, row2, col2) = prefer
		# t600030 : 4row, 9th seat
		# t1200037 : 10row, 16th seat
		#if self.seat_row >= 6 and self.seat_row <= 20 and self.seat_col >= 30 and self.seat_col <= 53: # TEST
		if self.seat_row >= row1 and self.seat_row <= row2 and self.seat_col >= col1 and self.seat_col <= col2: # REAL
			return True
		return False

	def isSeatSerial(self, other):
		if self.seat_row != other.seat_row:
			return False
		elif abs(self.seat_col-other.seat_col) == 1:
			return True
		else:
			return False



