#!/bin/bash
for i in {0..49}
	do
		sleep 2
		echo 1, 0 > ~/DESERT_Underwater-master/DESERT_Framework/DESERT/samples/desert_samples/Application/Paper_simulation/RL_mab_uw/synchronization.csv
		ns Simulation.tcl
	done
