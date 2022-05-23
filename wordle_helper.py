import os
import sys
import collections
from model import HelperResponse

def getLanguage():
    lang = 'en'

    if len(sys.argv)<2:
        print('usage: wordle-solver lang\n where lang is language used\ncurrently supported languages are: en, hr')
    elif sys.argv[1] == 'hr':
        lang = 'hr'
    else:
        print('using default language en')
    return lang

def getPossibleCharacters(lang):
    if lang == 'hr':
        return ['ertzuiopšđasdfghjklčćcvbnmž',
            'ertzuiopšđasdfghjklčćcvbnmž',
            'ertzuiopšđasdfghjklčćcvbnmž',
            'ertzuiopšđasdfghjklčćcvbnmž',
            'ertzuiopšđasdfghjklčćcvbnmž']
    elif lang == 'en':
        return ['qwertyuiopasdfghjklzxcvbnm',
                'qwertyuiopasdfghjklzxcvbnm',
                'qwertyuiopasdfghjklzxcvbnm',
                'qwertyuiopasdfghjklzxcvbnm',
                'qwertyuiopasdfghjklzxcvbnm']

def getGlobInput():
    glob = ''
    while not checkGlob(glob): 
        glob = input("enter glob e.g. 'a*d-i+e*u-' where '*' is yellow field,\n'+' is green field and '-' is gray field. Enter exit any time to exit.\n")

    if glob == 'exit':
        sys.exit('bye!') 
    return glob

def processGlob(poss, included, glob):
    starPlusCountByLetter = {}
    for index, item in enumerate(glob):
        #designator *,+ or -
        if index % 2!=0:
            character = glob[index-1]
            lettIndex = index//2
            if item=='*':
                poss[lettIndex] = poss[lettIndex].replace(character , '')
                if starPlusCountByLetter.get(character):
                    starPlusCountByLetter[character] += 1
                else:
                    starPlusCountByLetter[character] = 1
            elif item=='+':
                poss[lettIndex] = str(character)
                if starPlusCountByLetter.get(character):
                    starPlusCountByLetter[character] += 1
                else:
                    starPlusCountByLetter[character] = 1
            elif item=='-':
                #if minus then remove from all positions in poss array
                #unless it is in included (that means that letter repeats in glob)
                if character not in included:
                    for index2, charas_array in enumerate(poss):
                        poss[index2] = poss[index2].replace(character, '')
                else:
                    poss[lettIndex] = poss[lettIndex].replace(character , '')
    
    for letter in starPlusCountByLetter:
        countForLetter = starPlusCountByLetter.get(letter)
        if letter not in included:
            for i in range(countForLetter):
                  included+=letter
        elif included.count(letter)<countForLetter:
            missingCount = countForLetter-included.count(letter)
            for i in range(missingCount):
                  included+=letter

    return poss, included

def checkGlob(glob):
    if glob == 'exit':
        return True
    if len(glob) != 10:
        return False
    for index, item in enumerate(glob):
        if index %2 !=0:
            if item != '*' and item != '+' and item != '-':
                return False
        else:
            if not item.isalpha():
                return False
    return True
def getAllWordsFromDict(lang):
    dict = open(lang + '.dict', 'r')
    return dict.readlines()

def getResults(poss, included, lang):
    allWords = getAllWordsFromDict(lang) 
    resultWords = []
    for word in allWords:
        word = word.lower().strip()
        if len(word) != 5:
            continue
        #possible:
        isPossible = False
        for index, letter in enumerate(word):
            if letter not in poss[index]:
                break
            if index == 4:
                isPossible = True
        if not isPossible:
            continue
        #included:
        hasAllIncluded = True
        wordCopy=str(word)
        for letter in included:
            if letter not in wordCopy:
                hasAllIncluded = False
                break
            else:
                #in case of repeated letters in word
                wordCopy = wordCopy.replace(letter, '', 1)
        if isPossible and hasAllIncluded:
            resultWords.append(word)
    return resultWords 

def isEliminationSuggestionNeeded(included, results, iteration):
    if len(included) > 2 and (6-iteration) < len(results):
        return True
    else:
        return False

def getLettersByFrequency(lang):
    dict = open(lang + '.dict', 'r')
    words = dict.readlines()
    topLettersDict = {}
    for word in words:
        word = word.lower().strip()
        for letter in word:
            if topLettersDict.get(letter):
                topLettersDict[letter] += 1
            else:
                topLettersDict[letter] = 1
    sortedTopLetterDict =sorted(topLettersDict.items(), key=lambda x: x[1], reverse=True)
    keys = list(collections.OrderedDict(sortedTopLetterDict))
    return keys

