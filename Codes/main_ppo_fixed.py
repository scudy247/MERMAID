import csv
import wandb
import subprocess
import numpy as np
from ppo_fixed_subset import PPOAgent

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

# Loop over different subset sizes
for subset_size in [3, 4, 5, 6, 7, 8]:

    if log_wandb:
        wandb.init(
            project="combinatorial_ucb",
            tags=["ppo", f"subset{subset_size}"],
            name=f"ppo_subset_{subset_size}",
            reinit=True
        )

    agent = PPOAgent(num_arms=8, subset_size=subset_size)

    n_episode = 0
    n_max_episodes = 1000

    while n_episode <= n_max_episodes:
        state = 0
        action_index, log_prob = agent.select_action(state)
        actions = agent.get_action_arms(action_index)

        carriers = np.zeros(8, dtype=int)
        carriers[np.array(actions)] = 1

        run_simulation(carriers=carriers)

        with open('rewards.csv') as rewards_file_check:
            rewards_reader_check = csv.reader(rewards_file_check)
            row = next(rewards_reader_check)
            pdr = float(row[0])
            energy = float(row[1])

        reward = sum([pdr for _ in actions])
        next_state = state + 1

        agent.store_transition(state, action_index, log_prob, reward, next_state)
        agent.finish_episode()

        if log_wandb:
            log_data = {
                "pdr": pdr,
                "reward": reward,
                "energy": energy
            }
            for i, arm in enumerate(actions):
                log_data[f"action{i}"] = arm + 1
            wandb.log(log_data)

        print(f"Episode {n_episode} finished with reward {pdr}")
        n_episode += 1
