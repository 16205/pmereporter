from datetime import datetime
from modules import outbound, utils
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, PageBreak
import os
import re
import sys

def generate_pdfs(missions:dict, sources:dict, keys:list=None):
    """
    Generates PDF documents for each mission in the provided missions list, including ADR information and other mission details.

    Parameters:
    - missions (dict): A dictionary containing mission items, each with details such as start/end times, resources, customers, and ADR source information.
    - sources (dict): A dictionary containing source items with details such as UN number, package, isotope, activity, and other ADR relevant information.

    The function iterates over each mission, compiles relevant information into a structured format, and generates a PDF document for that mission.
    The generated PDF includes mission details, agent and client information, ADR information for sources involved in the mission, and signature fields.
    """

    # print("Generating pdfs...")

    # Define styles
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Justify', parent=styles['Normal'], fontSize=10, fontName='Helvetica', alignment=TA_JUSTIFY,))
    smaller_font_style = ParagraphStyle('SmallerFont', parent=styles['Normal'], fontSize=9, fontName='Helvetica')

    for mission in (missions):
        # Skip missions that have a key in "keys" input argument list (That is, missions not selected to be generated in GUI)
        if keys and mission.get('key') not in keys:
            continue
        # Convert start and end times to datetime objects
        mission_start = datetime.strptime(mission['start'], '%Y-%m-%d %H:%M:%S')
        mission_end = datetime.strptime(mission['end'], '%Y-%m-%d %H:%M:%S')  

        # Create content elements
        elements = []

        # Add content:
        # -----------Title-----------
        elements.append(Paragraph(f"Mission order n°{mission.get('key')} - Vinçotte NDT", styles['Title']))
        elements.append(Spacer(1, 10))

        # ------------------------------------- Mission details -------------------------------------
        elements.append(Paragraph(f"Mission details", styles['Heading2']))
                
        # Table data
        mission_table_data = []
            
        # -----------Date and time-----------
        mission_table_data.append([Paragraph("<b>Date of intervention</b>"), Paragraph(f"{mission_start.strftime('%d %b %Y')}")])
        mission_table_data.append([Paragraph("<b>Start time</b>"), Paragraph(f"{mission_start.strftime('%H:%M')}")])
        mission_table_data.append([Paragraph("<b>End time</b>"), Paragraph(f"{mission_end.strftime('%H:%M')}")])
        
        # -----------Agents-----------
        for index, item in enumerate(mission.get('resources')):
            agent_name_label = "<b>Agent</b><br/><br/>" if len(mission.get('resources')) == 1 else f"<b>Agent {index+1}</b><br/><br/>"
            agent_name = f"{item.get('firstName')} {item.get('lastName')}<br/>"
            
            agent_phone_label = "<b>Phone</b>"
            agent_phone1 = f"<br/>{item.get('mobile1')}" if item.get('mobile1') else ''
            agent_phone2 = f"<br/>{item.get('mobile2')}" if item.get('mobile2') else ''
            
            mission_table_data.append([Paragraph(agent_name_label+agent_phone_label), 
                                       Paragraph(agent_name+agent_phone1+agent_phone2)])
            
        # -----------Clients-----------
        for index, item in enumerate(mission['customers']):
            client_name_label = "<b>Client</b><br/><br/>" if len(mission.get('customers', '')) == 1 else f"<b>Client {index+1}</b><br/><br/>"    
            client_name = f"{item.get('label')}<br/>"

            client_phone_label = "<b>Phone</b>"
            client_phone1 = f"<br/>{item.get('phone1')}" if item.get('phone1') else ''
            client_phone2 = f"<br/>{item.get('phone2')}" if item.get('phone2') else ''
            
            mission_table_data.append([Paragraph(client_name_label+client_phone_label), 
                                       Paragraph(client_name+client_phone1+client_phone2)])

        # -----------Service order number-----------
        if mission.get('SOnumber') and mission.get('SOnumber') != 'None':
            mission_table_data.append([Paragraph("<b>Service order n°</b>"), Paragraph(f"{mission.get('SOnumber')}")])

        # -----------Location-----------
        if mission.get('location') == "Run get_locations()":
            raise ValueError('Mission intervention location missing, please first run ingest.get_locations()!')
        elif mission.get('location') and mission.get('location') != 'None': 
            location = utils.format_text(mission.get('location'))
            mission_table_data.append([Paragraph("<b>Intervention location</b>"), Paragraph(f"{location}")])
        else:
            location = "" # Set location to empty string for use in ADR sender/receiver information, so that "None" is not displayed

        # -----------Departure location-----------
        departureplace = mission.get('departurePlace')
        if departureplace:
            mission_table_data.append([Paragraph("<b>Departure location</b>"), Paragraph(f"{departureplace}")])
        else:
            departureplace = "" # Set departure place to empty string for use in ADR sender/receiver information, so that "None" is not displayed

        # -----------Vehicle-----------
        vehicle = mission.get('vehicle')
        if vehicle:
            mission_table_data.append([Paragraph("<b>Vehicle</b>"), Paragraph(f"{vehicle}")])
        
        # -----------Equipment-----------
        equipments = mission.get('equipment')
        if equipments:
            if len(equipments) > 1:
                for index, equipment in enumerate(equipments):
                    mission_table_data.append([Paragraph(f"<b>Adv. equipment {index+1}</b>"), Paragraph(f"{equipment}")])
            else:
                for equipment in equipments:
                    mission_table_data.append([Paragraph("<b>Adv. equipment</b>"), Paragraph(f"{equipment}")])

        # -----------Info/comments-----------
        comments = mission.get('comments')
        
        # Format text for pretty display
        for i in range(len(comments)):
            comments[i] = utils.format_text(comments[i])
                
        # Add separator between different types of comments
        separator = "<br/>----------------------------------------------------------------------------------------------<br/>"
        comments_text = separator.join([comment for comment in comments])

        comments_paragraph = []
        max_height = 500
        max_width = 320
        # actual_height = utils.calculate_paragraph_height(comments_text, max_width, styles['Normal'])

        # Checking if height > max height to avoid running 'ajust_paragraph_height' if not needed
        # if actual_height > max_height:
        #     # Split total comments text into two paragraphs if height > max height
        #     comments_paragraph = utils.ajust_paragraph_height(comments_text, max_height, max_width, styles['Normal'])
        # else:
        #     comments_paragraph.append(comments_text)

        # Split total comments text into two paragraphs if height > max height
        comments_paragraph = utils.ajust_paragraph_height(comments_text, max_height, max_width, styles['Normal'])

        # Display one paragraph per table row
        for comment in comments_paragraph:
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
        norm_crit_list = mission.get('normCr', [])
        techniques_list = mission.get('techniques', [])
        
        # Check if any techniques, norms or criteria are present
        if any(norm_crit_list) or any(techniques_list):
            # -----------Techniques, Norms & Criteria heading-----------
            elements.append(Paragraph("Techniques, Norms & Criteria", styles['Heading4']))
            
            tech_norm_crit_table_data = []

            k = 1
            for technique in techniques_list:
                tech_norm_crit_table_data.append([Paragraph(f"<b>Technique {k}</b>"), Paragraph(technique)])
                k += 1

            j = 1
            for norm_crit in norm_crit_list:
                tech_norm_crit_table_data.append([Paragraph(f"<b>Norm/Criteria {j}</b>"), Paragraph(norm_crit)])
                j += 1

            norm_crit_table = Table(tech_norm_crit_table_data, colWidths=[111, None])
            norm_crit_table.setStyle(style)

            elements.append(norm_crit_table)

        # ------------------------------------- ADR Information -------------------------------------
        # Check if RT mission
        mission_sources = mission.get('sources')
                
        # Check if any sources are present
        if any(mission_sources):
            elements.append(PageBreak())
            elements.append(Paragraph("<b>ADR Informatie / Information ADR</b>", styles['Heading2']))

            # -----------Sender / Receiver table-----------
            s_r_table_data = []
            addresses = {'Villers-Le-Bouillet': 'Rue de la métallurgie 47<br/>4530 Villers-Le-Bouillet',
                         'Houdeng': 'Chaussée Paul Houtart 88<br/>7100 Houdeng-Goegnies',
                         'Wijnegem': 'Bijkhoevelaan 7<br/>2110 Wijnegem'}
            # Check if one way transport
            if mission.get('oneWayTransport') == True:
                s_r_table_data.append([Paragraph("<b>Verzender / Expéditeur</b>"),
                                   Paragraph("<b>Bestemmeling / Destinataire</b>")])
                if mission.get('return') == True:
                    s_r_table_data.append([Paragraph(f"{client_name}<br/>{location}"),
                                            Paragraph(f"Vinçotte NV<br/><br/>{addresses.get(departureplace)}")])
                else:
                    s_r_table_data.append([Paragraph(f"Vinçotte NV<br/><br/>{addresses.get(departureplace)}"),
                                            Paragraph(f"{client_name}<br/>{location}")])
                s_r_table = Table(s_r_table_data)
                s_r_table.setStyle(style)
                elements.append(s_r_table)

            else:
                elements.append(Paragraph('Heen / Aller', styles['Heading5']))
                s_r_table_data.append([Paragraph("<b>Verzender / Expéditeur</b>"),
                                   Paragraph("<b>Bestemmeling / Destinataire</b>")])
                s_r_table_data.append([Paragraph(f"Vinçotte NV<br/><br/>{addresses.get(departureplace)}"),
                                        Paragraph(f"{client_name}<br/>{location}")])
                
                s_r_table = Table(s_r_table_data)
                s_r_table.setStyle(style)
                elements.append(s_r_table)

                elements.append(Paragraph('Terug / Retour', styles['Heading5']))
                s_r_table_data = []
                s_r_table_data.append([Paragraph("<b>Verzender / Expéditeur</b>"),
                                   Paragraph("<b>Bestemmeling / Destinataire</b>")])
                s_r_table_data.append([Paragraph(f"{client_name}<br/>{location}"),
                                        Paragraph(f"Vinçotte NV<br/><br/>{addresses.get(departureplace)}")])
                
                s_r_table = Table(s_r_table_data)
                s_r_table.setStyle(style)
                elements.append(s_r_table)
            
            # -----------Description-----------
            elements.append(Paragraph("<b>Getransporteerde ADR stoffen: / Marchandises ADR transportées:</b>", styles['Heading4']))
            
            i=0
            for source in mission_sources:
                # -----------Isotope n° heading-----------
                if len(mission_sources)>1:
                    i+=1
                    elements.append(Paragraph(f"<b>Isotope {i}</b>", styles['Heading5']))

                # Table data
                ADR_table_data = []

                # -----------Source internal identification (Vincotte)-----------
                ADR_table_data.append([Paragraph(f"<b>Identificatie /<br/>Identification</b>", smaller_font_style),
                                       Paragraph(f"{source}", smaller_font_style)])
                
                # -----------UN Number & description-----------
                UN_number = sources[source]['UNnumber']
                package = sources[source]['Package']
                ADR_table_data.append([Paragraph(f"<b>Beschrijving /<br/>Description</b>", smaller_font_style),
                                       Paragraph(f"{UN_number} RADIOACTIEVE STOFFEN, IN COLLI VAN TYPE {package}, 7, (E) /<br/>{UN_number} MATIÈRES RADIOACTIVES EN COLIS DE TYPE {package}, 7, (E)", smaller_font_style)])
                
                # -----------Isotope-----------
                isotope = sources[source]['Isotope']
                ADR_table_data.append([Paragraph(f"<b>Isotoop /<br/>Isotope</b>", smaller_font_style),
                                       Paragraph(f"{isotope}", smaller_font_style)])
                
                # -----------Activity-----------
                A0 = sources[source]['GBq']
                A0_date = utils.iso_to_datetime(sources[source]['Calibrationdate'])

                GBq, Ci = compute_activity(A0, A0_date, isotope, mission_start)
                ADR_table_data.append([Paragraph(f"<b>Activiteit op {mission_start.strftime('%d %b %Y')} /<br/>Activité le {mission_start.strftime('%d %b %Y')}</b>", smaller_font_style),
                                       Paragraph(f"{GBq} GBq - {Ci} Ci", smaller_font_style)])
                
                # -----------Package category-----------
                pckg_category = sources[source]['Label']
                ADR_table_data.append([Paragraph(f"<b>Label /<br/>Étiquette</b>", smaller_font_style),
                                       Paragraph(f"{pckg_category}", smaller_font_style)])
                
                # -----------Transport index-----------
                transport_index = sources[source]['Transportindex']
                ADR_table_data.append([Paragraph(f"<b>Transportindex /<br/>Indice de transport</b>", smaller_font_style),
                                       Paragraph(f"{transport_index}", smaller_font_style)])
                
                # -----------Physical state-----------
                physical_state = sources[source]['Physicalstate']
                ADR_table_data.append([Paragraph(f"<b>Fysiche toestand /<br/>État physique</b>", smaller_font_style),
                                       Paragraph(f"{physical_state}", smaller_font_style)])
                
                # -----------Certificate-----------
                certificate = sources[source]['Certificate']
                ADR_table_data.append([Paragraph(f"<b>Goedkeuringscertificaat /<br/>Certificat d'approbation</b>", smaller_font_style),
                                       Paragraph(f"{certificate}", smaller_font_style)])
                
                # -----------Certificate (Special Form)-----------
                certificate_sf = sources[source]['Certificate_x0028_specialform_x0']
                if certificate_sf is not None:
                    ADR_table_data.append([Paragraph(f"<b>Goedkeuringscertificaat - Special Form /<br/>Certificat d'approbation - Forme spéciale</b>", smaller_font_style),
                                       Paragraph(f"{certificate_sf}", smaller_font_style)])
                    
                # TODO: Replace dict accesses by .get() to avoid errors when none

                # -----------Focus-----------
                focus = sources.get(source).get('Focus')
                if focus is not None:
                    ADR_table_data.append([Paragraph("<b>Focus /<br/>Foyer</b>", smaller_font_style),
                                           Paragraph(f"{focus} mm", smaller_font_style)])

                # Create the table with the data
                ADR_table = Table(ADR_table_data, colWidths=[125, None])

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

                elements.append(Spacer(1, 10))

                if len(mission_sources)>1 and i < len(mission_sources):
                    elements.append(PageBreak())

            # -----------Signatures of concerned parties-----------
            elements.append(Paragraph("Signatures", styles['Heading4']))
            elements.append(Spacer(1, 10))
            
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

        # Create directory to store generated PDFs
        day_missions = mission_start.strftime('%Y%m%d')
        if not os.path.exists(f"./generated/{day_missions}"):
            os.makedirs(f"./generated/{day_missions}")
        
        # Get names for file naming
        names = ""
        for resource in mission.get('resources'):
            names += resource.get('lastName') + " " + resource.get('firstName') + " - "
        
        # Create a PDF document
        doc = SimpleDocTemplate(f"./generated/{day_missions}/{names}{mission.get('key')}.pdf", pagesize=A4, topMargin=100)
        
        # Build the PDF document
        try:
            doc.build(elements, onFirstPage=add_header_footer, onLaterPages=add_header_footer)
        except Exception as e:
            raise Exception(f"Please close the document \"{e.filename}\" and try again.")
            
    # print("Pdfs generated!")
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
    logo1_path = utils.resource_path("./media/Vincotte_RGB_H.png")
    logo2_path = utils.resource_path("./media/Member-Group-Kiwa-FC.jpg")
    canvas.drawImage(logo1_path, 75, 759, width=52, height=52)  # Draw the first logo
    canvas.drawImage(logo2_path, 135, 760, width=62.28, height=30)  # Draw the second logo
    
    # Optionally add more elements here (e.g., footer text)
    
    canvas.restoreState()

