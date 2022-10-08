import math
import random
from typing import List
from music21 import stream, chord, note, roman, converter, pitch
from pychord import Chord
import pygame
from mido import MidiFile


#the constants used
generationSize = 10
probabilityOfMatingFailure = 30
probabilityOfMutation = 0.05
#n is the number of chords needed
# numberOfGenerations is a counter to count the generations made so far
#file num is input file number we're working on -> where 0 is barbie file
n = 0
numberOfGenerations: int = 0
fileNum = 0
#population: population of accompaniments we're working on
# inputMelody: current melody we're working on;
# melody: list of all input melodies; notes: list of notes in current input melody
population = list()
inputMelody: stream.Stream
melody = []
notes = []

##contains the root note, which represents the chord ~3 notes
class gene:
    c = Chord('Am')
    ##choose a random chord
    def __init__(self):
        options = ["C", "C#", "Db", "D", "Eb", "E", "F", "F#","Gb","G","Ab","A","Bb","B","Cm",
                   "C#m", "Dm","D#m","Ebm","Em","Fm","F#m","Gm","G#m","Abm","Am","A#m","Bbm","Bm",
                   "Cdim", "C#dim", "Ddim", "Csus2", "C#sus2" , "Dsus2","Ebsus2", "Esus2", "Fsus2", "F#sus2",
                    "Gsus2", "Absus2", "Asus2", "Bbsus2", "Bsus2","Csus4", "C#sus4", "Dsus4", "Ebsus4",
                   "Esus4", "Fsus4", "F#sus4", "Gsus4", "Absus4", "Asus4", "Bbsus4", "Bsus4"]
        ch = options[random.randint(0,51)]
        self.c = Chord(ch)

    ##mutation occurs with the probability specified above
    def mutate(self):
        if(random.uniform(0,1) <= probabilityOfMutation):
            options = ["C", "C#", "Db", "D", "Eb", "E", "F", "F#", "Gb", "G", "Ab", "A", "Bb", "B", "Cm",
                       "C#m", "Dm", "D#m", "Ebm", "Em", "Fm", "F#m", "Gm", "G#m", "Abm", "Am", "A#m", "Bbm", "Bm",
                       "Cdim", "C#dim", "Ddim", "Csus2", "C#sus2", "Dsus2", "Ebsus2", "Esus2", "Fsus2", "F#sus2",
                       "Gsus2", "Absus2", "Asus2", "Bbsus2", "Bsus2", "Csus4", "C#sus4", "Dsus4", "Ebsus4",
                       "Esus4", "Fsus4", "F#sus4", "Gsus4", "Absus4", "Asus4", "Bbsus4", "Bsus4"]
            ch = options[random.randint(0, 51)]
            self.c = Chord(ch)

##represents the melody of the accompaniment
class Individual:
    genes = []
    fitness = 0.0
    global n
    ##fitness is the beautiness, the higher the fitness the better
    def __init__(self):
        self.genes = []
        for i in range(n):
            temp = gene()
            self.genes.append(temp)
        self.fitness = self.calculateFitness()

    ##after mating, mutation could occure, and then fitness is calculated
    def  mate(self, temp):
        child= Individual()
        for i in range(n):
            if(random.uniform(0,1) <= 0.5):
                child.genes[i] = self.genes[i]
            else:
                child.genes[i] = temp.genes[i]
            child.genes[i].mutate()
        return child

    def calculateFitness(self):
        temp= 0.0
        #get stream of individual + list of chords
        s = stream.Stream()
        chordsList = []
        for ch in self.genes:
            tempStr = ""
            strng = ch.c.components(True)
            for i in strng:
                tempStr += i
                tempStr += ' '
            chrd = chord.Chord(tempStr)
            chordsList.append(chrd)
            s.append(chrd)

        #criteria 1
        if s.analyze('key') == inputMelody.analyze('key'):
            temp+=20
        else:
            temp-=20

        #criteria 2
        ki = inputMelody.analyze('key')
        for x in chordsList:
            sf = roman.romanNumeralFromChord (x, ki)
            if isCorrectRomanNumeral(sf):
                temp+=5
            elif(isChordSus(x)):
                temp+=1
            else:
                temp-=5

        #criteria 3
        j = 0
        for x in chordsList:
            F = x.notes[0].pitch.freq440
            if(j < len(notes)):
                for y in notes[j]:
                    F2 = note.Note(y).pitch.freq440
                    temp-= (math.log(math.lcm(F,F2)) * 2)
                j+=1
        return temp

    ##for comparison used in sorting, we define lower than and greater than operators
    def __lt__(self, right):
        return self.fitness < right.fitness
    def __gt__(self, right):
        return self.fitness > right.fitness

