import random
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator

class LearningAgent(Agent):
    """An agent that learns to drive in the smartcab world."""

    def __init__(self, env):
        super(LearningAgent, self).__init__(env)  # sets self.env = env, state = None, next_waypoint = None, and a default color
        self.color = 'red'  # override color
        self.planner = RoutePlanner(self.env, self)  # simple route planner to get next_waypoint
        # TODO: Initialize any additional variables here
        self.Q = {}
        self.pi = {}
        self.alpha = 1
        self.gema = 0
        self.ACTIONS = [None, 'forward', 'left', 'right']

    def reset(self, destination=None):
        self.planner.route_to(destination)
        # TODO: Prepare for a new trip; reset any variables here, if required

    def update(self, t):
        # Gather inputs
        self.next_waypoint = self.planner.next_waypoint()  # from route planner, also displayed by simulator
        inputs = self.env.sense(self)
        deadline = self.env.get_deadline(self)

        # TODO: Update state
        self.state = inputs
        self.state['next_waypoint'] = self.next_waypoint
        self.state = tuple(self.state.items())
        # TODO: Select action according to your policy

        action = random.choice(self.ACTIONS) if self.state not in self.pi else self.pi[self.state]
        # Execute action and get reward
        reward = self.env.act(self, action)

        # TODO: Learn policy based on state, action, reward
        next_state = self.env.sense(self)
        next_state['next_waypoint'] = self.planner.next_waypoint()
        next_state = tuple(next_state.items())
        next_action = random.choice(self.ACTIONS) if next_state not in self.pi else self.pi[next_state]
        sta_act = (self.state, action)
        self.Q[sta_act] = (1 - self.alpha) * self.Q.get(sta_act, 0) + self.alpha*(reward + self.gema*self.Q.get((next_state, next_action), 0))
        acts_Q = [self.Q.get((self.state, act)) for act in self.ACTIONS]
        if None not in acts_Q:
            max_Q = max(acts_Q)
            max_acts = [act for act in self.ACTIONS if max_Q==self.Q.get((self.state, act))]
            self.pi[self.state] = random.choice(max_acts)
        #print self.Q
        #print 
        #print self.pi
        print "LearningAgent.update(): deadline = {}, inputs = {}, action = {}, reward = {}".format(deadline, inputs, action, reward)  # [debug]


def run():
    """Run the agent for a finite number of trials."""

    # Set up environment and agent
    e = Environment()  # create environment (also adds some dummy traffic)
    a = e.create_agent(LearningAgent)  # create agent
    e.set_primary_agent(a, enforce_deadline=True)  # set agent to track

    # Now simulate it
    sim = Simulator(e, update_delay=0.5)  # reduce update_delay to speed up simulation
    sim.run(n_trials=100)  # press Esc or close pygame window to quit


if __name__ == '__main__':
    run()
