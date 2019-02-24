from logical_classes import *
from kb_and_inference_engine import *
from read import *
import os

class GameMaster(object):

    """
    Abstract parent class of game masters. Must not be instantiated directly.

    A game master maintains the state of a game, produces summary of the current state,
    handles external request to make a move (and make the transition between game state),
    and determine if the winning condition has been achieved.

    Attributes:
        kb (KnowledgeBase): the Knowledge Base object that keeps track of the rules and game state
        moveableQuery (Fact): the Fact object with which a Game Master queries for all MOVABLE statements
        required (list of Fact): all MOVABLE statements that must be present in the KB in the winning game state
        forbidden (list of Fact): all MOVABLE statements that must not be in the KB in the winning game state
    """

    TXTS_DIRECTORY_PATH='flatfiles'

    def __init__(self):
        self.kb = KnowledgeBase([], [])
        self.moveableQuery = self.produceMovableQuery()
        self.required = None
        self.forbidden = None

    def produceMovableQuery(self):
        """
        Create the Fact object that could be used to query
        the KB of the presently available moves. This function
        is called once per game.

        Must be overridden by each non-abstract children classes.

        Returns:
             A Fact object that could be used to query the currently available moves
        """
        raise NotImplementedError('Subclasses must override produceMovableQuery() '\
            'to provide the query for facts starting with MOVABLE predicate')

    def isMovableLegal(self, movable_statement):
        """
        Checks if a MOVABLE statement is a legal move in the current game state.

        Args:
            movable_statement: A Statement object that may or may not contain a presently viable move

        Returns:
            True if the move is legal; False otherwise.
        """
        return movable_statement in self.getMovables()

    def makeMove(self, movable_statement):
        """
        Takes a MOVABLE statement and makes the corresponding move. This will
        result in a change of the game state, and therefore requires updating
        the KB in the Game Master.

        Must be overridden by each non-abstract children classes.

        Args:
            movable_statement: A Statement object that contains one of the currently viable moves

        Returns:
            None
        """
        raise NotImplementedError('Subclasses must override makeMove(..) '\
            'to make a move to change the game state')

    def reverseMove(self, movable_statement):
        """
        Move in the reverse direction as specified by the
        input MOVABLE statement. This function is used to
        undo the effect of a move. Useful in backtracking
        to an older game state.

        Must be overridden by each non-abstract children classes.

        Args:
            movable_statement: A Statement object that contains one of the previously viable moves

        Returns:
            None
        """
        raise NotImplementedError('Subclasses must override reverseMove(..) '\
            'to make the reverse move specified by the argument')

    def getGameState(self):
        """
        Returns a representation of the game in the current state.

        Must be overridden by each non-abstract children classes.

        Returns:
            A Tuple of Tuples that represent the game state
        """
        raise NotImplementedError('Subclasses must override getGameState() '\
            'to return a summary of the current game state')

    def getMovables(self):
        """
        Returns a list of MOVABLE statements that represent the moves currently available.
        
        The output Statements will be sorted in ascending orders, first order by the text of predicates,
        then by each Term in the Statement.

        Returns:
            A list of MOVABLE statements indicating the presently viable moves, if at least one is present;
            False otherwise.
        """
        listOfBindings = self.kb.kb_ask(self.moveableQuery)
        if listOfBindings:
            statements = [instantiate(self.moveableQuery.statement,bindings) for bindings in listOfBindings]
            statements.sort()
            return statements
        else:
            return listOfBindings

    def read(self, file_name, path=TXTS_DIRECTORY_PATH):
        """
        Read and assert all Facts and Rules from a file in the KB.

        Args:
            file_name: the name of the file
            path: path to the directory that contains said file

        Returns:
            None
        """
        final_path = os.path.join(path, file_name)
        for fr in read_tokenize(final_path):
            self.kb.kb_assert(fr)

    def setWinningCondition(self, required, forbidden):
        """
        Take two lists of Facts in string form, parse them, and save them
        for checking if the winning condition is met.

        Args:
            required: a list of strings that specify the Facts that must be present when the winning condition is met
            forbidden: a list of strings that specify the Facts that must NOT be present when the winning condition is met

        Returns:
            None
        """
        self.required = [parse_input(r) for r in required]
        forbidden_ff = getForbiddensFactStrings(forbidden)
        self.forbidden = []
        for f in forbidden_ff:
            if f not in required:
                self.forbidden.append(parse_input(f))

    def isWon(self):
        """
        Check if the winning condition is met, with the list of Required Facts
        and the list of forbidden Facts specified by the setWinningCondition method.

        Returns:
            True if winning condition is met; False otherwise

        Raises:
            Uninitialized Exception: Raises exception if the winning conditions were not set by setWinningCondition
        """
        for v in self.required:
            if not self.kb.kb_ask(v):
                return False
        for v in self.forbidden:
            if self.kb.kb_ask(v):
                return False
        return True
