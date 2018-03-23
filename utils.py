#!/usr/bin//python
# -*- coding: utf-8 -*-

############################################################################
#    Copyright (C) 2008 by Tomáš Košan                                     #
#    t.kosan@k25.cz                                                        #
#                                                                          #
#    This program is free software; you can redistribute it and#or modify  #
#    it under the terms of the GNU General Public License as published by  #
#    the Free Software Foundation; either version 2 of the License, or     #
#    (at your option) any later version.                                   #
#                                                                          #
#    This program is distributed in the hope that it will be useful,       #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of        #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         #
#    GNU General Public License for more details.                          #
#                                                                          #
#    You should have received a copy of the GNU General Public License     #
#    along with this program; if not, write to the                         #
#    Free Software Foundation, Inc.,                                       #
#    59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.             #
############################################################################

def float2engstr(float_num):
	
	abs_num = abs(float_num)
	
	if abs_num == 0:
		return (str(0))
	
	if  abs_num >= 1E-9 and abs_num < 1E-6:
		return str(float_num*1E9)+"n"
	
	if  abs_num >= 1E-6 and abs_num < 1E-3:
		return (str(float_num*1E6)+"u")
	
	if  abs_num >= 1E-3 and abs_num < 1:
		return (str(float_num*1000)+"m")
	
	if  abs_num >= 1 and abs_num < 1000:
		return (str(float_num))
	
	if abs_num >= 1000 and abs_num < 900E3:
		return (str(float_num/1000)+"k")
	
	if abs_num >= 900E3 and abs_num < 900E6:
		return (str(float_num/1E6)+"M")
	
	

if __name__ == "__main__":
	float2engstr(9E-9)
	float2engstr(100E-6)
	float2engstr(5E-3)	
	