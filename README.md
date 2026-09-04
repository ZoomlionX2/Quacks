# Quacks: Board Game Simulator & Data Analysis

A dual-component project featuring a Python-based simulation engine for the board game *The Quacks of Quedlinburg*, paired with a Jupyter Notebook data analysis that evaluates optimal gameplay strategies.

## Project Overview
The purpose of this project is to discover the most effective strategies in the board game *The Quacks of Quedlinburg*. It consists of two main parts:
1. **Simulation:** A Python application that models all aspects of the two-player variation of the game (excluding the fortune-teller cards). The simulation engine assigns one player a strategy profile built from a combination of options for each decision point in the game. The second player makes random choices. Each of the 914,400 strategy profiles is tested 100 times in the full simulation and the results are saved to parquet files.
2. **Analysis**: The simulation results are analyzed in a Jupyter Notebook. Machine learning models identify the most crucial decision points in the game and the best strategic options for each decision point in order to maximize the win rate and player score.

## Core Insights
* Managing risk has an overwhelming impact on success. In general, a player should not draw additional chips if the risk of exploding their pot exceeds 20%.
* Black and Purple chips perform best on average, followed by Blue.
* The highest value pair of chips should be purchased during the buying phase.
* Rubies should be spent on droplet advances.
* The flask has a very minimal impact on the outcome of the game. It is best used when there is a risk of exploding but high percentage of colored chips remain in the player's bag.
* In the event of an explosion, it is best to choose money for the first six rounds.

## Instructions
To run the simulation locally, follow these instructions:
1. Clone this repository, except for the analysis folder.
2. Run main.py. A basic UI will appear with numeric options.
3. To run the full simulation, enter 1 and follow the menu prompts. Please note: the simulation plays nearly 100 million matches and takes several hours to run.
4. The output will be saved in "simulation_output/full_simulation_results" as multiple parquet files.
Note: You can select option 3 from the main menu to create a custom simulation. Follow the menu to configure how many matches you would like to simulate and to build a strategy profile to test.

To run the Jupyter Notebook locally, follow these instructions:
1. Clone just the analysis folder.
2. Use the environment.yml file to create the conda environment.
3. Open the Jupyter Notebook file quacks.ipynb and run each cell.
