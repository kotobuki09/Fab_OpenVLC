% Parameters
fc = 2.4e9; % Carrier frequency (Hz)
c = 3e8; % Speed of light (m/s)
lambda = c/fc; % Wavelength (m)
d = 1:0.1:30; % Distance (m)
Pt = 4; % Transmit power (dBm)
Gt = 1; % Transmit antenna gain (dBi)
Gr = 1; % Receive antenna gain (dBi)
L = 5; % System loss factor (dB)
N = 100; % Number of subcarriers
T = 1/20e6; % Symbol time (s)
fs = N*20e6; % Sampling frequency (Hz)
t = (0:T:(N-1)*T).'; % Time vector
M = 16; % Modulation order
R = 2/3; % Coding rate
SNR_threshold = 20; % SNR threshold for outage (dB)
max_data_rate = 20e6; % Maximum data rate (bps)

% Calculate path loss
PL = 20*log10(4*pi*d/lambda) + L;

% Generate fading coefficients
H = sqrt(1/2)*(randn(N,length(d)) + 1j*randn(N,length(d)));

% Calculate received power and noise power
Pr = 1e-3*10.^(0.1*(Pt + Gt + Gr - PL)); % Received power (W)
N0 = 1e-20; % Noise power spectral density (W/Hz)
noise_power = N0*20e6; % Noise power (W)

% Calculate SNR
SNR = abs(H).^2.*repmat(Pr./(N*noise_power),N,1);

% Calculate outage probability
outage_prob = 1 - mean(SNR > 10^(0.1*SNR_threshold),1);

% Calculate achievable rate using Shannon capacity formula
C = fs*R*log2(1 + SNR);

% Limit achievable rate to max_data_rate
C(C > max_data_rate) = max_data_rate;

% Calculate average throughput accounting for outage probability
throughput = mean(C.*(1 - outage_prob),1);

% Plot CSI as a function of distance
figure;
plot(d.', abs(squeeze(H(50,:)).'))
title('Channel State Information (CSI) as a function of distance')
xlabel('Distance (m)')
ylabel('CSI')

% Plot throughput as a function of distance
figure;
plot(d, throughput/1e6)
title('Throughput as a function of distance')
xlabel('Distance (m)')
ylabel('Throughput (Mbps)')
