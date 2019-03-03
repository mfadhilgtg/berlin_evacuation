# berlin_evacuation

Berlin Evacuation scenario for Self-Organizing Multi-Agent Systems

# Initial Setup
 - Install EPOS
 - Create a python environment for installing required packages
 - Activate python environment
 - `pip install requirements.txt`
 - Create `source_data` and `input` folders
 - Copy in `berlin-v5.0.network.xml`, `berlin-v5.0.person-attributes.xml`,
   and `berlin-v5.2-1pct.plans.xml` into `source_data`. (Needs to be unzipped)

# Generating Input Files
 - `python configure_network.py --network source_data/berlin-v5.0.network.xml --center 4595460 5821710 --radius 20000`
 - `python3 generate_dummy_plans.py --plans source_data/berlin-v5.2-1pct.plans.xml --center 4595460 5821710 --radius 20000`
 - `python generate_iepos_files.py --network input/evacuation_network.xml --plans input/dummy_plans.xml --center 4595460 5821710 --radius 20000`

# Updating Evacuation Plans from EPOS Result
- `python --plans input/dummy_plans.xml --epos_plans input/selected-plans.csv --mapping input/agent_mapping.csv --network input/evacuation_network.xml`

# Plotting Figures
- Agents' plan histogram `python plot_plans.py --network input/evacuation_network.xml --plans input/dummy_plans.xml --center 4595460 5821710 --radius 2000`