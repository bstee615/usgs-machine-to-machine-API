import json
from usgsDataTypes import usgsDataTypes
from usgsMethods import usgsMethods
from otherMethods import otherMethods
from pprint import pprint
import time


def main():
    # In order not to store the login/password in the code - auth with json-formatted text file:
    # {"username": "username", "password": "password"}
    txt_path = r"json_pass.txt"
    with open(txt_path, 'r') as file:
        json_data = json.load(file)
        usgs_username = json_data['username']
        usgs_password = json_data['password']

    api = usgsMethods()  # instance created
    api.login(usgs_username, usgs_password)

    # show your permissions
    permissions = api.permissions()
    print(f"Your login permissions is {permissions['data']}", end='\n' * 2)

    api.loud_mode = True

    catalog = 'EE'  # NASA EarthExplorer
    search = api.datasetSearch(catalog)
    collections = search["data"]
    print(len(collections), 'collections')
    collections = [d for d in collections if 'landsat' in d["collectionName"].lower() or 'sentinel' in d["collectionName"].lower()]
    print('filtered to', len(collections), 'landsat/sentinel collections')
    collections = sorted(collections, key=lambda d: (str(d["datasetCategoryName"]), str(d["collectionName"])))
    print('Categories:')
    print('\n'.join(sorted(set('* ' + d["datasetCategoryName"] for d in collections if d["datasetCategoryName"] is not None))))
    print('Datasets:')
    print('\n'.join(sorted(set(f'* {d["collectionName"]:30s} {d["datasetAlias"]}' for d in collections))))

    # datasetName = 'LANDSAT_8_C2'
    datasetName = 'SENTINEL_2A'

    # Let's find some scenes by location!
    # Region of interest coordinates. Too long coordinates list may throw 404 HTTP errors!
    # Examples:
    # 'Point' [lat ,lon]
    # 'Polygon' [[ [lat ,lon], [lat ,lon], ... ]]
    ROI = [[
        [59.19852, 63.06039],
        [59.62473, 64.80140],
        [62.05751, 65.70580],
        [62.86149, 65.26510],
        [63.24590, 64.51990],
        [65.99469, 64.58008],
        [66.97107, 64.50871],
        [67.49873, 64.08241],
        [68.96698, 64.44441],
        [70.34046, 64.31480],
        [71.58613, 63.35573],
        [73.10955, 63.37922],
        [76.69435, 63.02787],
        [77.98457, 62.51861],
        [79.89941, 62.77741],
        [81.03670, 63.14609],
        [83.96038, 62.48975],
        [85.97549, 61.48612],
        [84.16387, 60.85305],
        [82.12599, 60.53366],
        [77.11535, 60.73926],
        [76.67393, 59.58814],
        [74.99998, 58.69959],
        [72.52650, 59.15018],
        [69.39066, 59.91733],
        [66.74067, 58.64882],
        [65.70599, 58.65047],
        [61.15117, 61.67129],
        [59.40793, 62.09941],
        [59.19852, 63.06039],
    ]]

    print('Searching ROI in dataset', datasetName)

    geoJson = usgsDataTypes.GeoJson(type='Polygon', coordinates=ROI)
    spatialFilter = usgsDataTypes.SpatialFilterGeoJson(filterType='geojson', geoJson=geoJson)
    acquisitionFilter = usgsDataTypes.AcquisitionFilter(start="2020-06-01", end="2020-06-31")
    sceneFilter = usgsDataTypes.SceneFilter(acquisitionFilter=acquisitionFilter,
                                            cloudCoverFilter=None,
                                            datasetName=datasetName,
                                            ingestFilter=None,
                                            metadataFilter=None,
                                            seasonalFilter=None,
                                            spatialFilter=spatialFilter)

    sceneSearchResult = api.sceneSearch(datasetName=datasetName, maxResults=10, startingNumber=None,
                                        metadataType='full',
                                        sortField=None,
                                        sortDirection='ASC',
                                        sceneFilter=sceneFilter,
                                        compareListName=None,
                                        bulkListName=None,
                                        orderListName=None,
                                        excludeListName=None)

    # print(json.dumps(sceneSearchResult['data']['results'], indent=2))
    print(len(sceneSearchResult['data']['results']), 'results')
    print('\n'.join('* ' + r["displayId"] for r in sceneSearchResult['data']['results']))

    print(f"\nDownloading:")
    
    all_begin = time.time()

    filesizes = []
    runtimes = []
    entityIds = []
    displayIds = []

    try:
        # productName = 'LandsatLook Quality Image'
        productName = 'L1C Tile in JPEG2000 format'
        for searchResult in sceneSearchResult['data']['results']:
            entityIds.append(searchResult["entityId"])
            displayIds.append(searchResult["displayId"])
            entityId = searchResult['entityId']
            filesize = otherMethods.request_filesize(api, datasetName=datasetName, productName=productName, entityId=entityId)

            print(f"The file size of {productName} with entityId={entityId} is {filesize} bytes", end='\n' * 2)
            filesizes.append(filesize)

            begin = time.time()
            results = otherMethods.download(api, datasetName=datasetName, entityId=entityId, productName=productName,
                                            output_dir=r'downloads')
            end = time.time()
            runtime = end-begin
            runtimes.append(runtime)
            print('Download time:', runtime)
            print(results)
    finally:
        api.logout()

        all_end = time.time()
        all_runtime = all_end-all_begin
        print('Total time:', all_runtime)

        results = {
            "all_runtime": all_runtime,
            "runtimes": runtimes,
            "filesizes": filesizes,
            "entityIds": entityIds,
            "displayIds": displayIds,
        }
        if len(runtimes) > 0:
            print(f'Average download time: {sum(runtimes) / len(runtimes):.3f}s')
        if len(filesizes) > 0:
            print(f'Average download size: {(sum(filesizes) / len(filesizes))/1e6:,.3f}MB')
        with open('results.json', 'w') as f:
            json.dump(results, f, indent=2)
    print('Done!')


if __name__ == '__main__':
    main()
