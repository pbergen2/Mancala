# Author: Peter Bergen
import sys
import time
from dataclasses import dataclass
from typing import List, Tuple, Dict, Optional

P1_STORE = 6
P2_STORE = 13

@dataclass(frozen=True)
class State:
    track: Tuple[int, ...]  # length 14
    turn: int               # ply count
    player: int             # 1 or 2
    pie: int                # 0 or 1

def parse_state(line: str) -> State:
    parts = line.strip().split()
    if len(parts) != 17:
        
        raise ValueError(f"Expected 17 integers, got {len(parts)} tokens.")
    nums = list(map(int, parts))
    p1_pits = nums[0:6]
    p1s = nums[6]
    p2_pits = nums[7:13]
    p2s = nums[13]
    turn = nums[14]
    player = nums[15]
    pie = nums[16]

    track = list(p1_pits) + [p1s] + list(p2_pits) + [p2s]
    return State(tuple(track), turn, player, pie)

def is_terminal(st: State) -> bool:
    t = st.track
    p1_empty = all(t[i] == 0 for i in range(0, 6))
    p2_empty = all(t[i] == 0 for i in range(7, 13))
    return p1_empty or p2_empty

def finalize_if_terminal(track: List[int]) -> List[int]:
    
    p1_empty = all(track[i] == 0 for i in range(0, 6))
    p2_empty = all(track[i] == 0 for i in range(7, 13))
    if p1_empty and not p2_empty:
        rem = sum(track[i] for i in range(7, 13))
        for i in range(7, 13):
            track[i] = 0
        track[P2_STORE] += rem
    elif p2_empty and not p1_empty:
        rem = sum(track[i] for i in range(0, 6))
        for i in range(0, 6):
            track[i] = 0
        track[P1_STORE] += rem
    return track

def opposite_pit(pos: int) -> Optional[int]:
    
    if pos == P1_STORE or pos == P2_STORE:
        return None
    if 0 <= pos <= 5:
        
        return 12 - pos
    if 7 <= pos <= 12:
        
        return 12 - pos
    return None

def legal_actions(st: State) -> List[int]:
    t = st.track
    actions = []
    if st.pie == 1:
        actions.append(0) 
    if st.player == 1:
        for a in range(1, 7):
            if t[a - 1] > 0:
                actions.append(a)
    else:
        for a in range(1, 7):
            
            if t[7 + (a - 1)] > 0:
                actions.append(a)
    return actions

def apply_pie(st: State) -> State:
    t = list(st.track)
    p1_pits = t[0:6]
    p1s = t[P1_STORE]
    p2_pits = t[7:13]
    p2s = t[P2_STORE]

    new_track = list(p2_pits) + [p2s] + list(p1_pits) + [p1s]
    return State(tuple(new_track), st.turn + 1, 1 if st.player == 2 else 2, 0)

def apply_move(st: State, action: int) -> State:
    if action == 0:
        return apply_pie(st)

    t = list(st.track)
    player = st.player

    if player == 1:
        start_pos = action - 1  # 0..5
        store_pos = P1_STORE
        opp_store = P2_STORE
        own_pit_range = range(0, 6)
    else:
        start_pos = 7 + (action - 1)  # 7..12
        store_pos = P2_STORE
        opp_store = P1_STORE
        own_pit_range = range(7, 13)

    stones = t[start_pos]
    t[start_pos] = 0

    pos = start_pos
    while stones > 0:
        pos = (pos + 1) % 14
        if pos == opp_store:
            continue
        t[pos] += 1
        stones -= 1

    if pos in own_pit_range and pos != store_pos and t[pos] == 1:
        opp = opposite_pit(pos)
        if opp is not None and t[opp] > 0:
            captured = t[opp] + t[pos]
            t[opp] = 0
            t[pos] = 0
            t[store_pos] += captured

    t = finalize_if_terminal(t)

    if pos == store_pos:
        next_player = player
    else:
        next_player = 2 if player == 1 else 1

    return State(tuple(t), st.turn + 1, next_player, st.pie if action != 0 else 0)

def score_terminal(st: State, root_player: int) -> int:
    t = st.track
    p1s = t[P1_STORE]
    p2s = t[P2_STORE]
    diff = (p1s - p2s) if root_player == 1 else (p2s - p1s)
    return diff * 10000

