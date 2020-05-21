"""
Subcontroller module for Alien Invaders

This module contains the subcontroller to manage a single level or wave in the Alien
Invaders game.  Instances of Wave represent a single wave.  Whenever you move to a
new level, you are expected to make a new instance of the class.

The subcontroller Wave manages the ship, the aliens and any laser bolts on screen.
These are model objects.  Their classes are defined in models.py.

Most of your work on this assignment will be in either this module or models.py.
Whether a helper method belongs in this module or models.py is often a complicated
issue.  If you do not know, ask on Piazza and we will answer.

Arunabh Chaudhuri ac2237
12/4/18
"""
from game2d import *
from consts import *
from models import *
import random

# PRIMARY RULE: Wave can only access attributes in models.py via getters/setters
# Wave is NOT allowed to access anything in app.py (Subcontrollers are not permitted
# to access anything in their parent. To see why, take CS 3152)


class Wave(object):
    """
    This class controls a single level or wave of Alien Invaders.

    This subcontroller has a reference to the ship, aliens, and any laser bolts on screen.
    It animates the laser bolts, removing any aliens as necessary. It also marches the
    aliens back and forth across the screen until they are all destroyed or they reach
    the defense line (at which point the player loses). When the wave is complete, you
    should create a NEW instance of Wave (in Invaders) if you want to make a new wave of
    aliens.

    If you want to pause the game, tell this controller to draw, but do not update.  See
    subcontrollers.py from Lecture 24 for an example.  This class will be similar to
    than one in how it interacts with the main class Invaders.

    #UPDATE ME LATER
    INSTANCE ATTRIBUTES:
        _ship:   the player ship to control [Ship]
        _aliens: the 2d list of aliens in the wave [rectangular 2d list of Alien or None]
        _bolts:  the laser bolts currently on screen [list of Bolt, possibly empty]
        _dline:  the defensive line being protected [GPath]
        _lives:  the number of lives left  [int >= 0]
        _time:   The amount of time since the last Alien "step" [number >= 0]

    As you can see, all of these attributes are hidden.  You may find that you want to
    access an attribute in class Invaders. It is okay if you do, but you MAY NOT ACCESS
    THE ATTRIBUTES DIRECTLY. You must use a getter and/or setter for any attribute that
    you need to access in Invaders.  Only add the getters and setters that you need for
    Invaders. You can keep everything else hidden.

    You may change any of the attributes above as you see fit. For example, may want to
    keep track of the score.  You also might want some label objects to display the score
    and number of lives. If you make changes, please list the changes with the invariants.

    LIST MORE ATTRIBUTES (AND THEIR INVARIANTS) HERE IF NECESSARY
    _dir:       If the wave should be moving left or right on the screen (int; 0 for right, 1 for left, 2 for down)
    _count:     The varible to check alien steps[int]
    _d:         Number of aliens dead or if cross line it is -2
    _pewSound:  Alien Sound [Sound]
    _bs:        Blaster Sound[Sound]
    _tp:        Total points earned by player[int]

    """
    def __init__(self):
        self._aliens = []
        for i in range(ALIENS_IN_ROW):
            r =[]
            for j in range(ALIEN_ROWS):
                if j == 0:
                    r.append(Alien((ALIEN_H_SEP + ALIEN_WIDTH)+ i * ALIEN_H_SEP + (i * ALIEN_WIDTH),
                    700 - ALIEN_CEILING - (j * ALIEN_HEIGHT) - (j * ALIEN_V_SEP) , ALIEN_WIDTH,ALIEN_HEIGHT,'alien3.png'))
                elif j < 3 and j > 0:
                    r.append(Alien((ALIEN_H_SEP + ALIEN_WIDTH)+ i * ALIEN_H_SEP + (i * ALIEN_WIDTH),
                    700 - ALIEN_CEILING - (j * ALIEN_HEIGHT) - (j * ALIEN_V_SEP) , ALIEN_WIDTH,ALIEN_HEIGHT,'alien2.png'))
                elif j >= 3:
                    r.append(Alien((ALIEN_H_SEP + ALIEN_WIDTH)+ i * ALIEN_H_SEP + (i * ALIEN_WIDTH),
                    700 - ALIEN_CEILING - (j * ALIEN_HEIGHT) - (j * ALIEN_V_SEP) , ALIEN_WIDTH,ALIEN_HEIGHT,'alien1.png'))
            self._aliens.append(r)
        self._ship = Ship(x=GAME_WIDTH/2,y=SHIP_BOTTOM, width=SHIP_WIDTH,height=SHIP_HEIGHT,
        bottom=SHIP_BOTTOM,movement=SHIP_MOVEMENT,lives=SHIP_LIVES,source='ship.png')
        self._dline = GPath(points=[0,DEFENSE_LINE,GAME_WIDTH,DEFENSE_LINE], linewidth=1, linecolor = 'black')
        self._time = 0
        self._dir = 0
        self._bolts = []
        self._time = 0
        self._count = 0
        self._lives = 3
        self._d = 0
        self._indicatorX = self._aliens[ALIENS_IN_ROW-1][ALIEN_ROWS-1].x
        self._indicatorY = self._aliens[ALIENS_IN_ROW-1][ALIEN_ROWS-1].y
        self._pewSound = Sound('pew1.wav')
        self._bs = Sound('blast1.wav')
        self._tp = 0

    def update(self, input, dt):
        self.check()
        self.d()
        self.destruct()
        self.delete()
        self.alienDestruct()
        self.aBolt()
        #Move Ship
        if self._ship != None:
            if input.is_key_down('right') == True and self._ship.x < GAME_WIDTH:
                self._ship.x += SHIP_MOVEMENT
            elif input.is_key_down('left') == True and self._ship.x > 0 :
                self._ship.x -= SHIP_MOVEMENT
        #Shoots bolts from ship
        if self._ship != None and (input.is_key_down('spacebar') or input.is_key_down('up') == True) and self.noPlayerBolt():
            self._bs.play()
            self._bolts.append(Bolt(x=self._ship.x, y = self._ship.y + 30, width = BOLT_WIDTH,
            height = BOLT_HEIGHT, fillcolor = 'black', velocity = BOLT_SPEED))
        #Moves Aliens
        if self._time > ALIEN_SPEED:
                self._time = 0
                self.move()
                self._count += 1 #CHANGE
        else:
                self._time += dt #CHANGE

    def move(self):
        r = GAME_WIDTH - (ALIEN_H_SEP + ALIEN_WIDTH/2)
        l = (ALIEN_H_SEP * ALIENS_IN_ROW) + (ALIEN_WIDTH * (ALIENS_IN_ROW - 1)) + ALIEN_WIDTH/2
        for a in range(ALIENS_IN_ROW):
            for b in range(ALIEN_ROWS):
                    if self._dir == 0:
                        if self._aliens[a][b] != None:
                            self._aliens[a][b].x += ALIEN_H_SEP
                        if a == ALIENS_IN_ROW - 1 and b == ALIEN_ROWS - 1:
                            self._indicatorX += ALIEN_H_SEP
                            if self._indicatorX >= r:
                                # Set self._dir = 2
                                self._dir = 2
                    elif self._dir == 1:
                        if self._aliens[a][b] != None:
                            self._aliens[a][b].x -= ALIEN_H_SEP
                        if a == ALIENS_IN_ROW - 1 and b == ALIEN_ROWS - 1:
                            self._indicatorX -= ALIEN_H_SEP
                            if self._indicatorX <= l:
                                # Set self._dir = 2
                                self._dir = 2
                    elif self._dir == 2:
                        if self._aliens[a][b] != None:
                            self._aliens[a][b].y -= ALIEN_H_SEP
                        if a == ALIENS_IN_ROW - 1 and b == ALIEN_ROWS - 1:
                            self._indicatorY -= ALIEN_H_SEP
                            if self._indicatorX >= r:
                                self._dir = 1
                            if self._indicatorX <= l:
                                self._dir = 0

    def aBolt(self):
                    #shoots bolts from aliens
        if self._count == BOLT_RATE: #change back to BOLT_RATE
            lastindex = 0
            col = []
            foundCol = False
            while(not foundCol):
                col = self._aliens[random.randint(0, ALIENS_IN_ROW-1)]
                for i in range(len(col)):
                    if col[i] != None:
                        foundCol = True
                        lastindex = i
            self._pewSound.play()
            self._bolts.append(Bolt(x=col[lastindex].x, y = col[lastindex].y,
            width = BOLT_WIDTH, height = BOLT_HEIGHT, fillcolor = 'black', velocity = -BOLT_SPEED))
            self._count = 0

    def delete(self):
            #deletes bolts when off screen
            for i in range(len(self._bolts)):
                self._bolts[i].y += self._bolts[i].getVelocity()
                if self._bolts[i].getVelocity() > 0:
                    if self._bolts[i].y + BOLT_HEIGHT/2 > GAME_HEIGHT:
                        del self._bolts[i]
                        break
                else:
                    if self._bolts[i].y <= 0:
                        del self._bolts[i]
                        break

    def alienDestruct(self):
            #alien destruction
            for a in range(ALIENS_IN_ROW):
                for b in range(ALIEN_ROWS):
                    for i in range(len(self._bolts)):
                        if self._aliens[a][b] != None:
                            if self._bolts[i].getVelocity() > 0 and self._aliens[a][b].collides(self._bolts[i]):
                                if self._aliens[a][b]._source == 'alien3.png':
                                    self._tp += 15
                                elif self._aliens[a][b]._source == 'alien2.png':
                                    self._tp += 10
                                elif self._aliens[a][b]._source == 'alien1.png':
                                    self._tp += 5
                                self._aliens[a][b] = None
                                self._d +=1
                                del self._bolts[i]
    def destruct(self):
            #ship destruction
            for i in range(len(self._bolts)):
                if self._ship != None and self._bolts[i].getVelocity() < 0 and self._ship.collides(self._bolts[i]):
                        self._ship = None
                        self._lives -= 1
                        del self._bolts[i]


        #check to see if aliens cross line
    def check(self):
        for a in range(ALIENS_IN_ROW):
            for b in range(ALIEN_ROWS):
                if self._aliens[a][b] != None and self._aliens[a][b].y <= DEFENSE_LINE:
                    self._d = -2
    def d(self):
        #check to see if all aliens are dead
        if self._d == (ALIEN_ROWS * ALIENS_IN_ROW):
            self._d = -1

        #if there is player bolt then return false, else return true
    def noPlayerBolt(self):
        for i in range(len(self._bolts)):
            if (self._bolts[i].getVelocity() > 0):
                return False
        return True
        #draw funciton for wave
    def draw(self, view):
        # DRAW METHOD TO DRAW THE SHIP, ALIENS, DEFENSIVE LINE AND BOLTS
        for a in range(ALIENS_IN_ROW):
            for b in range(ALIEN_ROWS):
                if self._aliens[a][b] != None:
                    self._aliens[a][b].draw(view)

        if self._ship != None:
            self._ship.draw(view)

        self._dline.draw(view)

        for a in range(len(self._bolts)):
            self._bolts[a].draw(view)
