#! /usr/bin/python
# This is licensed GNU GPL 2.0
# By Wesley Chalmers <wwchalme@uwaterloo.ca>

# This script is for use in the University of Waterloo course, CS343: Concurrency and Parallelism
# THIS SCRIPT IS FOR TEST PURPOSES ONLY, AND ITS VERIFICATION IS NOT ANY SORT OF GUARANTEE OF THE CORRECTNESS OF YOUR PROGRAM

#verify.py: Verifies the output of a5 executable

# This script works by going through each line of the program output, and updating the state of objects representing the objects 
# from the a5 program. Based on this state, the script is able to do basic sanity checking of the output to locate and report any major 
# inconsistencies.

import re
import string
def read_line1():
	#Read initial line to get number of students, machines, and couriers
	LINE1 = raw_input()
	#print LINE1
	pattern = re.compile("(Parent)\s+(WATOff)\s+(Names)\s+(Truck)\s+(Plant)\s+(Stud([0-9]+)+\s+)+(Mach([0-9]+)+\s+)+(Cour([0-9]+)+\s*)+")
	m = pattern.match(LINE1)
	if (m == None):
		raise Exception("Error!")
	numStudents = int(m.group(7)) + 1
	numMachines = int(m.group(9)) + 1
	numCouriers = int(m.group(11)) + 1
	return (numStudents, numMachines, numCouriers)

class SimObj:
	# Everything has an S and F
	started = False
	ended = False

class WATOffice(SimObj):
	workToBeDone = False
	studentToTransfer = 0
	amtToTransfer = 0
	workGiven = False
	jobsToGive = []
	jobs = 0

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
	machines = []
	numToPurchase=0
	nsIndex = 0
	def __init__(self):
		self.machines = []

class Machine(SimObj):
	quantities = [0,0,0,0]
	quantity = 0
	cost = 0
	refillStarted = 0
	registered = False
	reloading = False
	
class Courier(SimObj):
	idn = 0
	working = False
	amtToTransfer = 0
	studentId = 0
	jobTaken = False
	def __init__(this,_id):
		this.idn = _id

class Truck(SimObj):
	#This value is not used since the output does not tell us the quantities of individual sodas.
	quantities = [0,0,0,0]
	#This is the total number of sodas on the truck
	quantity = 0
	#This is the vending machine we expect to visit next/are currently visiting.
	vendingMachineDelivering = 0
	#This is to prevent throwing an error on first delivery
	firstDelivery = False
	#This is to make sure that nothing happens between DUd
	delivering = False



def read_line(numbers):
	ln = raw_input()
	if (ln == "*"*23):
		#23 asterisks is the indication that the output is finished
		return None
	out = []
	i = 0
	while (i < len(ln)):
		j = i
		while (i < len(ln) and ln[i] != '\t'):
			i = i + 1
			#if (i == len(ln)):
			#	break
		out.append(ln[j:i])
		i = i + 1
	while len(out) < sum(numbers) + 5:
		out.append('')
	return out	

def parse_one_number(string):
	return int(string[1:])