def check_sources_double_bookings(missions: list) -> dict:
    """
    This function iterates over a list of missions and identifies sources that are booked during overlapping times.
    It returns a dictionary with sources as keys and the list of mission keys during which overlaps occur as values.

    Parameters:
    missions (list): A list of mission dictionaries. Each dictionary must contain a 'sources' key, which is a list of sources,
                     and 'start' and 'end' keys with datetime strings.

    Returns:
    double_bookings (dict): A dictionary of sources with overlapping bookings, along with the mission keys where these overlaps occur.
    """
    booked_sources = {}

    # Iterate over all missions
    for mission in missions:
        sources = mission.get('sources', [])
        mission_start = datetime.strptime(mission['start'], '%Y-%m-%d %H:%M:%S')
        mission_end = datetime.strptime(mission['end'], '%Y-%m-%d %H:%M:%S')

        # Store sources with their respective mission keys and timings
        for source in sources:
            if source not in booked_sources:
                booked_sources[source] = []
            booked_sources[source].append({'key': mission['key'], 'start': mission_start, 'end': mission_end})

    # Check for double bookings in booked_sources
    double_bookings = {}
    for source, entries in booked_sources.items():
        if len(entries) > 1:
            # Check for overlapping times
            for i in range(len(entries)):
                for j in range(i + 1, len(entries)):
                    if entries[i]['end'] > entries[j]['start'] and entries[i]['start'] < entries[j]['end']:
                        if source not in double_bookings:
                            double_bookings[source] = []
                        double_bookings[source].extend([entries[i]['key'], entries[j]['key']])
                        break

    # Remove duplicate mission keys in the results
    for source in double_bookings:
        double_bookings[source] = list(set(double_bookings[source]))

    return None if not double_bookings else double_bookings


