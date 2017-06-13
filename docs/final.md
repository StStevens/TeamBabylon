---
layout: default
title   Final Report
---

## Project Summary:
Our project’s aim was to create Malmo agents that would learn to fight different enemies using Q-learning. In addition to training the bots in combat, we hoped to compare the performance of two different bots, a general bot and a specialist. The main difference between these two bots is that the general bot learns a combat strategy independent of the type of enemy that it is fighting, while the specialist learns a combat strategy specific to each mob type. Our hope was that the general bot would show an improvement over a naive bot, and that the specialist would show a greater improvement over the general bot. We believed this because with its more specific world state, accounting not just for position and health, but also the type of enemy, the specialist would learn to tailor its combat to a certain mob type.

For the most recent update to our project, our group focused on expanding the state space, and along with it, the abilities of our bot. The main focus here was the ability to use both the bow and the sword, and switch between the two as the bot saw fit during combat. Given the increase in the number of possible actions, specifically those focused on attacking, we felt it was limiting for the bot to have to decide between either a movement action or an attack action. We therefore have implemented a dual Q-Table system, in which the bot associates rewards with both an attack action and a movement action separately, so they can be executed simultaneously, rather than having to decide between one or the other.
