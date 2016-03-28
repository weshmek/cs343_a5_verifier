#! /usr/bin/python
#verify.py: Verifies the output of a5 executable
import re
import string
def read_line1():
	#Read initial line to get number of students, machines, and couriers
	Couriers = []
	Machines = []
	Students = []
	LINE1 = raw_input()
	#print LINE1
	pattern = re.compile("(Parent)\s+(WATOff)\s+(Names)\s+(Truck)\s+(Plant)\s+(Stud([0-9])+\s+)+(Mach([0-9])+\s+)+(Cour([0-9])+\s*)+")
	m = pattern.match(LINE1)
	if (m == None):
		raise Exception("Error!")
	numStudents = int(m.group(7)) + 1
	numMachines = int(m.group(9)) + 1
	numCouriers = int(m.group(11)) + 1
	return (numStudents, numMachines, numCouriers)

class SimObj:
	started = False
	ended = False

class WATOffice(SimObj):
	workToBeDone = False
	studentToTransfer = 0
	amtToTransfer = 0
	workGiven = False
	jobsToGive = []

class Job:
	studentAmt = 0
	studentId = 0
	def __init__(self,_id, amt):
		self.studentAmt = amt
		self.studentId = _id


class Student(SimObj):
	account = 0
	balance = 0
	favouriteSoda = 0
	numBottles = 0
	cardLost = True
	machine = 0

class Machine(SimObj):
	quantities = [0,0,0,0]
	cost = 0
	refillStarted = 0
	registered = False
	
class Courier(SimObj):
	idn = 0
	working = False
	amtToTransfer = 0
	studentId = 0
	jobTaken = False
	def __init__(this,_id):
		this.idn = _id



def read_line(numbers):
	ln = raw_input()
	if (ln == "*"*23):
		return None
	out = []
	i = 0
	j = 0
	while (i < len(ln)):
		j = i
		while (ln[i] != '\t'):
			i = i + 1
			if (i == len(ln)):
				break
		out.append(ln[j:i])
		i = i + 1
	while len(out) < sum(numbers) + 5:
		out.append('')
	return out	


class State:
	students = []
	machines = []
	couriers = []
	parent = None
	watoff = None
	names = None
	truck = None
	plant = None
	def __init__(self, _students, _machines, _couriers, _parent, _watoff, _names, _truck, _plant):
		self.students = _students
		self.machines = _machines
		self.couriers = _couriers
		self.parent = _parent
		self.watoff = _watoff
		self.names = _names
		self.truck = _truck
		self.plant = _plant

	

class Line:
	parent = ""
	watoff = ""
	names = ""
	truck = ""
	plant = ""
	students = []
	machines = []
	couriers = []
	def __init__(self, line, numbers):
		self.parent = line[0]
		self.watoff = line[1]
		self.names = line[2]
		self.truck = line[3]
		self.plant = line[4]
		self.students = []
		self.machines = []
		self.couriers = []
		for i in range(numbers[0]):
			self.students.append(line[5 + i])
		for i in range(numbers[1]):
			self.machines.append(line[5 + numbers[0] + i])
		for i in range(numbers[2]):
			self.couriers.append(line[5 + numbers[0] + numbers[1] + i] )

def passline(st):
	return st == "..." or st == "\n" or st == "\t" or st == ''

def check_parent(state, line):
	if passline(line.parent):
		return
	elif state.parent.ended == True:
		raise Exception("Error! Parent operation after parent kill!")
	elif line.parent == 'S':
		if state.parent.started == True:
			raise Exception("Error! Parent started Twice!")
		state.parent.started = True
		
	elif line.parent[0] == 'D':
		studentNum = int(line.parent[1])
		studentAmt = int(line.parent[3])
		state.students[studentNum].account += studentAmt
	elif line.parent[0] == 'F':
		state.parent.ended = True
		
		
	else:
		print line.parent
		raise Exception("Error! Unknown operation for parent!")

def check_watoff(state, line):
	if passline(line.watoff):
		return
	elif state.watoff.ended == True:
		print line.watoff
		raise Exception("Error! WATOffice operation after kill!")
	elif line.watoff == "S":
		if state.watoff.started	== True:
			raise Exception("Error! WATOffice started twice!")
		state.watoff.started = True
	elif line.watoff[0] == 'C':
		studentId = int(line.watoff[1])
		studentAmt = int(line.watoff[3])
		#if state.students[studentId].started == False or state.students[studentId].ended == True:
		#	raise Exception("Error! Zombie student!")
		if studentAmt != 5:
			raise Exception("Error! Student must create WATCard with $5 balance!")
		if state.students[studentId].cardLost != True:
			raise Exception("Error! Attempting to create non-lost card!")
		for j in state.watoff.jobsToGive:
			if j.studentId == studentId:
				raise Exception("Error! C Student requesting two jobs at same time!")
		state.watoff.jobsToGive.append(Job(studentId, studentAmt))
		if state.watoff.jobsToGive == []:
			raise Exception("Error! Empty array!")
		state.students[studentId].cardLost = False
	elif line.watoff[0] == 'T':
		studentId = int(line.watoff[1])
		studentAmt = int(line.watoff[3])
		#if state.students[studentId].started == False or state.students[studentId].ended == True:
		#	raise Exception("Error! Zombie student!")
		for j in state.watoff.jobsToGive:
			if j.studentId == studentId:
				raise Exception("Error! T Student " + str(studentId) + " requesting two jobs at same time!" + str(j.studentAmt) + " " + str(studentAmt))
		state.watoff.jobsToGive.append(Job(studentId, studentAmt))
	elif line.watoff[0] == 'W':
		return
	elif line.watoff[0] == 'F':
		state.watoff.ended = True
	else:
		print line.watoff
		raise Exception("Error! WATOffice unrecognized operation!")