def send_om(missions:dict, keys:list[str], sender_name:str, progress_callback=None):
    # print("Sending mission orders...")

    # Variables for process tracking
    total_missions = len(missions)
    processed_count = 0

    # Iterate over all missions
    for mission in (missions):
        # Skip missions that have a key in "keys" input argument list (That is, missions not selected to be generated in GUI)
        if keys and mission.get('key') not in keys:
            continue
        # Initialize empty list of recipients
        recipients = []
        # For finding files via filename
        names = ""
        # Iterate over all mission resources
        for resource in mission.get('resources'):
            recipients.append(resource.get('email'))
            names += f"{resource.get('lastName')} {resource.get('firstName')} - "
        # Remove any empty or None values
        recipients = [r for r in recipients if r and r != '']
        number = mission.get('key')
        mission_start = datetime.strptime(mission['start'], '%Y-%m-%d %H:%M:%S')
        intervention_date = mission_start.strftime('%d/%m/%Y')
        
        subject = f"Mission order n°{number} - {intervention_date}"
        
        content = f"Please find in attachment the Intervention Document (Nr: {number}).\n\nKind regards,\n\n{sender_name}\n\n"
            
        attachment_path = [f"generated/{mission_start.strftime('%Y%m%d')}/{names}{number}.pdf"]

        additional_attachments_path = f"temp/attachments/{mission_start.strftime('%Y%m%d')}/{number}"
        
        if os.path.isdir(additional_attachments_path):
            for file in os.listdir(additional_attachments_path):
                attachment_path.append(f"{additional_attachments_path}/{file}")

        sender_address = 'NDTplanning@vincotte.be'

        # # recipients_str is for development purposes
        # recipients_str = "[\n"
        # for recipient in recipients:
        #     recipients_str += recipient + ",\n"
        # recipients_str += "]\n\n"
        # content += recipients_str
        
        outbound.send_email(subject, recipients, content, attachment_path, sender_address)
        
        # Update processed count and emit progress
        processed_count += 1
        progress = int((processed_count / total_missions) * 100)
        if progress_callback:
            progress_callback(progress)

    # print("Mission orders sent!")

