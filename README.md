# The GaiaDe Tool: Gaia Detection Tool
Input a known star via a catalogue ID (Gai DR3, TIC, HIP, HD) to produce a sensitivity map displaying Gaia's estimated ability to detect companions across a range of masses and orbital semi-major axes.

## Set-Up:
Run the following to install necessary modules (using a venv is recommended):

```
pip install -r requirements.txt
```

## Functionality:
- This tool accepts single star targets or a file with many targets (.csv or .txt)
- Accepted catalogue IDs are Gaia DR3, TIC, HIP, and HD
    - Others may work as well but have not been tested; The tool queries Simbad for the given ID
- Produce sensitivity plot of gaia's ability to detect a companion around the given star(s)
    - Creates a contour plot in 2D space defined by the companions mass and semi-major axis
    - Allows the user to understand what type of companions would be detectable around the given star(s)