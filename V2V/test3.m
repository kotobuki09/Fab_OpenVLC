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
t = (0:T:(N-1)*T).'; % Time vector
M = 16; % Modulation order
R = 2/3; % Coding rate
SNR_threshold = 20; % SNR threshold for outage (dB)

% Initialize variables
dl=[20	20	20	20	19	18	17	16	15	15	15	15	15	15	16	17	18	19	20	20	20	20	20	20	21	22	23	24	25	25	25	25	25	25	25	25	24	23	22	22	22	22	22	22	22	23	24	25	26	27	27	27	27	27	27	27	27	27	26	25	24	23	22	21	20	19	19	19	19	19	19	19	19	19	19	19	18	17	16	15	14	14	14	14	14	14	14	15	16	17	18	19	19	19	19	19	19	19	19	19	19	18	17	16	15	14	14	14	14	14	14	15	16	17	18	19	20	21	22	22	22	22	22	22	22	22	23	24	25	25	25	25	25	25	25	25	26	27	28	29	29	29	29	29	29	29	29	28	27	26	25	24	24	24	24	24	24	24	24	23	22	21	20	20	20	20	20	20	20	20	21	22	23	23	23	23	23	23	23	23];

t_sim = length(dl)*10; % Simulation time (s)
t_step = 10; % Time step (s)
num_steps = round(t_sim/t_step); % Number of time steps
throughput = zeros(1, num_steps);
distance = zeros(1, num_steps);
d_range = dl;

% Main loop
d_idx = 1; % Index for distance range
d_change_step = 1; % Steps between distance changes
d_change_counter = d_change_step; % Counter for distance changes
d = d_range(d_idx); % Initial distance

for i = 1:num_steps
    % Change distance every d_change_step steps
    if d_change_counter == d_change_step
        d_idx = d_idx + 1; % Update distance index
        if d_idx > length(d_range)
            d_idx = 1;
        end
        d = d_range(d_idx); % Update distance
        d_change_counter = 0; % Reset distance change counter
    end
    d_change_counter = d_change_counter + 1; % Increment distance change counter
    
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
    t_axis(i) = (i*t_step)*0.1;
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
