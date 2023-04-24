Installation
-----------
Python is required to run all scripts

To install required libraries run ```pip install -r requirements.txt```

Preferred OS is linux based or WSL for windows.

Data
-----------
Data used follow set structure which cannot be changed (see image below). Provided demodata are included to show full functionality of this app and are representing a fraction of actual Bionano Saphyr output data.

#### Images

To upload custom data, the images have to be converted to TIFF file format. Since original Saphyr images come in JXR file format, 
script convert.sh can be used to convert files and set them to required structure with using JxrDecApp library for linux.

Run
 ```apt-get update apt-get install libjxr-tools``` to install JxrDecApp

Run ```./files/images/raw/convert.sh``` to convert images placed in _files/images/raw_ folder in Saphyr data structure with scan number related to existing directory in _files/images/converted_ as an argument

#### Bnx files
BNX files have to be placed in _files/bnx/scans_ directory and have to be split to scans using Bionano tool available at 
https://github.com/bionanogenomics/splitSaphyrBNXByScan and named _Scan01.bnx,... (default output of the tool)

Usage
-----------

### Convert images to BNX file
To convert an image to BNX file, run 
``` python3 -m src.BNXFile.BNXConverter -i scan/channel/inputFile -o outputFile```. 
Note that path including scan and channel has to be present in declaring the input image.

To show help and all possible flags, run with help flag ```python3 -m src.BNXFile.BNXConverter -h```.

If any needed files are missing (images have to be present from both channels), error message appears.

Final output will be present in the _files/bnx/output_ directory.

#### Examples:

``` python3 -m src.BNXFile.BNXConverter -i '1/channel1/B1_CH1C001.tiff' -o 'myBNX.bnx'```:
converts image from bank 1 and column 1 to BNX file using most optimal parameter congifuration

``` python3 -m src.BNXFile.BNXConverter -i '1/channel1/B1_CH1C001.tiff' -o 'myBNX.bnx' -f 'mean' -t 300```:
converts image using mean filter to process images and thresholds fluorescent marks with intensity lower than 300


``` python3 -m src.BNXFile.BNXConverter -i '1/channel1/B1_CH1C001.tiff' -o 'myBNX.bnx' -l 0```:
converts image using approach based on using maxima to find fluorescent marks


### Check precision of chosen configuration
Compares chosen parameters for converting BNX files to reference BNX file from Bionano using a sample of molecules in one scan.

Reference BNX file for checked scan has to be present and all images representing checked scan should be present to avoid skipping some data.

Run ``` python3 -m src.Experiments.BNXvsImage.ValidityChecker -s 1'``` to check most optimal configuration for scan 1.

### Examples:
Run ``` python3 -m src.Experiments.BNXvsImage.ValidityChecker -s 1 -t 1000 -f 'none'```: check precision for scan 1 for marks with intensity over 1000 without using any image filter

Run ``` python3 -m src.Experiments.BNXvsImage.ValidityChecker -s 1 -d 0```: check precision of fluorescent marks marked in BNX file actually being found in an image (opposite direction)

