# Mudumalai 3D Soundscape System

A high-fidelity **3D Spatial Audio and Sensor Fusion System** simulating a real-time embedded environment (STM32H7). This project implements a comprehensive DSP pipeline designed for immersive 3D soundscapes using HRTF spatialization, Doppler effects, and sensor-driven listener positioning.

## 🚀 Key Features

- **96kHz Audio Pipeline**: High-resolution digital signal processing for studio-quality audio.
- **HRTF Spatializer**: Simulated 288-direction resolution (24 azimuth × 12 elevation) using FFT-based convolution.
- **Sensor Fusion (100Hz)**: Integrates UWB and 9-DOF IMU data via Kalman filtering for precise real-time listener tracking.
- **Dynamic 3D Environment**: Real-time relative positioning, distance attenuation, and Doppler effect simulation.
- **Embedded Simulation**: Emulates an STM32H7 environment with timer interrupts and DMA-like audio callbacks.
- **Multiplexed Audio Assets**: Sequential playback of environmental assets (Forest, River, Night, Wind, Leaves).

## 🛠 Technical Architecture

The system follows a modular architecture designed for high-performance DSP tasks:

### 1. DSP Pipeline (`dsp_pipeline.py`)
Coordinates the signal flow for multiple mono sources:
`Source Chunks` ➔ `Distance Attenuation` ➔ `Doppler` ➔ `HRTF Spatialization` ➔ `Post-Mix EQ/Reverb` ➔ `Crosstalk Cancellation` ➔ `Stereo Output`

### 2. HRTF Engine (`hrtf_engine.py`)
- Uses **Overlap-Save FFT convolution**.
- Implements **Woodworth's model** for precise ITD (Interaural Time Difference) calculation.
- Models **ILD (Interaural Level Difference)** and high-frequency acoustic pinna notches.

### 3. Sensor Fusion (`sensor_fusion.py`)
- Employs **Kalman Filtering** to fuse positional data (UWB/GPS) with orientation data (IMU/Quaternions).
- Updates at **100Hz** via a simulated STM32 timer interrupt.

## 📦 Installation

This project requires Python 3.8+ and several scientific computing libraries.

### Quick Start (Automatic Setup)

Run the `run.py` script. It will automatically create a virtual environment, install dependencies, and launch the system.

```powershell
python run.py
```

### Manual Installation

If you prefer to set it up manually:

```bash
pip install -r requirements.txt
python main.py
```

**Required Dependencies:**
- `numpy`, `scipy`, `sounddevice`, `soundfile`, `pyquaternion`, `librosa`, `keyboard`

## 🎮 Controls & Usage

The system supports both **Demo Mode** (auto-movement) and **Manual Interaction**.

- **W / S**: Move Forward/Backward (Y-axis)
- **A / D**: Move Left/Right (X-axis)
- **Arrow Left / Right**: Rotate head (Yaw)
- **Arrow Up / Down**: Look up/down (Pitch)

*Note: Interacting with any control will automatically switch the system from Demo to Manual mode.*

## 📂 Project Structure

- `main.py`: The central system entry point and simulation loop.
- `audio_engine.py`: Manages audio asset loading (MP3/WAV) and chunking.
- `hrtf_engine.py`: Core 3D spatialization logic.
- `dsp_pipeline.py`: Orchestrates the flow from source to sound.
- `sensor_fusion.py`: Handles IMU/UWB data integration.
- `stm32_controller_sim.py`: Simulates the real-time controller environment.
- `imu_simulator.py`: Generates synthetic sensor data for testing.
- `crosstalk.py` & `eq_reverb.py`: Environment-specific audio enhancements.

## 📄 License

[Insert License Type - e.g., MIT]

---
*Developed as part of the 3D_DSP_Project.*
