from enum import IntEnum, Enum
from flask import url_for
from boardgame import Boardgame

class Phase(IntEnum):
    CHOOSE_GUESSER = 1
    CHOOSE_WORD = 2
    GIVE_CLUES = 3
    CROP_CLUES = 4
    MAKE_GUESS = 5
    EVALUATION = 6

class Privilege(Enum):
    KICK_ANYBODY     = 'KICK_ANYBODY'
    RENAME_ANYBODY   = 'RENAME_ANYBODY'
    ADVANCE_PHASE    = 'ADVANCE_PHASE'
    CHOOSE_GUESSER   = 'CHOOSE_GUESSER'
    CHOOSE_WORD      = 'CHOOSE_WORD'
    GIVE_CLUE        = 'GIVE_CLUE'
    SEE_SOLUTION     = 'SEE_SOLUTION'
    SEE_OPEN_CLUES   = 'SEE_OPEN_CLUES'
    SEE_ALL_CLUES    = 'SEE_ALL_CLUES'
    CROP_CLUES       = 'CROP_CLUES'
    MAKE_GUESS       = 'MAKE_GUESS'
    RESTART_GAME     = 'RESTART_GAME'
    SEE_EVALUATION   = 'SEE_EVALUATION' 

phasentexte = {
    Phase.CHOOSE_GUESSER: 'Wer soll raten?',
    Phase.CHOOSE_WORD: 'Was soll geraten werden?',
    Phase.GIVE_CLUES: 'Hinweise abgeben',
    Phase.CROP_CLUES: 'Doppelte streichen',
    Phase.MAKE_GUESS: 'Lösung raten',
    Phase.EVALUATION: 'Auswertung',
}    

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
            self.phase = list(Phase)[0]
            self.reset()
        self.phase = Phase(self.phase.value + 1)
        self.incVersion()

    ##
    # player perspective
    ##

    def get_privileges(self, viewer_pid):
        privileges = [
            Privilege.KICK_ANYBODY,
            Privilege.RENAME_ANYBODY,
            Privilege.ADVANCE_PHASE,
            Privilege.RESTART_GAME
        ]

        if self.phase == Phase.CHOOSE_GUESSER:
            privileges.append(Privilege.CHOOSE_GUESSER)

        elif self.phase == Phase.CHOOSE_WORD:
            if self.isGuesser(viewer_pid):
                pass
            else:
                privileges.append(Privilege.CHOOSE_WORD)
                privileges.append(Privilege.SEE_SOLUTION)

        elif self.phase == Phase.GIVE_CLUES:
            if self.isGuesser(viewer_pid):
                pass
            elif viewer_pid not in self.clues:
                privileges.append(Privilege.SEE_SOLUTION)
                privileges.append(Privilege.GIVE_CLUE)
            else:
                privileges.append(Privilege.SEE_SOLUTION)
                privileges.append(Privilege.SEE_ALL_CLUES)

        elif self.phase == Phase.CROP_CLUES:
            if self.isGuesser(viewer_pid):
                pass
            else:
                privileges.append(Privilege.SEE_SOLUTION)
                privileges.append(Privilege.SEE_ALL_CLUES)
                privileges.append(Privilege.CROP_CLUES)

        elif self.phase == Phase.MAKE_GUESS:
            if self.isGuesser(viewer_pid):
                privileges.append(Privilege.SEE_OPEN_CLUES)
                privileges.append(Privilege.MAKE_GUESS)
            else:
                privileges.append(Privilege.SEE_ALL_CLUES)
                privileges.append(Privilege.SEE_SOLUTION)

        elif self.phase == Phase.EVALUATION:
            privileges.append(Privilege.SEE_SOLUTION)
            privileges.append(Privilege.SEE_ALL_CLUES)
            privileges.append(Privilege.SEE_EVALUATION)

        return privileges

    def perspective_clues(self, privileges):
        clues = {}
        for pid, word in self.clues.items():
            actions = {}
            if Privilege.CROP_CLUES in privileges:
                actions['set_hidden'] = {
                        'method': 'PUT',
                        'url': url_for('set_clue_hidden', pid=pid)
                }
            clues[pid] = {
                'pid': pid,
                'name': self.getPlayerName(pid),
                'word': word,
                'hidden': pid in self.hiddenClues,
                'actions': actions
            } 
        if Privilege.SEE_ALL_CLUES not in privileges:
            for pid, clue in clues.items():
                if any([pid in self.hiddenClues,
                        Privilege.SEE_OPEN_CLUES not in privileges]):
                    clue['word'] = ''
        return clues

    def perspective_solution(self, privileges):
        if Privilege.SEE_SOLUTION in privileges:
            return self.solution
        return None            

    def perspective_actions(self, privileges):
        actions = {}

        if Privilege.ADVANCE_PHASE in privileges:
            actions['next_phase'] = {
                'description': 'Phase beenden',
                'method': 'POST',
                'url': url_for('next_phase')
            }

        if Privilege.RESTART_GAME in privileges:
            actions['reset_game'] = {
                'description': 'Phase beenden',
                'method': 'POST',
                'url': url_for('reset_game')
            }            

        if Privilege.CHOOSE_GUESSER in privileges:
            actions['choose_guesser'] = {
                'method': 'PUT',
                'url': url_for('choose_guesser')
            }

        if Privilege.CHOOSE_WORD in privileges:
            actions['choose_word'] = {
                'method': 'PUT',
                'url': url_for('choose_solution')
            }

        if Privilege.GIVE_CLUE in privileges:
            actions['give_clue'] = {
                'method': 'POST',
                'url': url_for('give_clue')
            }

        if Privilege.MAKE_GUESS in privileges:
            actions['make_guess'] = {
                'method': 'PUT',
                'url': url_for('make_guess')
            }

        return actions

    def perspective(self, viewer_pid):
        perspective = super().perspective(viewer_pid)

        privileges = self.get_privileges(viewer_pid)
        perspective.update({
            'my_clue': self.clues.get(viewer_pid), # TODO is this even used?
            'phase': {
                'number': self.phase.value,
                'code': self.phase.name,
                'description': phasentexte[self.phase]
            },
            'guesser_pid': self.guesser_pid,
            'guess': self.guess,
            'solution': self.perspective_solution(privileges),
            'clues': self.perspective_clues(privileges),
            'actions': self.perspective_actions(privileges)
        })
        return perspective
