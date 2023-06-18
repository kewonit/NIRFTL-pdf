# NIRFTL-pdf

Extracting data from nirf pdfs using pdfquery &amp; pandas

The values inside the text box, [76.54, 347.551, 92.108, 354.511] in the snippet refers the “Left, Bottom, Right, Top” coordinates of the text box.
You can think about the pdf page in terms of X-Y coordinates. The X-axis spans the width of the PDF page and the Y-axis spans the height of the page.
Every element has its bounds defined by a bounding box which consists of 4 coordinates.
These coordinates (X0, Y0, X1, Y1) represent left, bottom, right and top of the text box, which would give us the location of data we are interested in the PDF page.

Using the textbox coordinates from the XML file, we can extract each piece of relevant information individually using their corresponding text box coordinates, 
and then combined all scraped information into single observation. 
In the following, we write a function to use “pdf.pq(‘LTTextLineHorizontal:overlaps_bbox(“#, #, #, #”)’).text()” to extract the data inside each textbox, then use pandas to construct a dataframe.

[More info at this blog](https://towardsdatascience.com/scrape-data-from-pdf-files-using-python-and-pdfquery-d033721c3b28)

BTW this is built just for BTECH (Engineering) NIRF data!
