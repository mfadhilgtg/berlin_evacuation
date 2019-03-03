# 1% Network Statistics
mean node location:   (4597361.76, 5812272.12)
median node location: (4596113.67, 5817409.35) 
Selected center location: (4595460 5821710)
Selected radius: 25000 km (93 exit nodes)
20000 km radius gives 

Not all links are roads. Some are public transport only.

# Running the network configurator
python3 configure_network.py --network ./source_data/berlin-v5.0.network.xml --center 4595460 5821710 --radius 20000
TODO task
Should probably have a "source_data" folder and a "input" folder that somehow manages downloading the correct data.
