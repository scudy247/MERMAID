import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from itertools import combinations
from torch.distributions import Categorical


class PolicyNetwork(nn.Module):
    def __init__(self, input_dim, action_dim):
        super(PolicyNetwork, self).__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, 64),
            nn.Tanh(),
            nn.Linear(64, 64),
            nn.Tanh(),
            nn.Linear(64, action_dim)
        )
        self.apply(self.init_weights)

    def init_weights(self, m):
        if isinstance(m, nn.Linear):
            nn.init.xavier_uniform_(m.weight)
            nn.init.constant_(m.bias, 0.0)

    def forward(self, x):
        return self.net(x)


class ValueNetwork(nn.Module):
    def __init__(self, input_dim):
        super(ValueNetwork, self).__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, 64),
            nn.Tanh(),
            nn.Linear(64, 64),
            nn.Tanh(),
            nn.Linear(64, 1)
        )
        self.apply(self.init_weights)

    def init_weights(self, m):
        if isinstance(m, nn.Linear):
            nn.init.xavier_uniform_(m.weight)
            nn.init.constant_(m.bias, 0.0)

    def forward(self, x):
        return self.net(x)


class PPOAgent:
    def __init__(self, num_arms, subset_size, gamma=0.99, clip_eps=0.2, lr=3e-4):
        self.num_arms = num_arms
        self.subset_size = subset_size
        self.gamma = gamma
        self.clip_eps = clip_eps

        self.action_list = list(combinations(range(num_arms), subset_size))
        self.action_size = len(self.action_list)

        self.policy_net = PolicyNetwork(input_dim=1, action_dim=self.action_size)
        self.value_net = ValueNetwork(input_dim=1)

        self.optimizer_policy = optim.Adam(self.policy_net.parameters(), lr=lr)
        self.optimizer_value = optim.Adam(self.value_net.parameters(), lr=lr)

        self.memory = []

    def select_action(self, state):
        state_tensor = torch.tensor([[state]], dtype=torch.float32)

        with torch.no_grad():
            logits = self.policy_net(state_tensor)

            if torch.isnan(logits).any():
                print("❌ NaN in logits! Replacing with zeros.")
                logits = torch.zeros_like(logits)

            logits = torch.clamp(logits, -10, 10)

            probs = torch.softmax(logits, dim=-1)
            probs = torch.clamp(probs, min=1e-6, max=1.0)

            if torch.isnan(probs).any() or not torch.isfinite(probs).all():
                print("❌ NaN/Inf in probs! Replacing with uniform distribution.")
                probs = torch.ones_like(probs) / probs.size(-1)

        dist = Categorical(probs)
        action = dist.sample()
        log_prob = dist.log_prob(action)
        return action.item(), log_prob.item()

    def get_action_arms(self, action_index):
        return self.action_list[action_index]

    def store_transition(self, state, action, log_prob, reward, next_state):
        self.memory.append((state, action, log_prob, reward, next_state))

    def finish_episode(self):
        if not self.memory:
            return

        states, actions, old_log_probs, rewards, next_states = zip(*self.memory)

        returns = []
        G = 0
        for r in reversed(rewards):
            G = r + self.gamma * G
            returns.insert(0, G)
        returns = torch.tensor(returns, dtype=torch.float32).unsqueeze(1)

        if returns.numel() > 1 and returns.std() > 1e-6:
            returns = (returns - returns.mean()) / (returns.std() + 1e-6)
        else:
            returns = returns - returns.mean()


        states_tensor = torch.tensor(states, dtype=torch.float32).unsqueeze(1)
        actions_tensor = torch.tensor(actions, dtype=torch.int64).unsqueeze(1)
        old_log_probs_tensor = torch.tensor(old_log_probs, dtype=torch.float32).unsqueeze(1)

        logits = self.policy_net(states_tensor)
        logits = torch.clamp(logits, -10, 10)
        probs = torch.softmax(logits, dim=-1)
        probs = torch.clamp(probs, min=1e-6, max=1.0)

        dist = Categorical(probs)
        new_log_probs = dist.log_prob(actions_tensor.squeeze()).unsqueeze(1)

        values = self.value_net(states_tensor)
        advantages = returns - values.detach()

        ratio = torch.exp(new_log_probs - old_log_probs_tensor)
        clipped_ratio = torch.clamp(ratio, 1 - self.clip_eps, 1 + self.clip_eps)
        policy_loss = -torch.min(ratio * advantages, clipped_ratio * advantages).mean()

        self.optimizer_policy.zero_grad()
        policy_loss.backward()
        self.optimizer_policy.step()

        value_loss = nn.MSELoss()(values, returns)
        self.optimizer_value.zero_grad()
        value_loss.backward()
        self.optimizer_value.step()

        self.memory.clear()