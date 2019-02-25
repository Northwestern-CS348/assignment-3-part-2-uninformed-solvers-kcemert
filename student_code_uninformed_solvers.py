
from solver import *
import queue



class SolverDFS(UninformedSolver):
    def __init__(self, gameMaster, victoryCondition):
        super().__init__(gameMaster, victoryCondition)
        self.movables = queue.Queue()

    def get_children(self):
        movables = self.gm.getMovables()

        parent = self.currentState
        depth = parent.depth

        childlist = []


        for m in movables:
            self.gm.makeMove(m)
            game_state = GameState(self.gm.getGameState(), depth + 1, m)
            game_state.parent = parent
            if game_state not in self.visited:
                childlist.append(game_state)
                self.visited[game_state] = False
            elif self.visited[game_state] == False:
                childlist.append(game_state)

            self.gm.reverseMove(m)
    
        return childlist


    def solveOneStep(self):
        """
        Go to the next state that has not been explored. If a
        game state leads to more than one unexplored game states,
        explore in the order implied by the GameMaster.getMovables()
        function.
        If all game states reachable from a parent state has been explored,
        the next explored state should conform to the specifications of
        the Depth-First Search algorithm.

        Returns:
            True if the desired solution state is reached, False otherwise
        """

        if self.currentState.state == self.victoryCondition:
            return True
        self.visited[self.currentState] = True
        nextState = self.currentState.nextChildToVisit
        children = self.get_children()
        self.currentState.children = children

        while nextState == len(self.currentState.children):
            if self.currentState.depth == 0:
                nextState = self.currentState.nextChildToVisit
                break
            move = self.currentState.requiredMovable
            self.currentState = self.currentState.parent
            self.gm.reverseMove(move)
            nextState = self.currentState.nextChildToVisit
        
        
        child = self.currentState.children[nextState]

        if self.visited[child] == False:
            self.currentState.nextChildToVisit += 1
            self.gm.makeMove(child.requiredMovable)
            self.currentState = child
            return False
        
        if self.currentState.state == self.victoryCondition:
            return True

        return False

   

class SolverBFS(UninformedSolver):
    def __init__(self, gameMaster, victoryCondition):
        super().__init__(gameMaster, victoryCondition)
        self.nodes = queue.Queue()
        self.list_moves_root_to_child = dict()

    def get_children(self):
        movables = self.gm.getMovables()

        parent = self.currentState
        depth = parent.depth

        children = []

        for m in movables:
            self.gm.makeMove(m)
            parent_moves = self.list_moves_root_to_child[parent].copy()

            game_state = GameState(self.gm.getGameState(), depth + 1, m)
            game_state.parent = parent

            if game_state not in self.visited:
                children.append(game_state)
                self.visited[game_state] = False
                self.nodes.put(game_state)
                self.list_moves_root_to_child[game_state] = []
                self.list_moves_root_to_child[game_state].extend(parent_moves)
                self.list_moves_root_to_child[game_state].append(game_state)

            self.gm.reverseMove(m)

        return children

    def solveOneStep(self):
        """
        Go to the next state that has not been explored. If a
        game state leads to more than one unexplored game states,
        explore in the order implied by the GameMaster.getMovables()
        function.
        If all game states reachable from a parent state has been explored,
        the next explored state should conform to the specifications of
        the Breadth-First Search algorithm.

        Returns:
            True if the desired solution state is reached, False otherwise
        """

        if self.currentState.state == self.victoryCondition:
            return True
        
        self.visited[self.currentState] = True

        if self.currentState.depth == 0:
            self.list_moves_root_to_child[self.currentState] = []

        children = self.get_children()
        self.currentState.children = children

        prev_list_moves = self.list_moves_root_to_child[self.currentState]
        prev_list_moves.reverse()

        self.currentState = self.nodes.get()
        curr_list_moves = self.list_moves_root_to_child[self.currentState]
        
        for m in prev_list_moves:
            self.gm.reverseMove(m.requiredMovable)

        for m in curr_list_moves:
            self.gm.makeMove(m.requiredMovable)

        if self.currentState.state == self.victoryCondition:
            return True
        
        return False
        
        

