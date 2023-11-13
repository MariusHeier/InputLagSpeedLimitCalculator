# Input Lag Network Simulator

## Introduction
This tool, designed for gamers, measures your network's input lag "speed limit" - the threshold of lag advantage you need to consistently win in different network conditions. 

## Features
- **Real-Time Network Measurement:** Captures live ping data to represent your current network conditions accurately.
- **Game Simulation:** Utilizes actual network data to simulate gaming scenarios, assessing how network variability affects outcomes.
- **Input Lag Analysis:** Experiments with different input lag settings to understand their effect on win rates under specific network conditions.

## Installation
1. **Download:** Visit [Input Lag Speed Limit Calculator](https://github.com/MariusHeier/InputLagSpeedLimitCalculator/raw/main/dist/InputLagSpeedLimitCalculator.zip) to download the tool.
2. **Execution:** Run the `.exe` file on Windows or use the Python version if you have trust issues with exe files
3. **Server Selection:** Choose the gaming server location closest to you for accurate measurements.

## Usage
- **Measure Ping:** The tool starts by measuring ping data from your selected server.
- **Run Simulations:** It then runs game simulations using this data, applying various input lag settings to each virtual player.
- **Analyze Results:** Your "speed limit" is the smallest amount of input-lag that will Impact your game. The win rate is what factor you consider to be an advantage in a 10 round game. 90% means you win 9 out of 10 rounds.


## How It Works
The simulator measures your network's ping and inputs this data into a gaming scenario. By systematically increasing the input lag on one of the virtual players and observing the outcomes, the tool identifies your network's input lag "speed limit."

## Practical Implications
This tool helps determine if efforts to reduce input lag (like upgrading hardware or optimizing settings) will meaningfully improve your competitive gaming performance.

## Additional Resources
- **Project video:** Video covering this project is on YouTube [here](https://www.youtube.com/watch?v=kijU75PGMMk).
- **Source Code:** For those interested in the technical aspects, the source code is available in this repository.

## Disclaimer
This tool is in beta. Results and experiences may vary based on individual network conditions and gaming setups.


