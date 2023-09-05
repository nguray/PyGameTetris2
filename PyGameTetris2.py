
'''  Simple Tetris using PyGame
         August 2023          
      Raymond NGUYEN THANH       
'''
import sys, random
from os import path
from enum import IntEnum, unique
import pygame
from pygame.locals import *
from datetime import datetime

DARK_GREY = (55,55,55)

# Constants
WIN_WIDTH = 480
WIN_HEIGHT = 560

@unique
class Tetrominoe(IntEnum):
    
    NoShape = 0
    ZShape = 1
    SShape = 2
    LineShape = 3
    TShape = 4
    SquareShape = 5
    LShape = 6
    MirroredLShape = 7


class Shape:
    

    tetroBag = [1,2,3,4,5,6,7,7,6,5,4,3,2,1]
    idTetroBag = 14

    coordsTable = (
        ((0, 0),     (0, 0),     (0, 0),     (0, 0)),
        ((0, -1),    (0, 0),     (-1, 0),    (-1, 1)),
        ((0, -1),    (0, 0),     (1, 0),     (1, 1)),
        ((0, -1),    (0, 0),     (0, 1),     (0, 2)),
        ((-1, 0),    (0, 0),     (1, 0),     (0, 1)),
        ((0, 0),     (1, 0),     (0, 1),     (1, 1)),
        ((-1, -1),   (0, -1),    (0, 0),     (0, 1)),
        ((1, -1),    (0, -1),    (0, 0),     (0, 1))
    )

    def __init__(self,nx :int,ny :int):
        '''     '''
        self.coords = [[0,0] for i in range(4)]
        self.pieceShape = Tetrominoe.NoShape
        self.set_shape(Tetrominoe.NoShape)
        self.x = nx
        self.y = ny
        
    def shape(self):
        '''returns shape'''
        return self.pieceShape
        
    def set_shape(self, shape):
        '''sets a shape'''
        table = Shape.coordsTable[shape]
        for i in range(4):
            for j in range(2):
                self.coords[i][j] = table[i][j]
        self.pieceShape = shape

    def tetris_randomizer(self)->int:
        iSrc = 0
        ityp = 0
        if Shape.idTetroBag<14:
            ityp = Shape.tetroBag[Shape.idTetroBag]
            Shape.idTetroBag += 1
        else:
            # Shuttle Bag
            for _ in range(14):
                iSrc = random.randint(0, 13)
                ityp = Shape.tetroBag[iSrc]
                Shape.tetroBag[iSrc] = Shape.tetroBag[0]
                Shape.tetroBag[0] = ityp
            ityp = Shape.tetroBag[0]
            Shape.idTetroBag = 1
            #print(Shape.tetroBag)
        return ityp

    def set_random_shape(self):
        '''chooses a random shape'''
        self.set_shape(self.tetris_randomizer())
               
    def min_x(self)->int:
        '''returns min x value'''
        m = self.coords[0][0]
        for i in range(1,4):
            m = min(m, self.coords[i][0])
        return m
        
    def max_x(self)->int:
        '''returns max x value'''
        m = self.coords[0][0]
        for i in range(1,4):
            m = max(m, self.coords[i][0])
        return m
        
    def min_y(self)->int:
        '''returns min y value'''
        m = self.coords[0][1]
        for i in range(1,4):
            m = min(m, self.coords[i][1])
        return m
        
    def max_y(self)->int:
        '''returns max y value'''
        m = self.coords[0][1]
        for i in range(1,4):
            m = max(m, self.coords[i][1])
        return m
        
    def rotate_left(self):
        '''rotate shape to the left'''
        if self.pieceShape == Tetrominoe.SquareShape:
            return
        for id,[vx,vy] in enumerate(self.coords):
            self.coords[id][0] = -vy
            self.coords[id][1] = vx

    def rotate_right(self):
        '''rotate shape to the right'''        
        if self.pieceShape == Tetrominoe.SquareShape:
            return
        for id,[vx,vy] in enumerate(self.coords):
            self.coords[id][0] = vy
            self.coords[id][1] = -vx

    def draw (self,display_surf):
        ''' Draw Tetromino '''
       # Afficher la pièce courant
        cs = Tetris.CELL_SIZE-2
        cs1 = Tetris.CELL_SIZE-1
        ox = self.x + Tetris.OX
        oy = self.y + Tetris.OY
        for [vx,vy] in self.coords:        
            x = ox + vx * Tetris.CELL_SIZE
            y = oy + vy * Tetris.CELL_SIZE
            pygame.draw.rect(display_surf,Tetris.TBL_COLORS[self.shape()],(x+1,y+1,cs,cs),0)
            bottom = y + cs1
            right =  x + cs1
            pygame.draw.line(display_surf,DARK_GREY,(x,bottom),(right,bottom))
            pygame.draw.line(display_surf,DARK_GREY,(right,bottom),(right,y))

    def iX(self)->int:
        ix = int((self.x)/Tetris.CELL_SIZE)
        return ix
    
    def iY(self)->int:
        iy = int((self.y)/Tetris.CELL_SIZE)
        return iy

    def hit_left(self, curboard: list[int])->bool:
        fHit = False
        for [vx,vy] in self.coords:
            x = vx*Tetris.CELL_SIZE + self.x - 1
            y = vy*Tetris.CELL_SIZE + self.y
            ix = int(x/Tetris.CELL_SIZE)
            iy = int(y/Tetris.CELL_SIZE)
            if (ix>=0) and (ix<Tetris.NB_COLUMNS) and (iy>=0) and (iy<Tetris.NB_ROWS):
                if curboard[ix+iy*Tetris.NB_COLUMNS]!=0:
                    fHit = True
                    break
            y = vy*Tetris.CELL_SIZE + self.y + Tetris.CELL_SIZE - 1
            iy = int(y/Tetris.CELL_SIZE)
            if (ix>=0) and (ix<Tetris.NB_COLUMNS) and (iy>=0) and (iy<Tetris.NB_ROWS):
                if curboard[ix+iy*Tetris.NB_COLUMNS]!=0:
                    fHit = True
                    break
        return fHit
    
    def hit_right(self,curboard: list[int])->bool:
        fHit = False
        for [vx,vy] in self.coords:
            x = vx*Tetris.CELL_SIZE + self.x + Tetris.CELL_SIZE
            y = vy*Tetris.CELL_SIZE + self.y
            ix = int(x/Tetris.CELL_SIZE)
            iy = int(y/Tetris.CELL_SIZE)
            if (ix>=0) and (ix<Tetris.NB_COLUMNS) and (iy>=0) and (iy<Tetris.NB_ROWS):
                if curboard[ix+iy*Tetris.NB_COLUMNS]!=0:
                    fHit = True
                    break
            y = vy*Tetris.CELL_SIZE + self.y + Tetris.CELL_SIZE - 1
            iy = int(y/Tetris.CELL_SIZE)
            if (ix>=0) and (ix<Tetris.NB_COLUMNS) and (iy>=0) and (iy<Tetris.NB_ROWS):
                if curboard[ix+iy*Tetris.NB_COLUMNS]!=0:
                    fHit = True
                    break
        return fHit

    def hit_bottom(self)->bool:
        for [_,vy] in self.coords:
            y = vy*Tetris.CELL_SIZE + self.y
            iy = int(y/Tetris.CELL_SIZE)
            if (iy>=(Tetris.NB_ROWS-1)) and ((y%Tetris.CELL_SIZE)==0):
                return True
        return False

    def is_out_right_limit(self)->bool:
        for [vx,vy] in self.coords:
            x = vx*Tetris.CELL_SIZE + self.x
            y = vy*Tetris.CELL_SIZE + self.y
            ix = int(x/Tetris.CELL_SIZE)
            iy = int(y/Tetris.CELL_SIZE)
            if (ix>=Tetris.NB_COLUMNS):
                return True
        return False            
       
    def is_out_left_limit(self)->bool:
        for [vx,vy] in self.coords:
            x = vx*Tetris.CELL_SIZE + self.x
            y = vy*Tetris.CELL_SIZE + self.y
            ix = int(x/Tetris.CELL_SIZE)
            iy = int(y/Tetris.CELL_SIZE)
            if (ix<0):
                return True
        return False            

    def hit_ground(self, board: list[int])->bool:
        
        for [vx,vy] in self.coords:

            # Top Left
            ix = int((vx*Tetris.CELL_SIZE + self.x)/Tetris.CELL_SIZE)
            iy = int((vy*Tetris.CELL_SIZE + self.y)/Tetris.CELL_SIZE)
            if (ix>=0) and (ix<Tetris.NB_COLUMNS) and (iy>=0) and (iy<Tetris.NB_ROWS):
                t = board[ix+Tetris.NB_COLUMNS*iy]
                if t!=0:
                    return True                        
            # Top Right
            ix = int((vx*Tetris.CELL_SIZE + self.x + Tetris.CELL_SIZE - 1)/Tetris.CELL_SIZE)
            iy = int((vy*Tetris.CELL_SIZE + self.y)/Tetris.CELL_SIZE)
            if (ix>=0) and (ix<Tetris.NB_COLUMNS) and (iy>=0) and (iy<Tetris.NB_ROWS):
                t = board[ix+Tetris.NB_COLUMNS*iy]
                if t!=0:
                    return True        

            # Bottom Right
            ix = int((vx*Tetris.CELL_SIZE + self.x + Tetris.CELL_SIZE - 1)/Tetris.CELL_SIZE)
            iy = int((vy*Tetris.CELL_SIZE + self.y + Tetris.CELL_SIZE - 1)/Tetris.CELL_SIZE)
            if (ix>=0) and (ix<Tetris.NB_COLUMNS) and (iy>=0) and (iy<Tetris.NB_ROWS):
                t = board[ix+Tetris.NB_COLUMNS*iy]
                if t!=0:
                    return True        

            # Bottom Left
            ix = int((vx*Tetris.CELL_SIZE + self.x)/Tetris.CELL_SIZE)
            iy = int((vy*Tetris.CELL_SIZE + self.y + Tetris.CELL_SIZE -1)/Tetris.CELL_SIZE)
            if (ix>=0) and (ix<Tetris.NB_COLUMNS) and (iy>=0) and (iy<Tetris.NB_ROWS):
                t = board[ix+Tetris.NB_COLUMNS*iy]
                if t!=0:
                    return True        
                
        return False


