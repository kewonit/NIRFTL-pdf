import csv
import os
import pdfquery
import pandas as pd
import re


def pdfscrape(pdf):
    # The values inside the text box, [76.54, 347.551, 92.108, 354.511] in the snippet refers the “Left, Bottom, Right, Top” coordinates of the text box.
    # You can think about the pdf page in terms of X-Y coordinates. The X-axis spans the width of the PDF page and the Y-axis spans the height of the page.
    # Every element has its bounds defined by a bounding box which consists of 4 coordinates.
    # These coordinates (X0, Y0, X1, Y1) represent left, bottom, right and top of the text box, which would give us the location of data we are interested in the PDF page.

    # Using the textbox coordinates from the XML file, we can extract each piece of relevant information individually using their corresponding text box coordinates,
    # and then combined all scraped information into single observation.
    # In the following, we write a function to use “pdf.pq(‘LTTextLineHorizontal:overlaps_bbox(“#, #, #, #”)’).text()” to extract the data inside each textbox,
    # then use pandas to construct a dataframe.
    # More info at https://towardsdatascience.com/scrape-data-from-pdf-files-using-python-and-pdfquery-d033721c3b28
    # BTW this is built just for BTECH data

    # Extract just the ID from the box of name & id
    institute_id = pdf.pq(
        'LTTextLineHorizontal:overlaps_bbox("10.0, 524.137, 276.13, 533.137")').text()
    # Extact just the Title from the box of name & id
    institute_name = pdf.pq(
        'LTTextLineHorizontal:overlaps_bbox("10.0, 524.137, 276.13, 533.137")').text()
    year = pdf.pq(
        'LTTextLineHorizontal:overlaps_bbox("426.0, 168.551, 451.683, 175.551")').text()
    no_of_mean_package = pdf.pq(
        'LTTextLineHorizontal:overlaps_bbox("668.8, 151.0, 751.4, 182.0")').text()
    graduating_in_stipulated_time = pdf.pq(
        'LTTextLineHorizontal:overlaps_bbox("508.6, 168.551, 520.276, 175.551")').text()
    placed_in_the_year = pdf.pq(
        'LTTextLineHorizontal:overlaps_bbox("591.2, 168.551, 602.876, 175.551")').text()
    no_of_higher_edu = pdf.pq(
        'LTTextLineHorizontal:overlaps_bbox("756.4, 168.551, 768.076, 175.551")').text()
    college_tier = pdf.pq(
        'LTTextLineHorizontal:overlaps_bbox("668.8, 151.0, 751.4, 182.0")').text()
    no_of_male_students = pdf.pq(
        'LTTextLineHorizontal:overlaps_bbox("76.54, 347.551, 92.108, 354.551")').text()
    no_of_female_students = pdf.pq(
        'LTTextLineHorizontal:overlaps_bbox("140.08, 347.551, 151.756, 354.551")').text()
    total_students = pdf.pq(
        'LTTextLineHorizontal:overlaps_bbox("203.62, 347.551, 219.188, 354.551")').text()

    # Extra Data
    previous_year = pdf.pq(
        'LTTextLineHorizontal:overlaps_bbox("426.0, 192.551, 451.683, 199.551")').text()
    second_to_last = pdf.pq(
        'LTTextLineHorizontal:overlaps_bbox("426.0, 209.551, 451.683, 216.551")').text()
    previous_year_mean_package = pdf.pq(
        'LTTextLineHorizontal:overlaps_bbox("673.8, 192.551, 736.842, 199.551")').text()
    second_to_last_mean_package = pdf.pq(
        'LTTextLineHorizontal:overlaps_bbox("673.8, 209.551, 744.227, 216.551")').text()
    cat_id = pdf.pq(
        'LTTextLineHorizontal:overlaps_bbox("10.0, 524.137, 343.657, 533.137")').text()

    # Split text
    institute_id = extract_id_from_xml(institute_id)
    institute_name = extract_title_from_xml(institute_name)
    no_of_mean_package = extract_numeric_value(no_of_mean_package)
    previous_year_mean_package = extract_numeric_value(
        previous_year_mean_package)
    second_to_last_mean_package = extract_numeric_value(
        second_to_last_mean_package)
    cat_id = extract_id_from_xml(cat_id)

    # To determine the college tier on the basis of mean package
    college_tier = determine_tier(no_of_mean_package)

    # Combine all relevant information into a single observation
    page = pd.DataFrame({
        'institute_id': institute_id,
        'institute_name': institute_name,
        'year': year,
        'no_of_mean_package': no_of_mean_package,
        'college_tier': college_tier,
        'graduating_in_stipulated_time': graduating_in_stipulated_time,
        'placed_in_the_year': placed_in_the_year,
        'no_of_higher_edu': no_of_higher_edu,
        'no_of_male_students': no_of_male_students,
        'no_of_female_students': no_of_female_students,
        'total_students':  total_students,
        'source_pdf': f"https://www.nirfindia.org/nirfpdfcdn/2022/pdf/Engineering/{institute_id}.pdf",
        # Extra Data
        'previous_year':  previous_year,
        'second_to_last': second_to_last,
        'previous_year_mean_package': previous_year_mean_package,
        'second_to_last_mean_package': second_to_last_mean_package,
        'cat_id': cat_id
    }, index=[0])
    return page


