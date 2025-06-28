import numpy as np

# fixed number of subset arms, maybe to an analysis after the run for different values of subset.
class CombinatorialUCB:
    def __init__(self, num_arms, subset_size, delta=0.05):
        self.num_arms = num_arms  # Total number of base arms
        self.subset_size = subset_size  # Number of arms selected per round
        self.delta = delta  # Confidence parameter
        self.counts = np.zeros(num_arms)  # Number of times each arm was chosen
        self.rewards = np.zeros(num_arms)  # Total reward of each arm
        self.time_step = 0
    
    def select_arms(self):
        """Selects a subset of arms based on the UCB criterion."""
        self.time_step += 1
        ucb_values = np.zeros(self.num_arms)
        
        for i in range(self.num_arms):
            if self.counts[i] == 0:
                ucb_values[i] = float('inf')  # Encourage initial exploration
            else:
                mean_reward = self.rewards[i] / self.counts[i]
                confidence_bound = np.sqrt((2 * np.log(self.time_step)) / self.counts[i])
                ucb_values[i] = mean_reward + confidence_bound
        
        # Select subset_size arms with the highest UCB values
        selected_arms = np.argsort(ucb_values)[-self.subset_size:]
        return selected_arms
    
    def update(self, chosen_arms, received_rewards):
        """Updates the counts and rewards based on observed outcomes."""
        for arm, reward in zip(chosen_arms, received_rewards):
            self.counts[arm] += 1
            self.rewards[arm] += reward

# Example usage
if __name__ == "__main__":
    num_arms = 10  # Total number of base arms
    subset_size = 3  # Number of arms chosen in each round
    rounds = 100

    bandit = CombinatorialUCB(num_arms, subset_size)
    true_rewards = np.random.rand(num_arms)  # Simulated true reward probabilities
    
    for _ in range(rounds):
        chosen_arms = bandit.select_arms()
        received_rewards = np.random.binomial(1, true_rewards[chosen_arms])  # Simulated binary rewards
        bandit.update(chosen_arms, received_rewards)
    
    print("Final estimated rewards:", bandit.rewards / (bandit.counts + 1e-6))

