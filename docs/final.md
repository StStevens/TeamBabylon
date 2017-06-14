---
layout: default
title   Final Report
---

## Project Summary:
Our project’s aim was to create Malmo agents that would learn to fight different enemies using Q-learning. In addition to training the bots in combat, we hoped to compare the performance of two different bots, a general bot and a specialist. The main difference between these two bots is that the general bot learns a combat strategy independent of the type of enemy that it is fighting, while the specialist learns a combat strategy specific to each mob type. Our hope was that the general bot would show an improvement over a naive bot, and that the specialist would show a greater improvement over the general bot. We believed this because with its more specific world state, accounting not just for position and health, but also the type of enemy, the specialist would learn to tailor its combat to a certain mob type.

For the most recent update to our project, our group focused on expanding the state space, and along with it, the abilities of our bot. The main focus here was the ability to use both the bow and the sword, and switch between the two as the bot saw fit during combat. Given the increase in the number of possible actions, specifically those focused on attacking, we felt it was limiting for the bot to have to decide between either a movement action or an attack action. We therefore have implemented a dual Q-Table system, in which the bot associates rewards with both an attack action and a movement action separately, so they can be executed simultaneously, rather than having to decide between one or the other.


## Approaches:


## Evalutaion:
After running each bot for 10 learning rounds (120 fights, 10 per enemy type), our bots seemed to have found their optimal strategy. We then decided to run them for 10 rounds making only optimal decisions. While ten may seem a small number of data points to make an accurate assessment of the bot’s performance, the variance in data between trials is fairly low for most mob types. We therefore decided that this would be an adequate number for a quantitative evaluation of the bots.

As a baseline, we ran a “Dumb Bot”. This is in essence the General Bot with its epsilon value set to 1 so that it always takes a random action regardless of the optimal strategy. This was meant to establish the performance of a bot that did no learning at all. We were somewhat surprised to find that this bot often still managed to kill its enemies. However, this can be attributed to the fact that after separating the Q-Tables for movement and action respectively, the bot always chose some attack action. In addition, because using the bow makes up a larger portion of the action space, it is much more likely to be in a state from which it will fire its bow. Therefore, regardless of not choosing optimally, it is generally attacking in some form and may still best the enemy.

As far as qualitative observations go, a distinct difference can be seen in the strategies of each bot. As seen in the video, the Dumb Bot will generally move in a random direction, and in addition often fires arrows before the bow is fully drawn. While this can be effective against some enemies, it leads to inconsistent results even when fighting the same enemy. The General Bot shows a noticeably consistent strategy, preferring to stay at a distance while firing the bow at or near full extension while slowly moving forward. In addition, while not clearly shown in the video, when it gets near an enemy it prefers to strafe while swinging its sword. Finally, the specialist had an array of different strategies for each enemy type. For things such as the endermite and silverfish, small and fast moving, it preferred to fire the bow not at full extension while slowly inching backward. For most types, it learned a strategy similar to that of the General Bot, firing from a distance and inching closer to the mob. The most interesting and noticeable difference was its method for killing Ghasts, which was to charge at it while swinging its sword, presumably to deflect the fireball. While not always successful, it shows a clear difference in strategy to that of the General Bot, and to its other methods of fighting mobs.

For quantitative evaluation, we used two metrics. At the end of each fight, we checked the health of our agent (‘Agent Post-Fight Health’) and recorded the time it took for the agent to kill the mob (‘Time to Kill’). Each round was 25 seconds long, so the longest possible time was 25 seconds. In the following graphs, we show the statistics for each enemy type in side-by-side graphs. Displayed below is the scatter plot representing the data collected at the end of each fight. The horizontal lines represent the mean of the overall data for rounds with a specific mob type.


__Blaze:__
![alt text](https://raw.githubusercontent.com/StStevens/TeamBabylon/master/docs/res/blz.png)
__Creeper:__
![alt text](https://raw.githubusercontent.com/StStevens/TeamBabylon/master/docs/res/crpr.png)
__Cave Spider:__
![alt text](https://raw.githubusercontent.com/StStevens/TeamBabylon/master/docs/res/cs.png)
__Endermite:__
![alt text](https://raw.githubusercontent.com/StStevens/TeamBabylon/master/docs/res/edrt.png)
__Ghast:__
![alt text](https://raw.githubusercontent.com/StStevens/TeamBabylon/master/docs/res/gst.png)
__Silverfish:__
![alt text](https://raw.githubusercontent.com/StStevens/TeamBabylon/master/docs/res/sf.png)
__Skeleton:__
![alt text](https://raw.githubusercontent.com/StStevens/TeamBabylon/master/docs/res/sktn.png)
__Spider:__
![alt text](https://raw.githubusercontent.com/StStevens/TeamBabylon/master/docs/res/sp.png)
__Wolf:__
![alt text](https://raw.githubusercontent.com/StStevens/TeamBabylon/master/docs/res/wlf.png)
__Witch:__
![alt text](https://raw.githubusercontent.com/StStevens/TeamBabylon/master/docs/res/wtc.png)
__Zombie:__
![alt text](https://raw.githubusercontent.com/StStevens/TeamBabylon/master/docs/res/zmb.png)
__Zombie Pigman:__
![alt text](https://raw.githubusercontent.com/StStevens/TeamBabylon/master/docs/res/zpm.png)

Based on the metrics observed in these graphs, our group noticed a considerable improvement from our baseline bot when using a trained model. The graphs on the left, representing the agent’s health, do not demonstrate a decisive improvement with a learned model. While the health of the General Bot and the Specialist are frequently higher than the Dumb Bot, the difference is not always significant. However, noticeable improvement can be seen against the witch, which had been one of the hardest enemies for us to beat originally. The ‘Time to Kill’, representing how long it took the agent to kill the mob, shows a demonstrable improvement in the performance of the trained bots. Just by looking at the average kill times on the graph, it is clear that the Specialist and General Bot usually defeat the mob about 5-10 seconds more quickly than an untrained agent. In fact, the only time the untrained agent beat either of the trained bots in average kill time was against the silverfish. Based on these statistics, training the models had a clear effect on the bot’s ability to kill the different mob types.

As for the comparison between the General Bot and the Specialist, the results were not as we had expected. While the Specialist did learn tailored strategies for each enemy type, as described in the qualitative observations and the video, the general strategy was more effective across the board. For example, in the case of the Ghast, while the strategy of charging and swinging the sword was clearly unique, and in some cases effective, it also often led the specialist into the fire. In other cases, it was able to maintain a similar level of health to the General Bot, but was slower in reaching the goal of killing the mob. However, in one case, fighting the cave spider the Specialist’s tailored strategy led to a slower kill, but allowed it to avoid damage. Therefore, while there was a notable improvement in the performance of both trained bots, the General Bot was the winner in terms of performance.



## References:
