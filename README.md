# zipfile-dedup
This project takes two zipfiles, and dedeupes out duplicate files in the older zip file. Files are considered a match if their timestamps are equal, or exactly 1 hour out which seems to happen across daylight savings zones or time perfiods.

The program grew out of a need of company backup zipfiles growing beyond 200GB and not using disspace on removable drives effectively.

## Usage
`zipfile-dedup.py [-h] --old FILE_1 --recent FILE_2`

Program to deduplicate redundant files using a pair of zip files. Identical files found in both zip files will be de-duped from the a new image of the 'old' file.

## Optional arguments
```
-h, --help            show this help message and exit
    
--old FILE_1, -o FILE_1
                      Old file to be 'de-duped'. The file is not replaced. Typically it would be replaced manually.
    
--recent FILE_2, -r FILE_2
                      Recent file used as the most recent master, and will remain untouched.
```

## Example 
`zipfile-dedup.py -o BackupFiles20181001.zip --recent BackupFiles20181008.zip`

The new file is dropped into `/temp/`.
