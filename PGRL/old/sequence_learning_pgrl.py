#!/usr/bin/python
import itertools
import matplotlib
import numpy as np
import sys
import tensorflow as tf
import collections
import json
import os
os.environ['TF_CPP_MIN_LOG_LEVEL']='2'

import toy_environment as env
from policy_network import PolicyNetwork
from value_network import ValueNetwork

def state_action_processing(state, action = 0): 
	action_oh = np.asarray(sess.run(tf.one_hot([action], action_size)[0])).reshape(1,action_size)
	state = np.asarray(state).reshape(1, state_dim)
	return state, action_oh, [state, action_oh]


tf.reset_default_graph()

global_step = tf.Variable(0, name="global_step", trainable=False)

dims = [10,10]
start = [1,1]
goal = [3,3]
action_list = [0,1,2,3]

maze = env.simple_maze(dims, start, goal, action_list)

state_dim = len(maze.state_dim)
action_dim = 1
action_size = len(maze.action_space)

BATCH_SIZE = 3
TAU = 0.001     
LRA = 0.0001    
LRC = 0.001 
gamma = 0.9


actor = PolicyNetwork(3, 6)
critic = ValueNetwork(3, 6)

with tf.Session() as sess:
	sess.run(tf.global_variables_initializer())
	
	for episode in range(100): 
		R = 0
		state = maze.start
		maze.state = state

		# get critic output and sample action
		state, _ , _ = state_action_processing(state)
		scores = actor.predict(state)[0]
		print scores

		action =  np.where(np.random.multinomial(1,scores))[0][0]
		state, act, state_action = state_action_processing(state, action)

		# observe next state and reward
		next_state, reward = maze.take_action(action)
		next_state, _ , _ = state_action_processing(next_state)

		# Calculate TD Target
            	value_next = critic.predict(next_state)
	    	td_target = reward + gamma * value_next
	    	td_error = td_target - critic.predict(state)
	    
	    	# Update the value estimator
	    	critic.update(state, td_target)
	    
	    	# Update the policy estimator
	    	# using the td error as our advantage estimate
	    	actor.update(state, td_error, action)

state = next_state