def extract_id_from_xml(xml_text):
    # Extract the id without the institute name
    match = re.search(r'\[(.*?)\]', xml_text)
    if match:
        value = match.group(1)
        return value
    else:
        return ""


def extract_title_from_xml(xml_text):
    # Extract the institute name without the ID
    match = re.search(r'Institute Name: (.*?) \[', xml_text)
    if match:
        value = match.group(1)
        return value.strip()
    else:
        return ""


def determine_tier(mean_package):
    if mean_package:
        mean_package = extract_numeric_value(mean_package)
        # Deciding college tier on the basis on mean package
        if mean_package:
            mean_package = float(mean_package)
            if mean_package > 1000000:
                return '1'
            elif mean_package > 500000:
                return '2'
            else:
                return '3'
    return 'err'


def extract_numeric_value(value):
    # Remove non-numeric characters from the value
    value = re.sub('[^0-9.]', '', value)

    # Handle cases where the value contains both numbers and words
    if value:
        # Check if the value contains a decimal point
        if '.' in value:
            # Split the value into integer and fractional parts
            integer_part, fractional_part = value.split('.')
            # Remove any non-numeric characters from the integer part
            integer_part = re.sub('[^0-9]', '', integer_part)
            # Combine the cleaned integer and fractional parts
            value = f"{integer_part}.{fractional_part}"
        else:
            # Remove any non-numeric characters
            value = re.sub('[^0-9]', '', value)

    return value


# Path for input and output files
input_folder_path = './test'
output_file = 'output.csv'


# Iterate over PDF files in the folder
for filename in os.listdir(input_folder_path):
    if filename.endswith('.pdf'):
        file_path = os.path.join(input_folder_path, filename)

        # Extract institute ID from the filename
        institute_id = os.path.splitext(filename)[0]
        # Converting PDF into an Extensible Markup Language (XML), which includes data and metadata of a given PDF page
        pdf = pdfquery.PDFQuery(file_path)
        pdf.load(0)  # Load only the first page
        # pdf.tree.write('pdfXML.txt', pretty_print=True) is a performance bottleneck when scraping large number of pdfs, remove it after allocating the coordinates
        pdf.tree.write('pdfXML.txt', pretty_print=True)

        # Scrape the first page
        page = pdfscrape(pdf)

        # Save to output.csv without leaving lines between them
        with open(output_file, 'a', newline='') as f:
            writer = csv.writer(f)
            if f.tell() == 0:
                writer.writerow(page.columns)
            writer.writerow(page.values.flatten())
