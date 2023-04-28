import whisper

# Copyright 2020 Google, LLC.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START eventarc_audit_storage_server]
import os
from google.cloud import storage
from flask import Flask, request

def download_blob(bucket_name, source_blob_name, destination_file_name):
    """Downloads a blob from the bucket."""
    # The ID of your GCS bucket
    # bucket_name = "your-bucket-name"

    # The ID of your GCS object
    # source_blob_name = "storage-object-name"

    # The path to which the file should be downloaded
    # destination_file_name = "local/path/to/file"

    storage_client = storage.Client(project="322004009779")

    bucket = storage_client.bucket(bucket_name)

    # Construct a client side representation of a blob.
    # Note `Bucket.blob` differs from `Bucket.get_blob` as it doesn't retrieve
    # any content from Google Cloud Storage. As we don't need additional data,
    # using `Bucket.blob` is preferred here.
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)

    print(
        "Downloaded storage object {} from bucket {} to local file {}.".format(
            source_blob_name, bucket_name, destination_file_name
        )
    )

def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    # The ID of your GCS bucket
    # bucket_name = "your-bucket-name"
    # The path to your file to upload
    # source_file_name = "local/path/to/file"
    # The ID of your GCS object
    # destination_blob_name = "storage-object-name"

    storage_client = storage.Client(project="322004009779")
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    # Optional: set a generation-match precondition to avoid potential race conditions
    # and data corruptions. The request to upload is aborted if the object's
    # generation number does not match your precondition. For a destination
    # object that does not yet exist, set the if_generation_match precondition to 0.
    # If the destination object already exists in your bucket, set instead a
    # generation-match precondition using its generation number.
    generation_match_precondition = 0

    blob.upload_from_filename(source_file_name, if_generation_match=generation_match_precondition)

    print(
        f"File {source_file_name} uploaded to {destination_blob_name}."
    )

app = Flask(__name__)
# [END eventarc_audit_storage_server]


# [START eventarc_audit_storage_handler]
@app.route('/', methods=['POST'])
def index():
    # Gets the GCS bucket name from the CloudEvent header
    # Example: "storage.googleapis.com/projects/_/buckets/my-bucket"
    download_blob(
        bucket_name="cloudy2023pwproject.appspot.com",
        source_blob_name=bucket,
        destination_file_name="local_file",
    )
    bucket = request.headers.get('ce-subject')
    model = whisper.load_model("tiny.en.pt")
    result = model.transcribe("local_file")
    filename = bucket.split("/")[-1]
    text_file = open(f"{filename}.txt", "w")
    n = text_file.write('Welcome to pythonexamples.org')
    text_file.close()
    upload_blob(
        bucket_name="cloudy2023pwproject.appspot.com",
        source_file_name="{filename}.txt",
        destination_blob_name=f"files/{filename}.txt",
    )
    print(result["text"])
    print(f"Detected change in Cloud Storage bucket: {bucket}")
    return (f"Detected change in Cloud Storage bucket: {bucket}", 200)
# [END eventarc_audit_storage_handler]


# [START eventarc_audit_storage_server]
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
# [END eventarc_audit_storage_server]