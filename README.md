# The GaiaDe (Guide) Tool: Gaia Detection Tool
Input a known star via a catalogue ID (Gai DR3, TIC, HIP, HD) to produce a sensitivity map displaying Gaia's estimated ability to detect companions across a range of masses and orbital semi-major axes.

## Set-Up:
Run the following to install necessary modules (using a venv is recommended):

```
pip install -r requirements.txt
```

## Running the tool:
The tool is run via command line arguments with the following formats:

<ins>Single Target Example</ins>
```
python main.py TIC 408618999
```

<ins>Miltiple Objects in File Example</ins>
```
python main.py example_list.csv
```

<ins>Optional Flags</ins>

- ```--load_file example.pkl``` is used to load a previous query

- ```--dr5``` is used to change the observing timeline from the default of DR4 (5.5 years) to DR5 (10.5 years)
    - This changes the range of considered AU (period) values

## Functionality:
- This tool accepts single star targets or a file with many targets (.csv or .txt)
- Accepted catalogue IDs are Gaia DR3, TIC, HIP, and HD
    - Others may work as well but have not been tested; the tool queries Simbad for the given ID
- Produce sensitivity plot of gaia's ability to detect a companion around the given star(s)
    - Creates a contour plot in 2D space defined by the companions mass and semi-major axis
    - Allows the user to understand what type of companions would be detectable around the given star(s)

- If a query has already been run and you would like to interact with the data from that query again, the returned query will be saved as a .pkl file
    - by adding the ```--load_file``` keyword to the command line arguments, you can specify the file name of the saved query .pkl file and bypass the need to run the query again
    - example:

```
python main.py --load_file gaia_query_results.pkl
```
