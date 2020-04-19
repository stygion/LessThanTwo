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

    def phase_is_finishable(self):
        if self.phase is Phase.CHOOSE_GUESSER:
            return self.guesser_pid is not None
        if self.phase is Phase.CHOOSE_SOLUTION:
            return self.solution is not None
        if self.phase is Phase.GIVE_CLUES:
            return len(self.clues) + 1 >= len(self.players)
        if self.phase is Phase.CROP_CLUES:
            return True
        if self.phase is Phase.MAKE_GUESS:
            return self.guess is not None
        if self.phase is Phase.EVALUATION:
            return True

    def add_clue(self, pid, clue):
        self.clues[pid] = clue
        self.incVersion()        

    def remove_clue(self, pid):
        self.clues.pop(pid)
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
        if not self.phase_is_finishable:
            return

        if self.phase == list(Phase)[-1]:
            self.reset()
        else:            
            self.phase = Phase(self.phase.value + 1)
        if self.phase is Phase.CROP_CLUES:
            self._find_similar_clues()

        self.incVersion()

