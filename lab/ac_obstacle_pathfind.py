from typing import Dict, List, Tuple

import copy
import heapq
from itertools import count

import numpy as np

from ac_state_spatial import AutonomousCarSpatialDirection, AutonomousCarSpatialPosition

state_index = count()

class AutonomousCarPathfindingState:
    def __init__(self, env: np.ndarray, goal: AutonomousCarSpatialPosition, pos: AutonomousCarSpatialPosition, dir: AutonomousCarSpatialDirection, g: float):
        self.t = next(state_index)

        self.env = env
        self.goal = goal

        self.pos = pos
        self.dir = dir

        self.g: float = g
        self.h: float = self.heuristic()
        pass

    def neighbours(self) -> List[Tuple["AutonomousCarPathfindingState"]]:
        x, y = self.pos
        dx, dy = self.dir.vec()

        neighbours = []

        cand_x = x + dx
        cand_y = y + dy

        if 0 <= cand_x < self.env.shape[0] and 0 <= cand_y < self.env.shape[1] and not self.env[cand_x, cand_y]:
            neighbours.append((AutonomousCarPathfindingState(self.env, self.goal, (cand_x, cand_y), copy.copy(self.dir), self.g + 1)))
        
        neighbours.append((AutonomousCarPathfindingState(self.env, self.goal, self.pos, self.dir.cw(), self.g + 1)))
        
        neighbours.append((AutonomousCarPathfindingState(self.env, self.goal, self.pos, self.dir.ccw(), self.g + 1)))

        return neighbours

    def is_dest(self):
        return self.pos == self.goal
    
    def heuristic(self):
        return abs(self.goal[0] - self.pos[0]) + abs(self.goal[1] - self.pos[1])
    
    def __lt__(self, other):
        f = self.g + self.h
        other_f = other.g + other.h

        if f == other_f:
            # tiebreaking based on global index
            return self.t < other.t
        
        return f < other_f

    def __hash__(self):
        return hash((self.pos, self.dir))
    def __eq__(self, other):
        return (self.pos, self.dir) == (other.pos, other.dir)

    def __str__(self):
        return str((self.pos, self.dir.name))
    def __repr__(self):
        return str((self.pos, self.dir.name))
    

class AutonomousCarPathfinding:
    def __init__(self):
        pass

    def pathfind(self, env: np.ndarray, start: AutonomousCarSpatialPosition, dest: AutonomousCarSpatialPosition):
        start_state = AutonomousCarPathfindingState(env, dest, start, AutonomousCarSpatialDirection.FRONT, 0)

        return self._a_star(start_state)

    def _a_star(self, start_state: AutonomousCarPathfindingState):
        visited: Dict[AutonomousCarPathfindingState, Tuple[AutonomousCarPathfindingState, float]] = { start_state: (None, 0) }

        frontier: List[AutonomousCarPathfindingState] = []
        heapq.heappush(frontier, start_state)

        closest_state = start_state

        while len(frontier):
            curr_state = heapq.heappop(frontier)

            # update closest_state if we find a better match
            if curr_state.h < closest_state.h:
                closest_state = curr_state

                # exit if we find our goal
                if curr_state.is_dest():
                    break

            # skip if further path to visited point
            if curr_state in visited and visited[curr_state][1] < curr_state.g:
                continue

            for nbr_state in curr_state.neighbours():
                if nbr_state not in visited or visited[nbr_state][1] > curr_state.g:
                    visited[nbr_state] = (curr_state, nbr_state.g)
                    heapq.heappush(frontier, nbr_state)
        
        return self._backtrack(visited, closest_state)
    
    def _backtrack(self, visited, dest: AutonomousCarPathfindingState) -> List[Tuple[AutonomousCarSpatialDirection, AutonomousCarSpatialPosition]]:
        path: List[AutonomousCarPathfindingState] = []

        curr = dest
        while curr is not None:
            path.append(curr)

            curr, *_ = visited[curr]
        
        path.reverse()

        rel_path = []

        for i in range(len(path)):
            curr = path[i]
            prev_dir = AutonomousCarSpatialDirection.FRONT if i == 0 else path[i-1].dir

            rel_path.append((prev_dir.abs_to_rel(curr.dir), curr.pos))
        
        return rel_path