clear
close all

%% ------- COLLECTING DATA -------

mermaid_data = readmatrix('Combinatorial_MAB\pdr_cmab.xlsx','Range','B2:B1002');
ddqn_data = readmatrix('DDQN\pdr_ddqn.xlsx','Range','B2:B1002');
ppo_data = readmatrix('PPO\pdr_ppo.xlsx','Range','B2:B1002');

mermaid_energy_data = readmatrix('Combinatorial_MAB\energy_cmab.xlsx','Range','B2:B1002');
ddqn_energy_data = readmatrix('DDQN\energy_ddqn.xlsx','Range','B2:B1002');
ppo_energy_data = readmatrix('PPO\energy_ppo.xlsx','Range','B2:B1002');

mermaid_pdr = mean(mermaid_data, 'omitnan');
ddqn_pdr = mean(ddqn_data, 'omitnan');
ppo_pdr = mean(ppo_data, 'omitnan');

mermaid_energy = mean(mermaid_energy_data, 'omitnan');
ddqn_energy = mean(ddqn_energy_data, 'omitnan');
ppo_energy = mean(ppo_energy_data, 'omitnan');

max_pdr = max([mermaid_data(:); ddqn_data(:); ppo_data(:)], [], 'omitnan');
max_energy = max([mermaid_energy_data(:); ddqn_energy_data(:); ppo_energy_data(:)], [], 'omitnan');

%% ------- DEFINITION OF SOME VARIABLES -------
total_packets = 40;

delivered_mermaid = total_packets * mermaid_pdr / 100;
delivered_ddqn = total_packets * ddqn_pdr / 100;
delivered_ppo = total_packets * ppo_pdr / 100;

energy_per_pkt_mermaid = mermaid_energy / delivered_mermaid;
energy_per_pkt_ddqn = ddqn_energy / delivered_ddqn;
energy_per_pkt_ppo = ppo_energy / delivered_ppo;

energy_pkt_values = [energy_per_pkt_mermaid, energy_per_pkt_ddqn, energy_per_pkt_ppo];

episodes = 1:length(mermaid_data);

%% ------- PLOTTING DATA -------

bar_colors = [
    0.8500 0.3250 0.0980;  % MERMAID - dark orange
    0.4660 0.6740 0.1880;  % DDQN - olive green
    0.0000 0.4470 0.7410]; % PPO - dark blue

labels = {'MERMAID', 'DDQN', 'PPO'};

% ----------- AVERAGE PDR -----------
mean_values = [mermaid_pdr, ddqn_pdr, ppo_pdr];
hatch_angles = [45, 0, 90];

num_bars = numel(mean_values);

scale = 0.1;
spacing = scale * mean_values;
spacing = spacing / max(spacing);
spacing = spacing + 1;
x_pos = cumsum([0, spacing(1:end-1)]);

x_pos = x_pos - min(x_pos) + 1;

h4 = figure('NumberTitle', 'off', 'Name', 'Average PDR');
hold on;
set(gcf, 'Color', 'w');

set(gca, 'XTick', x_pos, 'XTickLabel', labels, 'FontSize', 14);
xlabel('Approach', 'FontSize', 16, 'FontWeight', 'bold');
ylabel('Average Packet Delivery Ratio [%]', 'FontSize', 16, 'FontWeight', 'bold');
ylim([0, ceil(max([mean_values, max_pdr]) + 5)]);
box on;

bar_handles = gobjects(1, num_bars);
for k = 1:num_bars
    bar_handles(k) = bar(x_pos(k), mean_values(k), ...
        'FaceColor', bar_colors(k,:), ...
        'EdgeColor', 'k', ...
        'LineWidth', 1.2, ...
        'BarWidth', 0.6);
end

drawnow;

for k = 1:num_bars
    hatchfill2(bar_handles(k), ...
        'HatchStyle', 'single', ...
        'HatchAngle', hatch_angles(k), ...
        'HatchColor', [0 0 0], ...
        'HatchLineWidth', 1.2);
end

