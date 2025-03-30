import logging, os

# Define the working directory for the log file
working_directory = "c:\\CODE\\game-development-library\\mazeSolver\\logs"
os.makedirs(working_directory, exist_ok=True)  # Create the directory if it doesn't exist

# Construct the full path to the log file
log_file_path = os.path.join(working_directory, "maze_solver.log")

# Configure logging
logging.basicConfig(
    filename=log_file_path,  # Log file name
    filemode="w",               # Overwrite the log file each time the program runs
    level=logging.INFO,         # Set the logging level (INFO, DEBUG, etc.)
    format="%(asctime)s - %(levelname)s - %(message)s"  # Log format
)

# Optional: Add a console handler to also print logs to the console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
console_handler.setFormatter(console_formatter)
logging.getLogger().addHandl# Log a test message
logging.info("Logging initialized. Log file is located at: " + log_file_path)