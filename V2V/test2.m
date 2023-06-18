% WiFi simulation scenarios
% Shows the relationship between distance and throughput

% Define simulation parameters
d_max = 50; % maximum distance between WiFi devices (meters)
d_step = 1; % distance step size (meters)
N = 10; % number of simulations at each distance
tx_rate = 54; % WiFi transmission rate (Mbps)

% Initialize variables
distances = 0:d_step:d_max;
throughputs = zeros(size(distances));

% Simulate WiFi scenarios
for i = 1:length(distances)
    d = distances(i);
    for j = 1:N
        % Assume the signal strength decays according to the inverse square law
        rssi = -40 - 20*log10(d) + randn()*2;
        % Calculate the throughput using the Shannon-Hartley theorem
        throughput = tx_rate * log2(1 + 10^(rssi/10));
        throughputs(i) = throughputs(i) + throughput;
    end
    throughputs(i) = throughputs(i) / N;
end

% Plot the results
plot(distances, throughputs);
xlabel('Distance (m)');
ylabel('Throughput (Mbps)');
title('WiFi Throughput vs Distance');
