# VISOR – Gamified Visual Assessment

## 1. Installation and Testing

To test the application, download the following two files from the latest release:

- `visor.exe`
- `visor.pck`

**Important:** Both files must be placed in the same directory. Once downloaded, simply run `visor.exe` to launch the application.

No additional installation is required.

## 2. Project Overview

VISOR is a gamified visual assessment application developed using **Godot Engine**. It is part of a project designed to monitor and evaluate the physiological challenges astronauts may experience during space missions, particularly those associated with microgravity and its effects on visual function.

The application aims to simulate optical assessment procedures through interactive visual stimuli and eye-position tracking using Virtual Reality (VR) headsets.

By presenting visual tasks in an interactive environment, VISOR seeks to collect information about eye movement and visual response, providing measurements that can later be processed and analyzed through the project's complementary dashboard.

## 3. Current Implementation

The current version provides the foundations of a 3D visual assessment environment.

Since VR eye-tracking integration is still part of the development roadmap, the current prototype runs on a conventional computer and uses **mouse movement as a substitute for eye tracking**. This allows the assessment environment and its underlying logic to be developed and tested independently of the final hardware.

The 3D scene represents the user's visual field:

- **Camera:** Represents the user's point of view.
- **Virtual Screen:** Represents the surface where visual stimuli are displayed.
- **Visual Targets:** Objects presented to the user during the assessment.
- **Gaze Cursor:** Represents the estimated gaze position, currently controlled by mouse movement.

The separation between gaze acquisition and assessment logic is intended to facilitate the future integration of actual eye-tracking data without requiring a complete redesign of the assessment environment.

## 4. Visual Assessment Environment

The application uses a 3D environment to simulate an optical examination.

Visual stimuli are generated within the user's field of view. In the current prototype, targets can appear around the center of the screen and move away from it, allowing the application to evaluate the user's interaction with objects at different positions in the visual field.

The movement and positioning of these targets provide a basis for developing different visual assessment exercises.

### Gaze Position

The application tracks the position of the mouse and translates it into a position on the virtual screen.

This is achieved through ray projection from the camera into the 3D scene, allowing the cursor to represent a position within the simulated visual field.

### Visual Angle

The virtual screen is positioned at a defined distance from the camera. This allows target positions to be expressed in terms of visual angles rather than only screen coordinates.

This is particularly relevant for optical assessments, where the angular displacement of a stimulus relative to the center of vision is more meaningful than its pixel distance.

## 5. Interaction and Measurements

The prototype includes the foundations for collecting information about the user's interaction with visual stimuli.

The current development focuses on:

- **Target positioning:** Controlling where visual stimuli appear within the visual field.
- **Gaze position:** Tracking the user's estimated point of focus.
- **Target movement:** Controlling stimulus displacement and speed.
- **Progress tracking:** Keeping track of assessment progress through a counter and progress indicator.
- **Elapsed time:** Measuring the time spent during the assessment.

These elements provide the foundation for extracting more meaningful visual performance parameters in future versions.

## 6. Development Roadmap

The project is designed to evolve from a mouse-controlled prototype into a VR-based visual assessment tool.

The main development objectives are:

### VR and Eye Tracking Integration
- Integrate a VR headset into the existing 3D environment.
- Replace mouse-based gaze estimation with actual eye-tracking measurements.
- Adapt the visual assessment environment to the headset's display and tracking capabilities.

### Visual Assessment Tasks
- Develop controlled visual stimuli and assessment exercises.
- Implement different target movement patterns.
- Evaluate gaze position and response during visual tasks.

### Data Acquisition
- Record gaze position and timestamps.
- Extract relevant parameters from eye movement.
- Organize assessment results for subsequent processing and visualization.

## 7. Technologies

- **Godot Engine:** 3D environment, application logic, visual stimuli and user interaction.
- **GDScript:** Application scripting and assessment logic.
- **Virtual Reality / Eye Tracking:** Intended hardware platform for gaze acquisition.
- **Git / GitHub:** Version control and project collaboration.

## 8. Repository Structure

This repository contains two main development branches:

- **`visor`:** Development of the gamified visual assessment application.
- **`dashboard`:** Data post-processing, organization and visualization.

Each branch contains its own README with further information about its implementation and functionality.

## 9. Future Integration

VISOR is intended to work as part of a larger monitoring system.

The data collected during visual assessments will be transferred to the dashboard component, where it can be processed, organized and combined with complementary measurements from other monitoring devices.

This integration aims to provide a more comprehensive overview of the astronaut's physiological condition and support the interpretation of potential visual changes associated with microgravity.