def parse_two_numbers(string):
	i = 1
	ret = []
	while(string[i] != ','):
		i += 1
	ret.append(int(string[1:i]))
	ret.append(int(string[i+1:]))
	return ret




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
		nums = parse_two_numbers(line.parent)
		studentNum = nums[0]
		studentAmt = nums[1]
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
		nums = parse_two_numbers(line.watoff)
		studentId = nums[0]
		studentAmt = nums[1]
		if state.students[studentId].started == False or state.students[studentId].ended == True:
			print studentId
			raise Exception("Error! Zombie student!")
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
		state.watoff.jobs += 1
	elif line.watoff[0] == 'T':
		nums = parse_two_numbers(line.watoff)
		studentId = nums[0]
		studentAmt = nums[1]
		#if state.students[studentId].started == False or state.students[studentId].ended == True:
		#	raise Exception("Error! Zombie student!")
		for j in state.watoff.jobsToGive:
			if j.studentId == studentId:
				raise Exception("Error! T Student " + str(studentId) + " requesting two jobs at same time! " + str(j.studentAmt) + " " + str(studentAmt))
		state.watoff.jobsToGive.append(Job(studentId, studentAmt))
		state.watoff.jobs += 1
	elif line.watoff[0] == 'W':
		state.watoff.jobs -= 1
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
		nums = parse_two_numbers(cmd)
		studentId = nums[0]
		studentAmt = nums[1]
		if state.watoff.jobsToGive == []:
			raise Exception("Error! Courier: No job to give!")
		if me.working == True:
			raise Exception("Error! Courier Working twice!")
		for j in state.watoff.jobsToGive:
			if j.studentId == studentId:
				if j.studentAmt != studentAmt:
					raise Exception("Error! courier mismatched jobs!")
				state.watoff.jobsToGive.remove(j)
				break
		for j in state.watoff.jobsToGive:
			if j.studentId == studentId:
				raise Exception("Error! Two jobs for one student!")
		if j == None:
			raise Exception("Error! No matching job!")
		me.amtToTransfer = studentAmt
		me.studentId = studentId
		me.working = True
	elif cmd[0] == 'T':
		nums = parse_two_numbers(cmd)
		studentId = nums[0]
		studentAmt = nums[1]
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
		nums = parse_two_numbers(cmd)
		flavour = nums[0]
		bottles = nums[1]
		if me.started == True:
			raise Exception("Error! Student started twice!")
		me.favouriteSode = flavour
		me.numBottles = bottles
		me.numToPurchase = bottles
		me.started = True	
	elif cmd[0] == 'V':
		#TODO: For some reason, in the output given by the sample executable,
		# 	NameServer N outputs always appear AFTER (or on the same line) as the student V output.
		# 	This is counterintuitive, since the nameserver should generate the name before the student gets to use it.
		#	For that reason, this section is incomplete.
		machine = parse_one_number(cmd) #Nameserver needs to check this
		#if me.machine != machine:
		#	raise Exception("Error! Bad machine registration")
		if state.machines[machine].registered == False and (line.names[0] != 'R' and int(line.names[1]) != machine):
			raise Exception("Error! Unregistered machine!")
		me.machines.append(machine)
		return
	elif cmd[0] == 'B':
		#TODO
		flavour = parse_one_number(cmd)
		#if state.machines[me.machine].quantity == 0:
		#	raise Exception("Error! Empty vending machine!")
		# it's possible that the balance is insufficient, and the courier meant to replentish us is printed on the same line.
		# so, unfortunately, we have to read the lines of the couriers
		currentAmt = 0 # Amount given by courier on current line
		for i in range(len(line.couriers)):
			courier = state.couriers[i]
			if courier.working == True and courier.studentId == _id:
				if line.couriers[i][0] == 'T':
					nums = parse_two_numbers(line.couriers[i])
					currentAmt = nums[1]
					break
					
		if (me.balance + currentAmt) > state.machines[me.machines[-1]].cost:
			me.numBottles -= 1
			me.balance -= state.machines[me.machines[-1]].cost
			return
		me.balance -= state.machines[me.machines[-1]].cost
		if me.balance < 0:
			raise Exception("Error! Overspending!")
		me.numBottles -= 1
		return
	elif cmd[0] == 'L':
		if me.cardLost == True:
			raise Exception("Error! Student lost card twice!")
		me.cardLost = True
	elif cmd[0] == 'F':
		me.ended = True 
		if me.numBottles != 0:
			errorStr = ("Error! Student supposed to purchase " + str(me.numToPurchase) + ", actual: " + str(me.numBottles))
			raise Exception(errorStr)
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
		#TODO: For some reason, in the output given by the sample executable,
		# 	NameServer N outputs always appear AFTER (or on the same line) as the student V output.
		# 	This is counterintuitive, since the nameserver should generate the name before the student gets to use it.
		#	For that reason, this section is incomplete.
		nums = parse_two_numbers(cmd)
		studentId = nums[0]
		machine = nums[1]
		studMach = state.students[studentId].machines[state.students[studentId].nsIndex]
		#studMach = state.students[studentId].machines[0]
		#if (len(state.students[studentId].machines) > 1):
		#	state.students[studentId].machines.pop()
		state.students[studentId].nsIndex += 1
		if studMach != machine:
			errstr = "Error! Vending Machine reg mismatch! Nameserver: " + str(machine) + " Student: " + str(state.students[studentId].machines[0]) + " studId: " + str(studentId)
			raise Exception(errstr)
		#state.students[studentId].machine = machine	
	elif cmd[0] == 'R':
		machine = parse_one_number(cmd)
		state.machines[machine].registered = True
	elif cmd[0] == 'F':
		me.ended = True
	else:
		print cmd
		raise Exception("Error! nameserver unknown command!")

def check_machine(_id, state, line):
	me = state.machines[_id]
	cmd = line.machines[_id]
	if passline(cmd):
		return
	elif me.ended == True:
		raise Exception("Error! Zombie machine!")
	elif cmd[0] == 'S':
		cost = parse_one_number(cmd)
		if me.started == True:
			raise Exception("Error! Machine started twice!")
		me.started = True
		me.cost = cost
		return
	if me.started == False:
		raise Exception("Error! Must start machine first!")
	elif cmd[0] == 'r':
		me.reloading = True
		return
	elif cmd[0] == 'R':
		me.reloading = False
		return
	if me.reloading == True:
		raise Exception("Error! Machine can't do things while reloading!")
	if cmd[0] == 'B':
		nums = parse_two_numbers(cmd)
		flavour = nums[0]
		remaining = nums[1]
		#if (remaining > me.quantities[flavour]):
		#	raise Exception("Error! Machine Inusfficient quantity bought!")
		me.quantities[flavour] = remaining
		me.quantity -= 1
		#Can't check quantities of individual flavour, but can at least check that machine isn't below empty
		if me.quantity < 0:
			print "id: " + str(_id)
			print flavour
			print remaining
			raise Exception("Error! Too much bought!")
		return
	if cmd[0] == 'F':
		me.ended = True
		return
	print cmd
	raise Exception("Error! Machine unknown operation!")
		
		
