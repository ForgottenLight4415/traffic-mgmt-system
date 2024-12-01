# AI-Driven Adaptive Traffic Management System

An innovative project utilizing AI to analyze traffic density and dynamically adjust traffic signals based on real-time inputs. This system leverages YOLOv8 for object detection and a Flask-based backend to process videos/images and determine optimal signal timings.

---

## Project Links

- **Project Proposal**: [View Proposal](https://sites.google.com/view/ece-5554-group-seven-project/home)
- **Google Colab Notebook**: [View Colab](https://colab.research.google.com/drive/1i6OkipB5IgmMdbMjLeJyxVhBdE7F_qzU)

---

## Project Contributors

- **Vishal Pednekar**
- **Pratham Joshi**
- **Atharva Salunke**

---

## Features

1. **Video Upload and Processing**:
   - Upload traffic videos to the Flask backend.
   - The system processes each frame using YOLOv8 for object detection and annotates vehicles with bounding boxes.
   - Processed videos are saved for download.

2. **Image-Based Signal Decision**:
   - Upload traffic intersection images.
   - The system determines the lane with the highest traffic density and returns the corresponding green signal.

3. **Dynamic Traffic Signal Control**:
   - Based on vehicle counts, dynamically recommend which lane’s signal should turn green.
   - Outputs lane-specific vehicle counts as JSON.

---

## File Structure

```
AI-Traffic-Management/
│
├── app.py                 # Flask application
├── uploads/               # Folder for uploaded files
├── processed/             # Folder for processed outputs
├── best.pt                # Trained YOLOv8 model file
├── requirements.txt       # Python dependencies
├── README.md              # Project documentation
```

---

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-repo-link.git
   cd AI-Traffic-Management
   ```

2. **Set Up Python Environment**:
   - It’s recommended to use a virtual environment.
   ```bash
   python -m venv venv
   source venv/bin/activate  # For Linux/Mac
   venv\Scripts\activate     # For Windows
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Download YOLOv8 Model**:
   - Place your trained `best.pt` file in the root directory.

---

## Usage

### **1. Start the Flask App**
Run the Flask application:
```bash
python app.py
```

The app will start on `http://127.0.0.1:5000`.

---

### **2. Endpoints**

#### **A. Video Upload and Processing**
- **URL**: `/upload`
- **Method**: `POST`
- **Description**: Upload a video for processing with YOLOv8.
- **Request**:
  - `file` (form-data): The traffic video file to upload.
- **Response**:
  ```json
  {
      "message": "Video uploaded and processed successfully!",
      "processed_file": "processed/processed_video.mp4"
  }
  ```

#### **B. Image-Based Signal Decision**
- **URL**: `/process-image`
- **Method**: `POST`
- **Description**: Upload an image of a traffic intersection to determine the green signal.
- **Request**:
  - `file` (form-data): The traffic image file to upload.
- **Response**:
  ```json
  {
      "lane_with_green_signal": "north",
      "vehicle_counts": {
          "north": 5,
          "south": 3,
          "east": 2,
          "west": 1
      }
  }
  ```

---

## Testing

### **Using `curl`**

1. **Video Upload**:
   ```bash
   curl -X POST -F "file=@path/to/video.mp4" http://127.0.0.1:5000/upload
   ```

2. **Image Signal Processing**:
   ```bash
   curl -X POST -F "file=@path/to/image.jpg" http://127.0.0.1:5000/process-image
   ```

### **Using Postman**

1. Create a new request.
2. Set the URL to `http://127.0.0.1:5000/upload` or `http://127.0.0.1:5000/process-image`.
3. Select the **POST** method.
4. Under the **Body** tab, choose **form-data**.
5. Add a key `file` and upload your file.

---

## Future Work

1. **Integration with Live Traffic Feeds**:
   - Enable real-time traffic management using live camera inputs.

2. **IoT Integration**:
   - Synchronize with smart traffic lights for direct control.

3. **Enhanced Analytics**:
   - Provide dashboards for historical data and trend analysis.

4. **Model Optimization**:
   - Train the YOLO model on larger, more diverse datasets for improved accuracy.
