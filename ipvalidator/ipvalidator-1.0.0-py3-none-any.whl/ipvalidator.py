#!/usr/bin/env python

import sys
import re

class IpValidationError(Exception):

	pass

class IpValidator:

	def __init__(self,ip):

		self.ip = ip

		self.reset()

		self.check_format()

		self.check_all_octets()

		#self.check_first_octet()

		self.check_subnet_mask()

		self.calculate_network_address()

		self.calculate_broadcast_address()


	def reset(self):

		self.first_octet = 0
		self.second_octet = 0
		self.third_octet = 0
		self.fourth_octet = 0

		self.subnet_mask = 0

		self.network_address = ''
		self.broadcast_address = ''		


	def binary_to_ipv4(binary_string):

		octet1 = binary_string[0:8]
		octet2 = binary_string[8:16]
		octet3 = binary_string[16:24]
		octet4 = binary_string[24:32]

		return (str((int(octet1, 2))) + "." + str((int(octet2, 2))) + "." + str((int(octet3, 2))) + "." + str((int(octet4, 2))))

	binary_to_ipv4 = staticmethod(binary_to_ipv4)



	def check_all_octets(self):

		if self.first_octet == 0 or self.first_octet > 223:

			raise IpValidationError("The first octet must be between 1 to 223")

		if self.second_octet > 255 or self.third_octet > 255 or self.fourth_octet > 255:

			raise IpValidationError("Octet value must be between 0 to 255")



	def check_format(self):

		res = re.search(r'^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})/(\d{1,2})$', self.ip)

		if res is not None:

			self.first_octet = int(res.group(1))
			self.second_octet = int(res.group(2))
			self.third_octet = int(res.group(3))
			self.fourth_octet = int(res.group(4))

			self.subnet_mask = int(res.group(5))

		else:

			raise IpValidationError("Invalid format")

	def check_first_octet(self):

		if self.first_octet == 0 or self.first_octet > 223:

			raise IpValidationError("The first octet must be between 1 to 223")

	def check_subnet_mask(self):

		if self.subnet_mask < 8 or self.subnet_mask > 30:

			raise IpValidationError("Subnet mask must be between 8 to 30")


	def calculate_network_address(self):

		first_octet_binary = "{0:0>8b}".format(self.first_octet)
		second_octet_binary = "{0:0>8b}".format(self.second_octet)
		third_octet_binary = "{0:0>8b}".format(self.third_octet)
		fourth_octet_binary = "{0:0>8b}".format(self.fourth_octet)

#		print "%s %s %s %s" %(first_octet_binary, second_octet_binary, third_octet_binary, fourth_octet_binary) 

		binary_32bit_string_ip_address = first_octet_binary + second_octet_binary + third_octet_binary + fourth_octet_binary

		#print binary_32bit_string_network_address

		binary_32bit_string_network_address = ''

#		print "subnet mask type is %s" %(type(self.subnet_mask))

		index = 0

		for x in binary_32bit_string_ip_address:

			if index <= self.subnet_mask - 1:

				binary_32bit_string_network_address = binary_32bit_string_network_address + x

			else:

				binary_32bit_string_network_address = binary_32bit_string_network_address + '0'

			index = index + 1


		self.network_address = self.binary_to_ipv4(binary_32bit_string_network_address)

	#	print self.network_address


	def calculate_broadcast_address(self):

		first_octet_binary = "{0:0>8b}".format(self.first_octet)
		second_octet_binary = "{0:0>8b}".format(self.second_octet)
		third_octet_binary = "{0:0>8b}".format(self.third_octet)
		fourth_octet_binary = "{0:0>8b}".format(self.fourth_octet)
                
		binary_32bit_string_ip_address = first_octet_binary + second_octet_binary + third_octet_binary + fourth_octet_binary
                
		binary_32bit_string_broadcast_address = ''
		
		index = 0
                
		for x in binary_32bit_string_ip_address:
                       
			if index <= self.subnet_mask - 1:
                                
				binary_32bit_string_broadcast_address = binary_32bit_string_broadcast_address + x
                        
			else:
                                
				binary_32bit_string_broadcast_address = binary_32bit_string_broadcast_address + '1'
                        
			index = index + 1
                
		self.broadcast_address = self.binary_to_ipv4(binary_32bit_string_broadcast_address)

	#	print self.broadcast_address

	
	def check_ip(self):

		ipv4 = str(self.first_octet) + "." + str(self.second_octet) + "." + str(self.third_octet) + "." + str(self.fourth_octet)

		if ipv4 == self.network_address:

			print ("The IP address provided is a network address\n")
			sys.exit(0)

		if ipv4 == self.broadcast_address:

			print ("The IP address provided is a broadcast address\n")
			sys.exit(0)

		return (True, self.network_address, self.broadcast_address)	


if __name__ == '__main__':

	user_inp = input("Enter an IP address in a.b.c.d/nn format: ")
	i1 = IpValidator(user_inp)

	print (i1.check_ip())
