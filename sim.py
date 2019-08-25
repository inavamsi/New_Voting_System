import random
import copy
from statistics import mode 
import numpy as np

def str2list(line):
	newl=line.split(' ')
	rl=[]
	for no in newl:
		if (no == '' or no ==' ' or no =='\n'):
			continue
		rl.append((int)(no))
	return rl

class Election():
	def __init__(self,filename):
		fo = open(filename, "r+")
		self.counties = 0    #number of counties
		self.pvotes =0       #number of positve votes per person
		self.nvotes=0        #number of negative votes per person
		self.candidate_list=[]  # list of lists, one list per county
		# for a county candidate indexed by county number, list will be numbers from 0..n-1
		self.voter_list_c =[] # list of lists, one list per county
		# For a county, voter list will be a list of dictionaries - county : 0, posvotelist: [], negvotelist: []
		#Note: vote is -1 if not cast
		self.voter_list_d=[]
		#stored as a dictionary
		self.victors=[]

		firstline=str2list(fo.readline())
		self.counties=firstline[0]
		self.pvotes=firstline[1]
		self.nvotes=firstline[2]

		for i in range(self.counties):
			self.candidate_list.append(str2list(fo.readline()))

		for i in range(self.counties):
			self.voter_list_c.append([])

		while True:
			line = fo.readline()
			if not line:
				break

			voterdet=str2list(line)
			d={}
			d['county']=voterdet[0]
			d['pvotes']=voterdet[1:1+self.pvotes]
			d['nvotes']=voterdet[1+self.pvotes:]
			self.voter_list_d.append(d)
			self.voter_list_c[d['county']].append((d['pvotes'],d['nvotes']))

		fo.close()

	def show(self):
		print("Number of Counties : ",self.counties)
		print("Number of Positive Votes : ",self.pvotes)
		print("Number of Negative Votes : ",self.nvotes)
		print(" ")

		for i in range(len(self.candidate_list)):
			print("Candidate List of County ",i," : ",self.candidate_list[i])

		for i in range(len(self.voter_list_c)):
			print("Voter List of County ",i," : ",self.voter_list_c[i])
		print(" ")

	def vote_metric(self, cno, new_candl, cand, c_vl, param):
		#cur_cl = self.candidate_list[cno]
		best_cand=0
		worst_cand=0
		dnc=0
		total_pvotes=0
		total_nvotes=0

		for (orig_pvl,orig_nvl) in c_vl:
			pvl=list(filter(lambda a: a in new_candl, orig_pvl))
			nvl=list(filter(lambda a: a in new_candl, orig_nvl))
			if(cand not in pvl):
				dnc+=1
			if(len(pvl)!=0):
				total_pvotes+=pvl.count(cand)/len(pvl)
				if self.first_most_frequent(pvl) == cand:
					best_cand+=1
			if(len(nvl)!=0):
				total_nvotes+=nvl.count(cand)/len(nvl)
				if self.first_most_frequent(nvl) ==cand:
					worst_cand+=1

		if param ==1:  #FPTP Voting if new_candl==candidate_list[cno]
			return best_cand
		if param ==2:  #quadratic Voting if new_candl==candidate_list[cno]
			return total_pvotes
		if param ==3: #Democracy2.1 if new_candl==candidate_list[cno]
			return best_cand - worst_cand

		return None

	def first_most_frequent(self,l):
		(values,counts) = np.unique(l,return_counts=True)
		ind=np.argmax(counts)
		return values[ind]

	def countywinnerlist(self, cno,param,club):
		new_candl=copy.deepcopy(self.candidate_list[cno])
		votelist=copy.deepcopy(self.voter_list_c[cno])
		
		if club==True:
			if cno%2==0:
				pair=cno+1
			else:
				pair =cno-1
			new_candl=list(set(self.candidate_list[cno]) | set(self.candidate_list[pair]))
			votelist=self.voter_list_c[cno]+self.voter_list_c[pair]


		if param ==4:
			return self.recurse(cno,new_candl,votelist)

		ranklist = sorted(new_candl, key=lambda x: self.vote_metric(cno,new_candl,x,votelist,param))
		ranklist.reverse()
		return ranklist

	def recurse(self,cno,candl,vl):
		if len(candl)<=2:
			return candl
		ranklist =sorted(candl, key=lambda x: self.vote_metric(cno,candl,x,vl,1))
		ranklist.reverse()
		#print(ranklist)
		smalllist= self.recurse(cno,ranklist[:-1],vl)
		smalllist.append(ranklist[-1])
		return smalllist

	def winners(self,param,club,arg):
		self.victors=[]
		for i in range(self.counties):
			self.victors.append(self.countywinnerlist(i,param,club)[0])
		
		self.score(arg)

	def wintable(self,param,club,arg):
		self.victors=[]
		for i in range(self.counties):
			self.victors.append(self.countywinnerlist(i,param,club)[0])
		
		return self.score2(arg)

	def show_winlist(self,cno,club):
		print("County ",cno)
		print(self.countywinnerlist(cno,1,club))
		print(self.countywinnerlist(cno,2,club))
		print(self.countywinnerlist(cno,3,club))
		print(self.countywinnerlist(cno,4,club))

	def acc_indx(self,victors_l):
		tot_hap=0
		tot_voters=0
		for v in self.voter_list_d:
			if victors_l[v['county']] in v['pvotes']:
				tot_hap+=1
			if victors_l[v['county']] in v['nvotes']:
				tot_hap-=1
			tot_voters+=1

		return 50*(1+tot_hap/tot_voters)

	def thr_indx(self,victors_l):
		thr=0
		tot_voters=0
		for v in self.voter_list_d:
			if victors_l[v['county']] in v['pvotes']:
				thr+=1
			tot_voters+=1

		return 100*thr/tot_voters

	def match_indx(self,victors_l):
		tot_hap=0
		tot_voters=0
		for v in self.voter_list_d:
			tot_hap+=v['pvotes'].count(victors_l[v['county']])/self.pvotes
			tot_hap+=v['nvotes'].count(victors_l[v['county']])/self.nvotes
			tot_voters+=1

		return 100*tot_hap/tot_voters

	def score(self,arg):
		rand_cl=[]
		for i in range(self.counties):
			rand_cl.append(random.choice(self.candidate_list[i]))

		if arg ==1:
			print("Acceptance Index scale 0 to 100")
			print(self.victors)
			print("Value = ",self.acc_indx(self.victors))
			print(rand_cl)
			print("Value for random selection = ",self.acc_indx(rand_cl))

		if arg ==2:
			print("Threshold scale from 0 to 100")
			print(self.victors)
			print("Value = ",self.thr_indx(self.victors))
			print(rand_cl)
			print("Value for random selection = ",self.thr_indx(rand_cl))

		if arg ==3:
			print("Match scale from 0 to 100")
			print(self.victors)
			print("Value = ",self.match_indx(self.victors))
			print(rand_cl)
			print("Value for random selection = ",self.match_indx(rand_cl))

	def score2(self,arg):
		if arg ==1:
			return self.acc_indx(self.victors)

		if arg ==2:
			return self.thr_indx(self.victors)

		if arg ==3:
			return self.match_indx(self.victors)
			

#_________________end of class Election



# input file format
a = Election('input1')
#a.show()


#param=1 fptp
#param=2 quadratic
#param=3 d2.1
#param=4 stv
#club=True - club counties
param =4
club=False


#To print for candidate rank list for a county for all elction types and clubbing counties bool
#a.show_winlist(0,False)
#a.show_winlist(1,False)
#a.show_winlist(0,True)
 
# To show countywise winners for a county, elction type, club bool
#print(a.countywinnerlist(0,param,club))
#print(a.countywinnerlist(1,param,club))

arg=3
#to show population sentiment values for different metrics
# arg=1 - thrshold, enugh people have voted for winning candidate
# arg=2 - acceptance index, - no of people who have accepted result
# arg=3 - match index, how close is result to poll
#print(" ")
#a.winners(param,club,arg)



'''print("Together")
print(a.countywinnerlist(3,1,True))
print(a.countywinnerlist(3,2,True))
print(a.countywinnerlist(3,3,True))
print(a.countywinnerlist(3,4,True))
'''
print("param ","arg ","Indx_value ","victors")
for param in [1,2,3,4]:
	for arg in [1,2,3]:
		print(param," ",arg," ",a.wintable(param,club,arg)," (",a.victors,")")

