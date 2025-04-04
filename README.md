# File Locker with DeepFace

## Overview
This project implements a **file locking and unlocking system** using **DeepFace for face recognition**. It ensures that files can only be unlocked by an authorized user, providing an extra layer of security.

## Features
- **Face-based authentication** using DeepFace
- **Lock and unlock files** with a simple UI
- **Live camera feed** for capturing verification images
- **Hidden file encryption** using Windows `attrib` command

## Technologies Used
- **Python** (PyQt5, OpenCV, DeepFace)
- **Face Recognition** (DeepFace Library)
- **GUI Development** (PyQt5)
- **File Attribute Manipulation** (Windows `attrib` command)

## Installation
### Prerequisites
Ensure you have Python 3.8+ installed and install the dependencies:
```sh
pip install PyQt5 opencv-python deepface
```

## Usage
1. **Run the application**:
   ```sh
   python complete.py
   ```
2. **Capture a reference image** by clicking "Capture Image".
3. **Lock a file** by entering the file path and clicking "Lock File".
4. **Unlock a file** by verifying your face and clicking "Unlock File".

## How It Works
1. **File Locking**:
   - User selects a file to lock.
   - The file is hidden and marked as a system file (`attrib +h +s`).
2. **File Unlocking**:
   - The system captures a verification image.
   - DeepFace compares the new image with the stored reference image.
   - If verification is successful, the file is unhidden (`attrib -h -s`).

## Future Enhancements
- **Cross-platform support** (Linux & macOS file locking methods)
- **Stronger encryption instead of simple attribute hiding**
- **Multiple user authentication** for shared file access

## License
This project is licensed under the MIT License.

## Contact
For any issues or improvements, please raise a GitHub issue or contribute via pull requests!
