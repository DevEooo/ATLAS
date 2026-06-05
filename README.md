<div align="center">
    <img alt="UI Preview" width="650" height="400" src="https://github.com/user-attachments/assets/4f292411-bfc8-4f41-a867-d43140f51919" />
    <h6>ATLAS UI Preview</h6>
</div>

<p align="center">
  <a href="https://www.python.org/downloads/release/python-3142/"><img src="https://img.shields.io/badge/python-v3.14.2-blue?logo=python"></a>
  <a href=""><img src="https://img.shields.io/badge/license-MIT-green"></a>
</p>

---

## Project Overview: ATLAS (Attendance Tracking & Live Verification System)

This project was actually developed regarding from these issues and its solution:

### Issues:
- Inconvenient & Inefficient Workflow: The interns must waiting for manual logbook queue at guard post.
- Security Risks: The risk of missing logbook or even damaged logbook.

### Solution: 
By implementing Face Recognition System, ATLAS can eliminate those issues and digitizes the attendance process, data integrity through any local databases (I'm using SQLite in this case) and providing a seamless user experience.  

---

## The theory that I've implemented on this project

### 1. The ROI (Region of Interest) Layout
To improve accuracy in crowded environments, ATLAS utilizes an **oval-shaped ROI** layout. This ensures the system focuses only on the primary user in front of the camera, preventing "false triggers" from background movement or other people passing by.

### 2. Recognition Logic & Euclidean Principles
The system calculates the similarity between faces using **Euclidean distance** algorithms. To ensure high reliability, I implemented a strict **Confidence Threshold** logic:

| Threshold Range | Status | Action |
| :--- | :--- | :--- |
| **< 0.50** | ✅ **Match Found** | Attendance recorded successfully. |
| **0.50 - 0.65** | ⚠️ **Low Confidence** | System prompts user to try a different angle. |
| **> 0.65** | ❌ **Unknown** | Face isn't recognized in the database. |

> **Note:** A lower threshold indicates a higher degree of similarity between the detected face and the database record.
---
## Main Features

- Real-time Face Detection: Agile and accurate recognition using OpenCV, Pickle and Face Recognition Libraries.
- Sleek UI: Clean and understandable UI by providing oval layout in the middle and feedback UI made with Tkinter.
- Downloadable Logs: Effortless exportable logs and automatically converted to Excel format.
- Local Databases Integration: Secure interns log & profiles.
- Secure Exportable Logs: Protected system with hardcoded secrets for downloading those logs.

---

## Techs that I've used for this project

| Component | Technology |
| :--- | :--- |
| Language | Python |
| AI/ML Libraries | OpenCV, Face Recognition |
| Database | SQLite |
| GUI | Tkinter |
| Others | Pickle, Pillow, Numpy |

---

## Project Architecture 

To ensure the system runs efficiently as I expected, so, I've designed these workflow for this project.

### Entity Relationship Diagram (ERD) 
<div align="center">
    <img width="600" height="340" alt="ERD" src="https://github.com/user-attachments/assets/398c0b73-23da-4160-a952-03af2689b8a1" />
</div>

### Flowchart
<div align="center">
    <img width="600" height="680" alt="Flowchart" src="https://github.com/user-attachments/assets/31261f63-12db-4d9f-a184-358c052936b3" />
</div>

Unfortunately, these Project Architecture are still written in local language (Bahasa Indonesia), not in English.

---

## Miscellaneous
<div align="center">
    <img width="640" height="410" alt="Screenshot 2026-02-23 082807" src="https://github.com/user-attachments/assets/cb1b94a3-039f-455a-8784-0b5de817440a" />
</div>

