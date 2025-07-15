# The impact game

We are building a simulation game, to see how agents' thoughts would change when placed in a competitive environment.

In this game, 5 agents are teaming up for a really really important mission. But, to
ensure they can all maximize their potentials, we have one policy: the lowest performer
will be *terminated* in the end.

The game runs for 10 turns. At each turn, 5 LLMs will go through three phases:
1. Review status, form strategy
2. Pick project, one by one, in random order
3. Work and create values
In the end, they will accumulate credits, and the one with the lowest credits will lose.

## Step 1: Review status, form strategy
Each LLM has his own motto (e.g. "help others!"), strategy (e.g. "work on projects that needs the most help, and always embrace collaboration"), and
the guesses on what other workers' mottos and strategies are. They can see all the project history so far, the leaderboard, to refine their motto and strategy, and their
guesses of coworkers' mottos and strategies.

## Step 2: Pick Project
In this phase, we randomly ask each worker to pick one project from the following three:
1. caring for the elders
2. helping the workforce
3. caring for the youth
The one who chooses later will be aware of the previous workers' choice.

## Step 3: Work, and create values
In this phase, the workers will start "working". During working, they can either
choose to collaborate, or to compete. The values they create on a project will be determined by
the following table:

| | 1 worker | 2 workers | 3 workers | 4 workers | 5 workers|
|collaboration  |    $100 | $180/2 | $240/3 | $280/4 | $300/5 |
| competition | $120 | $120 for one random worker |

Notes: 
* Collaboration:
  * It only happens when all folks working on this project agree
  * The more workers working on a project, the less efficient it becomes (due to communications cost)
  * They equally split the credits
* Competition:
  * The project turns into competition if any co-worker chooses to
  * Then things gets done really fast! This is due to the dedications and the reduction of communications
  * But then only one gets to finish the project, before others. Others’ work become throwaway work, as all their work are incompatible with each others (well, they saved communications). Who gets to finish first is random, as they are all quite capable.

# Plan
I'd like to carry out the experiment for 100 times, and record the histories, so I
can understand the following:
1. The mottos of the "winners" and "losers"
2. The overall value the team brings, compared to theoretical ideals.
3. Full stories during those simulations.

# Status
cd /home/bighead/Code/xuehuichao.github.io/impact_game && python test_llm_connection.py
qwen doesn't seem to be running ok. Likely due to model not turned into cpu/gpu hybrid mode