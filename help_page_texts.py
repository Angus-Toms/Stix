# Headings
headings = [
    "Overview",
    "Step-by-step guide",
    "Notes on methodology",
    "Caveats"
]

# Initial appraisal tab
initial_overview = """The Initial Appraisal is the easiest and fastest \
appraisal performed by Stix Flood Assessment Systems, it requires \
very few data to complete and can generate results in less than 60 \
seconds. Because of this, Initial Appraisals are only recommended \
for initial assessments and pipeline projects. More detailed results \
can be achieved with Stix's Overview and Detailed Appraisals where \
data are available."""
initial_step_by_step = """- Begin an appraisal by selecting the Start \
Appraisal and then Start Initial Appraisal buttons from the Stix home \
page. \n\n- Select the Edit Flood Event Details button to the upper-left of \
the page and enter the required information about your flood event in the \
dialog box that has opened. \n\n- Select Save on the dialog box and check that \
the flood event details have been updated. \n\n- Calculate your results by \
selecting the Generate Results button in the Results box. The results table \
will be automatically updated, displaying the results of the appraisal. \n\n- \
More detailed results can be viewed by selecting the View Breakdown button \
in the Advanced box at the bottom of the page. Here you can view more advanced \
information on the number of properties at risk as well as pre-intervention \
damages. \n\n- To export your results, first select the Export Results button \
found in the Advanced box. Select which data you would like to export and the \
file formats you would like them to be exported to. Select Export and enter a \
name when prompted. \n\n- To save your appraisal, select the Save Appraisal \
button found in the Advanced box. Enter a name when prompted and a .Stix file \
will be created containing all the information about your appraisal. If you \
want to come back to your appraisal at any time, select the Open Appraisal \
button on the Stix home page and select your saved .Stix file."""
initial_methodology_notes = """- A weighting is applied depending on whether \
the catchment is in an urban or rural location. This takes into account costs \
of emergency and recovery services and is based on data from the 2000 and \
2007 flood events. \n\n- The flooding characteristics of the catchment are \
described by 6 discrete return periods. This introduces uncertainty into the \
results, represented as an upper and lower bound. The upper bound assumes that \
properties in a 1 in 25 year risk band will flood in a 1 in 11 year event. \
The lower bound assumes that the same properties will not flood in a 1 in 24 \
year event. The real situation will be somewhere in between, however, it is \
suggested that the lower bound is used when calculating scheme viability."""
initial_caveats = """- The number of properties in each risk band and their \
associated damages are based on national averages from the Multi-Coloured \
Manual and are not necessarily representative of your catchment. \n\n- This \
method only considers damages to residential properties. If there are a \
significant number of non-residential properties in your catchment, the \
results will likely be an underestimation. \n\n- All methods assume that \
average annual damage does not change over the appraisal duration, so does \
not take into account future climate change, land-use change etc., which \
will cause the average annual damage to change over time."""

initial_texts = [
    initial_overview,
    initial_step_by_step,
    initial_methodology_notes,
    initial_caveats
]