def quick_move_gain(st: State, action: int, for_player: int) -> Tuple[int, bool]:
    before = st.track[P1_STORE] if for_player == 1 else st.track[P2_STORE]
    nxt = apply_move(st, action)
    after = nxt.track[P1_STORE] if for_player == 1 else nxt.track[P2_STORE]
    gain = after - before
    extra = (nxt.player == for_player)
    return gain, extra

def heuristic(st: State, root_player: int) -> int:
    t = st.track
    p1s = t[P1_STORE]
    p2s = t[P2_STORE]
    p1_pits = sum(t[i] for i in range(0, 6))
    p2_pits = sum(t[i] for i in range(7, 13))

    if root_player == 1:
        store_diff = p1s - p2s
        pit_diff = p1_pits - p2_pits
    else:
        store_diff = p2s - p1s
        pit_diff = p2_pits - p1_pits

    mobility = len(legal_actions(st)) if st.player == root_player else -len(legal_actions(st))

    tactical = 0
    if st.player == root_player:
        best_gain = 0
        best_extra = 0
        for a in legal_actions(st):
            if a == 0 and st.pie != 1:
                continue
            g, ex = quick_move_gain(st, a, root_player) if st.player == root_player else (0, False)
            if g > best_gain:
                best_gain = g
                best_extra = 1 if ex else 0
        tactical += best_gain * 40 + best_extra * 25
    else:
        best_opp_gain = 0
        best_opp_extra = 0
        for a in legal_actions(st):
            if a == 0 and st.pie != 1:
                continue
            g, ex = quick_move_gain(st, a, st.player)
            if g > best_opp_gain:
                best_opp_gain = g
                best_opp_extra = 1 if ex else 0
        tactical -= best_opp_gain * 40 + best_opp_extra * 25

    return store_diff * 120 + pit_diff * 8 + mobility * 3 + tactical

class TimeUp(Exception):
    pass

def choose_move(state: State, time_limit_ms: int = 500) -> int:
    start = time.perf_counter()
    deadline = start + (time_limit_ms / 1000.0) * 0.92

    root = state.player
    tt: Dict[Tuple[Tuple[int, ...], int, int], Tuple[int, int]] = {}

    best_action = 1
    legals = legal_actions(state)
    if legals:
        best_action = legals[0] if legals[0] != 0 else (legals[1] if len(legals) > 1 else 0)

    def time_check():
        if time.perf_counter() >= deadline:
            raise TimeUp()

    def minimax(st: State, depth: int, alpha: int, beta: int) -> int:
        time_check()

        key = (st.track, st.player, st.pie)
        if key in tt:
            saved_depth, saved_val = tt[key]
            if saved_depth >= depth:
                return saved_val

        if is_terminal(st):
            val = score_terminal(st, root)
            tt[key] = (depth, val)
            return val

        if depth == 0:
            val = heuristic(st, root)
            tt[key] = (depth, val)
            return val

        acts = legal_actions(st)

        def order_key(a: int) -> int:
            if a == 0:
                return 500
            g, ex = quick_move_gain(st, a, st.player)
            return g * 100 + (50 if ex else 0)

        acts.sort(key=order_key, reverse=True)

        if st.player == root:
            value = -10**18
            for a in acts:
                nxt = apply_move(st, a)
                value = max(value, minimax(nxt, depth - 1, alpha, beta))
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
        else:
            value = 10**18
            for a in acts:
                nxt = apply_move(st, a)
                value = min(value, minimax(nxt, depth - 1, alpha, beta))
                beta = min(beta, value)
                if alpha >= beta:
                    break

        tt[key] = (depth, value)
        return value

    depth = 1
    try:
        while True:
            time_check()
            acts = legal_actions(state)

            def root_order(a: int) -> int:
                if a == 0:
                    return 500
                g, ex = quick_move_gain(state, a, root)
                return g * 100 + (50 if ex else 0)

            acts.sort(key=root_order, reverse=True)

            cur_best = best_action
            cur_best_val = -10**18

            alpha = -10**18
            beta = 10**18

            for a in acts:
                time_check()
                nxt = apply_move(state, a)
                val = minimax(nxt, depth - 1, alpha, beta)
                if val > cur_best_val:
                    cur_best_val = val
                    cur_best = a
                alpha = max(alpha, cur_best_val)

            best_action = cur_best
            depth += 1

    except TimeUp:
        pass

    return best_action

def main():
    line = sys.stdin.readline()
    if not line:
        return
    st = parse_state(line)
    action = choose_move(st, time_limit_ms=500)
    sys.stdout.write(str(action) + "\n")
    sys.stdout.flush()

if __name__ == "__main__":
    main()