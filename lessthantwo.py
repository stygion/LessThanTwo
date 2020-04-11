from flask import url_for
from boardgame import Boardgame

PH01_CHOOSE_GUESSER = 'choose_guesser'    
PH02_CHOOSE_WORD = 'choose_word'
PH03_GIVE_CLUES = 'give_clues'
PH04_CROP_CLUES = 'crop_clues'
PH05_GUESS_SOLUTION = 'guess_solution'
PH06_EVALUATION = 'evaluation'

transition = {
    PH01_CHOOSE_GUESSER: PH02_CHOOSE_WORD,
    PH02_CHOOSE_WORD: PH03_GIVE_CLUES,
    PH03_GIVE_CLUES: PH04_CROP_CLUES,
    PH04_CROP_CLUES: PH05_GUESS_SOLUTION,
    PH05_GUESS_SOLUTION: PH06_EVALUATION,
    PH06_EVALUATION: PH01_CHOOSE_GUESSER
}

class LessThanTwo(Boardgame):

    def __init__(self):
        super().__init__()
        self.reset()

    def reset(self):        
        self.phase = PH01_CHOOSE_GUESSER
        self.guesser_pid = None
        self.solution = None
        self.guess = None
        self.clues = {}
        self.hiddenClues = []

    def playerPids(self):
        return [pid for pid in self.players if pid != self.guesser_pid]

    def setGuesser(self, guesser_pid):
        if self.isKnownPlayer(guesser_pid):
            self.guesser_pid = guesser_pid

    def isGuesser(self, pid):
        return self.guesser_pid == pid

    def setSolution(self, solution):
        self.solution = solution

    def addClue(self, pid, clue):
        self.clues[pid] = clue

    def hideClue(self, pid):
        self.hiddenClues.append(pid)

    def unhideClue(self, pid):
        self.hiddenClues.remove(pid)

    def makeGuess(self, guess):
        self.guess = guess

    def nextPhase(self):
        self.phase = transition[self.phase]
        if self.phase == PH01_CHOOSE_GUESSER:
            self.reset()

    def maySeeClues(self, pid):
        return self.isKnownPlayer(pid) and pid in self.clues

    ##
    # player perspective
    ##

    def perspective_clues(self, viewer_pid):
        clues = {
            pid: {
                'pid': pid,
                'word': word,
                'hidden': pid in self.hiddenClues,
            } for pid, word in self.clues.items()
        }
        if not self.maySeeClues(viewer_pid):
            for clue in clues.values():
                clue['word'] = '?'
        return clues

    def perspective_solution(self, viewer_pid):
        if viewer_pid == self.guesser_pid:
            return None
        else:
            return self.solution        

    def perspective_actions(self, viewer_pid):
        actions = {
            'next_phase': {
                'description': 'Nächste Phase',
                'method': 'POST',
                'url': url_for('next_phase')
            }
        }

        if self.phase == PH01_CHOOSE_GUESSER:
            actions['choose_guesser'] = {
                    'method': 'PUT',
                    'url': url_for('choose_guesser')
            }

        if self.phase == PH02_CHOOSE_WORD:
            if not self.isGuesser(viewer_pid):
                actions['choose_solution'] = {
                    'method': 'PUT',
                    'url': url_for('choose_solution')                    
                }

        if self.phase == PH03_GIVE_CLUES:
            if not self.isGuesser(viewer_pid):
                if not viewer_pid in self.clues:
                    actions['give_clue'] = {
                        'method': 'POST',
                        'url': url_for('give_clue')                    
                    }

        if self.phase == PH04_CROP_CLUES:
            if not self.isGuesser(viewer_pid):
                pass
                # TODO hide/unhide actions

        if self.phase == PH05_GUESS_SOLUTION:
            if self.isGuesser(viewer_pid):
                actions['make_guess'] = {
                    'method': 'PUT',
                    'url': url_for('make_guess')                    
                }

        if self.phase == PH06_EVALUATION:
            pass

        return actions

    def perspective(self, viewer_pid):
        perspective = super().perspective(viewer_pid)

        stage = {
            'phase': self.phase,
            'guesser_pid': self.guesser_pid,
            'guess': self.guess,
            'solution': self.perspective_solution(viewer_pid),
            'clues': self.perspective_clues(viewer_pid),
            'actions': self.perspective_actions(viewer_pid)
        }
        perspective['stage'] = stage

        return perspective