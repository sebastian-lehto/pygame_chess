#This class is for:
#   Storing the information about the state of the game
#   Determining and making valid moves
#   Keeping a log of valid moves
class GameState():
    test = "!!!!!!"
    def __init__(self):
        
        #The board is essentially an 8x8 lists of lists
        #   Each list represents a row on the chessboard
        #   The first character 'w' or 'b' represents the color of the piece
        #   The second character represents the type of piece 'K', 'Q', 'R', 'N', 'B', 'P'
        #   "--" represents an empty space
        self.board = [
            ["bR","bN","bB","bQ","bK","bB","bN","bR"],
            ["bP","bP","bP","bP","bP","bP","bP","bP"],
            ["--","--","--","--","--","--","--","--"],
            ["--","--","--","--","--","--","--","--"],
            ["--","--","--","--","--","--","--","--"],
            ["--","--","--","--","--","--","--","--"],
            ["wP","wP","wP","wP","wP","wP","wP","wP"],
            ["wR","wN","wB","wQ","wK","wB","wN","wR"]]

        #We'll keep track of whos turn it is to move
        self.whiteToMove = True

        #A log of the moves made is necessary to undo moves or review the game afterwards
        self.moveLog = []

        #Keeping track of the kings makes checking for checks, checkmates and stalemates easier
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)

        #Keeping track of pinned pieces and checks makes check-implementation more efficient
        self.pins =  []
        self.checks = []
        self.inCheck = False
        self.checkMate = False
        self.staleMate = False

        #Keeping track of where an en passant move can be made
        self.enpassantPossible = ()

        #Keeping track of castling rights
        self.currentCastlingRight = CastleRights(True, True, True, True)
        self.castleRightsLog = [CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                        self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)]
        
        
    #Updates the state of the game acordingly with given move, adds move to the move log
    #   and changes whos turn it is to move (won't work for castling, en-passant
    #   or pawn promotion
    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)
        
        #If a king was moved, update the kings location
        if move.pieceMoved == "wK":
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == "bK":
            self.blackKingLocation = (move.endRow, move.endCol)

        #en passant
        if move.enpassantMove:
            self.board[move.startRow][move.endCol] = "--"
            
        #update enpassantPossible
        if move.pieceMoved[1] == 'P' and  abs(move.startRow - move.endRow) == 2:
            print((move.startRow + move.endRow)//2, "_", move.startCol)
            self.enpassantPossible = ((move.startRow + move.endRow)//2, move.startCol)
        else:
            self.enpassantPossible = ()

        #castle move
            if move.castleMove:
                #if we move to the right: kingside castle
                if move.endCol - move.startCol == 2:
                    #Copy rook from old position to new position and erase the old rook
                    self.board[move.endRow][move.endCol - 1] = self.board[move.endRow][move.endCol + 1]
                    self.board[move.endRow][move.endCol + 1] = "--"
                #else queenside castle
                else:
                    #Copy rook from old position to new position and erase the old rook
                    self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 2]
                    self.board[move.endRow][move.endCol - 2] = "--"
            
        #update castling rights
        self.updateCastleRights(move)
        self.castleRightsLog.append(CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                        self.currentCastlingRight.wqs, self.currentCastlingRight.bqs))

                
        self.whiteToMove = not self.whiteToMove

    def makePawnPromotion(self, row, col, piece):
        move = Move((row, col), (row, col), self.board)
        move.pieceMoved = piece
        move.pieceCaptured = self.board[row][col]
        move.moveID = move.moveID + 50000
        self.makeMove(move)
        self.whiteToMove = not self.whiteToMove
        

        
    #Undoes previous move and removes it from the move log. Also switches turns back
    def undoMove(self):
        
        if len(self.moveLog) != 0:
            lastMove = self.moveLog.pop()
            self.board[lastMove.startRow][lastMove.startCol] = lastMove.pieceMoved
            self.board[lastMove.endRow][lastMove.endCol] = lastMove.pieceCaptured
            self.whiteToMove = not self.whiteToMove
            #If a king was moved, update the kings location
            if lastMove.pieceMoved == "wK":
                self.whiteKingLocation = (lastMove.startRow, lastMove.startCol)
            elif lastMove.pieceMoved == "bK":
                self.blackKingLocation = (lastMove.startRow, lastMove.startCol)

            #undong enpassant
            if lastMove.enpassantMove:
                self.board[lastMove.endRow][lastMove.endCol] = "--"
                self.board[lastMove.startRow][lastMove.endCol] = lastMove.pieceCaptured
                self.enpassantPossible = (lastMove.endRow, lastMove.endCol)

            #undo 2 square pawn move
            if lastMove.pieceMoved[1] == 'P' and abs(lastMove.startRow - lastMove.endRow) == 2:
                self.enpassantPossible = ()

            #undo castling rights from the move that has been undone
            self.castleRightsLog.pop()
            #set new castling right as the last from the log
            self.currentCastlingRight.wks = self.castleRightsLog[-1].wks
            self.currentCastlingRight.wqs = self.castleRightsLog[-1].wqs
            self.currentCastlingRight.bks = self.castleRightsLog[-1].bks
            self.currentCastlingRight.bqs = self.castleRightsLog[-1].bqs
            

            #undo castle move
            if lastMove.castleMove:
                #if move was kingside castle
                if lastMove.endCol - lastMove.startCol == 2:
                    #copy from new position to old position and erase new rook
                    self.board[lastMove.endRow][lastMove.endCol + 1] = self.board[lastMove.endRow][lastMove.endCol - 1]
                    self.board[lastMove.endRow][lastMove.endCol - 1] = "--"
                #else queenside castle
                else:
                    self.board[lastMove.endRow][lastMove.endCol - 2] = self.board[lastMove.endRow][lastMove.endCol + 1]
                    self.board[lastMove.endRow][lastMove.endCol + 1] = "--"
                   
    def updateCastleRights(self, move):
        #if king has moved, remove castling rights from that side
        if move.pieceMoved == "wK":
            self.currentCastlingRight.wks = False
            self.currentCastlingRight.wqs = False
        elif move.pieceMoved == "bK":
            self.currentCastlingRight.bks = False
            self.currentCastlingRight.bqs = False
        #if rook has moved check which side it was from and remove castling rights from that side
        elif move.pieceMoved == "wR":
            if move.startRow == 7:
                if move.startCol == 0:
                    self.currentCastlingRight.wqs = False
                elif move.startCol == 7:
                    self.currentCastlingRight.wks = False
        elif move.pieceMoved == "bR":
            if move.startRow == 0:
                if move.startCol == 0:
                    self.currentCastlingRight.wqs = False
                elif move.startCol == 7:
                    self.currentCastlingRight.wks = False
    
    def getPawnPromotionMoves(self):
        moves = self.getValidMoves()
        promotionMoves = []
        for m in range(len(moves) -1, -1, -1):
            if (moves[m].pieceMoved == "bP" and moves[m].endRow == 7)or (moves[m].pieceMoved == "wP" and moves[m].endRow == 0):
                promotionMoves.append(moves[m])

        return promotionMoves

        
    #Defining all moves that don't lead to checks for the maker of the move
    def getValidMoves(self):
        moves = []
        #Check is pieces are pinned or player is checked
        self.inCheck, self.pins, self.checks = self.checkForPinsAndChecks()
        #Determine the location of the relevant king
        if self.whiteToMove:
            kingRow = self.whiteKingLocation[0]
            kingCol = self.whiteKingLocation[1]
        else:
            kingRow = self.blackKingLocation[0]
            kingCol = self.blackKingLocation[1]
        if self.inCheck:
            # if only one piece is checking, capture, block or move king
            if len(self.checks) == 1:
                moves = self.getPossibleMoves()
                check = self.checks[0]
                checkRow = check[0]
                checkCol = check[1]
                pieceChecking = self.board[checkRow][checkCol]
                validSquares = []
                if pieceChecking[1] == 'N':
                    validSquares = [(checkRow, checkCol)]
                else:
                    for i in range(1, 8):
                        validSquare = (kingRow + check[2] * i, kingCol + check[3] * i)
                        validSquares.append(validSquare)
                        if validSquare[0] == checkRow and validSquare[1] == checkCol:
                            break
                for i in range(len(moves) -1 , -1, -1):
                    if moves[i].pieceMoved[1] != 'K':
                        if not (moves[i].endRow, moves[i].endCol) in validSquares:
                            moves.remove(moves[i])
            else: #more than one check. King has to move
                self.getKingMoves(kingRow, kingCol, moves)
        else:
            moves = self.getPossibleMoves()

        if len(moves) == 0:
            if self.inCheck:
                self.checkMate = True
            else:
                self.staleMate = True
        else:
            self.checkMate = False
            self.staleMate = False
        
        return moves

    #Defining all moves that don't defy the rules for how different types of pieces can move
    #   optional parameter 'kingMovesIncluded' allows the checking of castle moves without recursion
    def getPossibleMoves(self, kingMovesIncluded=True):
        
        testMove = Move((6,4), (5,4), self.board)
        
        moves = []
        #Going through each square on the board
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                turn = self.board[row][col][0]
                #If the piece on this square belongs to the player whos turn it is to move
                if (turn == 'w' and self.whiteToMove == True or turn == 'b' and self.whiteToMove == False):
                    piece = self.board[row][col][1]
                    #Determine possible moves for this piece
                    if piece == 'P':
                        self.getPawnMoves(row, col, moves)
                    elif piece == 'R':
                        self.getRookMoves(row, col, moves)
                    elif piece == 'B':
                        self.getBishopMoves(row, col, moves)
                    elif piece == 'Q':
                        self.getRookMoves(row, col, moves)
                        self.getBishopMoves(row, col, moves)
                    elif piece == 'K':
                        if kingMovesIncluded:
                            self.getKingMoves(row, col, moves)
                    elif piece == 'N':
                        self.getKnightMoves(row, col, moves)

        return moves

    #Helper method for checking if end square is on the board
    def onBoard(self, row, col, board):
        return row >= 0 and row < len(self.board) and col >= 0 and col < len(self.board[row])
    
    #Pawns can move one square forward, two squares forward if in their starting position
    #   and can capture pieces that are diagonally adjacent and infront of them
    def getPawnMoves(self, row, col, moves):
        #Check if piece is pinned
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
            
        #If the pawn is white
        if self.whiteToMove == True:
            #Check if the square infront is empty and on board
            if self.onBoard(row-1, col, self.board) and self.board[row-1][col] == "--":
                #Only if piece is not pinned or pinning allows
                if not piecePinned or pinDirection == (-1, 0):
                    #Add one square move to moves
                    moves.append(Move((row, col), (row - 1, col), self.board))
                    #Check if two square move is possible
                    if row == 6 and self.board[row-2][col] == "--":
                        moves.append(Move((row, col), (row - 2, col), self.board))

            #Check if diagonally adjacent squares have black pieces (that can be captured)
            if self.onBoard(row-1, col-1, self.board) and  self.board[row-1][col-1][0] == 'b':
                #Only if piece is not pinned or pinning allows
                if not piecePinned or pinDirection == (-1, -1):
                    moves.append(Move((row, col), (row-1, col-1), self.board))
            elif (row - 1, col - 1) == self.enpassantPossible:
                moves.append(Move((row, col), (row-1, col-1), self.board, isEnpassantMove=True))
                
            if self.onBoard(row-1, col+1, self.board) and  self.board[row-1][col+1][0] == 'b':
                #Only if piece is not pinned or pinning allows
                if not piecePinned or pinDirection == (-1, 1):
                    moves.append(Move((row, col), (row-1, col+1), self.board))
            elif (row - 1, col + 1) == self.enpassantPossible:
                moves.append(Move((row, col), (row-1, col+1), self.board, isEnpassantMove=True))

        #If the pawn is black
        elif self.whiteToMove == False:
            #Check if the square infront is empty
            if self.onBoard(row+1, col, self.board) and  self.board[row+1][col] == "--":
                #Only if piece is not pinned or pinning allows
                if not piecePinned or pinDirection == (1, 0):
                    #Add one square move to moves
                    moves.append(Move((row, col), (row + 1, col), self.board))
                    #Check if two square move is possible
                    if row == 1 and self.board[row+2][col] == "--":
                        moves.append(Move((row, col), (row + 2, col), self.board))
                        
            #Check if diagonally adjacent squares have black pieces (that can be captured)
            if self.onBoard(row+1, col-1, self.board) and  self.board[row+1][col-1][0] == 'w':
                #Only if piece is not pinned or pinning allows
                if not piecePinned or pinDirection == (1, -1):
                    moves.append(Move((row, col), (row+1, col-1), self.board))
            elif (row + 1, col - 1) == self.enpassantPossible:
                moves.append(Move((row, col), (row+1, col-1), self.board, isEnpassantMove=True))
            if self.onBoard(row+1, col+1, self.board) and  self.board[row+1][col+1][0] == 'w':
                #Only if piece is not pinned or pinning allows
                if not piecePinned or pinDirection == (1, 1):
                    moves.append(Move((row, col), (row+1, col+1), self.board))
            elif (row + 1, col + 1) == self.enpassantPossible:
                moves.append(Move((row, col), (row+1, col+1), self.board, isEnpassantMove=True))

    #Knights always move 2 squares horizontaly and 1 verically or vice versa
    #   they can also jump over pieces
    def getKnightMoves(self, row, col, moves):
        #Check if piece is pinned
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piecePinned = True
                self.pins.remove(self.pins[i])
                break
            
        directions = ((2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2))
        enemyColor = 'b' if self.whiteToMove else 'w'
        for d in directions:
            endRow = row + d[0]
            endCol = col + d[1]
            if self.onBoard(endRow, endCol, self.board):
                endPiece = self.board[endRow][endCol]
                if endPiece == "--" or endPiece[0] == enemyColor:
                    if not piecePinned:
                        moves.append(Move((row, col), (endRow, endCol), self.board))

        
    #Rooks can move along a rank or file and can't jump over pieces
    def getRookMoves(self, row, col, moves):

        #Check if piece is pinned
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                if self.board[row][col][1] != 'Q':
                    self.pins.remove(self.pins[i])
                break

        #Go through each possible direction, adding empty squares to possible moves
        #   until a square with a piece on it is found. If enemy piece add final move
        #   If piece is pinned only add moves along the pin direction
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
        enemyColor = 'b' if self.whiteToMove else 'w'
        for d in directions:
            
            for i in range(1, 8):
                endRow = row + d[0] * i
                endCol = col + d[1] * i
                
                if self.onBoard(endRow, endCol, self.board):
                    endPiece = self.board[endRow][endCol]
                    if endPiece != "--":
                        if endPiece[0] == enemyColor:
                            if not piecePinned or pinDirection == (d[0], d[1]) or pinDirection == (-1 * d[0], -1 * d[1]):
                                moves.append(Move((row, col), (endRow, endCol), self.board))
                            break
                        else:
                            break
                    else:
                        if not piecePinned or pinDirection == (d[0], d[1]) or pinDirection == (-1 * d[0], -1 * d[1]):
                            moves.append(Move((row, col), (endRow, endCol), self.board))


    #Bishops can move diagonaly and can't jump over pieces
    #   loops go through viable squares until thye meet the end of the board
    #   or meet a ppiece. Then determine if piece can be captured
    def getBishopMoves(self, row, col, moves):
        #Check if piece is pinned
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        enemyColor = 'b' if self.whiteToMove else 'w'
        for d in directions:
            
            for i in range(1, 8):
                endRow = row + d[0] * i
                endCol = col + d[1] * i
                
                if self.onBoard(endRow, endCol, self.board):
                    endPiece = self.board[endRow][endCol]
                    if endPiece != "--":
                        if endPiece[0] == enemyColor:
                            if not piecePinned or pinDirection == (d[0], d[1]) or pinDirection == (-1 * d[0], -1 * d[1]):
                                moves.append(Move((row, col), (endRow, endCol), self.board))
                            break
                        else:
                            break
                    else:
                        if not piecePinned or pinDirection == (d[0], d[1]) or pinDirection == (-1 * d[0], -1 * d[1]):
                            moves.append(Move((row, col), (endRow, endCol), self.board))   

    #Knights move two squares in one direction and one in another
    def getKingMoves(self, row, col, moves):
        rowMoves = (-1, -1, -1, 0, 0, 1, 1, 1)
        colMoves = (-1, 0, 1, -1, 1, -1, 0, 1)
        allyColor = "w" if self.whiteToMove else "b"
        for i in range(8):
            endRow = row + rowMoves[i]
            endCol = col + colMoves[i]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:
                    if allyColor == 'w':
                        self.whiteKingLocation = (endRow, endCol)
                    else:
                        self.blackKingLocation = (endRow, endCol)
                    inCheck, pins, checks = self.checkForPinsAndChecks()
                    if not inCheck:
                        moves.append(Move((row, col), (endRow, endCol), self.board))
                    if allyColor == 'w':
                        self.whiteKingLocation = (row, col)
                    else:
                        self.blackKingLocation = (row, col)
                        
        self.getCastleMoves(row, col, moves, allyColor)

    #Returns valid castle moves for king in given row and column
    def getCastleMoves(self, row, col, moves, allyColor):
        #No castling can be done if king is in check
        if len(self.checks) > 0 and self.board[self.checks[0][0]][self.checks[0][1]][0] != allyColor:
            return
        if (self.whiteToMove and self.currentCastlingRight.wks) or (not self.whiteToMove and self.currentCastlingRight.bks):
            self.getKingsideCastleMoves(row, col, moves, allyColor)
        if (self.whiteToMove and self.currentCastlingRight.wqs) or (not self.whiteToMove and self.currentCastlingRight.bqs):
            self.getQueensideCastleMoves(row, col, moves, allyColor)
        
    def getKingsideCastleMoves(self, row, col, moves, allyColor):
        if self.board[row][col + 1] == "--" and self.board[row][col + 2] == "--":
            if not self.squareUnderAttack(row, col + 1, moves, allyColor) and not self.squareUnderAttack(row, col + 2, moves, allyColor):
                moves.append(Move((row, col), (row, col + 2), self.board, isCastleMove=True))

    def getQueensideCastleMoves(self, row, col, moves, allyColor):
        if self.board[row][col - 1] == "--" and self.board[row][col - 2] == "--" and self.board[row][col - 3] == "--":
            if not self.squareUnderAttack(row, col - 1, moves, allyColor) and not self.squareUnderAttack(row, col - 2, moves, allyColor):
                moves.append(Move((row, col), (row, col - 2), self.board, isCastleMove=True))


    def squareUnderAttack(self, row, col, moves, allyColor):
        self.whiteToMove = not self.whiteToMove
        moves = self.getPossibleMoves(kingMovesIncluded=False)
        for m in moves:
            if m.endRow == row and m.endCol == col and m.pieceMoved[0] != allyColor:
                self.whiteToMove = not self.whiteToMove
                return True
        self.whiteToMove = not self.whiteToMove
        return False

    #Returns wether or not player is in check, a list of pins and checks
    #   1. is player in check
    #   2. allied pieces that are blocking a check
    #   3. pieces that check the allied king
    def checkForPinsAndChecks(self):
        pins = []
        checks = []
        inCheck = False
        if self.whiteToMove:
            enemyColor = "b"
            allyColor = "w"
            startRow = self.whiteKingLocation[0]
            startCol = self.whiteKingLocation[1]
        else:
            enemyColor = "w"
            allyColor = "b"
            startRow = self.blackKingLocation[0]
            startCol = self.blackKingLocation[1]
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            d = directions[j]
            possiblePin = ()
            for i in range(1, 8):
                endRow = startRow + d[0] * i
                endCol = startCol + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == allyColor:
                        if possiblePin == ():
                            possiblePin = (endRow, endCol, d[0], d[1])
                        else:
                            break
                    elif endPiece[0] == enemyColor:
                        pieceType = endPiece[1]
                        if (0 <= j <= 3 and pieceType == 'R') or \
                               (4 <= j <= 7 and pieceType == 'B') or \
                               (i == 1 and pieceType == 'P' and ((enemyColor == 'w' and 6 <= j <= 7) or (enemyColor == 'b' and 4 <= j <= 5))) or \
                                (pieceType == 'Q') or (i == 1 and pieceType == 'K'):
                            if possiblePin == ():
                                inCheck = True
                                checks.append((endRow, endCol, d[0], d[1]))
                                break
                            else:
                                pins.append(possiblePin)
                                break
                        else:
                            break
                else:
                    break #off board
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        for m in knightMoves:
            endRow = startRow + m[0]
            endCol = startCol + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] == enemyColor and endPiece[1] == 'N':
                    inCheck = True
                    checks.append((endRow, endCol, m[0], m[1]))

        return inCheck, pins, checks
            
