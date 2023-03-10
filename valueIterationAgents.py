# valueIterationAgents.py
# -----------------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


# valueIterationAgents.py
# -----------------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


import mdp, util

from learningAgents import ValueEstimationAgent
import collections

class ValueIterationAgent(ValueEstimationAgent):
    """
        * Please read learningAgents.py before reading this.*

        A ValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs value iteration
        for a given number of iterations using the supplied
        discount factor.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 100):
        """
          Your value iteration agent should take an mdp on
          construction, run the indicated number of iterations
          and then act according to the resulting policy.

          Some useful mdp methods you will use:
              mdp.getStates()
              mdp.getPossibleActions(state)
              mdp.getTransitionStatesAndProbs(state, action)
              mdp.getReward(state, action, nextState)
              mdp.isTerminal(state)
        """
        self.mdp = mdp
        self.discount = discount
        self.iterations = iterations
        self.values = util.Counter() # A Counter is a dict with default 0
        self.runValueIteration()

    def runValueIteration(self):
        # Write value iteration code here
        "*** YOUR CODE HERE ***"
        for iteration in range(self.iterations):
          states = self.mdp.getStates()
          TempCounter = util.Counter()
          for state in states:
            MaxVal = float("-inf")
            for action in self.mdp.getPossibleActions(state):
              Qvalue = self.computeQValueFromValues(state, action)
              if Qvalue > MaxVal:
                MaxVal = Qvalue
              TempCounter[state] = MaxVal
          self.values = TempCounter

    def getValue(self, state):
        """
          Return the value of the state (computed in __init__).
        """
        return self.values[state]


    def computeQValueFromValues(self, state, action):
        """
          Compute the Q-value of action in state from the
          value function stored in self.values.
        """
        "*** YOUR CODE HERE ***"
        TSandP = self.mdp.getTransitionStatesAndProbs(state, action)
        value = 0
        for TS in TSandP:
          stateTransitionReward = self.mdp.getReward(state, action, TS[0])
          value = value + stateTransitionReward + self.discount*(self.values[TS[0]]*TS[1])
          

        return value

    def computeActionFromValues(self, state):
        """
          The policy is the best action in the given state
          according to the values currently stored in self.values.

          You may break ties any way you see fit.  Note that if
          there are no legal actions, which is the case at the
          terminal state, you should return None.
        """
        "*** YOUR CODE HERE ***"
        StateAction = util.Counter()
        for a in self.mdp.getPossibleActions(state):
          StateAction[a] = self.computeQValueFromValues(state,a)
        Policy = StateAction.argMax()
        return Policy

    def getPolicy(self, state):
        return self.computeActionFromValues(state)

    def getAction(self, state):
        "Returns the policy at the state (no exploration)."
        return self.computeActionFromValues(state)

    def getQValue(self, state, action):
        return self.computeQValueFromValues(state, action)

class AsynchronousValueIterationAgent(ValueIterationAgent):
    """
        * Please read learningAgents.py before reading this.*

        An AsynchronousValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs cyclic value iteration
        for a given number of iterations using the supplied
        discount factor.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 1000):
        """
          Your cyclic value iteration agent should take an mdp on
          construction, run the indicated number of iterations,
          and then act according to the resulting policy. Each iteration
          updates the value of only one state, which cycles through
          the states list. If the chosen state is terminal, nothing
          happens in that iteration.

          Some useful mdp methods you will use:
              mdp.getStates()
              mdp.getPossibleActions(state)
              mdp.getTransitionStatesAndProbs(state, action)
              mdp.getReward(state)
              mdp.isTerminal(state)
        """
        ValueIterationAgent.__init__(self, mdp, discount, iterations)

    def runValueIteration(self):
        "*** YOUR CODE HERE ***"

        states = self.mdp.getStates()
        for state in states:
            self.values[state] = 0
        statesNum = len(states)
        for i in range(self.iterations):
            stateIndex = i % statesNum
            state = states[stateIndex]

            Terminal = self.mdp.isTerminal(state)
            if not Terminal:
                action = self.getAction(state)
                Qval = self.getQValue(state, action)
                self.values[state] = Qval

class PrioritizedSweepingValueIterationAgent(AsynchronousValueIterationAgent):
    """
        * Please read learningAgents.py before reading this.*

        A PrioritizedSweepingValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs prioritized sweeping value iteration
        for a given number of iterations using the supplied parameters.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 100, theta = 1e-5):
        """
          Your prioritized sweeping value iteration agent should take an mdp on
          construction, run the indicated number of iterations,
          and then act according to the resulting policy.
        """
        self.theta = theta
        ValueIterationAgent.__init__(self, mdp, discount, iterations)

    def runValueIteration(self):
        "*** YOUR CODE HERE ***"
        states = self.mdp.getStates()
        fringe = util.PriorityQueue()
        predecessors = {}

        for s in states:
            self.values[s] = 0
            predecessors[s] = self.getPredecessors(s)
        for s in states:
            Terminal = self.mdp.isTerminal(s)

            if not Terminal:
                currentVal = self.values[s]
                diff = abs(currentVal - self.maxQvalue(s))
                fringe.push(s, -diff)
        for i in range(self.iterations):
            if fringe.isEmpty():
                return

            s = fringe.pop()
            self.values[s] = self.maxQvalue(s)

            for p in predecessors[s]:
                diff = abs(self.values[p] - self.maxQvalue(p))
                if diff > self.theta:
                    fringe.update(p, -diff)


    def maxQvalue(self, state):
        return max([self.getQValue(state, a) for a in self.mdp.getPossibleActions(state)])

    def getPredecessors(self, state):
        predecessorSet = set()
        states = self.mdp.getStates()

        if not self.mdp.isTerminal(state):

            for p in states:
                Terminal = self.mdp.isTerminal(p)
                legalActions = self.mdp.getPossibleActions(p)

                if not Terminal:
                    for action in legalActions:
                            TSandP = self.mdp.getTransitionStatesAndProbs(p, action)
                            for sPrime, T in TSandP:
                                if (sPrime == state) and (T > 0):
                                    predecessorSet.add(p)

        return predecessorSet