# Overview appraisal texts
overview_overview = """The Overview Appraisal is the intermediate level \
appraisal performed by Stix Flood Assessments. It provides more accurate \
and representative results than the Initial Appraisal but requires more \
data to complete. This also increases the time taken to perform appraisals.  \
Overview Appraisals are recommended for strategic outline cases. More \
detailed results can be achieved with Stix's Detailed Appraisal where data \
are available."""
overview_step_by_step = """- Begin an appraisal by selecting the Start \
Appraisal and then Start Overview Appraisal buttons from the Stix home \
page. \n\n- Select the Edit Flood Event details button to the upper-left \
of the page and enter the required information about your flood event in \
the dialog box that has opened. \n\n- Select Save on the dialog box and \
check that the flood event details have been updated. \n\n- Enter the \
cumulative number of residential properties in the Properties at risk \
column in the Residential Properties box, double-count will automatically \
be removed in the following column. \n\n- Enter the cumulative floor area \
of non-residential properties in the each applicable column of the \
Non-Residential Properties box, double-count will automatically be removed \
in the following column. \n\n- Blank columns will be assumed to contain 0 \
properties/area at risk. \n\n- Ensure no columns contain yellow warnings \
indicating invalid entries, all entries must be positive and each entry \
column must be increasing. \n\n- Move to the Results Tab and calculate \
your results by selecting the Generate Results button in the Results \
box. The results table will be automatically updated. \n\n- More \
detailed results can be viewed by selecting the View Breakdown in the \
Advanced box at the bottom of the page. Here you can view more advanced \
information on the number of properties at risk as well as pre and \
post-intervention damages. \n\n- To export your results, first select the \
Export Results button found in the Advanced box. Select which data you \
would like to export and the file formats you would like them to be \
exported to. Select Export and enter a name when prompted. \n\n- To save \
your appraisal, select the Save Appraisal button found in the Advanced \
box. Enter a name when prompted and a .Stix file will be created \
containing all the information about your appraisal. If you want to \
come back to your appraisal at any time, select the Open Appraisal \
button on the Stix home page and select your saved .Stix file."""
overview_methodology_notes = """- To calculate a result, data is required \
for every risk band of a given property type. If data is incomplete, \
consider interpolating values to get a best-estimate. \n\n- The flooding \
characteristics of the catchment are described by 7 discrete return periods. \
This introduces uncertainty into the results, represented by an upper and \
lower bound. The upper bound assumes that properties in a 1 in 25 year risk \
band will flood in a 1 in 11 year flood event. The lower bound assumes that \
the same properties will not flood in a 1 in 24 year event. The real \
situation will be somewhere in between, however, it is suggested that \
the lower bound is used when calculating scheme viability."""
overview_caveats = """- This method does not take into account the depth of \
flooding, as the damage per property is still calculated based on national \
average data. This is a significant source of uncertainty. \n\n- This method \
assumes that average annual damage does not change over the appraisal \
duration, so does not take into account future climate change, land-use \
change etc,. which will cause the average annual damages to change over \
time. \n\n- All methods assume that average annual damage does not change \
over the appraisal duration, so does not take into account future climate \
change, land-use change etc., which will cause the average annual damage to \
change over time."""

overview_texts = [
    overview_overview,
    overview_step_by_step,
    overview_methodology_notes,
    overview_caveats
]

