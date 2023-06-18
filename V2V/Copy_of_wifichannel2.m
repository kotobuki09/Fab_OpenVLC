% Parameters
fc = 2.4e9; % Carrier frequency (Hz)
c = 3e8; % Speed of light (m/s)
lambda = c/fc; % Wavelength (m)
Pt = 0.5; % Transmit power (dBm)
Gt = 1; % Transmit antenna gain (dBi)
Gr = 1; % Receive antenna gain (dBi)
L = 5; % System loss factor (dB)
N = 100; % Number of subcarriers
BW = 5e6; % Bandwidth (Hz)
T = 1/BW; % Symbol time (s)
fs = BW*N; % Sampling frequency (Hz)
t_step = T; % Time step (s)
t_sim = t_step*length(d_list); % Simulation time (s)
num_steps = length(d_list); % Number of time steps
M = 4; % Modulation order
R = 1/2; % Coding rate
SNR_threshold = 20; % SNR threshold for outage (dB)

% Initialize variables
d_idx = 1; % Index for current distance
d_list = [20 20 20 20 19 18 17 16 15 15 15 15 15 15 16 17 18 19 20 20 20 20 20 20 21 22 23 24 25 25 25 25 25 25 25 25 24 23 22 22 22 22 22 22 22 23 24 25 26 27 27 27 27 27 27 27 27 27 26 25 24 23 22 21 20 19 19 19 19 19 19 19 19 19 19 18 17 16 15 14 14 14 14 14 14 14 15 16 17 18 19 19 19 19 19 19 19 19 19 18 17 16 15 14 14 14 14 14 14 15 16 17 18 19 20 21 22 22 22 22 22 22 22 22 23 24 25 25 25 25 25 25 25 25 26 27 28 29 29 29 29 29 29 29 29 28 27 26 25 24 24 24 24 24 24 24 24 23 22 21 20 20 20 20 20 20 20 20 21 22 23 23 23 23 23 23 23];
d = d_list(d_idx); % Initial distance

throughput = zeros(1, num_steps);
distance = zeros(1, num_steps);
time_axis = zeros(1, num_steps);

for i = 1:num_steps
    % Check if distance needs to be changed
    if i > 1 && mod(i-1, d_change_step) == 0
        d_idx = d_idx + 1;
        if d_idx > length(d_list)
            break;
        end
        d = d_list(d_idx);
    end
    
    % Calculate path loss
    PL = 20*log10(4*pi*d/lambda) + L;
    
    % Calculate received power
    Pr = 1e-3*10.^(0.1*(Pt + Gt + Gr - PL));
    
    % Calculate noise power
    N0 = 1e-20;
    noise_power = N0*BW;
    
    % Generate fading coefficients
    H = sqrt(1/2)*(randn(N, 1) + 1j*randn(N, 1));
    
    % Calculate SNR
    SNR = abs(H).^2.*Pr./(N*noise_power);
    
    % Calculate outage probability
    outage_prob = 1 - mean(SNR > 10^(0.1*SNR_threshold));
    
    % Calculate achievable rate using Shannon capacity formula
    C = BW*R*log2(1 + SNR);
    
    % Calculate average throughput accounting for outage probability
    throughput(i) = mean(C.*(1 - outage_prob));
    
    % Save distance and time
    distance(i) = d;
    time_axis(i) = i*t_step;
end

% Plot throughput as a function of time
subplot(2,1,1);
plot(t_axis, throughput/1e6)
title('Throughput as a function of time')
xlabel('Time (s)')
ylabel('Throughput (Mbps)')

% Plot distance as a function of time
subplot(2,1,2);
plot(t_axis, distance)
title('Distance as a function of time')
xlabel('Time (s)')
ylabel('Distance (m)')