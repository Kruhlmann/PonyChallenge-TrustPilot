# Trustpilot Code challenge
[Challenge link](https://ponychallenge.trustpilot.com/index.html)

## Objective
*Given a random maze consisting of a 15x25 grid containing a monster find a path for the player to the exit.*

## Algorithm
The algorithm I used is based on each move to a new tile having an associated cost. Every 'round' the AI will move the player according to which move is the cheapest.
The cost consists of 3 different values:

| Name                     | Value range                                          	 |
| ------------------------ | ------------------------------------------------------- |
| Distance to exit         | \[0 -> `sqrt(maze_width ** 2 + maze_heightn ** 2)`\]    |
| Trail penalty            | \[0 -> 100\]                                            |
| Monster vicinity penalty | \[999999 -> 999999\]                                    |

## Demo
![demo gif](demo.gif)
