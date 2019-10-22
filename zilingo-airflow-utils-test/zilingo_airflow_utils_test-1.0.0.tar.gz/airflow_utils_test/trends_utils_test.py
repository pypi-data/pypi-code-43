from google.cloud import storage
from apiclient import errors


def list_blobs_with_prefix(bucket_name, prefix, suffix, delimiter=None):
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blobs = bucket.list_blobs(prefix=prefix, delimiter=delimiter)

    blob_files_list = []
    for blob in blobs:
        blob_files_list.append(str(blob.name))

    filtered_files_name_list = []
    for blob_name in blob_files_list:
        if blob_name.endswith(suffix):
            filtered_files_name_list.append(blob_name)

    return filtered_files_name_list


def list_all_blobs_in_gcs_folder(bucket_name, prefix, delimiter=None):
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blobs = bucket.list_blobs(prefix=prefix, delimiter=delimiter)

    blob_files_list = []
    for blob in blobs:
        if blob.name != prefix:
            blob_files_list.append(str(blob.name))

    return blob_files_list


def delete_file_from_drive(service, file_id):
    """Permanently delete a file, skipping the trash.

    Args:
      service: Drive API service instance.
      file_id: ID of the file to delete.
    """
    try:
        service.files().delete(fileId=file_id).execute()
        print("File Deleted from Drive: ", file_id)
    except errors.HttpError as error:
        print('An error occurred: %s' % error)


def delete_files_from_gcs(files_list, bucket_name):
    # Delete the Zip Files from the GCS
    for file_name in files_list:
        """Deletes a blob from the bucket."""
        storage_client = storage.Client()
        bucket = storage_client.get_bucket(bucket_name)
        blob = bucket.blob(file_name)
        blob.delete()
        print('File {} deleted.'.format(file_name))
