# Fab OpenVLC Roadmap

This roadmap identifies practical improvements that can make Fab OpenVLC easier to reproduce, extend, and use in research. It is not a fixed release commitment; proposals and pull requests are welcome.

## Priority 1: Reproducible setup

- Document tested operating-system, kernel, OpenVLC, Fabric, Python, hostapd, iperf, and WiFi-driver versions.
- Add a hardware compatibility matrix for BeagleBone Black boards and USB WiFi adapters.
- Provide pre-flight scripts that validate dependencies, interfaces, addresses, and permissions.
- Separate required files from archived testbed snapshots and third-party source trees.
- Add a minimal end-to-end quick-start path.

## Priority 2: Experiment quality

- Publish small example traces for VLC quality, WiFi RSSI, throughput, and handover events.
- Standardize experiment metadata and filenames.
- Add scripts that reproduce the main plots from raw data.
- Define baseline scenarios, metrics, and expected output.
- Document timing, synchronization, and measurement limitations.

## Priority 3: Controller extensibility

- Separate testbed configuration from controller logic.
- Define a clear interface for adding new handover policies.
- Add structured logging for decisions and link transitions.
- Add simulation or mock inputs so controller logic can be tested without hardware.
- Explore additional link-quality and context-aware decision strategies.

## Priority 4: Community and maintenance

- Label beginner-friendly and research-oriented issues.
- Add release notes and versioned testbed configurations.
- Improve architecture diagrams and module-level documentation.
- Add contribution examples for documentation, hardware testing, and algorithms.
- Track known hardware and software limitations openly.

## Suggested contribution projects

1. **Hardware compatibility report** — reproduce the setup with another WiFi adapter and document results.
2. **One-command diagnostics** — create a script that checks interfaces, drivers, services, and connectivity.
3. **Mock controller test** — replay recorded channel measurements without a physical testbed.
4. **Experiment bundle** — contribute raw data, metadata, analysis code, and a reproducible figure.
5. **Modernized controller** — isolate configuration and update dependency assumptions while preserving behavior.

Open an issue before beginning a large change so the scope and validation method can be discussed.