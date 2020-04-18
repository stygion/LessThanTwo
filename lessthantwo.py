from enum import IntEnum
from boardgame import Boardgame

class Phase(IntEnum):
    CHOOSE_GUESSER = 1
    CHOOSE_SOLUTION = 2
    GIVE_CLUES = 3
    CROP_CLUES = 4
    MAKE_GUESS = 5
    EVALUATION = 6


class LessThanTwo(Boardgame):

    def __init__(self):
        super().__init__()
        self.reset()

    def reset(self):
        self.phase = Phase.CHOOSE_GUESSER
        self.guesser_pid = None
        self.solution = None
        self.guess = None
        self.clues = {}
        self.hiddenClues = []
        self.incVersion()        

    def playerPids(self):
        return [pid for pid in self.players if pid != self.guesser_pid]

    def setGuesser(self, guesser_pid):
        if self.isKnownPlayer(guesser_pid):
            self.guesser_pid = guesser_pid
        self.incVersion()            

    def isGuesser(self, pid):
        return self.guesser_pid == pid

    def setSolution(self, solution):
        self.solution = solution
        self.incVersion()        

    def addClue(self, pid, clue):
        self.clues[pid] = clue
        self.incVersion()        

    def setClueHidden(self, pid, hidden):
        if hidden:
            self.hideClue(pid)
        else:
            self.unhideClue(pid)
        self.incVersion()            

    def hideClue(self, pid):
        self.hiddenClues.append(pid)

    def unhideClue(self, pid):
        self.hiddenClues.remove(pid)

    def makeGuess(self, guess):
        self.guess = guess
        self.nextPhase()
        self.incVersion()

    def nextPhase(self):
        if self.phase == list(Phase)[-1]:
            self.reset()
        else:            
            self.phase = Phase(self.phase.value + 1)
        self.incVersion()

