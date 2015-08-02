Prerequisites :-

In order to use this tool you need to install Google app engine launcher or Google Cloud SDK shell.


Upload Tool:-

1. Download the folder and extract.
2. Place the csv file(s) in the same folder where app.yaml file exists.
3. Upload the app using either Google cloud SDK shell or Google app engine launcher.

Upload using Google cloud sdk shell:-
1. Invoke Google cloud sdk shell
2. cd [path where app.yaml exists]
3. Type - appcfg.py update app.yaml
4. Enter
5. Invoke url "https://2-dot-local-amenities.appspot.com/" to use the tool and upload the csv files added in the  application's directory.


Upload using Google app engine launcher:-
Assumption - After app engine installation, preferences must have been set (i.e., Python path, App engine SDK). Preferences could be accessed by clicking on Edit -> Preferences.

1. Invoke app engine launcher.
2. Add the existing application.(Click File -> Add existing application)
3. Click deploy button.
4. Invoke url "https://2-dot-local-amenities.appspot.com/" to use the tool and upload the csv files added in the  application's directory.


Limitations :- Please make sure every csv file doesn't have more than 5000 lines. Because Integration tool cannot tranform the csv lines into data models for more than 5000 lines and will display "Deadline exceeded error". Hence split your csv files into several files with 5000 lines in each and add to the app directory to upload.