#Move class makes making and recording moves much simpler
#   also not using any loops makes efficient
class Move():
    
    #Chess notation will make keeping track of moves simpler

    #Turns chess notation ranks into row numbers used in the code
    ranksToRows = {"1": 7,"2": 6,"3": 5,"4": 4,"5": 3,"6": 2,"7": 1,"8": 0}

    #Turn chess notation files into columns used in the code
    filesToCols = {"a": 0,"b": 1,"c": 2,"d": 3,"e": 4,"f": 5,"g": 6,"h": 7}

    #These turn chess notation back to rows and columns used in the code
    rowsToRanks = {value: key for key, value in ranksToRows.items()}
    colsToFiles = {value: key for key, value in filesToCols.items()}

    def __init__(self, startSq, endSq, board, isEnpassantMove=False, isCastleMove=False):
        self.startCol = startSq[1]        
        self.startRow = startSq[0]
        self.endCol = endSq[1] 
        self.endRow = endSq[0]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol

        self.enpassantMove = isEnpassantMove
        if self.enpassantMove:
            self.pieceCaptured = "wP" if self.pieceMoved == "bP" else "bP"

        self.castleMove = isCastleMove
        
        
    
    #Override equals method
    def __eq__(self, other):
        if isinstance(other, Move):
           return self.moveID == other.moveID
        return False

    #Override str method 
    def __str__(self):
        return str(self.moveID)
    
    #Turns move into imperfect chess notation
    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)
        

    #Turns given row-column combination to rank-file notation
    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]
        
class CastleRights():
    
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs

    
        













        
        

    
        
