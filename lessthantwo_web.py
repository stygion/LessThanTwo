from flask import url_for
from lessthantwo import LessThanTwo, Phase
from enum import Enum

class Privilege(Enum):
    KICK_ANYBODY     = 'KICK_ANYBODY'
    RENAME_ANYBODY   = 'RENAME_ANYBODY'
    ADVANCE_PHASE    = 'ADVANCE_PHASE'
    CHOOSE_GUESSER   = 'CHOOSE_GUESSER'
    CHOOSE_SOLUTION  = 'CHOOSE_SOLUTION'
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
    Phase.CHOOSE_SOLUTION: 'Was soll geraten werden?',
    Phase.GIVE_CLUES: 'Hinweise abgeben',
    Phase.CROP_CLUES: 'Doppelte streichen',
    Phase.MAKE_GUESS: 'Lösung raten',
    Phase.EVALUATION: 'Auswertung',
}    

class LessThanTwo_WebAdapter(object):

    def __init__(self, game):
        assert isinstance(game, LessThanTwo), 'Expected an instance of LessThanTwo'
        self.game = game

    def perspective(self, viewer_pid):
        perspective = {
            'version': self.game.version,
            'players': self.players(viewer_pid),
            'phase': self.phase(),
            'guesser_pid': self.game.guesser_pid,
            'guess': self.game.guess,
            'solution': self.solution(viewer_pid),
            'clues': self.clues(viewer_pid),
            'actions': self.general_actions(viewer_pid)
        }
        return perspective

    def phase(self):
        return {
                'number': self.game.phase.value,
                'code': self.game.phase.name,
                'description': phasentexte[self.game.phase]
            }

    def players(self, viewer_pid):
        players = []
        for pid, player in self.game.players.items():
            player = { 
                    'pid': pid,
                    'name': player.get('name'),
                    'actions': {
                        'remove': {
                            'method': 'DELETE',
                            'url': '/default/player/%s' % pid
                        },
                        'rename': {
                            'method': 'PUT',
                            'url': '/default/player/%s/name' % pid
                        }
                    },
                    'is_me': pid == viewer_pid,
                }
            players.append(player)
        return players




    def clues(self, viewer_pid):

        ## determine viewer privileges
        
        viewer_is_guesser = self.game.isGuesser(viewer_pid)
        sees_all_clues = (
            self.game.phase >= Phase.EVALUATION or
            (
                not viewer_is_guesser and
                viewer_pid in self.game.clues
            )
        )
        sees_unique_clues = (
                viewer_is_guesser and
                self.game.phase >= Phase.MAKE_GUESS
        )
        may_hide_clues = (
                self.game.phase == Phase.CROP_CLUES and
                not viewer_is_guesser                
        )

        clues = {}
        for pid, word in self.game.clues.items():
            clue_is_hidden = pid in self.game.hiddenClues
            clue = {
                'pid': pid,
                'name': self.game.getPlayerName(pid),
                'word': word,
                'hidden': clue_is_hidden,
            } 
            if may_hide_clues:
                clue['actions'] = {
                    'set_hidden': {
                        'method': 'PUT',
                        'url': url_for('set_clue_hidden', pid=pid)
                    }
                }
            
            clues[pid] = clue
            
        if not sees_all_clues:
            for pid, clue in clues.items():
                if any([pid in self.game.hiddenClues,
                        not sees_unique_clues]):
                    clue['word'] = ''
        return clues

    def solution(self, viewer_pid):
        may_see_solution = (
            not self.game.isGuesser(viewer_pid) or
            self.game.phase >= Phase.EVALUATION 
        )
        if may_see_solution:
            return self.game.solution
        else:
            return None            

    def general_actions(self, viewer_pid):
        phase = self.game.phase

        may_advance_phase = True
        may_restart_game = True
        may_choose_guesser = (
            phase is Phase.CHOOSE_GUESSER
        )
        may_choose_solution = (
            phase is Phase.CHOOSE_SOLUTION and
            not self.game.isGuesser(viewer_pid)
        )
        may_give_clue = (
            phase is Phase.GIVE_CLUES and 
            not self.game.isGuesser(viewer_pid) and
            not viewer_pid in self.game.clues
        )
        may_make_guess = (
            phase is Phase.MAKE_GUESS and
            self.game.isGuesser(viewer_pid)
        )

        actions = {}
        if may_advance_phase:
            actions['next_phase'] = {
                'description': 'Phase beenden',
                'method': 'POST',
                'url': url_for('next_phase')
            }

        if may_restart_game:
            actions['reset_game'] = {
                'description': 'Phase beenden',
                'method': 'POST',
                'url': url_for('reset_game')
            }            

        if may_choose_guesser:
            actions['choose_guesser'] = {
                'method': 'PUT',
                'url': url_for('choose_guesser')
            }

        if may_choose_solution:
            actions['choose_solution'] = {
                'method': 'PUT',
                'url': url_for('choose_solution')
            }

        if may_give_clue:
            actions['give_clue'] = {
                'method': 'POST',
                'url': url_for('give_clue')
            }

        if may_make_guess:
            actions['make_guess'] = {
                'method': 'PUT',
                'url': url_for('make_guess')
            }

        return actions







    ##
    # player perspective
    ##
    #
    # def get_privileges(self, viewer_pid):
    #     privileges = [
    #         Privilege.KICK_ANYBODY,
    #         Privilege.RENAME_ANYBODY,
    #         Privilege.ADVANCE_PHASE,
    #         Privilege.RESTART_GAME
    #     ]
    #     if self.game.phase == Phase.CHOOSE_GUESSER:
    #         privileges.append(Privilege.CHOOSE_GUESSER)
    #     elif self.game.phase == Phase.CHOOSE_SOLUTION:
    #         if self.game.isGuesser(viewer_pid):
    #             pass
    #         else:
    #             privileges.append(Privilege.CHOOSE_SOLUTION)
    #             privileges.append(Privilege.SEE_SOLUTION)
    #     elif self.game.phase == Phase.GIVE_CLUES:
    #         if self.game.isGuesser(viewer_pid):
    #             pass
    #         elif viewer_pid not in self.game.clues:
    #             privileges.append(Privilege.SEE_SOLUTION)
    #             privileges.append(Privilege.GIVE_CLUE)
    #         else:
    #             privileges.append(Privilege.SEE_SOLUTION)
    #             privileges.append(Privilege.SEE_ALL_CLUES)
    #     elif self.game.phase == Phase.CROP_CLUES:
    #         if self.game.isGuesser(viewer_pid):
    #             pass
    #         else:
    #             privileges.append(Privilege.SEE_SOLUTION)
    #             privileges.append(Privilege.SEE_ALL_CLUES)
    #             privileges.append(Privilege.CROP_CLUES)
    #     elif self.game.phase == Phase.MAKE_GUESS:
    #         if self.game.isGuesser(viewer_pid):
    #             privileges.append(Privilege.SEE_OPEN_CLUES)
    #             privileges.append(Privilege.MAKE_GUESS)
    #         else:
    #             privileges.append(Privilege.SEE_ALL_CLUES)
    #             privileges.append(Privilege.SEE_SOLUTION)
    #     elif self.game.phase == Phase.EVALUATION:
    #         privileges.append(Privilege.SEE_SOLUTION)
    #         privileges.append(Privilege.SEE_ALL_CLUES)
    #         privileges.append(Privilege.SEE_EVALUATION)
    #     return privileges
