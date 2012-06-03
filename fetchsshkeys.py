#!/usr/local/bin/env python
# -*- coding:utf-8 -*-
# -*- python -*-
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
# Based on the updatesshkeys.py script by Cándido Rodríguez Montes <kan@cica.es> found at
# https://forja.rediris.es/projects/fedssh/ 
# Converted for use with gitolite to retrieve keys by Matjaž Pečan <matjaz.pecan@gmail.com>


import  os, sys, time, errno, subprocess

try:
  import ldap
except ImportError:
  print("Unable to locate the 'ldap' module.  Please install python-ldap.  " \
        "(http://python-ldap.sourceforge.net)")
  sys.exit(1)
  
# Configuration options
# Server address
server = 'ldap://ldap.iaeste.net:389'
# Base DN to search under
dnbase = 'ou=people,dc=iaeste,dc=net'
# Bind user and password
dnuser = ''
dnpass = ''
# class of the user object
objectclass = 'account'
# User name attribute
usratt  = 'uid'
# Group attribute
groupatt = 'host'
# SSH key attribute
keyatt = 'sshPublicKey'
# Group griterion
group_criteria   = 'git'
keys_folder = '/home/git/.gitolite/keys'

def main():
	l = ldap.initialize(server)
	try:
		l.simple_bind_s(dnuser, dnpass)
		filter = '(&(objectClass='+objectclass+')('+groupatt+'='+group_criteria+'))'
		result_id = l.search(dnbase, ldap.SCOPE_ONELEVEL, filter)
		# Make sure our directory exists
		create_directory(keys_folder)
		# Change current path to keys directory
		os.chdir(keys_folder)
		while 1:
			result_type, result_data = l.result(result_id, 0)
			if result_data == []:
				break;
			elif result_type == ldap.RES_SEARCH_ENTRY:
				for i in range(len(result_data)):
					# Get username
					user = result_data[i][1][usratt]
					for j in range(len(result_data[i][1][keyatt])):
						# Create subdir in case it does not exist
						create_directory(str(j)+'/')
						fd = open(str(j)+'/'+user+'.pub', "w")
						fd.write(result_data[i][1][keyatt][j])
						fd.close()					
		subprocess.call(['gitolite', 'trigger SSH_AUTHKEYS'])
	
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
	
#main()

def create_directory(path):
	try:
		os.makedirs(path)
	except OSError as e:
		if e.errno != errno.EEXIST:
			raise


if __name__ == "__main__":
  main()