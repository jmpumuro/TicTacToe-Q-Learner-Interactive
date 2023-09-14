import os
import json
from google.cloud import storage

class CloudClient:
    def __init__(self, model_name, config_file="config.json"):
        self.model_name = model_name
        self.config_file = config_file
        self.load_config()

    def load_config(self):
        try:
            with open(self.config_file, 'r') as config_file:
                self.config = json.load(config_file)
        except FileNotFoundError:
            raise FileNotFoundError(f"Config file {self.config_file} not found.")

    def upload_model(self):
        # Authenticate with Google Cloud
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = self.config["google_cloud_credentials"]

        # Initialize a client
        storage_client = storage.Client(project=self.config["google_cloud_project_id"])

        # Get the bucket
        bucket = storage_client.get_bucket(self.config["agent_models"])

        # Construct the model file path
        model_file_path = os.path.join(self.config["Q-learning/agent"], self.model_name)

        # Upload your model file to the bucket
        model_blob = bucket.blob(model_file_path)
        model_blob.upload_from_filename(self.model_name)