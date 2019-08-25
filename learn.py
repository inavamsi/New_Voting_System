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

	def vote_metric(self, cno, new_candl, cand, c_vl, a1,a2,a3,a4,a5):
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

		return a1*best_cand - a2*worst_cand - a3*dnc+ a4*total_pvotes - a5*total_nvotes

		return None

	def first_most_frequent(self,l):
		(values,counts) = np.unique(l,return_counts=True)
		ind=np.argmax(counts)
		return values[ind]

	def countywinnerlist(self, cno,a1,a2,a3,a4,a5):
		new_candl=copy.deepcopy(self.candidate_list[cno])
		votelist=copy.deepcopy(self.voter_list_c[cno])

		ranklist = sorted(new_candl, key=lambda x: self.vote_metric(cno,new_candl,x,votelist,a1,a2,a3,a4,a5))
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

	def score(self,a1,a2,a3,a4,a5):
		victors=[]
		for i in range(self.counties):
			victors.append(self.countywinnerlist(i,a1,a2,a3,a4,a5)[0])
		return self.acc_indx(victors)+self.thr_indx(victors)+self.match_indx(victors)

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


			

#_________________end of class Election



elections=[]

for i in range(1,6):
    filename='input'+(str)(i)
    elections.append(Election(filename))

maxscore=0
maxr=(0,0,0,0,0)
for i in range(0,1000):
    r1=random.random()
    r2=random.random()
    r3=random.random()
    r4=random.random()
    r5=random.random()
    newscore=0
    for el in elections:
        newscore+=el.score(r1,r2,r3,r4,r5)
    if newscore>maxscore:
        maxscore=newscore
        maxr=(r1,r2,r3,r4,r5)

print("Score of Ensemble Model :" maxscore/5)
print("parameters selected by ensemble model :",r1," ",r2," ",r3," ",r4," ",r5)




