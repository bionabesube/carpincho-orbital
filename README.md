# 🛰️ Carpincho Orbital
### Astronaut Health Monitoring for Space Missions

**Carpincho Orbital** is a project developed for the **NASA Space Apps Challenge 2026**, focused on exploring ways to monitor and assess the physiological and functional challenges astronauts may experience during space missions, particularly those associated with microgravity.

The project combines interactive visual assessments, data collection, and health monitoring tools to support the observation of potential changes in astronauts' visual and oculomotor functions, alongside complementary physiological indicators.

## 🚀 Project Overview

Carpincho Orbital is organized into two complementary components, each maintained in a dedicated Git branch:

### 1. VISOR — Gamified Visual Assessment

**Branch:** [`visor`](https://github.com/bionabesube/carpincho-orbital/tree/visor)

A 3D interactive visual assessment application developed with **Godot Engine**.

VISOR explores the use of interactive visual stimuli and gaze-position tracking to simulate optical assessment procedures in a virtual environment.

Its development includes:
- Interactive visual stimuli and target positioning.
- Visual field simulation through a 3D environment.
- Gaze-position estimation and interaction tracking.
- Assessment progress and response-time monitoring.
- A foundation for future VR headset and eye-tracking integration.

The current desktop prototype uses mouse movement as a substitute for gaze tracking while the VR integration is under development.

### 2. Health Monitoring Dashboard

**Branch:** [`dashboard`](https://github.com/bionabesube/carpincho-orbital/tree/dashboard)

A web-based platform designed to organize, visualize, and monitor astronaut health data throughout a space mission.

The dashboard brings together different sources of information, including:

- **Visual and oculomotor assessments:** visual field results, gaze metrics, fixation, blinks, and saccades.
- **Basic visual assessments:** visual acuity, refraction, and near-point measurements.
- **Wearable data:** sleep, resting heart rate, heart rate variability (HRV), skin temperature, and activity.
- **Symptoms and self-reports:** records of reported symptoms and observations.
- **Health follow-up:** longitudinal indicators and scheduled assessments.

It also provides functionality for importing wearable data through CSV files and organizing results over time.

## 🔄 Project Workflow

The two components are designed to work together as part of a complementary monitoring system.

1. **Visual assessment:** VISOR presents interactive visual tasks and collects user interaction data.
2. **Data acquisition:** assessment results and complementary measurements are collected from different sources.
3. **Data integration:** the dashboard organizes visual, physiological, and self-reported information.
4. **Monitoring and visualization:** longitudinal records allow the observation and comparison of changes throughout a mission.

The goal is to bring together different measurements to provide a broader perspective on astronaut health during spaceflight.

## 🌐 Live Demo

Explore the current web dashboard:

**[Carpincho Orbital — Mission Health Operations](https://carpincho-orbital.onrender.com/)**

The hosted version includes a demonstration environment with synthetic data to illustrate the proposed monitoring workflow and dashboard functionality.

## 📂 Repository Structure

This repository uses separate branches to maintain the development of each component:

| Branch | Description |
|---|---|
| `main` | General project overview and documentation |
| `visor` | Godot-based visual assessment application |
| `dashboard` | Health monitoring, data organization, and visualization platform |

Each development branch contains its own documentation with further details about its implementation and usage.

## 🛠️ Technologies

- **Godot Engine:** 3D environment and interactive visual assessment.
- **GDScript:** VISOR application logic.
- **Web technologies:** Health monitoring dashboard.
- **Git and GitHub:** Version control and collaborative development.
- **Virtual Reality and Eye Tracking:** Target hardware and future integration for visual assessment.

## ⚠️ Disclaimer

Carpincho Orbital is an experimental prototype developed for research and educational purposes.

The hosted dashboard uses synthetic demonstration data. The current visual assessment prototype is not a clinically validated perimetry tool, and the system is not a medical device. Its outputs should not be used for medical diagnosis or clinical decision-making.

## 🌎 About the Project

Carpincho Orbital explores how software development, biomedical engineering, and human physiology can come together to address the challenges of human space exploration.

**Built for NASA Space Apps Challenge 2026.**
