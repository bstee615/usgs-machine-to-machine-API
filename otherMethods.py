import os
import requests
import logging
from tqdm import tqdm
from usgsDataTypes import usgsDataTypes
from datetime import datetime


class otherMethods:
    """
    Implementation date: 06.08.2020

    Other methods to handle stuff like data download.
    """

    @classmethod
    def download(cls, api, datasetName, entityId, productName, output_dir):
        downloadOptions = api.downloadOptions(datasetName=datasetName, entityIds=entityId)
        datasetId, productId = None, None
        for downloadOption in downloadOptions['data']:
            if downloadOption['productName'] == productName:
                datasetId = downloadOption['datasetId']
                productId = downloadOption['id']
                break
        if (datasetId, productId) == (None, None):
            logging.error(f"{datetime.now()} Can't find productName={productName} in datasetName={datasetName}")
            return

        download = usgsDataTypes.Download(entityId=entityId, datasetId=datasetId, productId=productId,
                                          productName=productName)
        downloadRequest = api.downloadRequest(downloads=[download], returnAvailable=True)

        if downloadRequest['data']['failed'] != []:
            logging.error(f'{datetime.now()} downloadRequest failed see respond:\n{downloadRequest}')
            return

        availableDownloads = downloadRequest['data']['availableDownloads'] + \
                             downloadRequest['data']['preparingDownloads']
        results_list = []
        for availableDownload in availableDownloads:
            url = availableDownload['url']
            path = cls._download(url, output_dir)
            results_list.append(path)

        return results_list

    @classmethod
    def _download(cls, url, output_dir, chunk_size=1024):
        requests_log = logging.getLogger("requests.packages.urllib3")
        requests_log.setLevel(logging.DEBUG)
        requests_log.propagate = True
        import time
        begin = time.time()
        with requests.get(url, stream=True, allow_redirects=True) as r:
            expected_file_size = int(r.headers['Content-Length'])
            with tqdm(desc="Downloading", total=expected_file_size, unit_scale=True, unit='B') as progressbar:
                end = time.time()
                runtime = end-begin
                print('Initial GET request time:', runtime)
                file_name = r.headers['Content-Disposition'].split('"')[1]
                file_path = os.path.join(output_dir, file_name)
                with open(file_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=chunk_size):
                        if chunk:
                            progressbar.update(len(chunk))
                            f.write(chunk)

        if cls.is_download_ok(expected_file_size, file_path):
            return file_path
        else:
            # TODO Test the ability to continue files downloading.
            # TODO If it is possible to continue downloading, do not delete the file, but try to continue the interrupted download.
            os.remove(file_path)

    @classmethod
    def is_download_ok(cls, expected_file_size, filename):
        if os.path.isfile(filename):
            actual_file_size = os.path.getsize(filename)
            if expected_file_size == actual_file_size:
                return True
        return False

    @classmethod
    def request_filesize(cls, api, datasetName, productName, entityId):
        """
        :param api: (usgsMethods)  Instance of usgsMethods()
        :param datasetName: (str) In example: 'LANDSAT_8_C1'
        :param productName: (str) In example: 'Level-1 GeoTIFF Data Product'
        :param entityId: (str) entityId
        :return: (int) Product file size
        """
        downloadOptions = api.downloadOptions(datasetName=datasetName, entityIds=entityId)
        for downloadOption in downloadOptions['data']:
            if productName == downloadOption['productName']:
                file_size = int(downloadOption['filesize'])
                return file_size

