---
layout: default
title:  Status
---

**PROJECT SUMMARY:**
The goal of our project is to create and compare two Malmo agents that learn to fight enemies using Q-learning. One will learn to use a general fighting strategy that is independent of the type of enemy that it is fighting. The other will be a specialist, such that it takes into account the type of enemy it is fighting and makes more informed decisions using this information. By using Q-Learning, we are training our agent to make decisions based on the current state of its fight with a mob. Our hope is that our specialist agent, with its more informed world-state, will eventually learn to tailor its combat strategy to specific enemy types, and therefore become more effective than the generalist.

**APPROACH:**


**EVALUATION:**
To evaluate our prototype’s performance we are collecting statistics such as the health of the agent at the end of the round along with the time that it took the agent to kill the enemy, or timeout. Below are some graphs showing its performance.

The graphs show the total amount of health remaining after the fight in red and the time taken to kill the mob in blue (30s if we failed to kill the enemy). The number at the bottom represents the number of iterations we ran the bot. It is important to note that because updates to the q-table happen per action, not per round, the relatively small number of rounds yields a significant number of updates, and therefore a significant amount of learning.

The performance of the generalist bot (‘GB’) and the specialist bot (‘SB’) are displayed side-by-side for comparison.

![alt text](https://raw.githubusercontent.com/StStevens/TeamBabylon/master/docs/blaze.png)
![alt text](https://raw.githubusercontent.com/StStevens/TeamBabylon/master/docs/cave-spider.png)
![alt text](https://raw.githubusercontent.com/StStevens/TeamBabylon/master/docs/creeper.png)
![alt text](https://raw.githubusercontent.com/StStevens/TeamBabylon/master/docs/endermite.png)
![alt text](https://raw.githubusercontent.com/StStevens/TeamBabylon/master/docs/ghast.png)
![alt text](https://raw.githubusercontent.com/StStevens/TeamBabylon/master/docs/silverfish.png)
![alt text](https://raw.githubusercontent.com/StStevens/TeamBabylon/master/docs/skeleton.png)
![alt text](https://raw.githubusercontent.com/StStevens/TeamBabylon/master/docs/spider.png)
![alt text](https://raw.githubusercontent.com/StStevens/TeamBabylon/master/docs/witch.png)
![alt text](https://raw.githubusercontent.com/StStevens/TeamBabylon/master/docs/wolf.png)
![alt text](https://raw.githubusercontent.com/StStevens/TeamBabylon/master/docs/zombie.png)
![alt text](https://raw.githubusercontent.com/StStevens/TeamBabylon/master/docs/zombie-pigman.png)



**REMAINING GOALS AND CHALLENGES:**
Our prototype currently lacks the ability to use its bow in combat. Using the bow had proved challenging as the action requires a build-up to be timed. Before we consider the project finished we would like to make it possible for our bot to engage at range. In order to accomplish this we believe that we would need to separate movement actions from attack actions, which increases the algorithm complexity but allows the bot to take advantage of the ability to move and attack at the same time.

We also need to perform better evaluation of our model’s optimal policy. Currently  we are assessing the model’s performance while it’s still learning, but we would like it to display the optimal decisions for each state.

Our prototype is also unaware of the action it previously took. By adding the last action as a part of the state, it allow the prototype to develop attack patterns, like swinging and retreating, at the cost of a large increase in state space.

   Add Bow Support
   Split movement / attacking - Double Q table?
   Determine Optimal Policy
   Kill creepers better.

