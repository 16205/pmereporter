import json
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

def add_mission_location_intervention():
    pass

def generate_pdfs(missions, locations, sources):

    # Parse JSON data
    for mission in tqdm(missions["items"]):
        resources = {}
        customers = {}
        for resource in mission["resources"]:
            if not resource['label'].startswith("RG -") and not resource['label'].startswith("BUNKER ") and not resource['label'].startswith("Vincotte"):
                resources[f"{resource['key']}"] = {'name': resource['label'], 'phone': resource['mobile']}
        for customer in mission["customers"]:
            customers[f"{customer['key']}"] = {'name': customer['label'], 'phone': customer['phone']}
        
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
            agent_label = "<b>Agent</b><br/><br/>" if len(resources) == 1 else f"<b>Agent {index+1}</b><br/><br/>"
            agent_phone_label = "<b>Phone</b>"
            mission_table_data.append([Paragraph(agent_label+agent_phone_label), 
                                       Paragraph(f"{resources[item]['name']}<br/><br/>{resources[item]['phone']}")])
            

        # Clients
        for index, item in enumerate(customers):
            client_label = "<b>Client</b><br/><br/>" if len(customers) == 1 else f"<b>Client {index+1}</b><br/><br/>"    
            client_phone_label = "<b>Phone</b>"
            mission_table_data.append([Paragraph(client_label+client_phone_label), 
                                       Paragraph(f"{customers[item]['name']}<br/><br/>{customers[item]['phone']}")])

        # Location
        mission_table_data.append([Paragraph("<b>Intervention location</b>"), Paragraph(f"")])

        # Departure location
        if mission['fields']['DEPARTUREPLACE'] is not None:
            mission_table_data.append([Paragraph("<b>Departure location</b>"), Paragraph(f"{mission['fields']['DEPARTUREPLACE']}")])

        # Remarks
        if mission['remark'] is not None:
            mission_table_data.append([Paragraph("<b>Comments/Remarks</b>"), Paragraph(f"{mission['remark']}")])

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

        if sources is None:
            # ADR Information Heading -------------------------------------
            elements.append(PageBreak())
            elements.append(Paragraph("<b>ADR Information</b>", styles['Heading2']))

            # Description
            elements.append(Paragraph("<b>Marchandises ADR transportées:<br/>Getransporteerde ADR stoffen:</b>", styles['Heading3']))
            
            # UN number & description
            elements.append(Paragraph(f""))

        # Build the PDF document
        doc.build(elements, onFirstPage=add_header_footer, onLaterPages=add_header_footer)
    return

def add_header_footer(canvas, doc):
    # This function will draw the header/footer on each page
    canvas.saveState()

    # Footer
    footer_text = "Page %d" % doc.page
    canvas.setFont("Helvetica", 10)
    canvas.drawString(75, 20, footer_text)  # Adjust coordinates as needed

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