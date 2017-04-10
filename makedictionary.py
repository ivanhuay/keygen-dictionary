#!/usr/bin/python
import os

import itertools


class DictionaryMaker:
	def __init__(self):
		self.aditionalData = []
		self.simpleCollection = ["admin","adm","adm","2015","2016","2017","2014","2013"]
		self.convinationLevel = 2
		self.domainName = False
		self.address = False

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
		self.makeQuestion("birthdate or important date?(dd-mm-yyyy)","importantDate")
		self.makeQuestion("identifier or identification number?", "identification")
		self.makeQuestion("aditional data?","aditionalData")

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
        	if self.domainName:
            		self.simpleCollection.append(self.domainName)
            		self.simpleCollection.extend(self.domainName.split("."))
        	if self.address:
            		self.simpleCollection.append(self.address)
            		self.simpleCollection.extend(self.address.split(" "))
        	if len(self.aditionalData) > 0:
            		for data in self.aditionalData:
                		self.simpleCollection.append(data)
                		self.simpleCollection.extend(data.split(" "))
				tempTitles = []
		for text in self.simpleCollection:
			if not text.title() in self.simpleCollection:
				tempTitles.append(text.title())
		self.simpleCollection.extend(tempTitles)
        	self.greenPrint("Done")

	def greenPrint(self, text):
		print '\033[92m' + text + " " + u'\u2713' + '\033[0m'

	def generateDictionary(self):
		print "writing file..."
		lines = []
		for i in range(1, self.convinationLevel):
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
