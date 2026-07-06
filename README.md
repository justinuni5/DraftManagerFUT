# DraftManagerFUT

A state-driven football management and FUT draft simulator built with Python and Tkinter.

##  Core Architecture & Data Pipeline

This repository initializes the primary data pipeline and player scouting pool that drives the simulation's draft mechanics. By decoupling the static asset database from the live state engine, the architecture ensures modularity and easy data expansion.

###  1. The Master Draft Pool (`master_draft_pool.csv`)
This file acts as the central player database for the entire application. Instead of relying on rigid, hardcoded player objects, the system reads from this structural dataset to generate dynamic draft choices. 

* **Player Metadata:** Tracks classic identifiers including player name, age, era, nationality, and club association.
* **Attributes & Rating Matrix:** Defines core simulation vectors like Base Overall (`base_ovr`), Potential, and live tracking baselines such as `stamina` and `fatigue`.
* **Positional Versatility:** Maps structural role assignments via `primary_pos` (e.g., `CB`, `LW`) and lists eligible secondary positions under `alt_positions` to feed the tactical swap engine.

###  2. The Data Ingestion Engine (`pipeline.py`)
The pipeline serves as the ETL (Extract, Transform, Load) bridge between the raw CSV data matrix and the live Tkinter graphical user interface. 

* **Parsing & Validation:** Sanitizes the incoming CSV rows, ensuring that statistical ratings are converted to standard manipulation integers and alternative positions are formatted into readable Python arrays.
* **Object Inflation:** Instantiates individual string rows into high-fidelity `Player` class objects equipped with native runtime methods (such as tracking match stats, goal histories, and dynamic structural positioning).
* **Draft Pool Randomization:** Provisions isolated algorithmic subsets of players to feed the FUT-style draft selection screen, guaranteeing diverse team-building options on every playthrough.
