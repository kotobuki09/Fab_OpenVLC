# Contributing to Fab OpenVLC

Thank you for helping improve Fab OpenVLC. Contributions that make the hybrid VLC/WiFi testbed easier to reproduce, understand, test, or extend are especially welcome.

## Ways to contribute

You can help by:

- improving installation and troubleshooting documentation;
- testing additional WiFi adapters, Linux images, or BeagleBone Black configurations;
- reporting reproducible bugs with logs and hardware details;
- adding scripts that simplify setup, measurement, or experiment automation;
- improving handover policies, monitoring, visualization, or evaluation;
- contributing sample datasets, experiment traces, and reproducible results;
- reviewing open issues and pull requests.

## Before opening an issue

1. Read the main `README.md` and confirm that the documented setup steps were followed.
2. Search existing issues to avoid duplicates.
3. Remove passwords, private IP information, access tokens, and other sensitive data from logs.
4. Prepare the hardware, operating-system, driver, and dependency versions used in the testbed.

## Reporting a bug

A useful report should include:

- a short description of the expected and actual behavior;
- exact reproduction steps;
- BeagleBone Black model and operating-system image;
- OpenVLC version or commit;
- WiFi adapter model and driver version;
- relevant `fab`, `iperf`, kernel, hostapd, and controller logs;
- screenshots or plots when they clarify the problem.

## Proposing an enhancement

Describe the research or engineering problem, the proposed change, expected benefits, compatibility considerations, and how the result could be evaluated.

## Pull-request workflow

1. Fork the repository or create a feature branch.
2. Keep each pull request focused on one change.
3. Use clear commit messages.
4. Update documentation whenever setup, commands, hardware assumptions, or behavior changes.
5. Include tests, logs, or experiment evidence appropriate to the change.
6. Explain any hardware-only validation that maintainers must perform.
7. Link the related issue in the pull-request description.

Suggested branch names:

- `docs/<topic>`
- `fix/<problem>`
- `feature/<capability>`
- `experiment/<study>`

## Reproducibility checklist

For experiment-related contributions, provide as many of the following as possible:

- hardware topology and component versions;
- operating-system and kernel versions;
- dependency and driver versions;
- configuration files or a minimal configuration diff;
- commands used to start the VLC, WiFi, traffic, and controller components;
- raw or minimally processed measurements;
- analysis or plotting scripts;
- expected output and acceptance criteria;
- known limitations and sources of variability.

## Documentation style

Use concise Markdown, copy-pasteable commands, descriptive headings, and relative links to repository files. Define acronyms on first use and distinguish clearly between transmitter, receiver, and control-unit commands.

## Good first contributions

New contributors can begin with documentation corrections, hardware compatibility reports, log-sanitization examples, setup checks, plotting improvements, or minimal reproducibility scripts. Look for issues labeled `good first issue` or `help wanted`.

## Community expectations

Be respectful, constructive, and research-focused. Critique ideas and implementations rather than people, and give credit for prior work, test results, and external dependencies.