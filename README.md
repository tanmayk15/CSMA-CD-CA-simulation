# CSMA-CD-CA-simulation

This repository contains Python simulations for Carrier Sense Multiple Access with Collision Detection (CSMA/CD) and Carrier Sense Multiple Access with Collision Avoidance (CSMA/CA).
These are fundamental network access control methods used in Ethernet and Wi-Fi.

Features

Interactive Visualization – See how devices sense the medium, detect collisions, and apply backoff.

Manual and Auto Step Modes – Control the simulation step-by-step or let it run automatically.

Binary Exponential Backoff – Implements realistic collision handling.

Graphical UI with Matplotlib Buttons – Start, pause, and exit the simulation with a click.

Files

csma_cd_simulation.py – Basic CSMA/CD simulation with manual stepping.

csma_cd_sim_v3.py – Enhanced CSMA/CD simulation with both manual and automatic modes.

csma_ca_sim_v1.py – CSMA/CA simulation with collision avoidance and backoff timers.

Requirements

Install dependencies using pip:

pip install matplotlib numpy

How to Run

Run any script directly in Python:

python csma_cd_simulation.py


or

python csma_ca_sim_v1.py


A window will open showing network devices and the transmission medium. Use the on-screen buttons:

Next Step – Advance the simulation manually.

Auto Simulate – Run automatically (in v1/v3 scripts).

Exit – Close the simulation.

Concepts Illustrated

Carrier sensing (checking if the medium is busy).

Collision detection vs. collision avoidance.

Binary exponential backoff timers.

Sequential vs. random access behavior.

License

This project is open-source under the MIT License.
