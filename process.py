import json
from tqdm import tqdm
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Frame, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime

def get_resources_from_departments(departments):
    departments = departments.json()

    keys = [resource['key'] for resource in departments['resources']]

    return keys

def generate_pdfs(missions):

    # Parse JSON data
    for mission in tqdm(missions["items"]):
        resources = {}
        customers = {}
        for resource in mission["resources"]:
            if not resource['label'].startswith("RG -") and not resource['label'].startswith("BUNKER "):
                resources[f"{resource['key']}"] = {'name': resource['label'], 'phone': resource['mobile']}
        for customer in mission["customers"]:
            customers[f"{customer['key']}"] = {'name': customer['label'], 'phone': customer['phone']}
        
        # Create a PDF document
        doc = SimpleDocTemplate(f".\generated\{mission['key']}.pdf", pagesize=A4)

        # Define styles
        styles = getSampleStyleSheet()

        # Create content elements
        elements = []

        # Add a spacer of 25 points height (adjust as needed)
        elements.append(Spacer(1, 25))

        # # Title
        # canvas.saveState()
        # title = "Vinçotte - Mission order"
        # canvas.setFont("Helvetica", 15)
        # text_width = canvas.stringWidth(title, "Helvetica", 15)
        # canvas.drawString((doc.pagesize[0] - text_width) / 2, 800, title)

        """# Add logos
        logo1 = Image(logo1_path, width=60, height=60)
        logo2 = Image(logo2_path, width=207.6, height=100)
        elements.append(logo1)
        elements.append(logo2)"""

        # Add content
                
        # Parse the datetime string into a datetime object
        datetime_start = datetime.strptime(mission['start'], "%Y-%m-%dT%H:%M:%S")
        datetime_end = datetime.strptime(mission['end'], "%Y-%m-%dT%H:%M:%S")

        # Date
        elements.append(Paragraph(f"<b>Date of intervention:</b> {datetime_start.strftime('%d/%m/%Y')}"))
        elements.append(Spacer(1, 10))
        
        # Start & end times
        elements.append(Paragraph(f"<b>Start time:</b> {datetime_start.strftime('%H:%M')}"))
        elements.append(Paragraph(f"<b>End time:</b> {datetime_end.strftime('%H:%M')}"))
        elements.append(Spacer(1, 10))

        # Agents
        for index, item in enumerate(resources):
            elements.append(Paragraph(f"<b>Agent {index+1}:</b> {resources[item]['name']}"))
            elements.append(Paragraph(f"<b>Phone:</b> {resources[item]['phone']}"))
            elements.append(Spacer(1, 10))
        
        # Clients
        for index, item in enumerate(customers):
            elements.append(Paragraph(f"<b>Client:</b> {customers[item]['name']}"))    
            elements.append(Paragraph(f"<b>Phone:</b> {customers[item]['phone']}"))
            elements.append(Spacer(1, 10))   
        
        # Location
        elements.append(Paragraph(f"<b>Intervention location:</b> "))
        elements.append(Spacer(1, 10))

        # Departure location
        if mission['fields']['DEPARTUREPLACE'] is not None:
            elements.append(Paragraph(f"<b>Departure location:</b> {mission['fields']['DEPARTUREPLACE']}"))
            elements.append(Spacer(1, 10))

        # Remarks
        if mission['remark'] is not None:
            elements.append(Paragraph(f"<b>Remarks:</b> {mission['remark']}"))

        frame = Frame(50, 50, 400, 600, id='my_frame')
        
        # Table data
        data = [
            ['Header 1', 'Header 2', 'Header 3'],
            ['Data 1', 'Data 2', 'Data 3'],
            ['Data 4', 'Data 5', 'Data 6'],
            ['Data 7', 'Data 8', 'Data 9']
        ]

        # Create the table with the data
        table = Table(data)

        # Define a TableStyle with invisible borders
        style = TableStyle([
            ('TEXTCOLOR', (0,0), (-1,0), colors.black),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 10),
            ('TOPPADDING', (0,0), (-1,-1), 10),
            # Set border color to transparent to hide the table borders
            ('LINEABOVE', (0,0), (-1,-1), 0, colors.transparent),
            ('LINEBELOW', (0,0), (-1,-1), 0, colors.transparent),
            ('LINEBEFORE', (0,0), (-1,-1), 0, colors.transparent),
            ('LINEAFTER', (0,0), (-1,-1), 0, colors.transparent),
        ])

        # Apply the style to the table
        table.setStyle(style)

        # frame.add(table)

        # Build the PDF document
        doc.build(elements, onFirstPage=add_header_footer, onLaterPages=add_header_footer)
    return

def add_header_footer(canvas, doc):
    # This function will draw the header/footer on each page
    canvas.saveState()

    # Footer
    footer_text = "Page %d" % doc.page
    canvas.setFont("Helvetica", 10)
    canvas.drawString(40, 10, footer_text)  # Adjust coordinates as needed

    # Logo image to include
    logo1_path = "media\Vincotte_RGB_H.png"
    logo2_path = "media\Member-Group-Kiwa-FC.jpg"
    canvas.drawImage(logo1_path, 75, 759, width=52, height=52)
    canvas.drawImage(logo2_path, 135, 760, width=103.8, height=50)
    
    # Optionally add more elements here (e.g., footer text)
    
    canvas.restoreState()

def center_text(canvas, text, y, page_width, font_name, font_size):
    canvas.setFont(font_name, font_size)
    text_width = canvas.stringWidth(text, font_name, font_size)
    # Calculate X coordinate for centering the text
    x = (page_width - text_width) / 2
    
    canvas.drawString(x, y, text)