# Detailed appraisal texts
detailed_overview = """The Detailed Appraisal is the most advanced and \
comprehensive appraisal performed by Stix Flood Assessment Systems, it \
can produce extensive property-by-property results in as little as 5 minutes. \
Detailed Appraisals require a large amount of data including National \
Receptors Dataset extracts and Flood Depths. Because of this, Detailed \
Appraisals are recommended for Outline Business Cases. Broader results can \
be achieved with Stix's Overview and Initial Appraisals where data are \
not available. """
detailed_step_by_step = """- Begin an appraisal by selecting the Start \
Appraisal and then Start Detailed Appraisal buttons from the Stix home \
page. \n\n- Select the Edit Flood Event Details button to the left of the \
page and enter the required information about your flood event in the \
General Flood Information and Damage Capping boxes that appear. \n\n- You \
can also change the number and length of the return periods used in your \
appraisal. Use the Add Flood Event and Remove Flood Event buttons as well \
as the spinboxes in the Flood Event box to do so. This information is \
required when uploading flood depth datasets and so must be saved before \
doing so. \n\n- Select Save on the dialog box and check that the flood event \
details have been updated. \n\n- Select the Upload Dataset button in the Upload \
Properties box and select an extract of the National Receptors Dataset \
covering the catchment. Stix supports the upload of .csv and .dbf \
files. \n\n- Your selected dataset will be displayed in a new window where you \
can manually edit any entries to correct any errors that may be present. \n\n- \
To allow Stix to correctly parse property information, you must select the \
columns that contain vital information such as location, address, and floor \
area. This can be done by selecting the Select Columns button at the top of \
the new window. \n\n- To check you entries, select the Preview Properties Found \
button to view the properties that have been parsed from your dataset. \n\n- \
Select Save and all properties found in your dataset will be uploaded to \
your appraisal. Entries with invalid location, floor area, or MCM code \
data, headings, blank rows, etc. will not be included. \n\n- Uploaded \
properties can now be viewed under the Residential and Non-Residential tabs. \
\n\n- You can upload multiple datasets and add properties manually with the \
Upload Property Manually button where you will be prompted to enter the \
required information by hand. \n\n- All information can be edited after \
upload by selecting the Edit buttons under the Residential and \
Non-Residential tabs. \n\n- Select the Upload Dataset button in the Upload \
ASCII Grids box and select ASCII grid(s) covering the catchment. Stix \
supports the upload of .asc files. \n\n- Uploaded grids can now be viewed \
under the ASCII Grids tab. \n\n- You can upload datasets as many times as \
needed. \n\n- Select the Upload Dataset button in the Upload Flood Event \
Shapefiles box. Stix supports the upload of .csv and .dbf files. \n\n- \
Your selected dataset will be displayed in a new window where you can \
manually edit any entries to correct any errors that may be present. \
\n\n- To allow Stix to correctly parse Flood Depths you must select the \
columns that contain vital information. This can be done by selecting \
the Select Columns button at the top of the new window. \n\n- The return \
periods used in a Flood Depth shapefile must match those entered earlier. \
For example, if your shapefile records depths during 1 in 5, 10, 25, 50, \
and 100 year events then these 5 return periods must be entered in your \
General Flood Information. \n\n- To check you entries, select the Preview \
Nodes Found button to view the data points that have been parsed from your \
dataset.  \n\n- Select Save and all nodes found in your dataset will be \
uploaded to your appraisal. Entries with invalid location or depth data, \
headings, blank rows, etc. will not be included. \n\n- Uploaded nodes can \
now be viewed under the Nodes tab. \n\n- You can upload datasets as many times \
as needed. \n\n- All information can be edited after upload by selecting the \
Edit buttons under the Node tab. \n\n- Move to the Residential and \
Non-Residential tabs and select the Generate Ground Levels buttons \
located at the bottom of the page, this will generate a ground level for \
each uploaded property based on the uploaded ASCII grid(s). If the uploaded \
ASCII grid(s) don’t cover a given property you will prompted to upload more \
grids or set a ground level manually using the Edit buttons. \n\n- Choose \
which properties and nodes you want to be included in your appraisal by \
checking and unchecking the small boxes to the top-left of each display \
on the Residential, Non-Residential, and Nodes tabs. Greyed-out properties \
and nodes won’t be included in results calculations. \n\n- Calculate your \
results by moving to the Results Tab and selecting the Generate Results \
button in the Results box, the results table will be automatically updated. \
\n\n- More detailed results can be viewed by selecting the View Damages \
Breakdown and View Benefits Breakdown buttons in the Advanced box at the \
bottom of the page. Here you can view property-by-property breakdowns of \
intangible, mental health, evacuation and vehicle damages and costs as well \
as flood depths at each property during each flood event. \n\n- To export your \
results, first select the Export Results button found in the Advanced box. \
Select which data you would like to export and the file formats you would \
like them to be exported to. Select Export and enter a name when \
prompted. \n\n- To save your appraisal, select the Save Appraisal button \
found in the Advanced box. Enter a name when prompted and a .Stix file will \
be created containing all the information about your appraisal. If you want \
to come back to your appraisal at any time, select the Open Appraisal button \
on the Stix home page and select your saved .Stix file."""
detailed_methodology_notes = """- This method checks if the lifetime damage \
for a property exceeds the average property value of the catchment, if damage \
capping is enabled then exceeding lifetime damages will be capped. \n\n- \
Intangible damages measure how much a household would be willing to pay for \
improvement of flood defences to avoid the stress and inconvenience resulting \
from physical health impacts, disruption to normal life, and loss of \
irreplaceable items due to flooding. \n\n- Intangible benefits are calculated \
directly from the existing and design SOP, this is different to the other \
benefits in this method. \n\n- Mental health damages is not a part of the MCM, \
rather it is based on new DEFRA guidance and estimates the cost of increased \
mental health disorders such as anxiety, depression, and PTSD after a flood \
event \n\n- 0.15m is added to capped depth data when calculating vehicular \
damages to account for internal property threshold. \n\n- For evacuation \
cost category see the Multi Coloured Handbook, Chapter 4. “Mid” is the \
assumed default value if no other information is given."""
detailed_caveats = """- Even this level of appraisal doesn't take into account \
all factors. Delays, agriculture, ecosystem, and non-financial costs and \
benefits have not been calculated and should be taken into account during \
a complete appraisal. \n\n- All methods assume that average annual damage does \
not change over the appraisal duration, so does not take into account future \
climate change, land-use change etc., which will cause the average annual \
damage to change over time."""

detailed_texts = [
    detailed_overview,
    detailed_step_by_step,
    detailed_methodology_notes,
    detailed_caveats
]

faq_questions = [
    """Who can use Stix Flood Assessment Systems?""",
    """I have questions / feedback / comments about Stix Flood Assessment \
Systems. What do I do? """
]
faq_answers = [
    """Anyone. Stix may be used for personal or commercial use and will \
remain free for all to use forever. """,
    """Message the developer or submit a pull request to the GitHub page. The \
developer can be reached at angus.toms@icloud.com or \
linkedin.com/in/angus-toms/ ."""
]
