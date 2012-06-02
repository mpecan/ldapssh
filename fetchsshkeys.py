#!/usr/local/bin/env python
#
# -*-python-*-
#
################################################################################
# License
################################################################################
# Copyright (c) 2012 Cándido Rodríguez Montes, Matjaž Pečan.  All rights reserved.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
################################################################################ 
#
# Based on the updatesshkeys.py script by Cándido Rodríguez Montes found at
# https://forja.rediris.es/projects/fedssh/ 
# Converted for use with gitolite to retrieve keys by Matjaž Pečan <matjaz.pecan@gmail.com>


import ldap, os, sys, time

# Configuration options
server = 'ldaps://ldap.klika.si:636'
dnbase = 'ou=people,dc=iaeste,dc=net'
#dnuser = 'uid=git,ou=people,dc=iaeste,dc=net'
# Bind user and password
dnuser = ''
dnpass = ''
# class of the user object
objectclass = 'account'
# User name attribute
usratt  = 'uid'
# SSH key attribute
keyatt = 'sshPublicKey'
host   = 'git'
keys_folder = '/home/git/.gitolite/keys'
users = []
l = ldap.initialize(server)
try:
	l.simple_bind_s(dnuser, dnpass)
	filter = '(&(objectClass='+objectclass+')(host='++'))'
	result_id =  l.search(dnbase, ldap.SCOPE_ONELEVEL, filter, [usratt])
	while 1:
		result_type, result_data = l.result(result_id, 0)
		if result_data == []:
			break;
		elif result_type == ldap.RES_SEARCH_ENTRY:
			for i in range(len(result_data)):
				users.append(result_data[i][1][usratt][0])
	for data_users in users:
		keys = []
		filter = '(&(objectClass='+objectclass+')('+useratt+'=' + data_users + '))'
		result_id = l.search(dnbase, ldap.SCOPE_ONELEVEL, filter, [keyatt])
		try:
			os.makedirs(keys_folder)
		except OSError as e:
			if e.errno != errno.EEXIST:
				raise
		os.chgdir(keys_folder)
		while 1:
			result_type, result_data = l.result(result_id, 0)
			if result_data == []:
				break;
			elif result_type == ldap.RES_SEARCH_ENTRY:
				for i in range(len(result_data)):
					for key in result_data[i][1][keyatt]:
						keys.append(key)
		for i in range(len(keys)):
			try:
				os.mkdir(str(i)+'/')
			except OSError as e:
				if e.errno != errno.EEXIST:
					raise
			fd = open(str(i)+'/'+data_user+'.pub', "w")
			fd.write(key[i])
			fd.close()
	os.exec('gitolite trigger SSH_AUTHKEYS')

except ldap.INVALID_CREDENTIALS:
	print "User or password is incorrect."
	sys.exit()

except ldap.LDAPError, e:
	if type(e.message) == dict and e.message.has_key('desc'):
		print e.message['desc']
	else:
		print e
	sys.exit()

l.unbind()

