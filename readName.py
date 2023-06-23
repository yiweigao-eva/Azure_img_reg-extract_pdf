
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials

from PIL import Image
import os
import time
from array import array
import sys

import config
import constant




subKey = config.SubKey
endpoint = config.Endpoint
computervisionClient = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subKey))


def ms_ocr(imgPath):
    image_stream = open(imgPath, "rb")
    read_response = computervisionClient.read_in_stream(image=image_stream,raw=True)     
    # Get the operation location (URL with an ID at the end) from the response
    read_operation_location = read_response.headers['Operation-Location']
    # Grab the ID from the URL
    operation_id = read_operation_location.split('/')[-1]

    # Call the "GET" API and wait for it to retrieve the results 
    while True:
        read_result = computervisionClient.get_read_result(operation_id)
        if read_result.status not in ['notStarted', 'running']:
            break
        time.sleep(1)

    resultStr = ""

    # Print the detected text, line by line
    if read_result.status == OperationStatusCodes.succeeded:
        for text_result in read_result.analyze_result.read_results:
            for line in text_result.lines:
                resultStr = resultStr + line.text

    return resultStr



def formatStr(full, pre, sub):
    if len(full) < len(pre) + len(sub):
        return ""
    if pre not in full:
        if len(pre) <= 2:
            print("pre err: " + full)
            return ""
        return formatStr(full, pre[1:-1], sub)
    elif sub not in full:
        if len(sub) <= 2:
            print("sub err: " + full)
            return ""
        return formatStr(full, pre, sub[1:-1])
    else:
        preIdx = full.index(pre)
        subIdx = full.index(sub)
        
        if subIdx - preIdx > 300:
            return formatStr(full[preIdx + len(pre):], pre, sub)
        return full[preIdx:subIdx]


if __name__ == "__main__" :
    # get file name
    dirName1 = os.listdir(constant.DirName)
    f = open(constant.ResultFileName, "w",encoding="utf-8")
    failCount = 0
    successCount = 0
    
    for dname in dirName1:
        time.sleep(10)
        pdfPath = constant.DirName + "/" + str(dname) + constant.TargetFileName
        if not os.path.exists(pdfPath):
            pdfPath = constant.DirName + "/" + str(dname) + constant.SecTargetFN

        pdfCtx = ms_ocr(pdfPath)
        area = formatStr(pdfCtx.replace(" ", ""), constant.PreSubStr, constant.SubSubStr)
        if area == "":
            failCount+=1
            print("FAILED " + pdfPath)
            f.write(str(dname) + " " + pdfCtx.replace(" ", "") + "\n")

            continue
        f.write(str(dname) + " " + area + "\n")
        print("SUCCESSED " + pdfPath)
        successCount+=1
    f.close()
   
    print("Total: " + str(failCount+successCount) + "Success: " + str(successCount) + "Failed: "+ str(failCount))