🚗 Multi-Object Tracking and Navigation in Dense Traffic
📌 Overview

This project presents a computer vision framework for multi-object vehicle tracking and traffic behavior analysis in highway and dense traffic scenarios. The system integrates vehicle detection, tracking, occlusion handling, behavior prediction, and risk-aware planning into a single pipeline for improved traffic understanding and safety analysis.

The framework uses YOLOv8 for vehicle detection and OC-SORT for multi-object tracking to maintain consistent vehicle identities across video frames. Additional modules are designed to handle temporary occlusions, validate vehicle motion using lane-based constraints, and predict possible vehicle behaviors for safety-aware decision support. 

The system produces annotated tracking videos and structured CSV logs, enabling both visual interpretation and quantitative traffic analysis.

🧠 System Pipeline

The proposed system follows a three-stage pipeline:

1️⃣ Perception

The perception stage detects and tracks vehicles in traffic videos.

Key components:

YOLOv8 for real-time vehicle detection

OC-SORT tracker for maintaining vehicle identities

Occlusion-aware tracking module for recovering temporarily hidden vehicles

Post-association validation using lane constraints to reduce identity switches

This stage generates stable vehicle trajectories and tracking identities across frames.

2️⃣ Behavior Prediction

The prediction module analyzes vehicle motion and lane information to estimate future behavior probabilities.

Possible predicted behaviors include:

Continue in the same lane

Lane change

Slow down

This probabilistic approach models uncertainty in traffic behavior. 

3️⃣ Risk-Sensitive Planning

Predicted behaviors are converted into risk-aware safety advisories.

Risk levels include:

Low Risk

Medium Risk

High Risk

Example advisories:

Maintain speed

Prepare to slow down

Increase following distance

This module enables traffic safety analysis and decision support.

Post-association validation using lane constraints to reduce identity switches

This stage generates stable vehicle trajectories and tracking identities across frames.

⚙️ Technologies Used

Python

YOLOv8 (Object Detection)

OC-SORT (Multi-Object Tracking)

OpenCV

NumPy

Pandas

📊 Outputs
🎥 Annotated Output Videos

The system produces videos showing:

Vehicle bounding boxes

Unique vehicle IDs

Trajectories

Occlusion recovery status

📄 CSV Log Files

The system generates structured logs for analysis:

File	Description

tracking.csv	Frame-wise vehicle tracking data

prediction.csv	Predicted vehicle behaviors

planning.csv	Risk level and safety advisory

These logs allow detailed traffic behavior analysis and system evaluation.

📈 Evaluation Metrics

The system focuses on tracking stability and occlusion handling.

Metric	Value

Identity Switch Rate	0.08

Occlusion Recovery Rate	> 0.9

Miss Detection Rate	Low

These results demonstrate robust tracking performance in dense traffic environments.

🚀 Future Work

Potential improvements include:

Real-time traffic monitoring using live video streams

Multi-camera traffic tracking systems

Integration with roadside sensors

Learning-based behavior prediction models

Automated lane detection for improved motion analysis

These enhancements can further improve traffic intelligence and safety analysis.
