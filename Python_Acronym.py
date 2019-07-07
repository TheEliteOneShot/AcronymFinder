import re
import numpy
import collections

## Python tested with python 3.30 & numpy packages
## Name: Zachary Laney
## Student ID: 2001116332

## CONFIGURATION SETTINGS
#********************************
# TEST FILE NAME (formatted text)
TEST_FILE_NAME = "testfile2.txt"
#File should be stored in same directory as executable
#********************************
MINIMUM_ACRONYM_SIZE = 3 ## Minimum allowable suspected acronym size
MAXIMUM_ACRONYM_SIZE = 10 ## Maximum allowable suspected acronym size
WINDOW_SIZE_MULTIPLE = 2 ## How many times to multiply the length of the suspected acronym for a chosen window size
ROLLING_QUEUE_SIZE = 21 ##Size of rolling queue of words as the document is scanned
## List of words that will be considered as STOPWORDS
STOP_WORD_LIST = ["ourselves", "hers", "between", "yourself", "but", "again", "there", "about", "once", "during", "out", "very", "having", "with", "they", "own", "an", "be", 
                  "some", "for", "do", "its", "yours", "such", "into", "of", "most", "itself", "other", "off", "is", "s", "am", "or", "who", "as", "from", "him", "each", "the", 
                  "themselves", "until", "below", "are", "we", "these", "your", "his", "through", "don", "nor", "me", "were", "her", "more", "himself", "this", "down", "should", 
                  "our", "their", "while", "above", "both", "up", "to", "ours", "had", "she", "all", "no", "when", "at", "any", "before", "them", "same", "and", "been", "have", 
                  "in", "will", "on", "does", "yourselves", "then", "that", "because", "what", "over", "why", "so", "can", "did", "not", "now", "under", "he", "you", "herself", 
                  "has", "just", "where", "too", "only", "myself", "which", "those", "i", "after", "few", "whom", "t", "being", "if", "theirs", "my", "against", "a", "by", "doing", 
                  "it", "how", "further", "was", "here", "than"]
#*********************************#
file = open(TEST_FILE_NAME, 'r', encoding='utf-8') ## Open our file
q = collections.deque([], maxlen = ROLLING_QUEUE_SIZE) ## keep a rolling queue for memory purposes

##Basically an enum. Provides easier manner for the LCSArray/bArray matrix processing
class Direction:
    UpLeft = 1
    Up = 2
    Left = 3
    pass

##Acronym Object provides unique instances of a possible acronym before the comparison phase with all the important information
class Acronym:
    def __init__ (self, _acronym, _definition, _size, _distance, _misses, _stopcount, _vector, _number):
        self.ACRONYM = _acronym
        self.DEFINITION = _definition
        self.SIZE = _size
        self.DISTANCE = _distance
        self.MISSES = _misses
        self.STOPCOUNT = _stopcount
        self.VECTOR = _vector
        self.NUMBER = _number      

