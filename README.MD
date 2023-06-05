# Todoapp

Todoapp is a FastAPI application that serves as the backend for a todo application.

# Installation
To install and setup the Todoapp, follow these steps: 

1- Clone the repositry 
```bash
git clone https://github.com/saleh-kh/Todoapp.git 
```
2- Navigate to the project directory:
```bash
cd Todoapp
```

3- Create a virtual environment:
```bash
python3 -m venv myenv
```

4- Activate the virtual enviroment(For Wiendows don't use source):

```bash
source myenv/bin/activate
```

5- Install the required dependencies:
```bash
pip install -r requirements.txt
```

# Usage
Before running make sure you have a valid database url and secret key.


 Start the application server 
```bash
uvicorn main:app --reload
```
 