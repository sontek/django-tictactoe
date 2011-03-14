from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _
from tictactoe.lib import Player_X, Player_O, Board
import hashlib
import random

class Game(models.Model):
    player1 = models.ForeignKey(User, related_name='player1')
    # user is allowed to be null because we invite people to games
    player2 = models.ForeignKey(User, blank=True, null=True, related_name='player2')

    def get_board(self):
        board = Board()
        moves = self.gamemove_set.all()

        for move in moves:
            if move.player == self.player1:
                board.pieces[move.move] = Player_X
            else:
                board.pieces[move.move] = Player_O

        return board

    def get_winner(self):
        return self.get_board().get_winner()

    def get_valid_moves(self):
        return self.get_board().get_valid_moves()

    class Meta:
        ordering = ['-id']

class GameInvite(models.Model):
    inviter = models.ForeignKey(User, related_name='inviter')
    invitee = models.ForeignKey(User, blank=True, null=True, related_name='invitee')
    invite_key = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        salt = hashlib.sha256(str(random.random())).hexdigest()[:5]
        self.invite_key = hashlib.sha256(salt + self.inviter.username).hexdigest()

        super(GameInvite, self).save(*args, **kwargs)


class GameMove(models.Model):
    game = models.ForeignKey(Game)
    player = models.ForeignKey(User)
    move = models.IntegerField()

    def clean(self):
        """ Validate the move, don't allow a move on a finished game """
        winner = self.game.get_winner()

        if winner or len(self.game.get_valid_moves()) == 0:
            raise ValidationError(_('This game has already completed'))

        super(GameMove, self).clean()

    def save(self, *args, **kwargs):
        self.clean()
        super(GameMove, self).save(*args, **kwargs)
