from game_master import GameMaster
from read import *
from util import *

class TowerOfHanoiGame(GameMaster):

    def __init__(self):
        super().__init__()
        
    def produceMovableQuery(self):
        """
        See overridden parent class method for more information.
        Returns:
             A Fact object that could be used to query the currently available moves
        """
        return parse_input('fact: (movable ?disk ?init ?target)')

    def getGameState(self):
        """
        Returns a representation of the game in the current state.
        The output should be a Tuple of three Tuples. Each inner tuple should
        represent a peg, and its content the disks on the peg. Disks
        should be represented by integers, with the smallest disk
        represented by 1, and the second smallest 2, etc.
        Within each inner Tuple, the integers should be sorted in ascending order,
        indicating the smallest disk stacked on top of the larger ones.
        For example, the output should adopt the following format:
        ((1,2,5),(),(3, 4))
        Returns:
            A Tuple of Tuples that represent the game state
        """
        # find all disks on pegs 1-3
        pegs = ["peg1", "peg2", "peg3"]

        # final game state tuple list
        game_state = []
        
        for peg in pegs:
            disks = self.kb.kb_ask(parse_input("fact: (on ?disk " + peg + ")"))
            pegnum = []

            if disks:
                for d in disks:
                    diskname = str(d.bindings[0].constant)
                    order = int(diskname[-1])
                    pegnum.append(order)
                pegnum.sort()

            game_state.append(tuple(pegnum))

        return tuple(game_state)
            


    def makeMove(self, movable_statement):
        """
        Takes a MOVABLE statement and makes the corresponding move. This will
        result in a change of the game state, and therefore requires updating
        the KB in the Game Master.
        The statement should come directly from the result of the MOVABLE query
        issued to the KB, in the following format:
        (movable disk1 peg1 peg3)
        Args:
            movable_statement: A Statement object that contains one of the currently viable moves
        Returns:
            None
        """
        
        pred = movable_statement.predicate
        
        # movable statement?
        if pred != "movable":
            print("Error: statement not a movable statement")
            return

        terms = movable_statement.terms
        disk = terms[0]
        peg = terms[1]
        targetpeg = terms[2]

        # retract related facts
        related = ["on", "top"]

        for pred in related:
            remove1 = parse_input("fact: (" + str(pred) + " " + str(disk) + " " + str(peg) + ")")
            self.kb.kb_retract(remove1)
            
        # change the top of the current peg
        disk_base_under_move = self.kb.kb_ask(parse_input("fact: (above " + str(disk) + " ?d)"))
        newtop = str(disk_base_under_move[0].bindings[0].constant)

        
        add = parse_input("fact: (top " + newtop + " " + str(peg) + ")")
        self.kb.kb_assert(add)


        # remove the above fact
        remove2 = parse_input("fact: (above " + str(disk) + " " + newtop + ")")
        self.kb.kb_retract(remove2)


        # add new disk on target peg
        newfact = parse_input("fact: (on "  + str(disk) + " " + str(targetpeg) + ")")
        self.kb.kb_assert(newfact)

        # find current top of target peg
        ask = parse_input("fact: (top ?d " + str(targetpeg) + ")")
        ttop = self.kb.kb_ask(ask)
        newtop = str(ttop[0].bindings[0].constant)
        
        # remove current top of target peg
        self.kb.kb_retract(parse_input("fact: (top " + newtop + " " + str(targetpeg) + ")"))

        
        # assert disk above previous top
        f1 = parse_input("fact: (above " + str(disk) + " " + newtop + ")")
        self.kb.kb_assert(f1)

        # assert new top of the target
        self.kb.kb_assert(parse_input("fact: (top " + str(disk) + " " + str(targetpeg) + ")"))

        
        return

    def reverseMove(self, movable_statement):
        """
        See overridden parent class method for more information.
        Args:
            movable_statement: A Statement object that contains one of the previously viable moves
        Returns:
            None
        """
        pred = movable_statement.predicate
        sl = movable_statement.terms
        newList = [pred, sl[0], sl[2], sl[1]]
        self.makeMove(Statement(newList))


class Puzzle8Game(GameMaster):

    def __init__(self):
        super().__init__()

    def produceMovableQuery(self):
        """
        Create the Fact object that could be used to query
        the KB of the presently available moves. This function
        is called once per game.
        Returns:
             A Fact object that could be used to query the currently available moves
        """
        return parse_input('fact: (movable ?piece ?initX ?initY ?targetX ?targetY)')

    def getGameState(self):
        """
        Returns a representation of the the game board in the current state.
        The output should be a Tuple of Three Tuples. Each inner tuple should
        represent a row of tiles on the board. Each tile should be represented
        with an integer; the empty space should be represented with -1.
        For example, the output should adopt the following format:
        ((1, 2, 3), (4, 5, 6), (7, 8, -1))
        Returns:
            A Tuple of Tuples that represent the game state
        """
        
        game_state = []

        row_names = ["pos1", "pos2", "pos3"]

        for r in row_names:        
            # iterate through the rows
            posfact = Fact(Statement(["posxy", "?tile", "?posx", str(r)]))
            positions = self.kb.kb_ask(posfact)

            # fill tuple with dummy values
            posnums = [10, 11, 12]


            for tile in positions:
                name = str(tile.bindings[0].constant)
                posx = str(tile.bindings[1].constant)

                if name == "empty":
                    order = -1
                else:
                    order = int(name[-1])
                
                if posx == "pos1":
                    posnums[0] = order
                elif posx == "pos2":
                    posnums[1] = order
                else:
                    posnums[2] = order
                
         
            game_state.append(tuple(posnums))

        return tuple(game_state)




    def makeMove(self, movable_statement):
        """
        Takes a MOVABLE statement and makes the corresponding move. This will
        result in a change of the game state, and therefore requires updating
        the KB in the Game Master.
        The statement should come directly from the result of the MOVABLE query
        issued to the KB, in the following format:
        (movable tile3 pos1 pos3 pos2 pos3)
        Args:
            movable_statement: A Statement object that contains one of the currently viable moves
        Returns:
            None
        """

        pred = movable_statement.predicate
        terms = movable_statement.terms

        tile = terms[0]
        tpx = terms[1]
        tpy = terms[2]
        epx = terms[3]
        epy = terms[4]

        if pred != "movable":
            print("Error: This is not a movable statement")
            return
    

        # retract previous position of tile
        remove = Fact(Statement(["posxy", str(tile), str(tpx), str(tpy)]))
        self.kb.kb_retract(remove)

        
        # retract previous position of empty space
        remove2 = Fact(Statement(["posxy", "empty", str(epx), str(epy)]))
        self.kb.kb_retract(remove2)
       
        # add new positions 
        newfact = Fact(Statement(["posxy", str(tile), str(epx), str(epy)]))
        self.kb.kb_add(newfact)
        
        newfact2 = Fact(Statement(["posxy", "empty", str(tpx), str(tpy)]))

        self.kb.kb_add(newfact2)

        return


    def reverseMove(self, movable_statement):
        """
        See overridden parent class method for more information.
        Args:
            movable_statement: A Statement object that contains one of the previously viable moves
        Returns:
            None
        """
        pred = movable_statement.predicate
        sl = movable_statement.terms
        newList = [pred, sl[0], sl[3], sl[4], sl[1], sl[2]]
        self.makeMove(Statement(newList))