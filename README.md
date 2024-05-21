# Tagging Audit Script

This project contains a Python script that checks AWS resources for specific tags and outputs the results in a CSV format.

## Requirements

- Python 3.x
- AWS CLI configured with appropriate permissions

## Setup

1. **Clone the repository**:
    ```sh
    git clone <your-repo-url>
    cd tagging-audit-scripts
    ```

2. **Create and activate a virtual environment**:
    - On **macOS and Linux**:
        ```sh
        python3 -m venv venv
        source venv/bin/activate
        ```
    - On **Windows**:
        ```sh
        python -m venv venv
        venv\Scripts\activate
        ```

3. **Install the required packages**:
    ```sh
    pip install -r requirements.txt
    ```

4. **Configure AWS CLI**:
    Ensure your AWS CLI is configured with the appropriate permissions to access the resources. You can configure it using:
    ```sh
    aws configure
    ```

## Running the Script

1. **Run the script**:
    ```sh
    python tagging_audit.py
    ```

2. The output will be written to a file named `tagged_resources.csv` in the current directory.

## Files

- `tagging_audit.py`: The main script file that performs the tagging audit.
- `requirements.txt`: A list of Python packages required to run the script.
- `.gitignore`: A list of files and directories to ignore in the git repository.
- `README.md`: This file, providing setup and usage instructions.

## Example Output

The script will generate a CSV file (`tagged_resources.csv`) with the following columns:
- `ResourceARN`: The ARN of the resource.
- `Region`: The AWS region of the resource.
- `Service`: The AWS service of the resource.
- `Tags`: All tags associated with the resource.

## Contributing

If you find any issues or have suggestions for improvements, please open an issue or create a pull request.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