def clean_data(missions):
    missions_cleaned = []
    for mission in missions['items']:
        # Initialize each mission with defaults
        mission_dict = {
            "key": mission.get('key'),
            "resources": [],
            "start": str(datetime.strptime(mission.get('start'), "%Y-%m-%dT%H:%M:%S")),
            "end": str(datetime.strptime(mission.get('end'), "%Y-%m-%dT%H:%M:%S")),
            "comments": [],
            "customers": [],
            "SOnumber": None,
            "departurePlace": mission.get('fields').get('DEPARTUREPLACE') if mission.get('fields').get('DEPARTUREPLACE') != '' else None,
            "vehicle": mission.get('fields').get('PR_INV') if mission.get('fields').get('PR_INV') != '' and mission.get('fields').get('PR_INV') != 'Raamcontract' else None,
            "equipment": [],
            "techniques": [],
            "normCr": [],
            "sources": [],
            "location": "Run get_locations()",
            "oneWayTransport": mission.get('fields').get('ONEWAYTRANSPORT'),
            "return": False,
            "attachmentLinks": []
        }

        # Populate SOnumber
        # Safely navigate the nested dictionaries
        project = mission.get('project')
        if project:
            mission_dict['SOnumber'] = project.get('fields').get('PROJET_SO_NUMBER')
        # Remove leading zeroes from SOnumbers
        if mission_dict['SOnumber']:
            mission_dict['SOnumber'] = mission_dict['SOnumber'].lstrip('0')

        # Convert mission key and mission SOnumber to string
        mission_dict['key'] = str(mission_dict['key'])
        mission_dict['SOnumber'] = str(mission_dict['SOnumber']) if mission_dict['SOnumber'] else None

        # Check if ADR return
        if mission_dict['departurePlace']:
            match = re.search(r'Client return(.*)', mission_dict['departurePlace'])
            if match:
                mission_dict['departurePlace'] = match.group(1).strip()
                mission_dict['return'] = True

        # Populate resources if available
        for resource in mission.get('resources', []):
            if not any(x in resource.get('label') for x in ["RG -", "BUNKER ", "Vincotte", "LABO ", "RX "]):
                mission_dict['resources'].append({
                    "lastName": resource.get('lastName'),
                    "firstName": resource.get('firstName'),
                    "mobile1": resource.get('mobile') if resource.get('mobile') not in ('+32', '') else None,
                    "mobile2": resource.get('phone') if resource.get('phone') not in ('+32', '') and \
                                                        resource.get('phone') != resource.get('mobile') else None,
                    "email": re.sub(r';.*$', '', resource.get('email')),    # Remove anything after the first semicolon (some agents have
                                                                            # multiple email addresses registered in the same field),
                    "AVnumber": resource.get('registrationNumber'),
                    "ADR": True if "ADR" in resource.get('label') else False
})
                
        # Populate comments if available
        mission_dict['comments'] = [mission.get('fields').get('COMMENTS_LOCATION'), 
                                    mission.get('remark'), 
                                    # mission.get('fields').get('TASKCOMMENTS'), 
                                    mission.get('customers')[0].get('fields').get('COMMENTSCUSTOMER') if mission.get('customers') else None]
        # Remove empty or None values
        mission_dict['comments'] = [comment for comment in mission_dict['comments'] if comment is not None and comment!= '']
        
        # Populate customers if available
        for customer in mission.get('customers', []):
            mission_dict['customers'].append({
                "label": customer.get('label'),
                "phone1": customer.get('phone') if customer.get('phone') not in ('+32', '') else None,
                "phone2": customer.get('mobile') if customer.get('mobile') not in ('+32', '') and \
                                                    customer.get('mobile') != customer.get('phone') else None,
            })

        # Populate techniques if available
        mission_dict['techniques'] = [mission.get('fields').get('JOBSEL1'),
                                     mission.get('fields').get('JOBSEL2')]
        # Remove empty or None values
        mission_dict['techniques'] = [technique for technique in mission_dict['techniques'] if technique is not None and technique!= '']

        # Populate normCr if available
        mission_dict['normCr'] = [mission.get('fields').get('NORMCR1'), 
                                   mission.get('fields').get('NORMCR2'), 
                                   mission.get('fields').get('NORMCR3'), 
                                   mission.get('fields').get('NORMCR4'), 
                                   mission.get('fields').get('NORMCR5'), 
                                   mission.get('fields').get('NORMCR6'), 
                                   mission.get('fields').get('NORMCR7')]
        # Remove empty or None values
        mission_dict['normCr'] = [normCr for normCr in mission_dict['normCr'] if normCr is not None and normCr!= '']

        # Populate equipment if available
        mission_dict['equipment'] = [mission.get('fields').get('PR_MAT1'),
                                     mission.get('fields').get('PR_MAT2'),
                                     mission.get('fields').get('PR_MAT3'),
                                     mission.get('fields').get('PR_MAT4')]
        # Remove empty or None values
        mission_dict['equipment'] = [eq for eq in mission_dict['equipment'] if eq is not None and eq!= '']
        
        # Populate sources if available
        mission_dict['sources'] = [mission.get('fields').get('SOURCES'),
                                   mission.get('fields').get('SOURCESII'),
                                   mission.get('fields').get('SOURCESIII'),
                                   mission.get('fields').get('SOURCESIV')]
        # Remove empty or None values
        mission_dict['sources'] = [s for s in mission_dict['sources'] if s is not None and s!= '']
        
        # Populate location if available
        mission_dict['location'] = mission.get('location') if mission.get('location') != '' else None

        # Populate attachment links if available
        mission_dict['attachmentLinks'] = [mission.get('fields').get('SALESORDER2'),
                                           mission.get('fields').get('SALESORDER4')
                                        #    mission.get('project').get('fields').get('GPINFO'),
                                        #    mission.get('customers')[0].get('fields').get('CU_INFORMATION')
                                           ]
        # Remove empty or None values and remove leading dots
        mission_dict['attachmentLinks'] = [utils.remove_leading_dots(link) for link in mission_dict['attachmentLinks'] if link is not None and link!= '' and link != '..']

        missions_cleaned.append(mission_dict)

    return missions_cleaned

def filter_rt_missions(missions):
    rt_missions = []
    for mission in missions:
        if mission['sources']:
            rt_missions.append(mission)
    return rt_missions

def generate_ADR_transport_list(missions, sources):
    pass