##fitness helper functions
def isChordSus(ch):
    temp = ["Csus2", "C#sus2", "Dsus2", "Ebsus2", "Esus2", "Fsus2", "F#sus2",
    "Gsus2", "Absus2", "Asus2", "Bbsus2", "Bsus2", "Csus4", "C#sus4", "Dsus4", "Ebsus4",
    "Esus4", "Fsus4", "F#sus4", "Gsus4", "Absus4", "Asus4", "Bbsus4", "Bsus4"]
    for x in temp:
        if ch == x:
            return 1
    return 0
def isCorrectRomanNumeral(sf):
    for x in sf.figure:
        if(x != 'I' and x!= 'V' and x!= 'v' and x!= 'i'):
            return 0
    return 1
def getInputNotes():
    tempList = []
    global notes
    notes = []
    d = 0
    for n in inputMelody.flat.notesAndRests:
        d += float(n.duration.quarterLength)
        if type(n) == 'rest':
            tempList.append('rest')
        if d == 1:
            notes.append(tempList)
        d -= 1
        tempList.clear()
        continue
        if d > 1:
            notes.append(tempList)
            d -= 1
            tempList.append('rest')
        if type(n) != 'rest':
            tempList.append(str(n.name))
            if d == 1:
                notes.append(tempList)
                d = 0
                tempList.clear()
                continue
            if d > 1:
                notes.append(tempList)
                d -= 1
                tempList.clear()
                tempList.append(str(n.name))

##create a random initial population to start with
def makeInitialPopulation():
    global population
    for i in range(generationSize):
        newIndividual = Individual()
        population.append(newIndividual)
    getInputNotes()

##selection part of the genetic algorithm
def selectAdvancedIndividuals():
    global population
    #sort to have the most fit first
    population.sort()
    #make a new population to store children
    newPopulation: List[Individual]= list()
    temp = Individual()
    #mating with giving the most fit a higher probability in mating
    i= len(population)-1
    while(i>=0):
        j= i-1
        while(j>=max(0,i-2)):
            probability= (random.randint(0,99))+(i*2)
            if(probability>probabilityOfMatingFailure):
                temp= population[i].mate(population[j])
                newPopulation.append(temp)
            j-=1
        i-=1

    for i in newPopulation:
        i.fitness = i.calculateFitness()
    #sort to have most fit first
    newPopulation.sort()
    newPopulation.reverse()
    #eliminate from the new population so that it suits the generation size
    while(int(len(newPopulation))>generationSize):
        newPopulation.pop()

    population = newPopulation
    return

##play the music file given
def playMusic(midiFile: MidiFile):
    pygame.mixer.init(44100, -16, 2, 1024)
    clock = pygame.time.Clock()
    pygame.mixer.music.load(midiFile.filename)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        clock.tick(30)

##add the output melody to the input so they can be played in sync
def JoinOutputWithInput(person):
    s = stream.Stream()
    for ch in person.genes:
        temp = ""
        strng = ch.c.components(True)
        for i in strng:
            temp += i
            temp += ' '
        chrd = chord.Chord(temp)
        s.append(chrd)
    y = 8
    for x in inputMelody.pitches:
            y = min(y, x.octave)
    for x in s.pitches:
        x.octave = y

    chordified = s.chordify()
    inputMelody.chordify()
    global fileNum
    name = "./result" + str(fileNum) + ".mid"
    chordified.write('midi', 'temp.mid')
    inputMelody.append(chordified)

    inputMelody.write('midi',name)
    name = "result" + str(fileNum) + ".mid"
    mf = MidiFile(name, clip=True)
    for msg in mf.play():
        if(msg.type == 'note_on' or msg.type == 'note_off'):
            msg.velocity = 44

    return mf

##read data from files and store it in lists
def readData():
    global melody
    melody.append(MidiFile('barbiegirl.mid', clip=True))
    melody.append(MidiFile('input1.mid', clip=True))
    melody.append(MidiFile('input2.mid', clip=True))
    melody.append(MidiFile('input3.mid', clip=True))

##take input, run the algorithm, print output
def start():
    readData()
    global numberOfGenerations, n, melody, population, inputMelody,fileNum

    for i in melody:
        if(fileNum != 1):
            fileNum+=1
            continue
        inputMelody = converter.parse(i.filename)
        n = len(inputMelody.recurse().getElementsByClass('Measure'))
        n *= 4
        print("For input number ",fileNum," , we'll run the algorithm for " ,n, " chords")
        makeInitialPopulation()
        numberOfGenerations = 0
        selectAdvancedIndividuals()
        for j in range(200):
            numberOfGenerations +=1
            selectAdvancedIndividuals()
            if(population[int(len(population))-1].fitness > 100):
                break
            print(numberOfGenerations)
        print("Playing the result for file " , fileNum, ": ")
        x = JoinOutputWithInput(population[int(len(population))-1])
        playMusic(x)
        population.clear()
        fileNum += 1
    return

start()