for k = 1:num_bars
    text(x_pos(k), mean_values(k) + 0.5, ...
        sprintf('%.2f%%', mean_values(k)), ...
        'HorizontalAlignment', 'center', ...
        'VerticalAlignment', 'bottom', ...
        'FontSize', 13, ...
        'FontWeight', 'bold', ...
        'Color', 'k');
end

exportgraphics(h4, "Average_PDR.pdf");

% ----------- CUMULATIVE REWARD -----------
window_size = 20;

mermaid_reward = movmean(mermaid_data, window_size, 'omitnan');
ddqn_reward = movmean(ddqn_data, window_size, 'omitnan');
ppo_reward = movmean(ppo_data, window_size, 'omitnan');

step = 20;
marker_indices = 1:step:length(episodes);

h9 = figure('NumberTitle', 'off', 'Name', 'Cumulative Reward');

plot(episodes, mermaid_reward, '-', 'Color', bar_colors(1,:), 'LineWidth', 1.25, ...
    'Marker', '*', 'MarkerIndices', marker_indices, 'MarkerSize', 4);
hold on;
plot(episodes, ddqn_reward, '-', 'Color', bar_colors(2,:), 'LineWidth', 1.25, ...
    'Marker', 's', 'MarkerIndices', marker_indices, 'MarkerSize', 4);
plot(episodes, ppo_reward, '-', 'Color', bar_colors(3,:), 'LineWidth', 1.25, ...
    'Marker', 'o', 'MarkerIndices', marker_indices, 'MarkerSize', 4);

xlabel('Episode', 'FontSize', 15, 'FontWeight', 'bold');
ylabel('Cumulative Reward', 'FontSize', 15, 'FontWeight', 'bold');

xlim([0, max(episodes)+1]);
ylim([0 60]);

legend({'MERMAID', 'DDQN', 'PPO'}, 'FontSize', 10, 'Location', 'northwest');
set(gca, 'FontSize', 13);
box on;
set(gcf, 'Color', 'w');

exportgraphics(h9, 'Cumulative_Reward.pdf');

% ----------- ENERGY PER PACKET -----------
hatch_angles = [45, 0, 90];
num_bars = numel(energy_pkt_values);

scale = 0.1;
spacing = scale * energy_pkt_values;
spacing = spacing / max(spacing);
spacing = spacing + 1;
x_pos = cumsum([0, spacing(1:end-1)]);
x_pos = x_pos - min(x_pos) + 1;

h8 = figure('NumberTitle', 'off', 'Name', 'Energy per Delivered Packet');
hold on;
set(gcf, 'Color', 'w');

set(gca, 'XTick', x_pos, 'XTickLabel', labels, 'FontSize', 14);
xlabel('Approach', 'FontSize', 16, 'FontWeight', 'bold');
ylabel('Energy per Delivered Packet [J/pkt]', 'FontSize', 16, 'FontWeight', 'bold');
ylim([0, ceil(max(energy_pkt_values) * 1.1 * 100) / 100]);
box on;

bar_handles = gobjects(1, num_bars);
for k = 1:num_bars
    bar_handles(k) = bar(x_pos(k), energy_pkt_values(k), ...
        'FaceColor', bar_colors(k,:), ...
        'EdgeColor', 'k', ...
        'LineWidth', 1.2, ...
        'BarWidth', 0.6);
end

drawnow;

for k = 1:num_bars
    hatchfill2(bar_handles(k), ...
        'HatchStyle', 'single', ...
        'HatchAngle', hatch_angles(k), ...
        'HatchColor', [0 0 0], ...
        'HatchLineWidth', 1.2);
end

for k = 1:num_bars
    text(x_pos(k), energy_pkt_values(k) + 0.01, ...
        sprintf('%.2f', energy_pkt_values(k)), ...
        'HorizontalAlignment', 'center', ...
        'VerticalAlignment', 'bottom', ...
        'FontSize', 13, ...
        'FontWeight', 'bold', ...
        'Color', 'k');
end

title('Energy per Delivered Packet', 'FontSize', 16, 'FontWeight', 'bold');

exportgraphics(h8, "Energy_per_packet.pdf");