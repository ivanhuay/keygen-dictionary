#!/usr/bin/python
import os

import itertools


class DictionaryMaker:
	def __init__(self):
		self.aditionalData = []
		self.simpleCollection = ["admin","adm","adm","2015","2016","2017","2014","2013"]
		self.convinationLevel = 2
		self.domainName = False
		self.fullName = False
		self.address = False
		self.importantDate = False
		self.identification = False

	def welcome(self):
		print("Welcome human, Please answer the following questions...")
		self.getInput()
		self.processInput()
		self.generateDictionary()

	def getInput(self):
		print("It is possible to enter an empty response...")
		self.convinationLevel = int(raw_input("convination level:"))
		self.makeQuestion("domain name?","domainName")
		self.makeQuestion("address?","address")
		self.makeQuestion("full name?","fullName")
		self.makeQuestion("birthdate or important date?(dd-mm-yyyy)","importantDate")
		self.makeQuestion("identifier or identification number?", "identification")
		self.makeQuestion("aditional data?","aditionalData")

	def processNumbers(self,inStr):
		numbers = [str(s) for s in inStr.split() if s.isdigit()]
		response = []
		for number in numbers:
			for i in range(1, len(number)):
				res = itertools.product(number,repeat = i)
				for convination in res:
					response.append(''.join(convination))
		return response

	def processStr(self,inStr):
		response = [str(s) for s in inStr.split() if not s.isdigit()]
		response.append(inStr)
		response.append("".join(inStr.split()))
		return response
	def processDomain(self,inStr):
		response = []
		response.append(inStr)
		response.extend(inStr.split("."))
		return response
	def processAddress(self,inStr):
		response = []
		response.append(inStr)
		response.extend(inStr.split())
		response.append(''.join(inStr.split()))
		response.extend(self.processNumbers(inStr))
		response.extend(self.processStr(inStr))
		return response
	def processDate(self,inStr):
		response = []
		if "/" in inStr:
			response.extends(inStr.split("/"))
		if "-" in inStr:
			response.extends(inStr.split("-"))
		return response

	def makeQuestion(self,questionStr,storeStr):
		nextQuestion = True

		if not getattr(self,storeStr):
			setattr(self,storeStr, [])

		storeSelf = getattr(self,storeStr)

		while nextQuestion:
			tempAnswer = raw_input(questionStr + " (empty = next question)")
			if tempAnswer != "":
				storeSelf.append(tempAnswer)
			else:
				nextQuestion = False
		setattr(self,storeStr,storeSelf)
	def processInput(self):
		print("processing data...")
        	if len(self.domainName) > 0:
			for domain in self.domainName:
            			self.simpleCollection.extend(self.processDomain(domain))
		if len(self.fullName) > 0:
			for fullName in self.fullName:
				self.simpleCollection.extend(self.processStr(fullName))
        	if len(self.address) > 0:
			for address in self.address:
            			self.simpleCollection.extend(self.processAddress(address))
        	if len(self.aditionalData) > 0:
            		for data in self.aditionalData:
                		self.simpleCollection.extend(self.processStr(data))
		if len(self.importantDate) > 0:
			for date in self.importantDate:
				self.simpleCollection.extend(self.processDate(date))
		if len(self.identification) > 0:
			for identification in self.identification:
				self.simpleCollection.extend(self.processAddress(identification))
		tempTitles = []
		for text in self.simpleCollection:
			if str(text).title() in self.simpleCollection:
				tempTitles.append(str(text).title())
		self.simpleCollection.extend(tempTitles)

		cleanList = []
		for stringPosible in self.simpleCollection:
			if stringPosible not in cleanList:
				cleanList.append(stringPosible)
		self.simpleCollection = cleanList
        	self.greenPrint("Done")

	def greenPrint(self, text):
		print '\033[92m' + text + " " + u'\u2713' + '\033[0m'

	def generateDictionary(self):
		print "writing file..."
		lines = []
		for i in range(1, self.convinationLevel + 1):
			# print self.simpleCollection
			res = itertools.product(self.simpleCollection, repeat=i)
			for j in res:
				posiblePass = ''.join(j)
				lines.append(posiblePass)
		self.makeFile(lines)
		self.greenPrint("write file done")
		self.makeFile(lines)

	def makeFile(self, lines):
		with open('pass.txt', 'a') as passFile:
			for line in lines:
				passFile.write(line+'\n')


dictionaryMaker  = DictionaryMaker()
dictionaryMaker.welcome()