def check_truck(state, line):
	me = state.truck
	cmd = line.truck
	if passline(cmd):
		return
	elif me.ended == True:
		#Truck with no driver!
		raise Exception("Error! Maximum Overdrive!")	
	elif cmd[0] == 'S':
		if me.started == True:
			raise Exception("Error! Truck started twice!")
		me.started = True
	elif cmd[0] == 'd':
		nums = parse_two_numbers(cmd)
		machineId = nums[0]
		amountLeft = nums[1]
		if me.delivering == True:
			raise Exception("Error! Truck already delivering!")
		if me.firstDelivery == False:
			me.firstDelivery = True
			me.vendingMachineDelivering = machineId
		elif machineId != me.vendingMachineDelivering % len(state.machines):
			raise Exception("Error! Machines delivered out of order!")
		if amountLeft != me.quantity:
			raise Exception("Error!")
		me.delivering = True
		me.vendingMachineDelivering = machineId
				
	elif cmd[0] == 'U':
		nums = parse_two_numbers(cmd)
		machineId = nums[0]
		if me.delivering == False:
			raise Exception("Error! Truck not delivering!")
		#TODO: I don't know
			
	elif cmd[0] == 'D':
		#TODO
		nums = parse_two_numbers(cmd)
		machineId = nums[0]
		amtLeft = nums[1]
		me.delivering = False
		me.vendingMachineDelivering += 1
		me.vendingMachineDelivering %= len(state.machines)
		state.machines[machineId].quantity += (me.quantity - amtLeft)
		#print "id: " + str(machineId) + " quantity: " + str(state.machines[machineId].quantity)
		me.quantity = amtLeft
		return
	elif me.delivering == True:
		raise Exception("Error! Truck doing something other than delivering!")
	elif cmd[0] == 'P':
		sodaAmount = parse_one_number(cmd)
		#TODO: Check factory delivered qty
		me.quantity = sodaAmount
		
	elif cmd[0] == 'F':
		me.ended = True
		
	
		

def verify_ended(state):
	if (state.parent.ended == False):
		raise Exception("Error! Parent still alive!")
	if (state.watoff.ended == False):
		raise Exception("Error! WatOffice still alive!")
	if state.names.ended == False:
		raise Exception("Error! Nameserver still alive!")
	if state.truck.ended == False:
		raise Exception("Error! Truck still allive!")
	#if state.plant.ended == False:
	#	raise Exception("Error! Plant still alive!")
	_id = 0
	for student in state.students:
		if student.ended == False:
			raise Exception("Error! Student " + str(_id) + " still alive!")
		_id += 1
	_id = 0
	for machine in state.machines:
		if machine.ended == False:
			raise Exception("Error! Machine " + str(_id) + " still alive!")
		_id += 1
	_id = 0
	for courier in state.couriers:
		if courier.ended == False:
			raise Exception("Error! Courier " + str(_id) + " still alive!")
		_id += 1

		

lines = []
#numbers = (numStudents, numMachines, numCouriers)
def verify_data(numbers):
	state = State([], [], [], SimObj(), WATOffice(), SimObj(), Truck(), SimObj())
	state.students = []
	for i in range(numbers[0]):
		state.students.append(Student())
	machines = []
	for i in range(numbers[1]):
		state.machines.append(Machine())
	couriers = []
	for i in range(numbers[2]):
		state.couriers.append(Courier(i))

	#Decode and read each line
	line = read_line(numbers)
	lines.append(line)
	while line:
		ln = Line(line, numbers)
		check_parent(state, ln)	
		check_truck(state, ln)
		for i in range(numbers[0]):
			check_student(i, state, ln)

		for i in range(numbers[1]):
			check_machine(i, state, ln)
		check_watoff(state, ln)
		for i in range(numbers[2]):
			check_courier(i, state, ln)	

		check_nameserver(state,ln)


		line = read_line(numbers)
		lines.append(line)
	if state.watoff.jobs != 0:
		raise Exception("Error! Mismatched (Ts + Cs) and Ws!")
	if state.watoff.jobsToGive != []:
		raise Exception("Error! Jobs remaining on exit!")
	verify_ended(state)
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
	raise
	exit(1)