def check_courier(_id, state, line):
	me = state.couriers[_id]	
	cmd = line.couriers[_id]
	if passline(cmd):
		return
	elif me.ended == True:
		raise Exception("Error! Courier operation after kill!")
	elif cmd[0] == 'S':
		if me.started == True:
			raise Exception("Error! Courier started twice!")
		me.started = True
	elif cmd[0] == 't':
		studentId = int(cmd[1])
		studentAmt = int(cmd[3])
		if state.watoff.jobsToGive == []:
			raise Exception("Error! Courier: No job to give!")
		if me.working == True:
			raise Exception("Error! Courier Working twice!")
		job = None
		for j in state.watoff.jobsToGive:
			if j.studentId == studentId:
				if j.studentAmt != studentAmt:
					raise Exception("Error! courier mismatched jobs!")
				job = j
				state.watoff.jobsToGive.remove(j)
				break
		for j in state.watoff.jobsToGive:
			if j.studentId == studentId:
				raise Exception("Error!")
		if j == None:
			raise Exception("Error! No matching job!")
		me.amtToTransfer = studentAmt
		me.studentId = studentId
		me.working = True
	elif cmd[0] == 'T':
		studentId = int(cmd[1])
		studentAmt = int(cmd[3])
		if me.working == False:
			raise Exception("Error! Not working!")
		if (me.amtToTransfer != studentAmt) or (me.studentId != studentId):
			raise Exception("Error! Mismatched jobs!")
		if state.students[studentId].account < studentAmt:
			raise Exception("Error! Not enough funds to finish job!")
		me.working = False
		state.students[studentId].balance += studentAmt
		state.students[studentId].account -= studentAmt
	elif cmd[0] == 'F':
		me.ended = True
	else:
		print cmd
		raise Exception("Error! Courier unrecognized command!")
		
		
	
def check_student(_id, state, line):
	me = state.students[_id]
	cmd = line.students[_id]
	if passline(cmd):
		return
	elif me.ended == True:
		raise Exception("Error! Zombie student!")
	elif cmd[0] == 'S':
		flavour = int(cmd[1])
		bottles = int(cmd[3])
		if me.started == True:
			raise Exception("Error! Student started twice!")
		me.favouriteSode = flavour
		me.numBottles = bottles
		me.started = True	
	elif cmd[0] == 'V':
		machine = int(cmd[1]) #Nameserver needs to check this
		#if me.machine != machine:
		#	raise Exception("Error! Bad machine registration")
		if state.machines[machine].registered == False and (line.names[0] != 'R' and int(line.names[1]) != machine):
			raise Exception("Error! Unregistered machine!")
		return
	elif cmd[0] == 'B':
		#TODO
		return
	elif cmd[0] == 'L':
		if me.cardLost == True:
			raise Exception("Error! Student lost card twice!")
		me.cardLost = True
	elif cmd[0] == 'F':
		me.ended = False
	else:
		print cmd
		raise Exception("Error! Student unknown command!")

def check_nameserver(state, line):
	me = state.names
	cmd = line.names
	if passline(cmd):
		return
	elif me.ended == True:
		raise Exception("Error! Zombie nameserver!")
	elif cmd[0] == 'S':
		if me.started == True:
			raise Exception("Error! Started twice!")
		me.started = True
	elif cmd[0] == 'N':
		studentId = int(cmd[1])
		machine = int(cmd[3])
		state.students[studentId].machine = machine
		
	elif cmd[0] == 'V':
		#TODO
		return
	elif cmd[0] == 'R':
		machine = int(cmd[1])
		state.machines[machine].registered = True
	elif cmd[0] == 'F':
		me.ended = True
	else:
		print cmd
		raise Exception("Error! nameserver unknown command!")
		

		

lines = []
def verify_data(numbers):
	state = State([], [], [], SimObj(), WATOffice(), SimObj(), SimObj(), SimObj())
	state.students = []
	for i in range(numbers[0]):
		state.students.append(Student())
	machines = []
	for i in range(numbers[1]):
		state.machines.append(Machine())
	couriers = []
	for i in range(numbers[2]):
		state.couriers.append(Courier(i))


	line = read_line(numbers)
	while line:
		lines.append(line)
		ln = Line(line, numbers)
		check_parent(state, ln)	
		check_nameserver(state,ln)
		for i in range(numbers[0]):
			check_student(i, state, ln)
		check_watoff(state, ln)
		for i in range(numbers[2]):
			check_courier(i, state, ln)	
		line = read_line(numbers)
	print "Verified"
		
				

numbers = read_line1()			
LINE2 = raw_input() # Discard

try:
	verify_data(numbers)
except BaseException as be:
	print "Exception!"
	for line in lines:
		print line
	print str(be)