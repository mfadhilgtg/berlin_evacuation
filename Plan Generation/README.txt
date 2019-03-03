## INTRODUCTION

This dataset was generated using the OpenBerlin scenario for Matsim that consists of synthetic population in Berlin according to "Zensus 2011". The original data contains daily activity-travel plans of the population and road network containing road capacity, number of lanes, and speed limit. The evacuation area in the scenario is defined as 2000 meter radius from the city center and there are 961 agents inside the area and 65 possible exit roads. 65 possible exit roads correspond to 65 possible plans that agents can choose. 

## DIRECTORY STRUCTURE

This dataset contains one set of scenario, which consists of Agent files and Goal Signal File, and code to generate new set of plans.

## AGENT INFO

There are 961 files, each corresponding to one agent. The naming scheme is as follows:

        agent_XXXX.plans

where XXXX stands for the agent identification which belongs to the range [0,961].

Due to different naming for agent id between EPOS input and Matsim scenario, mapping between the agents' id is provided in agent_mapping.csv with format line as follow

(ID in agent_XXXX.plans),(ID in Matsim scenario)

## PLANS INFO

Each agent file contains between 2 and 65 possible plans. Each line represents one possible plan. The format of the line is as follows:

(score):(value1,value2,value3, ....,value65)

where (score) indicates the distance between agent's position to the selected exit node. There are 65 comma-separated values after the colon sign (':'), each associated to ID of exit nodes. Selected exit node for each plan is represented as 1 and the other values are set to 0.

## GOAL SIGNAL FILE

Goal signal file contains the desired aggregation of the agents' plan. The goal signal consist of 65 comma-separated values associated to relative capacity of each possible exit node(number of vehicle per hour) scaled to the number of agents that a node can handle, such that the sum of goal signal values is equal to the total number of agents in the scenario.

## GENERATING NEW SCENARIO
 - Get `berlin-v5.0.network.xml` and `berlin-v5.0.person-attributes.xml` from MATSIM OpenBerlin Scenario `https://github.com/matsim-vsp/matsim-berlin.git`
 - Create `source_data` and `input` folders
 - Copy in `berlin-v5.0.network.xml`, `berlin-v5.0.person-attributes.xml`,
   and `berlin-v5.2-1pct.plans.xml` into `source_data`. (Needs to be unzipped)
 - Determine the desired evacuation center and radius and change the input argument
 - Configure the evacuation network,`python configure_network.py --network source_data/berlin-v5.0.network.xml --center 4595460 5821710 --radius 20000`
 - Update the dummy plans`python3 generate_dummy_plans.py --plans source_data/berlin-v5.2-1pct.plans.xml --center 4595460 5821710 --radius 20000`
 - Generate the IEPOS file`python generate_iepos_files.py --network input/evacuation_network.xml --plans input/dummy_plans.xml --center 4595460 5821710 --radius 20000`

## CONTACT

For inquiries, please contact Fadhil Ginting(gintingf@student.ethz.ch), Jordan Burklund (@student.ethz.ch)

