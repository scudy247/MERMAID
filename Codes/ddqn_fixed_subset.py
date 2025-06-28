import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from itertools import combinations
import random
from collections import deque

# Set random seed for reproducibility
np.random.seed(42)
torch.manual_seed(42)

class QNetwork(nn.Module):
    def __init__(self, input_dim, output_dim):
        super(QNetwork, self).__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.ReLU(),
            nn.Linear(128, 128),
            nn.ReLU(),
            nn.Linear(128, output_dim)
        )
    
    def forward(self, x):
        return self.net(x)

class DDQNAgent:
    def __init__(self, num_arms, subset_size, lr=1e-3, gamma=0.99, epsilon=1.0, epsilon_decay=0.995, epsilon_min=0.05):
        self.num_arms = num_arms
        self.subset_size = subset_size
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        
        self.action_list = list(combinations(range(num_arms), subset_size))
        self.action_size = len(self.action_list)

        self.q_net = QNetwork(input_dim=1, output_dim=self.action_size)
        self.target_net = QNetwork(input_dim=1, output_dim=self.action_size)
        self.target_net.load_state_dict(self.q_net.state_dict())
        self.optimizer = optim.Adam(self.q_net.parameters(), lr=lr)

        self.memory = deque(maxlen=10000)
        self.batch_size = 64
        self.update_target_every = 20
        self.train_step = 0

    def select_action(self, state):
        if np.random.rand() < self.epsilon:
            return random.randrange(self.action_size)
        state_tensor = torch.tensor([[state]], dtype=torch.float32)
        with torch.no_grad():
            q_values = self.q_net(state_tensor)
        return q_values.argmax().item()
    
    def remember(self, state, action, reward, next_state):
        self.memory.append((state, action, reward, next_state))
    
    def replay(self):
        if len(self.memory) < self.batch_size:
            return
        
        minibatch = random.sample(self.memory, self.batch_size)
        states, actions, rewards, next_states = zip(*minibatch)

        states = torch.tensor(states, dtype=torch.float32).unsqueeze(1)
        next_states = torch.tensor(next_states, dtype=torch.float32).unsqueeze(1)
        actions = torch.tensor(actions, dtype=torch.int64)
        rewards = torch.tensor(rewards, dtype=torch.float32)

        q_values = self.q_net(states)
        next_q_values = self.q_net(next_states)
        next_q_target = self.target_net(next_states)

        best_actions = next_q_values.argmax(dim=1)
        targets = rewards + self.gamma * next_q_target.gather(1, best_actions.unsqueeze(1)).squeeze()

        q_action = q_values.gather(1, actions.unsqueeze(1)).squeeze()

        loss = nn.MSELoss()(q_action, targets.detach())
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        self.train_step += 1
        if self.train_step % self.update_target_every == 0:
            self.target_net.load_state_dict(self.q_net.state_dict())
        
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def get_action_arms(self, action_index):
        return self.action_list[action_index]

# Example usage
if __name__ == "__main__":
    num_arms = 10
    subset_size = 3
    rounds = 200

    agent = DDQNAgent(num_arms=num_arms, subset_size=subset_size)
    true_rewards = np.random.rand(num_arms)

    for t in range(rounds):
        state = 0  # dummy state (can use timestep or a feature later)
        action_index = agent.select_action(state)
        selected_arms = agent.get_action_arms(action_index)
        received_rewards = np.random.binomial(1, true_rewards[list(selected_arms)])
        reward = sum(received_rewards)

        next_state = state + 1
        agent.remember(state, action_index, reward, next_state)
        agent.replay()

        if t % 20 == 0:
            print(f"Step {t}, Chosen arms: {selected_arms}, Reward: {reward}")
