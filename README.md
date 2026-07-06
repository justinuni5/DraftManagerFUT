#  DraftManagerFUT (Desktop Prototype & Proof of Concept)

An interactive, desktop-driven football management and FUT draft simulator built with Python and Tkinter. This repository serves as a fully functional desktop architecture prototype.

##  Project Status: Concluded & Pivoting to Web (HTML/JS)
**This desktop repository is now finalized and officially concluded as a completed Proof of Concept (PoC).** While building this desktop version, navigating heavy state-driven UI layouts, real-time matrix re-renders, and window lifecycle management within Python’s standard Tkinter framework surfaced distinct architectural bottlenecks. To scale this game with seamless, responsive animations, modern CSS grids, and cross-platform accessibility, **the project is being rebuilt from the ground up as a native web application utilizing an HTML/CSS/JavaScript stack.** The logic, database structures, and pipelines established in this repository will serve as the structural blueprint for the upcoming web release.

---

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

###  3. Core Match & UI Engine (`engine.py`, `game.py`, `ui_game.py`)
* **State-Driven Selection Engine:** An intuitive, click-to-swap squad engine that makes organizing your Starting Eleven and Bench options seamless without fragile absolute pixel-coordinate drag tracking.
* **Halftime Locker Room Tactics:** Interactive matchday simulation features allowing users to swap fatigued players with active bench options instantly to safeguard results during the second half.
* **Spoiler-Free Simulation Loop:** Real-time league standings calculations are visually isolated during active match gameplay sequences, preserving suspense and narrative surprise until final results are finalized.

---

##  Technical Specifications (Desktop Prototype)

- **Backend Logic:** Python 3.12+ 
- **Presentation Layer:** Tkinter (Python Standard Desktop UI Library)
- **Data Source:** Structural CSV Flat-File Matrix
- **Design Pattern:** Separated Presentation/Logic Engine Pattern

---

##  Key Architectural Takeaways for the Web Pivot

Building this desktop prototype highlighted several key reasons why migrating to a native web framework is the optimal path forward:
1. **Layout & Style Flexibility:** Handling complex multi-column grid spaces and dynamic color contrasts is infinitely cleaner using semantic HTML5 tags and CSS Flexbox/Grid compared to rigid desktop canvas widgets.
2. **State & Event Driven Dom Isolation:** Preventing elements from duplicating during continuous match loops is natively handled by modern browser DOM rendering or component-based UI frameworks.
3. **Distribution & Portability:** Web architectures remove local installation barriers, allowing the simulation to execute instantaneously on mobile or desktop browsers without local Python library prerequisites.