def getEliminationSuggestion(poss, results, lang):
    topLettersDict = {}
    notDeterminedIndices = []
    for index, letters in enumerate(poss):
        if not len(letters) == 1:
            notDeterminedIndices.append(index)
    for word in results:
        for index in notDeterminedIndices:
            if topLettersDict.get(word[index]):
                topLettersDict[word[index]] += 1
            else:
                topLettersDict[word[index]] = 1
 
    sortedTopLetterDict =sorted(topLettersDict.items(), key=lambda x: x[1], reverse=True)
    keys = list(collections.OrderedDict(sortedTopLetterDict))
    range = int(5)
    suggestions = []
    generalTopLetters = getLettersByFrequency(lang)
    possExtension = ""
    while not suggestions and range <= len(keys): 
        suggestionPoss = ["".join(keys[0:range]).join(possExtension),
                          "".join(keys[0:range]).join(possExtension),
                          "".join(keys[0:range]).join(possExtension),
                          "".join(keys[0:range]).join(possExtension),
                          "".join(keys[0:range]).join(possExtension)]
        suggestions =getResults(suggestionPoss, [], lang)
        if(range<(len(keys)-1)):            
            range += 1
        else:
            possExtension = generalTopLetters[0:10]
    #scoring suggestions
    scoredSuggestions = {}
    for word in suggestions:
        for letter in keys[0:range]:
            if letter in word and letter:
                if scoredSuggestions.get(word):
                    scoredSuggestions[word] +=1
                else:
                    scoredSuggestions[word] = 1
    sortedScoredSuggestions=sorted(scoredSuggestions.items(), key=lambda x: x[1], reverse=True)
    if len(sortedScoredSuggestions) == 0:
        return []
    topScore = sortedScoredSuggestions[0][1]
    topScoringItems=list(filter(lambda x: x[1]==topScore or x[1]==topScore-1, sortedScoredSuggestions))
    return topScoringItems[:50]

def getTopTip(results,suggestions):
        return list(set(results).intersection(list(map(lambda x: x[0], suggestions))))

def getTopStartingWords(poss, lang):
    allWords = getAllWordsFromDict(lang) 
    return getEliminationSuggestion(poss, allWords, lang)

def printResult(results):
    pretty = ''
    for index, word in enumerate(results):
        pretty += word.strip() + '\t'
        if (index+1)%10 ==0:
            pretty += '\n'
    pretty = pretty[:-1]
    print(pretty)

def printSuggestions(suggestions):
    pretty =''
    for index, tupple in enumerate(suggestions):
        pretty += tupple[0].strip() + '(' + str(tupple[1]) + ')' + '\t'
        if (index+1)%5 == 0:
            pretty += '\n'
    pretty = pretty[:-1]
    print(pretty)

def getApiResult(lang, globs):
    #letters that are in result word
    included = '' 
    #possible letters array
    poss = getPossibleCharacters(lang) 
    for glob in globs.split(','):
        if not checkGlob(glob):
            return 'glob not ok'
        poss, included = processGlob(poss,included, glob)
    results = getResults(poss, included,lang)
    suggestions = getEliminationSuggestion(poss, results, lang)
    topTip = getTopTip(results, suggestions)
    response = SolverResponse(results, suggestions, topTip)
    return response 

def main():
    lang = getLanguage()
    #letters that are in result word
    included = '' 
    #possible letters array
    poss = getPossibleCharacters(lang) 
    print('best starting words:')
    printSuggestions(getTopStartingWords(poss, lang))
    while True:
        glob = getGlobInput() 
        poss, included = processGlob(poss,included, glob)
        #results = executeGrepCommand(generateGrepCommand(poss, included,lang))
        results = getResults(poss, included, lang)
        suggestions = []
        if len(results) == 0:
            sys.exit('sorry no results found.:(')
        if len(results) == 1: 
            sys.exit('done! - result must be "' + results[0].strip() + '"') 
        suggestions = getEliminationSuggestion(poss, results, lang) 
        #words that are both in suggestion and in possible
        topTip = getTopTip(results, suggestions)
        print("elimination guess suggestions [suggestion(score)]:")
        printSuggestions(suggestions)            
        print('possible words:') 
        printResult(results)
        if len(topTip) > 0:
            print('TOP TIP: ')
            printResult(topTip)

if __name__ == "__main__":
   main()
