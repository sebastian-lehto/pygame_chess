#This class is for:
#

import pygame as p
import ChessEngine

p.init()

#By setting the width and height of the screen to 512 and
#   the dimension to 8 we have 64px per square on the board
WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = WIDTH // DIMENSION
MAX_FPS = 15
IMAGES = {}

#Loading imges often would be very pointless and costly so we'll only load them once
#Making a seperate function for loading the images will allow flexibility
#   (seperate piece-sets etc.)
def loadImages():
    pieces = ["bP","bR","bN","bB","bQ","bK","wP","wR","wN","wB","wQ","wK"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/"+piece+".png"), (SQ_SIZE, SQ_SIZE))

    #First we've made a list of the names of the pieces
    #   then we load the image for each piece and save it to IMAGES
    #   using the piece name as the key and the image as the value

def main():
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("pink"))

    #GameState object will keep track of the game and determine valid moves
    gs = ChessEngine.GameState()

    #Generate valid moves for pieces. Expensive operation!! Only call when necessary!!
    validMoves = gs.getValidMoves()
    promotionMoves = gs.getPawnPromotionMoves()
    moveMade = False
    highlight = [0, 0, 0, validMoves]

    #Just loading the images once instead of loading after each move
    
    loadImages()
    
    #Keeping track of the last square that the user has clicked (initially none)
    sqSelected = ()
    
    #Keeping track of up to two of the squares last clicked (two tuples)
    playerClicks = []
    running = True
    while running:
        
        if gs.checkMate:
            color = "black" if gs.whiteToMove else "white"
            drawText(screen, "CHECKMATE", color) 
        elif gs.staleMate:
            drawText(screen, "STALEMATE", "red")        

        #If we press X on the window stop this while -loop
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
                
            #key handlers
            elif e.type == p.KEYDOWN:
                
                #If key 'z' is pressed, undo previous move and make sure valid moves are checked again
                if e.key == p.K_z:
                    gs.undoMove()
                    moveMade = True
                elif e.key == p.K_r:
                    gs = ChessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    promotionMoves = gs.getPawnPromotionMoves()
                    highlight = [0, 0, 0, validMoves]
                    playerClicks = []
                    sqSelected = ()

            #mouse handler
            elif e.type == p.MOUSEBUTTONDOWN:
                
                #Use the location of the mouse to determine which of squares has been clicked
                location = p.mouse.get_pos()
                col = location[0]//SQ_SIZE
                row = location[1]//SQ_SIZE
                
                #If the user clicked the same square twice, don't make a move. Clear sqSelected and playerClicks
                if sqSelected == (row, col):
                    sqSelected = ()
                    playerClicks = []
                    highlight = [0, 0, 0, validMoves]
                elif len(playerClicks) == 0 and gs.board[row][col] == "--":
                    print("SELECT A PIECE INSTEAD")
                #If not, keep track of this click
                else:
                    sqSelected = (row, col)                    
                    playerClicks.append(sqSelected)
                    #If this was the players 1st click highlight square
                    if len(playerClicks) == 1:
                        highlight =  [row, col, 1, validMoves]
                    #If this was the players 2nd click and the move will be valid, move the piece and cancel highlight
                    if len(playerClicks) == 2:
                        highlight = [0, 0, 0, validMoves]
                        move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                print(move.getChessNotation())
                                if move in promotionMoves:
                                    gs.makeMove(validMoves[i])
                                    pieceColor = gs.board[playerClicks[1][0]][playerClicks[1][1]][0]
                                    piece = choosePromotionPiece(screen, pieceColor)
                                    gs.makePawnPromotion(playerClicks[1][0],playerClicks[1][1], piece)
                                else:
                                    gs.makeMove(validMoves[i])
                                moveMade = True
                            sqSelected = ()
                            playerClicks = []

        #If a move has been made since the last time valid moves were checked, check them again
        if moveMade:
            validMoves = gs.getValidMoves()
            promotionMoves = gs.getPawnPromotionMoves()
            moveMade = False
   
        #To run slower wait the amount of millisecond in MAX_FPS
        clock.tick(MAX_FPS)

        #Update the contents of the display
        p.display.flip()

        drawGameState(screen, gs, highlight)

choosingPromotion = False
     
