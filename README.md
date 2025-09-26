### Steps to Run

1. **Clone the repository**:

   ```bash
   git clone https://github.com/yourusername/Solar-Power-Prediction.git
   cd Solar-Power-Prediction

2. **Create and activate the Conda environment**:

    Create a new Conda environment with the necessary dependencies. Make sure you have conda installed. If not, you can download and install it from [here](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html).

    ```bash
    # Create a Conda environment
    conda create -p ./venv python=3.12 -y
    conda activate venv

3. **Install required dependencies**:
   ```bash
   pip install -r requirements.txt

4. **Run the Flask app**:
   ```bash
   streamlit run main.py

5. **Navigate to localhost**:
   Once the Flask app is running, follow these steps:

   1. Open your web browser.
   2. Navigate to http://127.0.0.1:8501/ or http://localhost:8501/
   3. Use the application to predict solar power generation using location only!

#### Contributing
Feel free to fork this project, improve it, and submit pull requests!

#### License
This project is MIT Licensed. See the LICENSE file for more details.

