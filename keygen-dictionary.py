#!/usr/bin/python3
import os

import itertools
import operator
from datetime import datetime

class DictionaryMaker:
    def __init__(self):
        self.aditionalData = []
        self.simpleCollection = ["admin", "adm", "adm", ".", "-", "_", "@"]
        self.convinationLevel = 2
        self.domainName = False
        self.fullName = False
        self.address = False
        self.importantDate = False
        self.identification = False
        self.fillSimpleCollection()

    def fillSimpleCollection(self):
        # Populate with the latest 10 years
        current_year = datetime.now().year
        list_years = [str(i) for i in range(current_year -10, current_year)]
        list_years_end = [str(i)[-2:] for i in range(current_year -10, current_year)]
        self.simpleCollection.extend(list_years)
        self.simpleCollection.extend(list_years_end)
        print(self.simpleCollection)

    def welcome(self):
        print("Welcome human, Please answer the following questions...")
        self.getInputs()
        self.processInput()
        self.generateDictionary()

    def getInputs(self):
        print("Usage: it is possible to enter an empty response...")
        convination = input("convination level: (2 recomended)")
        self.convinationLevel = 2
        if convination != "" :
            self.convinationLevel = int(convination)
        self.makeQuestion("Domain url?", "domainName")
        self.makeQuestion("Address?", "address")
        self.makeQuestion("Full Name?", "fullName")
        self.makeQuestion(
            "Birthdate or important date?(dd-mm-yyyy)", "importantDate")
        self.makeQuestion(
            "Identifier or identification number?", "identification")
        self.makeQuestion("Aditional data?", "aditionalData")

    def processNumbers(self, inStr):
        numbers = [str(s) for s in inStr.split() if s.isdigit()]
        response = []
        for number in numbers:
            for i in range(1, len(number)):
                res = itertools.product(number, repeat=i)
                for convination in res:
                    response.append(''.join(convination))
        return response

    def processStr(self, inStr):
        response = [str(s) for s in inStr.split() if not s.isdigit()]
        response.append(inStr)
        response.append("".join(inStr.split()))
        return response

    def processName(self, inStr):
        response = self.processStr(inStr)
        words = [str(s) for s in inStr.split() if not s.isdigit()]
        for word in words:
            response.append(word[0])
            response.append(word[0].title())
        res = itertools.product(response, repeat=2)
        for convination in res:
            response.append(''.join(convination))
        return self.cleanList(response)

    def processDomain(self, inStr):
        response = []
        response.append(inStr)
        response.extend(inStr.split("."))
        return response

    def processAddress(self, inStr):
        response = []
        response.append(inStr)
        response.extend(inStr.split())
        response.append(''.join(inStr.split()))
        response.extend(self.processNumbers(inStr))
        response.extend(self.processStr(inStr))
        return response

    def processDate(self, inStr):
        response = []
        if "/" in inStr:
            response.extend(inStr.split("/"))
        if "-" in inStr:
            response.extend(inStr.split("-"))

        if len(response) == 3 and len(response[2]) == 4:
            response.append(response[2][:2])
            response.append(response[2][2:])

        if len(response) == 0:
            return response

        res = itertools.combinations(response, 3)
        for convination in res:
            response.append(''.join(convination))

        print("date convinations: " + str(len(response)) + ".")
        return self.cleanList(response)

    def processIdentification(self, inStr):
        if(len(str(inStr)) == 1):
            numbers = [str(inStr)]
        else:
            numbers = [str(s) for s in inStr.split() if s.isdigit()]

        response = []
        for number in numbers:
            for i in range(1, len(number)):
                response.append(number[0:i])
                response.append(number[:i])
        return self.cleanList(response)

    def makeQuestion(self, questionStr, storeStr):
        nextQuestion = True

        if not getattr(self, storeStr):
            setattr(self, storeStr, [])

        storeSelf = getattr(self, storeStr)

        while nextQuestion:
            tempAnswer = input(questionStr + " (empty = next question): ")
            if tempAnswer != "":
                storeSelf.append(tempAnswer)
            else:
                nextQuestion = False
        setattr(self, storeStr, storeSelf)

    def processInput(self):
        print("Starting processing...")
        if len(self.domainName) > 0:
            print("Processing domain name...")
            for domain in self.domainName:
                self.simpleCollection.extend(self.processDomain(domain))
            if len(self.fullName) > 0:
                print("Processing full name...")
                for fullName in self.fullName:
                    self.simpleCollection.extend(self.processName(fullName))
        if len(self.address) > 0:
            print("Processing address...")
            for address in self.address:
                self.simpleCollection.extend(self.processAddress(address))
        if len(self.aditionalData) > 0:
            print("Processing additional data...")
            for data in self.aditionalData:
                self.simpleCollection.extend(self.processStr(data))
        if len(self.importantDate) > 0:
            print("Processing dates...")
            for date in self.importantDate:
                self.simpleCollection.extend(self.processDate(date))
        if len(self.identification) > 0:
            print("Processing identification...")
            for identification in self.identification:
                self.simpleCollection.extend(
                    self.processIdentification(identification))
        tempTitles = []
        for text in self.simpleCollection:
            if not str(text).title() in tempTitles:
                tempTitles.append(str(text).title())
        self.simpleCollection.extend(tempTitles)

        self.greenPrint("Done")

    def cleanList(self, list):
        return sorted(set(list))

    def greenPrint(self, text):
        print('\033[92m' + text + " " + u'\u2713' + '\033[0m')

    def generateDictionary(self):
        print("making words convinations...")
        print(str(len(self.simpleCollection)) + " words.")
        lines = []
        for i in range(1, self.convinationLevel + 1):
            print("starting level: " + str(i) + ".")
            res = itertools.product(self.cleanList(
                self.simpleCollection), repeat=i)
            for j in res:
                posiblePass = ''.join(j)
                lines.append(posiblePass)
            self.greenPrint("leven " + str(i) + ": done")
        print("cleaning List... " + str(len(lines)))
        lines = self.cleanList(lines)
        self.greenPrint("clen list done lines: " + str(len(lines)) + ".")

        print("writing " + str(len(lines)) + " lines in file...")
        self.makeFile(lines)
        self.greenPrint("write file done")

    def makeFile(self, lines):
        with open('pass.txt', 'a') as passFile:
            for line in lines:
                passFile.write(line + '\n')


try:
    dictionaryMaker = DictionaryMaker()
    dictionaryMaker.welcome()
except KeyboardInterrupt:
    print("\n\nKeygen interrupt, Bye!") 
