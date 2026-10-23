import csv
from itertools import combinations
from combinatorial_fixed_subset import CombinatorialUCB
import wandb
import subprocess
import numpy as np

log_wandb = True

def run_simulation(carriers):
    command = [
        "ns",
        "newSimulation.tcl",
        f"{carriers[0]}",
        f"{carriers[1]}",
        f"{carriers[2]}",
        f"{carriers[3]}",
        f"{carriers[4]}",
        f"{carriers[5]}",
        f"{carriers[6]}",
        f"{carriers[7]}",
    ]
    
    try:
        subprocess.run(command, check=True)
        print(f"Simulation launched successfully with carriers {carriers}")
    except subprocess.CalledProcessError as e:
        print(f"Error running simulation: {e}")
    except FileNotFoundError:
        print("Error: 'ns' command not found. Make sure NS-2 is installed and in your PATH")

for subset_size in [3, 4, 5, 6, 7, 8]:

    if log_wandb:
        wandb.init(
            project="combinatorial_ucb",
            entity="uwa",
            tags = ["combinatorial_ucb_subset", f"subset{subset_size}"],
            name = f"combinatorial_ucb_subset_{subset_size}",
            reinit = True)

    agent = CombinatorialUCB(num_arms=8, subset_size=subset_size)  

    all_combinations = list(combinations(range(8), subset_size))
    print(f"Exploring all {len(all_combinations)} combinations for subset size {subset_size}")
    for actions in all_combinations:
        carriers = np.zeros(8, dtype=int)
        carriers[list(actions)] = 1
        run_simulation(carriers=carriers)

        with open('rewards.csv') as rewards_file_check:
            rewards_reader_check = csv.reader(rewards_file_check)
            row = next(rewards_reader_check)
            pdr = float(row[0])
            energy = float(row[1])

        if log_wandb:
            for i, action in enumerate(actions):
                wandb.log({f"action{i}": action + 1}, commit=False)  # +1 to use 1-based carrier indices
            wandb.log({"pdr": pdr, "reward": pdr, "energy": energy}, commit=True)

        received_rewards = [pdr for _ in range(len(actions))]
        agent.update(actions, received_rewards)

    n_episode = 0
    n_max_episodes = 1000

    while(n_episode < (n_max_episodes-len(all_combinations)+1)):
        actions = agent.select_arms()
        carriers = np.zeros(8, dtype=int)
        carriers[actions] = 1

        run_simulation(carriers=carriers)

        with open('rewards.csv') as rewards_file_check:
            rewards_reader_check = csv.reader(rewards_file_check)
            row = next(rewards_reader_check)
            pdr = float(row[0])
            energy = float(row[1])

        if log_wandb:
            for i, action in enumerate(actions):
                wandb.log({f"action{i}": action + 1}, commit=False)
            wandb.log({"pdr": pdr, "reward": pdr, "energy": energy}, commit=True)

        received_rewards = [pdr for _ in range(len(actions))]
        agent.update(actions, received_rewards)

        print(f"Episode {n_episode} finished with reward {pdr}")
        n_episode += 1
