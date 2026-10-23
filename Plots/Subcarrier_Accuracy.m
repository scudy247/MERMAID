clear
close all

target_combination = [3, 5, 8];
num_episodes = 1000;

mermaid_actions = read_actions('Combinatorial_MAB');
ddqn_actions    = read_actions('DDQN');
ppo_actions     = read_actions('PPO');

scores_mermaid = compute_accuracy(mermaid_actions, target_combination);
scores_ddqn    = compute_accuracy(ddqn_actions, target_combination);
scores_ppo     = compute_accuracy(ppo_actions, target_combination);

raw_data = [
    sum(scores_mermaid == 0), sum(scores_ddqn == 0), sum(scores_ppo == 0);
    sum(scores_mermaid == 1), sum(scores_ddqn == 1), sum(scores_ppo == 1);
    sum(scores_mermaid == 2), sum(scores_ddqn == 2), sum(scores_ppo == 2);
    sum(scores_mermaid == 3), sum(scores_ddqn == 3), sum(scores_ppo == 3);
];

percent_data = raw_data / num_episodes * 100;

table_data = arrayfun(@(x) sprintf('     %.1f%%     ', x), percent_data, 'UniformOutput', false);

row_names = {'0 correct', '1 correct', '2 correct', '3 correct'};

h = figure('NumberTitle', 'off', 'Name', 'Accuracy Table');
t = uitable('Data', table_data, ...
        'ColumnName', {'MERMAID', 'DDQN', 'PPO'}, ...
        'RowName', row_names, ...
        'Units', 'normalized', ...
        'Position', [0, 0, 1, 1], ...
        'FontSize', 13, ...
        'FontName', 'Times New Roman', ...
        'FontWeight', 'bold', ...
        'ColumnWidth', {100});

fig_width = 600;
fig_height = 300;

table_width = 500;
table_height = 150;

set(t, 'Units', 'pixels');

left = (fig_width - table_width) / 2;
bottom = (fig_height - table_height) / 2;

set(t, 'Position', [left bottom table_width table_height]);

print(h, 'Accuracy_Table.png', '-dpng', '-r300');

function actions = read_actions(base_path)
    a0 = readmatrix(fullfile(base_path, 'action0.xlsx'), 'Range', 'B2:B1001');
    a1 = readmatrix(fullfile(base_path, 'action1.xlsx'), 'Range', 'B2:B1001');
    a2 = readmatrix(fullfile(base_path, 'action2.xlsx'), 'Range', 'B2:B1001');
    actions = [a0, a1, a2];
end

function scores = compute_accuracy(actions, target)
    scores = zeros(size(actions,1), 1);
    for i = 1:length(scores)
        scores(i) = sum(ismember(actions(i,:), target));
    end
end
