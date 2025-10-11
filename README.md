# NHL Game Score Prediction Project

This project is based on the Udem's IFT6758 Data Science Course Project.
This repository refactors the full three milestones code into a clean modular architecture.
The original project [`IFT6758-B01/iftt6758_project`](https://github.com/IFT6758-B01/iftt6758_project)

## Milestone Overview
- **Milestone 1:** Data acquisition, cleaning, visualization
- **Milestone 2:** Feature engineering, modelling, experiment tracking (WandB)
- **Milestone 3:** Model deployment, API serving, and Streamlit dashboard


## Structure Overview
- **src/data/** : API fetching and tidying
- **src/features/** : Feature engineering and utilities
- **src/models/** : ML model training, evaluation, and tracking
- **src/serving/** : Flask, clients, and Docker
- **src/visualization/** : EDA, shot maps, streamlit dashboard
- **src/utils/** : Config, logging, helpers

## Run
```bash
python main.py
```

## Next Steps
- Migrate milestone code into appropriate modules.
- Replace placeholders with actual logic.
- Validate with pytest and Docker.