class Tetris:

    NB_COLUMNS = 10
    NB_ROWS = 20
    CELL_SIZE  = int(WIN_WIDTH / (NB_COLUMNS + 9))
    OX = 10
    OY = 10
    TBL_COLORS = [0x000000, 0xCC6666, 0x66CC66, 0x6666CC,
                        0xCCCC66, 0xCC66CC, 0x66CCCC, 0xDAAA00]

    def __init__(self):
        '''   '''
        self.board = [0 for i in range(0,self.NB_COLUMNS*self.NB_ROWS)]
 
    def clear(self)->None:
        ''' Reset Board List '''
        self.board = [0 for i in range((self.NB_ROWS+1) * self.NB_COLUMNS)]


class App:

    heightScoreFileName = 'height_scores.txt'

    def __init__(self):
        '''    '''
        self._running = True
        self._display_surf = None
        self.size = self.width, self.height = WIN_WIDTH, WIN_HEIGHT
        #self.sprite = pygame.image.load('Test.png')
        self.nbCompletedLines = 0
        self.fGameOver = False
        self.input_velocity_x = 0
        self.velocity_x = 0
        self.velocity_y = 0
        self.curPiece = None
        self.nextPiece = Shape((Tetris.NB_COLUMNS +4 )*Tetris.CELL_SIZE,(Tetris.NB_ROWS//2+1)*Tetris.CELL_SIZE)
        self.nextPiece.set_random_shape()
        self.last_tick_h = 0
        self.last_tick_v = 0
        self.last_tick_erase = 0
        self.last_tick_rotate_shape = 0
        self.game = Tetris()
        self.runGame = False
        self.fGameOver = False
        self.pauseMode = False
        self.fDropBottom = False
        self.score = 0
        self.bestScore = 0
        self.largeText = pygame.font.Font('sansation.ttf',24)
        self.smallText = pygame.font.Font('sansation.ttf',16)
        self.sound = pygame.mixer.Sound('109662__grunz__success.wav')
        self.sound.set_volume(0.6)
        pygame.mixer.music.load('Tetris.wav')
        pygame.mixer.music.set_volume(0.4)
        pygame.mixer.music.play(-1)
        self.clock = pygame.time.Clock()
        now = datetime.now()
        random.seed(now.second)

 
    def on_init(self):
        '''    '''
        self._display_surf = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        pygame.display.set_caption('PyGame Tetris')
        self._running = True
        self.load_high_score()
 
    def on_event(self, event):
        '''    '''
        if event.type == pygame.QUIT:
            self._running = False
        if event.type == pygame.KEYDOWN:
            match event.key:
                case pygame.K_LEFT:
                    self.input_velocity_x = -1
                case pygame.K_RIGHT:
                    self.input_velocity_x = 1
                case pygame.K_UP:
                    if self.curPiece != None:
                        self.curPiece.rotate_right()
                        savX = self.curPiece.x
                        fUndo = False
                        if self.curPiece.hit_ground(self.game.board):
                            fUndo = True
                        elif self.curPiece.is_out_right_limit():
                            # Try to shift inside board
                            while True:
                                self.curPiece.x -= Tetris.CELL_SIZE
                                if not self.curPiece.is_out_right_limit():
                                    break
                            if self.curPiece.hit_ground(self.game.board):
                                fUndo = True
                        elif self.curPiece.is_out_left_limit():
                            # Try to shift inside board
                            while True:
                                self.curPiece.x += Tetris.CELL_SIZE
                                if not self.curPiece.is_out_left_limit():
                                    break
                            if self.curPiece.hit_ground(self.game.board):
                                fUndo = True
                        if fUndo:
                            self.curPiece.x = savX
                            self.curPiece.rotate_left()
                case pygame.K_DOWN:
                    if self.curPiece != None:
                        pass
                case pygame.K_ESCAPE:
                    self._running = False
                case pygame.K_SPACE:
                    if self.curPiece==None:
                        # Démarrer la partie
                        self.start_game()
                    else:
                        # Faire tomber la pièce
                        self.fDropBottom = True
                case pygame.K_p:
                    self.pauseMode ^= True
                case  pygame.K_q | pygame.K_a:
                    self.runGame = False
                    self.curPiece = None
                    self.pauseMode = False
                    if self.score>self.bestScore:
                        self.bestScore = self.score
                        self.save_high_score()
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                self.input_velocity_x = 0
            elif event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                pass


    def compute_score(self, nb_lines: int) -> int:
        if nb_lines==1:
            return 40
        elif nb_lines==2:
            return 100
        elif nb_lines==3:
            return 300
        elif nb_lines==4:
            return 1200
        elif nb_lines>4:
            return 2000
        return 0

    # def ajust_pos_left(self):
    #     ''' Décaler la pièce si elle dépasse le bord gauche '''
    #     dx = self.curPiece.min_x() + self.curPiece.x
    #     if (dx<0):
    #         self.curPiece.x -= dx

    # def ajust_pos_right(self):
    #     ''' Décaler la pièce si elle dépasse le bord droit '''
    #     dx = (self.curPiece.max_x() + self.curPiece.x) - (Tetris.NB_COLUMNS-1)
    #     if dx>0:
    #         self.curPiece.x -= dx

    def display_score(self):
        '''  '''
        self.smallText.bold = True
        textScore = 'SCORE : {:05d}'.format(self.score)
        textSurface = self.smallText.render(textScore,True,(255,255,0))
        textRect = textSurface.get_rect()
        textRect.left = 5
        textRect.top = self.height - 20
        self._display_surf.blit(textSurface,textRect)
        textScore = 'HighScore : {:05d}'.format(self.bestScore)
        textSurface = self.smallText.render(textScore,True,(255,255,0))
        textRect = textSurface.get_rect()
        textRect.right = self.width - 5
        textRect.top = self.height - 20
        self._display_surf.blit(textSurface,textRect)

    def start_game(self):
        '''  Démarrer le jeu '''
        self.last_tick_h = pygame.time.get_ticks()
        self.last_tick_v = pygame.time.get_ticks()
        self.last_tick_erase = pygame.time.get_ticks()
        self.new_piece()
        self.runGame = True
        self.fGameOver = False
        self.game.clear()

    def new_piece(self):
        ''' Creates a new shape '''
        self.curPiece = self.nextPiece
        self.curPiece.x = (Tetris.NB_COLUMNS // 2 )*Tetris.CELL_SIZE
        self.curPiece.y = -self.curPiece.min_y()*Tetris.CELL_SIZE
        self.nextPiece = Shape((Tetris.NB_COLUMNS +4 )*Tetris.CELL_SIZE,(Tetris.NB_ROWS//2+1)*Tetris.CELL_SIZE)
        self.nextPiece.set_random_shape()
    
    def compute_completed_lines(self)->int :

        nbL = 0
        for y in range(0,Tetris.NB_ROWS):
            #-- Check completed line
            f_complete = True
            for x in range(0,Tetris.NB_COLUMNS):
                if self.game.board[x + y * Tetris.NB_COLUMNS] == 0 :
                    f_complete = False
                    break
            if f_complete :
                nbL += 1
        return nbL

    def drop_piece(self):
        '''    '''
        ix = int((self.curPiece.x+1)/Tetris.CELL_SIZE)
        iy = int((self.curPiece.y+1)/Tetris.CELL_SIZE)
        for [vx,vy] in self.curPiece.coords:
            x = vx + ix
            y = vy + iy
            if (x>=0) and (x<Tetris.NB_COLUMNS) and (y>=0) and (y<Tetris.NB_ROWS) :
                self.game.board[x+y*Tetris.NB_COLUMNS] = self.curPiece.pieceShape
        self.nbCompletedLines = self.compute_completed_lines()
        if self.nbCompletedLines>0:
            self.score += self.compute_score(self.nbCompletedLines)
            self.last_tick_erase = pygame.time.get_ticks()
            return True

        return False
    
    def display_game_over(self):
        '''  '''
        textScore = 'Game Over'
        self.largeText.bold = True
        textSurface = self.largeText.render(textScore,True,(255,255,0))
        textRect = textSurface.get_rect()
        textRect.center = (self.width/2 ,self.height/2)
        self._display_surf.blit(textSurface,textRect)

    def display_pause(self):
        '''  '''
        textScore = 'PAUSE'
        self.largeText.bold = True
        textSurface = self.largeText.render(textScore,True,(255,255,0))
        textRect = textSurface.get_rect()
        textRect.center = (self.width/2 ,self.height/2)
        self._display_surf.blit(textSurface,textRect)

    def save_high_score(self):
        with open(App.heightScoreFileName,'w',encoding="utf-8") as f:
            f.write(str(self.bestScore)+'\n')

    def load_high_score(self):
        if path.exists(App.heightScoreFileName):
            with open(App.heightScoreFileName,'r',encoding="utf-8") as f:
                for li in f:
                    if li!='':
                        self.bestScore = int(li) 

    def on_render(self):
        '''  '''
        # Clear Window
        self._display_surf.fill((50,50,150))

        pygame.draw.rect(self._display_surf,(0,0,100),
                         (Tetris.OX,Tetris.OY,Tetris.CELL_SIZE*Tetris.NB_COLUMNS,Tetris.CELL_SIZE*Tetris.NB_ROWS),0)

        #self._display_surf.blit(self.sprite,(self.x,self.y))

        # Afficher la pièce courant
        if self.curPiece != None:
            self.curPiece.draw(self._display_surf)

        # Afficher la prochaine pièce
        if self.nextPiece != None:
            self.nextPiece.draw(self._display_surf)

        # Afficher le plateau
        cs  = Tetris.CELL_SIZE-2
        cs1 = Tetris.CELL_SIZE-1
        for j in range(Tetris.NB_ROWS):
            for i in range(Tetris.NB_COLUMNS):
                x = i * Tetris.CELL_SIZE + Tetris.OX
                y = j * Tetris.CELL_SIZE + Tetris.OY
                c = Tetris.TBL_COLORS[self.game.board[j*Tetris.NB_COLUMNS+i]]
                if c!=0:
                    pygame.draw.rect(self._display_surf,c,(x+1,y+1,cs,cs),0)
                    bottom = y+cs1
                    right  = x+cs1
                    pygame.draw.line(self._display_surf,DARK_GREY,(x,bottom),(right,bottom))
                    pygame.draw.line(self._display_surf,DARK_GREY,(right,bottom),(right,y))

        # Afficher le score courant
        self.display_score()

        # Afficher un message
        if self.fGameOver == True:
            self.display_game_over()
        elif self.pauseMode == True:
            self.display_pause()

        pygame.display.flip()

    def on_cleanup(self)->None:
        '''    '''
        if self.score>self.bestScore:
            self.bestScore = self.score
            self.save_high_score()
        pygame.quit()
        sys.exit()
 
    def on_execute(self)->None:
        '''    '''
        if self.on_init() == False:
            self._running = False

        while( self._running ):
            for event in pygame.event.get():
                self.on_event(event)
            self.on_update()
            self.on_render()
            # 60 => Smooth animation ??
            self.clock.tick(60)

        self.on_cleanup()

    def is_game_over(self)->bool:
        iTop = 0
        for x in range(0,Tetris.NB_COLUMNS):
            if self.game.board[iTop+x] != 0:
                return True
        return False

    def erase_top_completed_line(self):
        for y in range(0,Tetris.NB_ROWS):
            #-- Check completed line
            f_complete = True
            for x in range(0,Tetris.NB_COLUMNS):
                if self.game.board[x + y * Tetris.NB_COLUMNS] == 0 :
                    f_complete = False
                    break
            
            if f_complete :
                #-- Shift down the game board
                y1 = y
                while y1 > 0 :
                    ySrcOffset = (y1 - 1) * Tetris.NB_COLUMNS
                    yDesOffset = y1 * Tetris.NB_COLUMNS
                    for x in range(0,Tetris.NB_COLUMNS) :
                        self.game.board[x + yDesOffset] = self.game.board[x + ySrcOffset]
                    y1 -= 1
                return
            
    
    def on_update(self):
        '''    '''
        if self.runGame == True:
            if self.pauseMode == False:
                if self.curPiece != None:
                    
                    nbTicks = pygame.time.get_ticks()

                    if (nbTicks-self.last_tick_rotate_shape) > 700:
                        self.last_tick_rotate_shape = nbTicks
                        self.nextPiece.rotate_right()

                    if self.nbCompletedLines>0:
                        if (nbTicks-self.last_tick_erase) > 150:
                            self.last_tick_erase = nbTicks
                            self.erase_top_completed_line()
                            self.nbCompletedLines -= 1
                            self.sound.play()
                    
                    if self.fGameOver:
                        if (nbTicks-self.last_tick_h) > 20:
                            self.last_tick_h = nbTicks
                            self.runGame = False
                            self.curPiece = None
                            self.pauseMode = False
                            if self.score>self.bestScore:
                                self.bestScore = self.score
                                self.save_high_score()
                        return


                    if (nbTicks-self.last_tick_h)>20:
                        self.last_tick_h = nbTicks
                        for _ in range(4):
                            if self.velocity_x == 1:
                                dum = self.curPiece.x + self.velocity_x
                                if (dum % Tetris.CELL_SIZE)!=0:
                                    if not (self.curPiece.hit_right(self.game.board)):
                                        self.curPiece.x += self.velocity_x                    
                                else:
                                    self.curPiece.x += self.velocity_x
                                    self.velocity_x = 0
                            elif self.velocity_x == -1:
                                dum = self.curPiece.x + self.velocity_x
                                if (dum % Tetris.CELL_SIZE)!=0:
                                    if not (self.curPiece.hit_left(self.game.board)):
                                        self.curPiece.x += self.velocity_x                    
                                else:
                                    self.curPiece.x += self.velocity_x
                                    self.velocity_x = 0
                            else:            
                                if  self.input_velocity_x==-1:
                                    if (self.curPiece.x % Tetris.CELL_SIZE)==0:
                                        _x = self.curPiece.min_x() + self.curPiece.iX()
                                        if  _x > 0:
                                            self.velocity_x = -1
                                            if not (self.curPiece.hit_left(self.game.board)):
                                                self.curPiece.x += self.velocity_x
                                elif self.input_velocity_x==1:
                                    if (self.curPiece.x % Tetris.CELL_SIZE)==0:
                                        _x = self.curPiece.max_x() + self.curPiece.iX()
                                        if _x<(Tetris.NB_COLUMNS-1):
                                            self.velocity_x = 1
                                            if not (self.curPiece.hit_right(self.game.board)):
                                                self.curPiece.x += self.velocity_x

                    if self.fDropBottom:
                        nbRepeat = 10
                        timeout_delay = 10
                    else:
                        nbRepeat = 3
                        timeout_delay = 30
                    if (nbTicks-self.last_tick_v)>timeout_delay:
                        self.last_tick_v = nbTicks
                        for _ in range(nbRepeat):
                            # Test hit freeze tetromino's cells
                            fHit = False
                            for [vx,vy] in self.curPiece.coords:
                                x = vx*Tetris.CELL_SIZE + self.curPiece.x
                                y = vy*Tetris.CELL_SIZE + self.curPiece.y + Tetris.CELL_SIZE
                                ix = int(x/Tetris.CELL_SIZE)
                                iy = int(y/Tetris.CELL_SIZE)
                                if (ix>=0) and (ix<Tetris.NB_COLUMNS) and (iy>=0) and (iy<Tetris.NB_ROWS):
                                    if self.game.board[ix+iy*Tetris.NB_COLUMNS]!=0:
                                        fHit = True
                                        break
                                x = vx*Tetris.CELL_SIZE + self.curPiece.x + Tetris.CELL_SIZE - 1
                                ix = int(x/Tetris.CELL_SIZE)
                                if (ix>=0) and (ix<Tetris.NB_COLUMNS) and (iy>=0) and (iy<Tetris.NB_ROWS):
                                    if self.game.board[ix+iy*Tetris.NB_COLUMNS]!=0:
                                        fHit = True
                                        break
                            if (fHit):
                                if (self.curPiece.x % Tetris.CELL_SIZE)==0 and (self.curPiece.y % Tetris.CELL_SIZE)==0:
                                    self.dropPiece()
                                    self.fDropBottom = False
                                    if self.is_game_over():
                                        self.fGameOver = True
                                    else:
                                        self.newPiece()
                            else:
                                # Current Tetromino reach the bottom
                                if not self.curPiece.hit_bottom():
                                    self.curPiece.y += 1
                                    if (self.curPiece.x%Tetris.CELL_SIZE)==0:
                                        if (self.curPiece.y%Tetris.CELL_SIZE)==0:
                                            # Allow horizontal sliding
                                            if  self.input_velocity_x!=0:
                                                break
                                else:
                                    self.fDropBottom = False
                                    if self.input_velocity_x!=0:
                                        # Allow horizontal movement
                                        break
                                    else:
                                        # Freeze current Tetromino
                                        # Ajust Tetromino horizontal position
                                        if self.curPiece.x%Tetris.CELL_SIZE!=0:
                                            self.curPiece.x = (int(self.curPiece.x/Tetris.CELL_SIZE)+1)*Tetris.CELL_SIZE
                                        # Freeze
                                        self.drop_piece()
                                        if self.is_game_over():
                                            self.fGameOver = True
                                        else:
                                            self.new_piece()
                                        break

                    
 
if __name__ == "__main__" :
    pygame.init()
    theApp = App()
    theApp.on_execute()


