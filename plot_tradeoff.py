import xml.etree.ElementTree as ET
import argparse
import math
import numpy as np
import csv
import matplotlib.pyplot as plt


parser = argparse.ArgumentParser(description='Generate Plot')
parser.add_argument('--var0',required=True)
parser.add_argument('--var1',required=True)
parser.add_argument('--var2',required=True)
parser.add_argument('--var3',required=True)
parser.add_argument('--var4',required=True)
parser.add_argument('--var5',required=True)
parser.add_argument('--var6',required=True)
parser.add_argument('--var7',required=True)
parser.add_argument('--var8',required=True)
parser.add_argument('--var9',required=True)
parser.add_argument('--var10',required=True)
parser.add_argument('--variable',default=1,help='1 if beta, 0 if alpha')

args = parser.parse_args()
beta = np.arange(0., 1.1,0.1)
var_flag = int(args.variable)


globalcost_filename = 'global-cost.csv'
globalcost_file = [args.var0+globalcost_filename,args.var1+globalcost_filename,args.var2+globalcost_filename,args.var3+globalcost_filename,args.var4+globalcost_filename,args.var5+globalcost_filename,args.var6+globalcost_filename,args.var7+globalcost_filename,args.var8+globalcost_filename,args.var9+globalcost_filename,args.var10+globalcost_filename]

globalcost_list = []
for filename in globalcost_file:
	with open(filename, 'r') as f:
		for row in reversed(list(csv.reader(f))):
			globalcost = float(row[1]) 
			globalcost_list.append(globalcost)
			break

plt.plot(beta, globalcost_list)
plt.ylabel('Global cost')
if var_flag==1:
	plt.xlabel(r'$\beta$')
else:
	plt.xlabel(r'$\alpha$')
plt.show()

unfairness_filename = '/unfairness.csv'
unfairness_file = [args.var0+unfairness_filename,args.var1+unfairness_filename,args.var2+unfairness_filename,args.var3+unfairness_filename,args.var4+unfairness_filename,args.var5+unfairness_filename,args.var6+unfairness_filename,args.var7+unfairness_filename,args.var8+unfairness_filename,args.var9+unfairness_filename,args.var10+unfairness_filename]

unfairness_list = []
for filename in unfairness_file:
	with open(filename, 'r') as f:
		for row in reversed(list(csv.reader(f))):
			unfairness = float(row[1]) 
			unfairness_list.append(unfairness)
			break

plt.plot(beta, unfairness_list)
plt.ylabel('Unfairness')
if var_flag==1:
	plt.xlabel(r'$\beta$')
else:
	plt.xlabel(r'$\alpha$')
plt.show()


localcost_filename = '/local-cost.csv'
localcost_file = [args.var0+localcost_filename,args.var1+localcost_filename,args.var2+localcost_filename,args.var3+localcost_filename,args.var4+localcost_filename,args.var5+localcost_filename,args.var6+localcost_filename,args.var7+localcost_filename,args.var8+localcost_filename,args.var9+localcost_filename,args.var10+localcost_filename]

localcost_list = []
for filename in localcost_file:
	with open(filename, 'r') as f:
		for row in reversed(list(csv.reader(f))):
			localcost = float(row[1]) 
			localcost_list.append(localcost)
			break


plt.plot(beta, localcost_list)
plt.ylabel('Local Cost')
if var_flag==1:
	plt.xlabel(r'$\beta$')
else:
	plt.xlabel(r'$\alpha$')
plt.show()


localcost_filename = '/indexes-histogram.csv'
localcost_file = [args.var0+localcost_filename,args.var1+localcost_filename,args.var2+localcost_filename,args.var3+localcost_filename,args.var4+localcost_filename,args.var5+localcost_filename,args.var6+localcost_filename,args.var7+localcost_filename,args.var8+localcost_filename,args.var9+localcost_filename,args.var10+localcost_filename]

step = 0
for filename in localcost_file:
	indexhist_list = []
	with open(filename, 'r') as f:
		f.readline()
		for row in list(csv.reader(f)):
			indexhist = float(row[2]) 
			indexhist_list.append(indexhist)
		planindex = np.arange(0., 63,1)
		plt.bar(np.arange(63), indexhist_list,width=1)
		if var_flag==1:		
			plt.title(r'Selected Plan Histogram $\beta$ = {}'.format(step))
		else:
			plt.title(r'Selected Plan Histogram  $\alpha$ = {}'.format(step))
		plt.ylabel('Frequency', fontsize=14)
		plt.xlabel('Plan Index')
		plt.show()
		step+=0.1	
