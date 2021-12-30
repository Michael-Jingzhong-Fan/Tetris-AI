from board import Board, Direction, Rotation, Action, Shape
from random import Random
import time
import math

class Player:
    def __init__(self):
        self.numberOfHolesWeight = -1688.5
        self.columnMovementWeight = -105.5
        self.heightRangeWeight = -10.5
        self.totalHeightWeight = -20
        self.linesCompletedWeight = 50
        self.rowMovementWeight = -100.5
        self.smoothnessWeight = -20.5
        self.valleysWeight = -900
        self.heightsStandardDeviationWeight = -10
        #self.MaxHeightWeight = 500

    def choose_action(self, board):
        actionList = []

        bestScore = -1000000000
        bestPosition = 0
        bestRotation = 0
        Range = 11
        Range1 = 0

        for Position in range(Range1,Range):
            for Orientation in range(0,3):
                for Position1 in range(Range1,Range):
                    for Orientation1 in range(0,3):
                        clone = board.clone()
                        NumberOfMoves = Position - 5
                        landed = False
                        Angle = Orientation
                        while not landed and Angle > 0:
                            landed = clone.rotate(Rotation.Anticlockwise)
                            Angle -= 1
                        while not landed and NumberOfMoves > 0:
                            landed = clone.move(Direction.Right)
                            NumberOfMoves -=1
                        while not landed and NumberOfMoves < 0:
                            landed = clone.move(Direction.Left)
                            NumberOfMoves += 1
                        if not landed:
                            clone.move(Direction.Drop)

                        LinesCompletedScore = self.calculate_lines_completed(board, clone)*self.linesCompletedWeight

                        NumberOfMoves = Position1 - 5
                        landed = False
                        Angle = Orientation1
                        while not landed and Angle > 0:
                            landed = clone.rotate(Rotation.Anticlockwise)
                            Angle -= 1
                        while not landed and NumberOfMoves > 0:
                            landed = clone.move(Direction.Right)
                            NumberOfMoves -=1
                        while not landed and NumberOfMoves < 0:
                            landed = clone.move(Direction.Left)
                            NumberOfMoves += 1
                        if not landed:
                            clone.move(Direction.Drop)
                        
                        LinesCompletedScore1 = self.calculate_lines_completed(board, clone)*self.linesCompletedWeight
                        score = self.score_board(clone, board)
                        score = score + LinesCompletedScore1 + LinesCompletedScore
                        if score >= bestScore:
                            bestScore = score
                            bestPosition = Position
                            bestRotation = Orientation
        
        while bestRotation > 0:
            actionList.append(Rotation.Anticlockwise)
            bestRotation -= 1
        NumberOfMoves = bestPosition - 5        
        while NumberOfMoves > 0:
            actionList.append(Direction.Right)
            NumberOfMoves -=1
        while NumberOfMoves < 0:
            actionList.append(Direction.Left)
            NumberOfMoves += 1
        actionList.append(Direction.Drop)

        return actionList
    
    def score_board(self, clone, board):
        heights = self.get_heights(clone)
        totalHeight = sum(heights)

        maxYCanvas = max(heights)
        minYCanvas = min(heights)

        valleys = 0
        heightsRange = maxYCanvas - minYCanvas

        mean = sum(heights) / len(heights)   # mean
        var  = sum(pow(x-mean,2) for x in heights) / len(heights)  # variance
        math.sqrt(var)  # standard deviation
        heightsStandardDeviation = var
        
        for x in range(len(heights)-1):
            if abs(heights[x] - heights[x+1]) >= 4:
                valleys += (max(heights)-heights[x])

        if valleys == 1:
            valleys = 0
        
        smoothness = self.calculate_smoothness(heights)
        rowMovement, columnMovement = self.calculate_RowAndColumn_Movement(clone)

        linesCompleted = self.calculate_lines_completed(board, clone)
        numberOfHoles = self.holes_added(board, clone)

        totalHeightScore = totalHeight * self.totalHeightWeight
        columnMovementScore = self.columnMovementWeight * columnMovement
        #linesCompletedScore = linesCompleted * self.linesCompletedWeight
        rangeScore = self.heightRangeWeight * heightsRange
        rowMovementScore = self.rowMovementWeight * rowMovement
        numberOfHolesScore = self.numberOfHolesWeight * numberOfHoles
        smoothnessScore = smoothness * self.smoothnessWeight
        valleysScore = valleys * self.valleysWeight
        heightsStandardDeviationScore = heightsStandardDeviation * self.heightsStandardDeviationWeight
        #maxHeightScore = ((23-maxYCanvas)**2)*self.MaxHeightWeight

        score = (
            smoothnessScore
            + rowMovementScore
            + totalHeightScore
            + numberOfHolesScore
            + rangeScore
            + columnMovementScore
            #+ linesCompletedScore
            + valleysScore
            + heightsStandardDeviationScore
            #+ maxHeightScore
        )
        return score

    def get_heights(self, Clone):
        Columns = []
        columnHeights = [0,0,0,0,0,0,0,0,0,0]
        for x in Clone.cells:
            columnHeights[x[0]] += 1
        return columnHeights

    def calculate_smoothness(self, heights):
        smoothness = 0
        for x in range(len(heights) - 1):
            smoothness += abs(heights[x] - heights[x + 1])
        return smoothness

    def holes_added(self, board, clone):
        numHoles = 0
        for x in board.cells:
            lastY = x[1]+1
            while (x[0], lastY) not in board.cells and lastY < 23:
                numHoles += 1
                lastY += 1

        numHoles1 = 0
        for x in clone.cells:
            lastY = x[1]+1
            while (x[0], lastY) not in clone.cells and lastY < 23:
                numHoles += 1
                lastY += 1
        DeltaHoles = numHoles1 - numHoles
        return numHoles

    def calculate_RowAndColumn_Movement(self, clone):
        tiles = clone.cells
        rowMovement = 0
        columnMovement = 0
        #holes = self.holes(clone)
    
        for x in clone.cells:
            if (x[0], x[1]-1) not in clone.cells and x[1] > 0:
                rowMovement += 1
            if (x[0], x[1]+1) not in clone.cells and x[1] < 23:
                rowMovement += 1

        for x in clone.cells:
            if (x[0]+1, x[1]) not in clone.cells and x[1] < 9:
                columnMovement += 1
            if (x[0]-1, x[1]) not in clone.cells and x[1] > 0:
                columnMovement += 1

        return (rowMovement, columnMovement)

    def calculate_lines_completed(self, board, clone):
        OldNumberOfCells = 0
        NewNumberOfCells = 0
        for x in board.cells:
            OldNumberOfCells += 1
        for y in clone.cells:
            OldNumberOfCells += 1
        DeltaCellsNumber = NewNumberOfCells - OldNumberOfCells
        if DeltaCellsNumber < 0:
            return 0
        elif DeltaCellsNumber == -6:
            return -1600
        elif DeltaCellsNumber == -16:
            return -400
        elif DeltaCellsNumber == -26:
            return 400
        elif DeltaCellsNumber == -36:
            return 1600
        else:
            print(DeltaCellsNumber)
        
class RandoPlayer(Player):
    def __init__(self, seed=None):
        self.random = Random(seed)

    def print_board(self, board):
        print("--------")
        for y in range(24):
            s = ""
            for x in range(10):
                if (x,y) in board.cells:
                    s += "#"
                else:
                    s += "."
            print(s, y)

    def choose_action(self, board):
        self.print_board(board)
        time.sleep(0.5)
        if self.random.random() > 0.97:
            # 3% chance we'll discard or drop a bomb
            return self.random.choice([
                Action.Discard,
                Action.Bomb,
            ])
        else:
            # 97% chance we'll make a normal move
            return self.random.choice([
                Direction.Left,
                Direction.Right,
                Direction.Down,
                Rotation.Anticlockwise,
                Rotation.Clockwise,
            ])

SelectedPlayer = Player