class AcronymManager:
    AcronymAmount = 0 ## int amount of Acronym Objects
    AcronymList = [] ## An array of Acronym Objects

    @staticmethod
    ##Obtains the chosen acronym definition in the prewindow using the provided vector values
    def getDefintionFromVector(definition, vector):
        targetDefinition = ""
        
        ##Provide a chosen acronym definition string seperated by spaces
        for v in range(0, len(vector)):
            if (vector[v] > 0) & (len(targetDefinition) == 0):
                targetDefinition = targetDefinition + definition[v] ## If first word, don't use padding in front of string. 
            elif (vector[v] > 0 ):
                targetDefinition = targetDefinition + " " + definition[v] ## If not first word, add words to the string
        return targetDefinition

    @staticmethod
    ##Returns the array containing all Acronym Objects
    def getCurrentAcronymList():
        return AcronymManager.AcronymList

    @staticmethod
    ##Increments the int variable containing the amount of Acronym Objects that are in the static Acronym Object array
    def incrementAcronymAmount():
        AcronymManager.AcronymAmount = AcronymManager.AcronymAmount + 1
        return AcronymManager.AcronymAmount

    @staticmethod
    ##Stores an Acronym Object into a static array of Acronym Objects
    def storeAcronym(Acronym): 
        AcronymManager.AcronymList.append(Acronym.ACRONYM)

    @staticmethod
    ##Compares two vectors with the use of their unique information
    def compareVectors(v1, v2):
        if (v1.MISSES > v2.MISSES): #1
            return v2
        elif(v1.MISSES < v2.MISSES): #2
            return v1
        elif (v1.STOPCOUNT > v2.STOPCOUNT): #3
            return v2
        elif (v1.STOPCOUNT < v2.STOPCOUNT): #4
            return v1
        elif (v1.DISTANCE > v2.DISTANCE): #5
            return v2
        elif (v1.DISTANCE < v2.DISTANCE): #6
            return v1
        elif (v1.SIZE > v2.SIZE): #7
            return v2
        elif (v1.SIZE < v2.SIZE): #8
            return v1
        return v1
        pass

    @staticmethod
    ##Calculates all the unique information needed from the vector array in order to build an Acronym Object 
    def processVector(vector, typeArray, leaderArrayExpanded, acronym):

        FIRST = 0
        LAST = 0
        SIZE = 0
        DISTANCE = 0
        MISSES = 0
        STOPCOUNT = 0
        
        i = 0
        while (True):
            if (i < len(vector)) & (vector[i] == 0):
                i = i + 1
            else:
                break

        FIRST = i ##FIRST VALUE
        i = len(vector)

        while (True):
            if ((i > -1) & (vector[i-1] == 0)):
                i = i - 1
            else:
                break

        LAST = i ##LAST VALUE
        SIZE = LAST - FIRST ##SIZE VALUE
        DISTANCE = len(vector) - LAST ##DISTANCE VALUE

        for i in range(FIRST, LAST):
            if (vector[i] > 0) & (typeArray[i] == "s"):
                STOPCOUNT = STOPCOUNT + 1 ##STOPCOUNT VALUE
            elif ((vector[i] != 0) & (typeArray[i] != "s")) & ((vector[i] != 0) & (typeArray[i] != "h")):
                MISSES = MISSES +1 ##MISSES VALUE

        ## DEAL WITH CAPITALIZATION ISSUES HERE
        tArrayNoH = typeArray.copy()
        length = len(typeArray) - 1
        for i in range(0, length): ##Remove little h so our arrays match in length
            if (typeArray[i] == "h"):
                tArrayNoH.remove(typeArray[i])

        length = len(tArrayNoH)

        for word in range(0, length):
            if (tArrayNoH[word] == "w"):
                leaderArrayExpanded[word] = leaderArrayExpanded[word].capitalize()
            elif (tArrayNoH[word] == "H"):
                leaderArrayExpanded[word] = leaderArrayExpanded[word].capitalize()
                word = word + 1

        #Initialize an instance of an Acronym Object using all necessary information
        A = Acronym(acronym, leaderArrayExpanded, SIZE, DISTANCE, MISSES, STOPCOUNT, vector, AcronymManager.incrementAcronymAmount())
        ##Add that object to our static array of Acronym Objects
        AcronymManager.AcronymList.append(A)

    @staticmethod
    ##Parent function for executing the calculation of an Acronym Object's vector values
    def calculateVectorValues(listOfVectors, typeArray, expandedLeaderArray, acronym):
        ##Processes a vector within an array of vector arrays
        for vector in listOfVectors:
            AcronymManager.processVector(vector, typeArray, expandedLeaderArray, acronym)

    @staticmethod
    ## Builds an array of vectors from an array of stacks
    def buildVectorList(listOfStacks, leaderArray):
        vectorSize = 0
        acryVector = []
        listOfVectors = []
        ##Process each stack in a list in the array of lists
        for list in listOfStacks:
            vectorSize = len(leaderArray) # Acronym size * window size multiple
            acryVector = numpy.zeros([vectorSize])
            for node in list:
                acryVector[node[1]-1] = node[0]
            listOfVectors.append(acryVector)
        return listOfVectors

    @staticmethod
    ## Find all possible acronym matches in an LCSMatrix
    def parseLCSMatrix(bArray, LCSArray, acronym):
        Stack = []
        listOfStacks = []

        iDim = numpy.shape(bArray)[0]
        jDim = numpy.shape(bArray)[1]

        #Goes from top left to right. Picks the first "UpLeft" which signifies a new vector array. 
        #Finds the next "UpLeft" value and adds it to the array if the value is greater than the previous value.
        icount = 0
        LCSCount = len(acronym) + 1
        for i in range(1, iDim):
            for j in range(1, jDim):
                if (bArray[i,j] == Direction.UpLeft) & (LCSArray[i,j] == 1):
                    Stack.append((i, j))
                    LCSCount = LCSCount - 1
                    for x in range(i+1, iDim):
                        for y in range(j+1, jDim):
                            if (bArray[x,y] == Direction.UpLeft) & (LCSCount > 1):
                                LCSCount = LCSCount - 1
                                Stack.append((x,y))
                            if (LCSCount == 1):
                                listOfStacks.append(Stack.copy())
                                LCSCount = len(acronym) + 1
                                del Stack[:]
        return listOfStacks

    @staticmethod
    ##Build the Longest Common Subsequence matrix using all the necessary information
    def buildLCSMatrix(acronym, leader_type_expanded_Arrays):

        leaderArray = []
        expandedLeaderArray = []

        ##Build leader array
        for i in range(0, len(leader_type_expanded_Arrays[0])):
            leaderArray.append(leader_type_expanded_Arrays[0][i])

        #Build expanded leader array
        for i in range(0, len(leader_type_expanded_Arrays[2])):
            expandedLeaderArray.append(leader_type_expanded_Arrays[2][i])

        leaderString = ''.join(leaderArray)

        acronymLength = len(acronym)
        leaderLength = len(leaderString)

        #The longest common substring array
        LCSArray = numpy.zeros([acronymLength + 1, leaderLength + 1])
        bArray = LCSArray.copy()
        
        ##Build the bArray for the LCS array
        for c1 in range(1, acronymLength + 1):
            for c2 in range(1, leaderLength + 1):
                if acronym[c1 - 1].lower() == leaderString[c2 - 1]:
                    LCSArray[c1,c2] = LCSArray[c1 - 1, c2 - 1] + 1
                    bArray[c1,c2] = Direction.UpLeft
                elif LCSArray[c1 - 1, c2] >= LCSArray[c1, c2 - 1]:
                    LCSArray[c1, c2] = LCSArray[c1 - 1, c2]
                    bArray[c1,c2] = Direction.Up
                else:
                    LCSArray[c1, c2] = LCSArray[c1, c2 - 1]
                    bArray[c1,c2] = Direction.Left

        #Parse our LCSMatrix
        listOfStacks = AcronymManager.parseLCSMatrix(bArray, LCSArray, acronym)

        #Build a list of vectors with our LCSMatrix data
        listOfVectors = AcronymManager.buildVectorList(listOfStacks, leaderArray)

        if (len(listOfVectors) != 0):
           AcronymManager.calculateVectorValues(listOfVectors, leader_type_expanded_Arrays[1][::-1], expandedLeaderArray, acronym)

    @staticmethod
    ##Checks whether a given word is in the STOP_WORD_LIST 
    def isStopWord(word):
        for sw in STOP_WORD_LIST:
            if sw == word:
                return True
        return False

    @staticmethod
    ##Trys to detect whether something is a detected acronym or not
    def isAcronym(word):
        if word.isalpha() & word.isupper() & (len(word) >= MINIMUM_ACRONYM_SIZE) & (len(word) <= MAXIMUM_ACRONYM_SIZE):
            return True
        else:
            return False

    @staticmethod
    ##Trys to detect whether something is a word corresponding to only alphanumeric characters
    def isWord(word):
        word = re.search('[a-zA-Z]+', word)
        if word:
            answer = True
        else:
            answer = False
        return answer

    @staticmethod
    def generateWindow(currentQueue, suspectedAcronym):

        windowSize = len(suspectedAcronym) * WINDOW_SIZE_MULTIPLE
        leaderArray = []
        typeArray = []
        leaderArrayExpanded = []

        ##Build the array of first character leaders, expanded (full word) leaders, and corresponding word type array
        for i in range(0, windowSize):
            word = currentQueue.pop()
            if "-" in word:
                hyphenated_words = word.split("-")
                hyphenated_words.reverse()
                isFirst = 1
                for hyphenated_word in hyphenated_words: ## Deal with hyphenated words in a special manner
                    if isFirst == 1:
                        typeArray.append("h")
                        leaderArray.append(hyphenated_word[:1].lower())
                        isFirst = 0
                    else:
                        typeArray.append("H")
                        leaderArray.append(hyphenated_word[:1].lower())
            else:
                if AcronymManager.isStopWord(word):
                    typeArray.append("s")
                else:
                    typeArray.append("w")
                leaderArray.append(word[:1].lower())
            leaderArrayExpanded.append(word.lower())

        leaderArray = leaderArray[::-1] 

        leaderArrayExpanded.reverse()
        leader_type_expanded_Arrays = [leaderArray, typeArray, leaderArrayExpanded]

        return leader_type_expanded_Arrays

