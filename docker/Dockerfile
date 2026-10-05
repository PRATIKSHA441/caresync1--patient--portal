# -------------------------------------------------------
# STEP 1: Choose a base image.
# Think of this as a clean computer that already has
# Python 3.11 installed. We start from here.
# -------------------------------------------------------
FROM python:3.11-slim


# -------------------------------------------------------
# STEP 2: Set the working folder inside the container.
# All our files will go into /app inside the container.
# -------------------------------------------------------
WORKDIR /app


# -------------------------------------------------------
# STEP 3: Copy requirements.txt into the container first.
# We do this before copying the rest of the code so Docker
# can reuse this step when only the code changes.
# -------------------------------------------------------
COPY requirements.txt .


# -------------------------------------------------------
# STEP 4: Install the Python libraries.
# This runs pip install inside the container.
# --no-cache-dir keeps the container size small.
# -------------------------------------------------------
RUN pip install --no-cache-dir -r requirements.txt


# -------------------------------------------------------
# STEP 5: Copy all our application files into the container.
# The first dot = everything in our project folder.
# The second dot = the /app folder inside the container.
# -------------------------------------------------------
COPY . .


# -------------------------------------------------------
# STEP 6: Tell Docker our app listens on port 8000.
# This is documentation. The actual port mapping
# happens when you run the container (shown below).
# -------------------------------------------------------
EXPOSE 8000


# -------------------------------------------------------
# STEP 7: The command to start the application.
# uvicorn is the web server that runs FastAPI.
# --host 0.0.0.0 allows connections from outside the container.
# --port 8000 sets the port number.
# -------------------------------------------------------
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
