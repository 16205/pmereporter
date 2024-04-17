import json
import sys
import utils
from tqdm import tqdm
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, PageBreak, LayoutError
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY
from datetime import datetime

def get_resources_from_departments(departments):
    """
    Extracts and returns the keys of resources from the given departments.

    This function assumes that the input 'departments' is a response object from a request (e.g., from requests library)
    which contains a JSON body with a list of resources. It parses this JSON to extract the 'key' of each resource
    within the 'resources' list.

    Parameters:
    - departments: A response object that can be converted to JSON, expected to contain a 'resources' list.

    Returns:
    - A list of strings, where each string is the 'key' of a resource found in the input 'departments'.
    """

    departments = departments.json()

    keys = [resource['key'] for resource in departments['resources']]

    return keys

def generate_pdfs(missions:dict, sources:dict):
    """
    Generates PDF documents for each mission in the provided missions list, including ADR information and other mission details.

    Parameters:
    - missions (dict): A dictionary containing mission items, each with details such as start/end times, resources, customers, and ADR source information.
    - sources (dict): A dictionary containing source items with details such as UN number, package, isotope, activity, and other ADR relevant information.

    The function iterates over each mission, compiles relevant information into a structured format, and generates a PDF document for that mission.
    The generated PDF includes mission details, agent and client information, ADR information for sources involved in the mission, and signature fields.
    """

    print("Generating pdfs...")

    # Define styles
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Justify', parent=styles['Normal'], fontSize=10, fontName='Helvetica', alignment=TA_JUSTIFY,))
    smaller_font_style = ParagraphStyle('SmallerFont', parent=styles['Normal'], fontSize=9, fontName='Helvetica')

    for mission in tqdm(missions["items"]):
        resources = {}
        # customers = {}
        for resource in mission["resources"]:
            if not resource['label'].startswith("RG -") and not resource['label'].startswith("BUNKER ") and not resource['label'].startswith("Vincotte") and not resource['label'].startswith("LABO "):
                resources[f"{resource['key']}"] = {'name': resource['label'], 'phone1': resource['mobile'], 'phone2': resource['phone']}
        # for customer in mission["customers"]:
        #     # customers[f"{customer['key']}"] = {'name': customer['label'], 'phone1': customer['phone'], 'phone2': customer['mobile']}
        #     customers['key'] = customer

        # Create a PDF document
        doc = SimpleDocTemplate(f".\generated\{mission['key']}.pdf", pagesize=A4, topMargin=100)

        # Create content elements
        elements = []

        # Add content:
        # Title
        elements.append(Paragraph(f"Mission order n° {mission['key']} - Vinçotte NDT", styles['Title']))
        elements.append(Spacer(1, 10))

        # Mission details heading -------------------------------------
        elements.append(Paragraph(f"Mission details", styles['Heading2']))
                
        # Table data
        mission_table_data = []
        
        # Parse the datetime string into a datetime object
        datetime_start = datetime.strptime(mission['start'], "%Y-%m-%dT%H:%M:%S")
        datetime_end = datetime.strptime(mission['end'], "%Y-%m-%dT%H:%M:%S")
            
        # Date and time
        mission_table_data.append([Paragraph("<b>Date of intervention</b>"), Paragraph(f"{datetime_start.strftime('%d/%m/%Y')}")])
        mission_table_data.append([Paragraph("<b>Start time</b>"), Paragraph(f"{datetime_start.strftime('%H:%M')}")])
        mission_table_data.append([Paragraph("<b>End time</b>"), Paragraph(f"{datetime_end.strftime('%H:%M')}")])
        
        # Agents
        for index, item in enumerate(resources):
            agent_name_label = "<b>Agent</b><br/><br/>" if len(resources) == 1 else f"<b>Agent {index+1}</b><br/><br/>"
            agent_name = resources[item]['name']+"<br/>"
            
            agent_phone_label = "<b>Phone</b>"
            agent_phone1 = ""
            agent_phone2 = ""
            if resources[item]['phone1'] != '+32' and not None:
                agent_phone1 = "<br/>"+resources[item]['phone1']
            if resources[item]['phone2'] != '+32' and not None:
                if resources[item]['phone2'] != resources[item]['phone1']:
                    agent_phone2 = "<br/>"+resources[item]['phone2']
            
            mission_table_data.append([Paragraph(agent_name_label+agent_phone_label), 
                                       Paragraph(agent_name+agent_phone1+agent_phone2)])
            
        # Clients
        for index, item in enumerate(mission['customers']):
            client_name_label = "<b>Client</b><br/><br/>" if len(mission['customers']) == 1 else f"<b>Client {index+1}</b><br/><br/>"    
            client_name = mission['customers'][index]['label']+"<br/>"

            client_phone_label = "<b>Phone</b>"
            client_phone1 = ""
            client_phone2 = ""
            if mission['customers'][index]['phone'] != '+32' and not None:
                client_phone1 = "<br/>"+mission['customers'][index]['phone']
            if mission['customers'][index]['mobile'] != '+32' and not None:
                if mission['customers'][index]['mobile'] != mission['customers'][index]['phone']:
                    client_phone2 = "<br/>"+mission['customers'][index]['mobile']
            
            mission_table_data.append([Paragraph(client_name_label+client_phone_label), 
                                       Paragraph(client_name+client_phone1+client_phone2)])

        # Service order number
        if 'project' in mission and mission['project']['fields']['PROJET_SO_NUMBER'] is not None:
            so_number = (mission['project']['fields']['PROJET_SO_NUMBER']).lstrip("0")
            mission_table_data.append([Paragraph("<b>Service order n°</b>"), Paragraph(f"{so_number}")])
        
        # Location
        if 'location' in mission:
            if mission['location'] is not None:
                mission_table_data.append([Paragraph("<b>Intervention location</b>"), Paragraph(f"{mission['location']}")])
        else: 
            sys.exit('Mission intervention location missing, please first run ingest.get_locations()!')

        # Departure location
        departureplace = mission.get('fields').get('DEPARTUREPLACE')
        if departureplace is not None and departureplace!= '':
            mission_table_data.append([Paragraph("<b>Departure location</b>"), Paragraph(f"{departureplace}")])

        # Info/comments
        comments1 = mission.get('fields').get('COMMENTS_LOCATION')
        comments2 = mission.get('remark')
        comments3 = mission.get('fields').get('TASKCOMMENTS')
        comments4 = mission.get('customers')[0].get('fields').get('COMMENTSCUSTOMER')
        
        # Group comments in list
        comments = [comments1, comments2, comments3, comments4]

        # Format text for pretty display
        for i in range(len(comments)):
            if comments[i] is not None:
                comments[i] = utils.format_text(comments[i])
                
        # Add separator between different types of comments
        separator = "<br/>----------------------------------------------------------------------------------------------<br/>"
        comments_text = separator.join([comment for comment in comments if comment])

        comments_paragraph = []
        max_height = 500
        max_width = 320
        actual_height = utils.calculate_paragraph_height(comments_text, max_width, styles['Normal'])

        if actual_height > max_height:
            # Split total comments text into two paragraphs if height > max height
            comments_paragraph = utils.ajust_paragraph_height(comments_text, max_height, max_width, styles['Normal'])
        else:
            comments_paragraph.append(comments_text)

        # Print one paragraph per table row
        for comment in comments_paragraph:
            if comment is not None and comment != '':
                mission_table_data.append([Paragraph("<b>Remarks/comments</b>"), 
                                           Paragraph(comment)])

        # Create the table with the mission data
        mission_table = Table(mission_table_data, colWidths=[111, None])

        # Define a TableStyle
        style = TableStyle([
            ('TEXTCOLOR', (0,0), (-1,0), colors.black),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('GRID', (0,0), (-1,-1), 1, colors.darkslategray),
        ])

        # Apply the style to the table
        mission_table.setStyle(style)

        # Add table to list of flowables
        elements.append(mission_table)

        # Norms & criteria
        norm_crit_list = [mission.get('fields').get('NORMCR1'),
                          mission.get('fields').get('NORMCR2'),
                          mission.get('fields').get('NORMCR3'),
                          mission.get('fields').get('NORMCR4'),
                          mission.get('fields').get('NORMCR5'),
                          mission.get('fields').get('NORMCR6'),
                          mission.get('fields').get('NORMCR7')]
        
        # Check if any norms or criteria are present, that is not None
        if any(norm_crit_list):        
            elements.append(Paragraph("Norms & criteria", styles['Heading3']))

            norm_crit_table_data = []

            j = 1
            for norm_crit in norm_crit_list:
                if norm_crit is not None and norm_crit != '':
                    norm_crit_table_data.append([Paragraph(f"<b>Norm/Criteria {j}</b>"), Paragraph(norm_crit)])
                    j += 1

            norm_crit_table = Table(norm_crit_table_data, colWidths=[111, None])
            norm_crit_table.setStyle(style)

            elements.append(norm_crit_table)

        # ADR Information -------------------------------------
        # Check if RT mission
        s1 = mission['fields']['SOURCES']
        s2 = mission['fields']['SOURCESII']
        s3 = mission['fields']['SOURCESIII']
        if (s1 is not None or s2 is not None or s3 is not None) and (s1 != "" or s2 != "" or s3 != ""):
            elements.append(PageBreak())
            elements.append(Paragraph("<b>ADR Informatie / Information ADR</b>", styles['Heading2']))

            # Sender / Receiver table
            s_r_table_data = []
            s_r_table_data.append([Paragraph("<b>Verzender / Expéditeur</b>"),
                                   Paragraph("<b>Bestemmeling / Destinataire</b>")])
            addresses = {'Villers-Le-Bouillet': 'Rue de la métallurgie 47<br/>4530 Villers-Le-Bouillet',
                         'Houdeng': 'Chaussée Paul Houtart 88<br/>7100 Houdeng-Goegnies'}
            if 'Houdeng' in departureplace:
                departureplace = 'Houdeng'
            s_r_table_data.append([Paragraph(f"Vinçotte NV<br/><br/>{addresses.get(departureplace)}"),
                                   Paragraph(f"{client_name}<br/>{mission['location']}")])
            s_r_table = Table(s_r_table_data)
            s_r_table.setStyle(style)
            elements.append(s_r_table)
            
            # Description
            elements.append(Paragraph("<b>Getransporteerde ADR stoffen: / Marchandises ADR transportées:</b>", styles['Heading3']))
            
            # Set variables containing sources identification
            mission_sources = []

            if mission['fields']['SOURCES'] != "" and not None:
                mission_sources.append(mission['fields']['SOURCES'])
            if mission['fields']['SOURCESII'] != "" and not None:
                mission_sources.append(mission['fields']['SOURCESII'])
            if mission['fields']['SOURCESIII'] != "" and not None:
                mission_sources.append(mission['fields']['SOURCESIII'])
            if mission['fields']['SOURCESIV'] != "" and not None:
                mission_sources.append(mission['fields']['SOURCESIV'])
            
            i=0
            for source in mission_sources:
                if len(mission_sources)>1:
                    i+=1
                    elements.append(Paragraph(f"<b>Isotope {i}</b>", styles['Heading4']))

                # Table data
                ADR_table_data = []

                # Source internal identification (Vincotte)
                ADR_table_data.append([Paragraph(f"<b>Identificatie /<br/>Identification</b>", smaller_font_style),
                                       Paragraph(f"{source}", smaller_font_style)])
                
                # UN Number & description
                UN_number = sources[source]['UNnumber']
                package = sources[source]['Package']
                ADR_table_data.append([Paragraph(f"<b>Beschrijving /<br/>Description</b>", smaller_font_style),
                                       Paragraph(f"{UN_number} RADIOACTIEVE STOFFEN, IN COLLI VAN TYPE {package}, 7, (E) /<br/>{UN_number} MATIÈRES RADIOACTIVES EN COLIS DE TYPE {package}, 7, (E)", smaller_font_style)])
                
                # Isotope
                isotope = sources[source]['Isotope']
                ADR_table_data.append([Paragraph(f"<b>Isotoop /<br/>Isotope</b>", smaller_font_style),
                                       Paragraph(f"{isotope}", smaller_font_style)])
                
                # Activity
                A0 = sources[source]['GBq']
                A0_date = utils.iso_to_datetime(sources[source]['Calibrationdate'])

                GBq, Ci = compute_activity(A0, A0_date, isotope, datetime_start)
                ADR_table_data.append([Paragraph(f"<b>Activiteit op {datetime_start.strftime('%d/%m/%Y')} /<br/>Activité le {datetime_start.strftime('%d/%m/%Y')}</b>", smaller_font_style),
                                       Paragraph(f"{GBq} GBq - {Ci} Ci", smaller_font_style)])
                
                # Package category
                pckg_category = sources[source]['Label']
                ADR_table_data.append([Paragraph(f"<b>Label /<br/>Étiquette</b>", smaller_font_style),
                                       Paragraph(f"{pckg_category}", smaller_font_style)])
                
                # Transport index
                transport_index = sources[source]['Transportindex']
                ADR_table_data.append([Paragraph(f"<b>Transportindex /<br/>Indice de transport</b>", smaller_font_style),
                                       Paragraph(f"{transport_index}", smaller_font_style)])
                
                # Physical state
                physical_state = sources[source]['Physicalstate']
                ADR_table_data.append([Paragraph(f"<b>Fysiche toestand /<br/>État physique</b>", smaller_font_style),
                                       Paragraph(f"{physical_state}", smaller_font_style)])
                
                # Certificate
                certificate = sources[source]['Certificate']
                ADR_table_data.append([Paragraph(f"<b>Goedkeuringscertificaat /<br/>Certificat d'approbation</b>", smaller_font_style),
                                       Paragraph(f"{certificate}", smaller_font_style)])
                
                # Certificate (Special Form)
                certificate_sf = sources[source]['Certificate_x0028_specialform_x0']
                if certificate_sf is not None:
                    ADR_table_data.append([Paragraph(f"<b>Goedkeuringscertificaat - Special Form /<br/>Certificat d'approbation - Forme spéciale</b>", smaller_font_style),
                                       Paragraph(f"{certificate_sf}", smaller_font_style)])
                    
                # TODO: Replace dict accesses by .get() to avoid errors when none

                # Focus
                focus = sources.get(source).get('Focus')
                if focus is not None:
                    ADR_table_data.append([Paragraph("<b>Focus /<br/>Foyer</b>", smaller_font_style),
                                       Paragraph(f"{focus} mm", smaller_font_style)])

                # Create the table with the data
                ADR_table = Table(ADR_table_data, colWidths=[120, None])

                # Define a TableStyle
                styleADR = TableStyle([
                    ('TEXTCOLOR', (0,0), (-1,0), colors.black),
                    ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                    ('VALIGN', (0,0), (-1,-1), 'CENTER'),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 4.9),
                    ('TOPPADDING', (0,0), (-1,-1), 4.9),
                    ('GRID', (0,0), (-1,-1), 1, colors.darkslategray),
                ])

                # Apply the style to the table
                ADR_table.setStyle(styleADR)

                # Add table to list of flowables
                elements.append(ADR_table)

                elements.append(Spacer(1, 20))

                if len(mission_sources)>1 and i < len(mission_sources):
                    elements.append(PageBreak())

            elements.append(Paragraph("Signatures", styles['Heading4']))
            elements.append(Spacer(1, 20))
            signatures_table_data = []
            signatures_table_data.append(["Verzender / Expéditeur",
                                          "Vervoerder / Transporteur",
                                          "Bestemmeling / Destinataire"])
            signatures_table = Table(signatures_table_data, colWidths=150) 
            # Define a TableStyle
            style_sign = TableStyle([
                ('TEXTCOLOR', (0,0), (-1,0), colors.black),
                ('ALIGN', (0,0), (0,-1), 'LEFT'),
                ('ALIGN', (1,0), (1,-1), 'CENTER'),
                ('ALIGN', (2,0), (2,-1), 'RIGHT'),
                ('BOTTOMPADDING', (0,0), (-1,-1), 0),
                ('TOPPADDING', (0,0), (-1,-1), 0),
                ('GRID', (0,0), (-1,-1), 1, colors.transparent),
            ])

            # Apply the style to the table
            signatures_table.setStyle(style_sign)

            # Add table to list of flowables
            elements.append(signatures_table)

        # Build the PDF document
        try:
            doc.build(elements, onFirstPage=add_header_footer, onLaterPages=add_header_footer)
        except PermissionError as e:
            sys.exit(f"Please close the document \"{e.filename}\" and try again.")
            
    print("Pdfs generated!")
    return