## THE MAIN CLASS AND PROGRAM ENTRY POINT
class Main:
    for line in file:
        words = line.split() ## Read in all words
        for word in words:
            w = re.sub("[!@#$.;,()~{}]+", "", word) ## Prevent these characters from being read into the input
            if (AcronymManager.isAcronym(w)):
                AcronymManager.buildLCSMatrix(w, AcronymManager.generateWindow(q, w)) ##Begin acronym object building routine
            if AcronymManager.isWord(w):
                q.append(w)

    compareList = []
    fullList = []

    fullList = AcronymManager.getCurrentAcronymList()
    names = []
    for e in fullList:
        names.append(e.ACRONYM)

    i = 0

    finalAcronymNames = []
    exists = True
    finalAcronymNames = fullList.copy()
    names = list(set(names))
    finalAcronymNames = names

    targetSize = len(finalAcronymNames)
    finalList = []

    current = 0

    ifbreak = False

    ##Find a similar acronym objects in the fullList of possible acronyms with respective atrributes. Compare those acronym objects
    ##using compareVectors and remove it's return value. Repeat until the fullList only contains targetSize value of acronyms
    ##thereby producing our finalList. 
    while (current < targetSize):
        for e1 in fullList:
            for e2 in fullList:
                if (e1.ACRONYM == e2.ACRONYM) & (e1.NUMBER != e2.NUMBER):
                    temp = AcronymManager.compareVectors(e1,e2)
                    for e in fullList:
                        if (temp.NUMBER == e.NUMBER):
                            fullList.remove(e)
                    ifbreak = True
                    break
            if (ifbreak):
                ifbreak= False
                break

            finalList.append(e1)
            current = current + 1

    ######  CONSOLE OUTPUT BELOW ######
    col_width = len(word) + 4
    print("______________________________________________________________________________________")
    print("    Acronym     |                            Definition                              |")
    print("______________________________________________________________________________________")
    num = 0
    for e in fullList:
        definition = AcronymManager.getDefintionFromVector(e.DEFINITION, e.VECTOR)
        if (definition.endswith("'s")): ## Prevents acronym's from ending with "'s"
            definition = definition.replace("'s", "")
        print(str(num) + ":    " + e.ACRONYM.ljust(col_width) + "|" + definition.ljust(col_width))
        print("______________________________________________________________________________________")
        num = num + 1





