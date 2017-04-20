---
layout:	default
title:	Proposal
---

_Summary:_
	For our project, we plan to train an agent in combat against different types of enemies. In order to determine the success of our agent in combat, we will need to determine the "reward" for a particular fight, or the agent's score in a particular battle. To determine this we will need to collect statistics such as the damage dealt to the enemy, the amount of time needed to kill the enemy, the health remaining after the fight is over, and other factors that could be used in determining our effectiveness in combat. Our states will reflect whether we are using a long range or short range weapon, whether we are retreating or advancing, and whether or not we are currently attacking. 


_AI/ML Algorithms:_
	We plan to use reinforcement learning with Markov decision processes in order to accomplish this goal.


_Evaluation Plan:_
	As a baseline for our program, we would like to make an AI that uses a very simple combat system of just moving towards a target and swinging consistently. This will give us a baseline of the performance of simple, unreactive combat. By collecting statistics such as our health and the enemies health after the fight is over, how long it took the agent or the enemy to die, and what method of fighting we were using (ranged or unranged) we should be able to determine our performance in combat and track improvement over time.
	In order to determine if our algorithm is working we will fight an enemy such as zombie using our learning process. After several tests, we will determine if the metrics that we collect given that our learning process is running are an improvement over the baseline combat of running and swinging. This means that our health is higher, and our enemies are killed faster. In addition, in order to visualize the process, because we are using an MDP we will print the current state, as well as the relative probabilities of transitioning.