def compute_activity(A0:float, A0_date:datetime, isotope:str, date:datetime):
    """
    Computes the radioactive activity of an isotope at a given date based on its initial activity and half-life.

    The function calculates the remaining activity of a radioactive isotope on a specific date, given its initial activity,
    the date of the initial activity measurement, the isotope type, and the target date for which the activity is to be calculated.
    The calculation is based on the formula A = A0 * (1/2)^(Δt/T), where A0 is the initial activity, Δt is the time difference
    in days between the initial and target dates, and T is the half-life of the isotope in days.

    Parameters:
    - A0 (float): The initial activity of the isotope in GBq.
    - A0_date (datetime): The date of the initial activity measurement.
    - isotope (str): The type of the isotope, used to determine its half-life.
    - date (datetime): The target date for which the activity is to be calculated.

    Returns:
    - tuple: A tuple containing two float values:
        - The first float is the calculated activity in GBq on the target date.
        - The second float is the calculated activity in Ci on the target date.
    """
    half_life = {'Cs-137': 11012.05,
                 'Ir-192': 73.83,
                 'Se-75': 119.78}
    timedelta = date.date()-A0_date.date()
    days_diff_float = utils.timedelta_to_days_float(timedelta)
    GBq = round(A0*((1/2)**(days_diff_float/half_life[isotope])), 2)
    Ci = round((GBq / 37), 2)
    return GBq, Ci

