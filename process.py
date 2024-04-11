import json
import sys
from tqdm import tqdm
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Frame, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime

def get_resources_from_departments(departments):
    departments = departments.json()

    keys = [resource['key'] for resource in departments['resources']]

    return keys

def add_locations():
    pass

def generate_pdfs(missions, sources):
    print("Generating pdfs...")

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
        doc = SimpleDocTemplate(f".\generated\{mission['key']}.pdf", pagesize=A4, leftmargin=50, topMargin=100)

        # Define styles
        styles = getSampleStyleSheet()

        # Create content elements
        elements = []

        # Add content

        # Title
        elements.append(Paragraph(f"Mission order n° {mission['key']} - Vinçotte", styles['Title']))
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
        if mission['fields']['DEPARTUREPLACE'] is not None:
            mission_table_data.append([Paragraph("<b>Departure location</b>"), Paragraph(f"{mission['fields']['DEPARTUREPLACE']}")])

        # Info/comments
        comments1 = ""
        comments2 = ""
        comments3 = ""
        comments4 = ""
        if mission['fields']['COMMENTS_LOCATION'] is not None:
            comments1 = mission['fields']['COMMENTS_LOCATION']
        if mission['remark'] is not None:
            comments2 = mission['remark']
        if 'TASKCOMMENTS' in mission['fields']:
            if mission['fields']['TASKCOMMENTS'] is not None:
                comments3 = mission['fields']['TASKCOMMENTS']
        for index, item in enumerate(mission['customers']):
            if 'COMMENTSCUSTOMER' in mission['customers'][index]['fields']:
                if mission['customers'][index]['fields']['COMMENTSCUSTOMER'] is not None:
                    comments4 = mission['customers'][index]['fields']['COMMENTSCUSTOMER']
        
        comments = [comments1, comments2, comments3, comments4]
        separator = "<br/>----------------------------------------------------------------------------------------------<br/>"
        comments_paragraph = separator.join([comment for comment in comments if comment])
        
        mission_table_data.append([Paragraph("<b>Remarks/comments</b>"), 
                                   Paragraph(comments_paragraph)])        

        # Create the table with the data
        mission_table = Table(mission_table_data, colWidths=[111, None])

        # Define a TableStyle
        style = TableStyle([
            ('TEXTCOLOR', (0,0), (-1,0), colors.black),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('GRID', (0,0), (-1,-1), 1, colors.black),
        ])

        # Apply the style to the table
        mission_table.setStyle(style)

        # Add table to list of flowables
        elements.append(mission_table)

        # ADR Information Heading -------------------------------------
        if mission['fields']['SOURCES'] is not None or mission['fields']['SOURCESII'] is not None or mission['fields']['SOURCESIII'] is not None:
            elements.append(PageBreak())
            elements.append(Paragraph("<b>ADR Informatie<br/><i>Information ADR</i></b>", styles['Heading2']))

            # Description
            elements.append(Paragraph("<b>Marchandises ADR transportées:<br/>Getransporteerde ADR stoffen:</b>", styles['Heading3']))
            
            # Set variables containing sources identification
            mission_sources = []

            if mission['fields']['SOURCES'] != "" and not None:
                mission_sources.append(mission['fields']['SOURCES'])
            if mission['fields']['SOURCESII'] != "" and not None:
                mission_sources.append(mission['fields']['SOURCESII'])
            if mission['fields']['SOURCESIII'] != "" and not None:
                mission_sources.append(mission['fields']['SOURCESIII'])
            
            for source in mission_sources:
                # Table data
                ADR_table_data = []

                # Source internal identification (Vincotte)
                ADR_table_data.append([Paragraph(f"<b>Identification:</b>"),
                                       Paragraph(f"{source}")])
                
                # UN Number & description
                UN_number = sources[source]['UNnumber']
                description = sources[source]['ADRDescription']
                ADR_table_data.append([Paragraph(f"<b>UN Number & description:</b>"),
                                       Paragraph(f"{UN_number} {description}")])
                
                # Isotope
                isotope = sources[source]['Isotope']
                ADR_table_data.append([Paragraph(f"<b>Isotope:</b>"),
                                       Paragraph(f"{isotope}")])
                
                # Max activity
                max_activity = sources[source]['GBq']
                ADR_table_data.append([Paragraph(f"<b>Max activity (A0) [GBq]:</b>"),
                                       Paragraph(f"{max_activity}")])
                
                # Package category
                pckg_category = sources[source]['Label']
                ADR_table_data.append([Paragraph(f"<b>Package category label:</b>"),
                                       Paragraph(f"{pckg_category}")])
                
                # Transport index
                transport_index = sources[source]['Transportindex']
                ADR_table_data.append([Paragraph(f"<b>Transport index:</b>"),
                                       Paragraph(f"{transport_index}")])
                
                # Physical state
                physical_state = sources[source]['Physicalstate']
                ADR_table_data.append([Paragraph(f"<b>Physical state:</b>"),
                                       Paragraph(f"{physical_state}")])
                
                # Certificate
                certificate = sources[source]['Certificate']
                ADR_table_data.append([Paragraph(f"<b>Certificate:</b>"),
                                       Paragraph(f"{certificate}")])

                # Create the table with the data
                ADR_table = Table(ADR_table_data, colWidths=[111, None])

                # Define a TableStyle
                style = TableStyle([
                    ('TEXTCOLOR', (0,0), (-1,0), colors.black),
                    ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                    ('VALIGN', (0,0), (-1,-1), 'TOP'),
                    ('FONTNAME', (0,0), (-1,0), 'Helvetica'),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 5),
                    ('TOPPADDING', (0,0), (-1,-1), 5),
                    ('GRID', (0,0), (-1,-1), 1, colors.black),
                ])

                # Apply the style to the table
                ADR_table.setStyle(style)

                # Add table to list of flowables
                elements.append(ADR_table)

                elements.append(Spacer(1, 10))
        

        # Build the PDF document
        doc.build(elements, onFirstPage=add_header_footer, onLaterPages=add_header_footer)

    print("Pdfs generated!")
    return

def add_header_footer(canvas, doc):
    # This function will draw the header/footer on each page
    canvas.saveState()

    # Footer
    footer_text = "Page %d" % doc.page
    canvas.setFont("Helvetica", 10)
    canvas.drawString(75, 30, footer_text)  # Adjust coordinates as needed

    # Logo image to include
    logo1_path = "media\Vincotte_RGB_H.png"
    logo2_path = "media\Member-Group-Kiwa-FC.jpg"
    canvas.drawImage(logo1_path, 75, 759, width=52, height=52)
    canvas.drawImage(logo2_path, 135, 760, width=62.28, height=30)
    
    # Optionally add more elements here (e.g., footer text)
    
    canvas.restoreState()

def center_text(canvas, text, y, page_width, font_name, font_size):
    canvas.setFont(font_name, font_size)
    text_width = canvas.stringWidth(text, font_name, font_size)
    # Calculate X coordinate for centering the text
    x = (page_width - text_width) / 2
    
    canvas.drawString(x, y, text)