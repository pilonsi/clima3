 # AEMET OpenData Analysis Tool

Clima3 is a climate data visualization tool using the data provided by the AEMET
(Spanish Meteorological Association) OpenData API and processing it to extract the
trend for any user-selectable period, variable, and station.

The data is requested to the AEMET servers and is then processed, cleaned and holes,
if tolerable, are interpolated. Then a time series decomposition is applied (STL or
classical additive) to extract the trend, seasonal and remainder components. See 
below for more details on data handling and processing.

![Example of the analysis of mean daily temperature in the Almassora weather
station from 1971 to 2021](https://i.imgur.com/S0vASpb.png)

 ## Data processing
The data offered by the AEMET is an array of json objects, one for each day,
comprised between the selected dates for which there are records. Each json object
contains several fixed attributes about the selected weather station such as its
alphanumeric code, province, name and altitude, and the weather variables recorded
that day.

For each json in the received array the data is converted and retyped, and the fixed 
attributes are stripped, then the array is converted to a pandas dataframe using the
date as index. If for a given day there have been no records for any variable, no
object is returned from the API. The dataframe is therefore reindexed to add these 
missing days.

Sometimes, there is no data for the desired variable for the whole of the selected 
period (for example newer stations, stations that were added / removed instruments
along the years, or stations that stopped recording decades ago), or there are 
significant (multi-month, multi-year) gaps in the data. For those cases, the array
is first constrained to the actual older and newer dates for which there is data,
and then it is parsed again to look for remaining gaps in that period. Any gap bigger
than 62 days is not tolerated, and the array is constrained again, leaving the first
date after the gap as the oldest data point.

The quality of the data offered by AEMET through their OpenData API is not very
good, most datasets having missing days and big gaps of months between valid
data. The value of 62 days has been chosen because it still allows interpolation
to replicate missing data with an acceptable degree of accuracy and small impact
in large timeframes, while leaving a big portion of station datasets still useable.

To tailor the remaining data to our purposes the array is further constrained to
year boundaries, leaving out the initial or final year if not complete, and then
for leap years the data point for February the 29th is removed. Now the array can
be used for seasonal decomposition with a periodicity of 365 days.

After the array has been constrained to useable data, the remaining smaller data gaps
are interpolated using pandas' built-in interpolate function. The default
interpolation algorithm is Pchip but Akima, cubic spline, cubic, quadratic and linear
are also selectable.

Given the _random_ component of weather data, it is impossible to accurately 
replicate it when missing without using data from adjacent weather stations. Therefore,
the best option in this case is to restore the data gaps trying to follow the curve
of the seasonal component avoiding fluctuations to add the lowest error. This is why 
Pchip has been chosen as the default interpolation algorithm. Together with Akima it
is in the higher accuracy category, over single polynomials and standard splines, these
being in turn over linear interpolations. Akima, like splines, tends to overshoot and
oscillate when used in non-smooth data (like weather data) and therefore causes
undesirable spurious values which affect the later decomposition of the time series.
Pchip, being shape-preserving, follows the slope of the seasonal component more
naturally, avoiding unwanted oscillations. [1]

The interpolated data array is then fed to the time series decomposition algorithm.
It can be selected between a classical additive decomposition or an STL decomposition.

For the temperature data the STL decomposition is configured with 5 passes of the 
inner loop and no passes of the outer loop, no robustness is required since temperature
exhibits gaussian behavior. 35 is chosen as seasonal smoother based on the recommendations
from the original paper, where a dataset with similar seasonal behavior (CO2 data) is shown
as example. Testing with lower values yielded noise in the seasonal component, and higher
values had minimal change with respect to 35. The rest of the parameters are left to the
values recommended by the paper.

Sun and precipitation values do not fall in a normal distribution, and so, the
decomposition is configured with 2 passes of the inner loop and 10 of the outer loop
to add robustness iterations. For the sun data, the seasonal smoother is set to the same
value of 35 used for temperature since they have a similar seasonal pattern. The precipitation
data does not follow such a consistent pattern and as such, the seasonal smoother is set to 7,
the minimum recommended value, because if set to any higher value seasonal oscillations start
to appear in the remainder component. [2]

 ## Installation
Clone this repository and, in the source folder, run ```python3 -m pip install -r requirements.txt```
to install the required libraries. The minimum Python version is 3.7 as it is the older version
supported by PyQt6.

Once installed run ```python3 ./clima3/clima3.py```

In future revisions multithreading should be implemented to make the interface responsive while
data is being gotten from AEMET. From the time being it is recommended to check the status 
messages printed to stdout.

 ## References
[1] Dan, E. L., Dînşoreanu, M., & Mureşan, R. C. (2020). Accuracy of Six Interpolation
Methods Applied on Pupil Diameter Data. Transylvanian Institute of Neuroscience.
Available at: https://muresanlab.tins.ro/publications/preprints/Dan_et_al_AQTR_2020.pdf


[2] Cleveland, R. B., Cleveland, W. S., McRae J. E., &  Terpenning, I. (1990). STL: A
Seasonal-Trend Decomposition Procedure Based on Loess. Journal of Official Statistics.
Statistics Sweden. Available at: https://www.wessa.net/download/stl.pdf