def add_header_footer(canvas, doc):
    """
    Draws the header and footer on each page of a PDF document.

    This function is designed to be used as a callback by the ReportLab library during the PDF generation process.
    It adds a consistent header and footer to each page, enhancing the document's presentation and providing essential
    information like page numbers. The function also includes the company's logos in the header for branding purposes.

    Parameters:
    - canvas: The canvas represents the current page in the PDF document. It is used to draw the header and footer elements.
    - doc: The document object that is being generated. It provides context, such as the current page number.

    Returns:
    - None: This function directly modifies the canvas and does not return any value.
    """
    canvas.saveState()

    # Footer
    footer_text = "Page %d" % doc.page
    canvas.setFont("Helvetica", 10)
    canvas.drawString(75, 30, footer_text)  # Adjust coordinates as needed

    # Logo image to include
    logo1_path = "media\Vincotte_RGB_H.png"
    logo2_path = "media\Member-Group-Kiwa-FC.jpg"
    canvas.drawImage(logo1_path, 75, 759, width=52, height=52)  # Draw the first logo
    canvas.drawImage(logo2_path, 135, 760, width=62.28, height=30)  # Draw the second logo
    
    # Optionally add more elements here (e.g., footer text)
    
    canvas.restoreState()

def check_conflicts(missions:dict):
    """
    Checks for double bookings of sources. Looks for the presence of the same source in two different missions, 
    based on missions.json"""

    booked_sources = {}

    # Iterate over all missions
    for mission in missions['items']:
        sources = []
        sources.append(mission.get('fields').get('SOURCES'))
        sources.append(mission.get('fields').get('SOURCESII'))
        sources.append(mission.get('fields').get('SOURCESIII'))
        sources.append(mission.get('fields').get('SOURCESIV'))
        
        # Store any not None sources in booked_sources
        if any(sources):
            for s in sources:
                if s is None or s == '':
                    sources.remove(s)
                    break
                if s in booked_sources:
                    booked_sources[s].append(mission.get('key'))
                else:
                    booked_sources[s] = [mission.get('key')]
    
    # Check for double bookings in booked_sources
    if any(booked_sources):
        for source in booked_sources:
            if len(source) == 1:
                # Delete source from booked_sources
                del source

        return booked_sources