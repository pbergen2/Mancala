The agent uses Heuristic minimax search and Alpha-beta pruning to "see" several turns in advance, allowing it to plot lengthy strategies and avoid traps. It is excellent against random agents and simple, 1-turn "best move" agents. It is also excellent against human opposition, save for the most skilled players who may be able to play with 5-ish turns in advance in mind. This could easily be circumvented by simply increasing the amount of piles searched, which would be done by giving the agent more time to "think" (currently, it's capped at 500ms per move to ensure the program is easy to run and quick). 

An example of how the program is run, with one player being the agent and the other being presumably a human, but also another agent if you wish:

Sending 4 4 4 4 4 4 0 4 4 4 4 4 4 0 1 1 1 to player 1
Turn 1, Player 1 move: 4
Sending 4 4 4 0 5 5 1 5 4 4 4 4 4 0 2 2 1 to player 2
5
Turn 2, Player 2 move: 0
Sending 5 4 4 4 4 4 0 4 4 4 0 5 5 1 3 1 0 to player 1
Turn 3, Player 1 move: 6
Sending 5 4 4 4 4 0 1 5 5 5 0 5 5 1 4 2 0 to player 2
Turn 4, Player 2 move: 6
Sending 6 5 5 5 4 0 1 5 5 5 0 5 0 2 5 1 0 to player 1
Turn 5, Player 1 move: 2
Sending 6 0 6 6 5 1 2 5 5 5 0 5 0 2 6 1 0 to player 1
Turn 6, Player 1 move: 6
Sending 6 0 6 6 5 0 3 5 5 5 0 5 0 2 7 1 0 to player 1
Turn 7, Player 1 move: 1
Sending 0 1 7 7 6 1 4 5 5 5 0 5 0 2 8 1 0 to player 1
Turn 8, Player 1 move: 6

Simply input the numbers for the moves which you wish to do and the agent will reply with its most optimally caluclated response.
