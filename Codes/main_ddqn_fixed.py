import csv
import wandb
import subprocess
import numpy as np
from ddqn_fixed_subset import DDQNAgent  

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
            tags = ["ddqn", f"subset{subset_size}"],
            name = f"ddqn_subset_{subset_size}",
            reinit = True)

    agent = DDQNAgent(num_arms=8, subset_size=subset_size)
    n_episode = 0
    n_max_episodes = 1000

    while n_episode < (n_max_episodes+1):
        cumulative_reward = 0
        throughput_list = []

        state = 0  # dummy state
        action_index = agent.select_action(state)
        actions = agent.get_action_arms(action_index)

        # Initialize an array of 8 carriers, always select index 0
        carriers = np.zeros(8, dtype=int)
        carriers[np.array(actions)] = 1

        run_simulation(carriers=carriers)

        with open('rewards.csv') as rewards_file_check:
            rewards_reader_check = csv.reader(rewards_file_check)
            row = next(rewards_reader_check)
            pdr = float(row[0])
            energy = float(row[1])

            if log_wandb:
                for i, arm in enumerate(actions):
                    wandb.log({f"action{i}": arm + 1}, commit=False)  # +1 per uniformità con MAB
                wandb.log({"pdr": pdr, "reward": pdr, "energy": energy}, commit=True)


            # Each arm gets the same reward (or you could load arm-specific if available)
            received_rewards = [pdr for _ in actions]
            reward = sum(received_rewards)

            next_state = state + 1  # dummy progression
            agent.remember(state, action_index, reward, next_state)
            agent.replay()


        print(f"Episode {n_episode} finished with reward {pdr}")
        n_episode += 1
