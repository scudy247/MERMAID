#!/bin/bash
for i in {0..4}
	do
		ns mySimulation.tcl 15 "expLog.csv" 3 "BPSK" 1 1536 1 0 1 0 0 0 0 1 1
	done

