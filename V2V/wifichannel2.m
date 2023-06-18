% Parameters
fc = 2.4e9; % Carrier frequency (Hz)
c = 3e8; % Speed of light (m/s)
lambda = c/fc; % Wavelength (m)
Pt = 10; % Transmit power (dBm)
Gt = 1; % Transmit antenna gain (dBi)
Gr = 1; % Receive antenna gain (dBi)
L = 5; % System loss factor (dB)
N = 100; % Number of subcarriers
BW = 20e6; % Bandwidth (Hz)
T = 1/BW; % Symbol time (s)
fs = BW*N; % Sampling frequency (Hz)
t_step = 0.1; % Time step (s)
t_sim = t_step * 180; % Simulation time (s)
num_steps = round(t_sim/t_step); % Number of time steps

% Update distance range and step size
d_min = 2;
d_max = 10;
d_step = (d_max - d_min) / (num_steps - 1);
d_range = d_min:d_step:d_max;

% Initialize variables
throughput = zeros(1, num_steps);
distance = zeros(1, num_steps);
d_idx = 1; % Index for distance range
d = d_range(d_idx); % Initial distance

for i = 1:num_steps
    
    % Update distance
    d = d_range(d_idx); % Get current distance
    
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
    SNR_threshold = 20; % SNR threshold for outage (dB)
    outage_prob = 1 - mean(SNR > 10^(0.1*SNR_threshold));
    
    % Calculate achievable rate using Shannon capacity formula
    M = 16; % Modulation order
    R = 2/3; % Coding rate
    C = BW*R*log2(1 + SNR)/log2(M);
    
    % Calculate average throughput accounting for outage probability
    throughput(i) = mean(C.*(1 - outage_prob));
    
    % Save distance and time
    distance(i) = d;
    t_axis(i) = i*t_step;
    
    % Update distance index
    if mod(i, length(d_range)) == 0
        d_idx = 1;
    else
        d_idx = d_idx + 1;
    end
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
