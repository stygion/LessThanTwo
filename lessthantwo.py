from boardgame_util import similar
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
        self.duplicate_clues = set()
        self.incVersion()        

    def setGuesser(self, guesser_pid):
        if self.isKnownPlayer(guesser_pid):
            self.guesser_pid = guesser_pid
        self.incVersion()            

    def setSolution(self, solution):
        self.solution = solution
        self.incVersion()        

    def _find_similar_clues(self):
        for this_key, this_clue in self.clues.items():
            for that_key, that_clue in self.clues.items():
                if this_key != that_key and similar(this_clue, that_clue):
                    self.duplicate_clues.add(this_key)
                    self.duplicate_clues.add(that_key)

    def add_clue(self, pid, clue):
        self.clues[pid] = clue
        self.incVersion()        

    def setClueHidden(self, pid, hidden):
        if hidden:
            self.hideClue(pid)
        else:
            self.unhideClue(pid)
        self.incVersion()            

    def hideClue(self, pid):
        self.duplicate_clues.add(pid)

    def unhideClue(self, pid):
        self.duplicate_clues.remove(pid)

    def makeGuess(self, guess):
        self.guess = guess
        self.next_phase()
        self.incVersion()

    def next_phase(self):
        if self.phase == list(Phase)[-1]:
            self.reset()
        else:            
            self.phase = Phase(self.phase.value + 1)
        if self.phase is Phase.CROP_CLUES:
            self._find_similar_clues()

        self.incVersion()