def choosePromotionPiece(screen, color):
    choosingPromotion = True
    pieces = []
    if color == 'w':
        pieces = ["wQ", "wR", "wB", "wN"]
    elif color == 'b':
        pieces = ["bQ", "bR", "bB", "bN"]
    for c in range(0, 7, 2):
        p.draw.rect(screen, p.Color("Red"), p.Rect(c*SQ_SIZE, 3 * SQ_SIZE, SQ_SIZE * 2, SQ_SIZE * 2))
    for i in range(4):
        screen.blit(IMAGES[pieces[i]], p.Rect((i * 2)*SQ_SIZE + (SQ_SIZE / 2), 3 * SQ_SIZE + (SQ_SIZE / 2), SQ_SIZE, SQ_SIZE))
    p.display.flip()
    pieceChosen = "--"

    while pieceChosen == "--":
        
        for e in p.event.get():
            #mouse handler
            if e.type == p.MOUSEBUTTONDOWN:
                
                #Use the location of the mouse to determine which of squares has been clicked
                location = p.mouse.get_pos()
                col = location[0]//SQ_SIZE
                row = location[1]//SQ_SIZE

                if 2 < row < 5:
                    if 0 <= col < 2:
                        pieceChosen = pieces[0]
                    elif 2 <= col < 4:
                        pieceChosen = pieces[1]
                    elif 4 <= col < 6:
                        pieceChosen = pieces[2]
                    elif 6 <= col < 8:
                        pieceChosen = pieces[3]

    choosingPromotion = False
    return pieceChosen
        

#Handles all the graphics for current game state
def drawGameState(screen, gs, highlight):
    drawBoard(screen)
    drawHighlight(screen, highlight[0], highlight[1], highlight[2], highlight[3], gs)
    drawPieces(screen, gs.board)

 

#Draw squares on board
def drawBoard(screen):
    colors = [p.Color("pink"), p.Color("grey")]
    for row in range(DIMENSION):
        for column in range (DIMENSION):
            #Square color determined by wether its coordinate(row + column)
            #   is even (light) or odd (dark)
            color = colors[((row+column)%2)]

            #Draw a square the appropriate amount of SQ_SIZE:s to each direction
            #   0,0 = (0, 0); 1,1 = (64, 64) etc.
            p.draw.rect(screen, color, p.Rect(column*SQ_SIZE, row*SQ_SIZE, SQ_SIZE, SQ_SIZE))

#HIghlight selected piece
def drawHighlight(screen, row, column, switch, validMoves, gs):
    colors = [p.Color("pink"), p.Color("grey")]
    color = colors[((row+column)%2)]
    p.time.wait(10)
    
    
    if switch == 1:
        p.draw.rect(screen, p.Color("yellow"), p.Rect(column*SQ_SIZE, row*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        for s in validMoves:
            if (s.startRow == row and s.startCol == column):
                p.draw.rect(screen, p.Color("light yellow"), p.Rect(s.endCol*SQ_SIZE, s.endRow*SQ_SIZE, SQ_SIZE, SQ_SIZE))

    else:
        p.draw.rect(screen, color, p.Rect(column*SQ_SIZE, row*SQ_SIZE, SQ_SIZE, SQ_SIZE))

#Draw pieces on top of the squares
def drawPieces(screen, board):    
    for row in range(DIMENSION):
        for column in range(DIMENSION):
            piece = board[row][column]
            
            #If this space is not empty acording to GameState object
            if piece != "--":
                #Draw picture from IMAGES -dictionary with the right key
                #   IMAGES -dictionary uses same keys for images as GameState uses for
                #   pieces.
                screen.blit(IMAGES[piece], p.Rect(column*SQ_SIZE, row*SQ_SIZE, SQ_SIZE, SQ_SIZE))

#Draw the text at the end of the game
def drawText(screen, text, color):
    font = p.font.SysFont("arial", 64, True, False)
    textObject = font.render(text, 0, p.Color(color))
    textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH/2 - textObject.get_width()/2, HEIGHT/2 - textObject.get_height()/2)
    screen.blit(textObject, textLocation)

#Recommended python procedure:
#   Only run main() in this particular file
#   Won't run if module has been imported elsewhere
if __name__ == "__main__":        
    main()
