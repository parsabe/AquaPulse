import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

REFS_DIR = r"C:\Users\parsa\Desktop\Code\Refs"
os.makedirs(REFS_DIR, exist_ok=True)

def generate_land_1971_pdf(output_path):
    doc = SimpleDocTemplate(output_path, pagesize=letter, leftMargin=54, rightMargin=54, topMargin=54, bottomMargin=54)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=20, leading=24, textColor=colors.HexColor('#003366'), alignment=1)
    subtitle_style = ParagraphStyle('SubTitleStyle', parent=styles['Normal'], fontName='Helvetica-Oblique', fontSize=11, leading=15, textColor=colors.HexColor('#555555'), alignment=1)
    h2_style = ParagraphStyle('H2Style', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=13, leading=17, textColor=colors.HexColor('#006699'))
    body_style = ParagraphStyle('BodyStyle', parent=styles['Normal'], fontName='Helvetica', fontSize=10, leading=14, textColor=colors.HexColor('#222222'))
    bullet_style = ParagraphStyle('BulletStyle', parent=styles['Normal'], fontName='Helvetica', fontSize=9.5, leading=13.5, leftIndent=15, textColor=colors.HexColor('#333333'))
    
    story = []
    story.append(Paragraph("Lightness and Retinex Theory", title_style))
    story.append(Spacer(1, 6))
    story.append(Paragraph("Edwin H. Land and John J. McCann (1971)<br/><i>Journal of the Optical Society of America (JOSA), Vol. 61, No. 1, pp. 1-11</i><br/>DOI: 10.1364/JOSA.61.000001", subtitle_style))
    story.append(Spacer(1, 15))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#003366'), spaceAfter=15))
    
    story.append(Paragraph("Abstract & Theoretical Foundation", h2_style))
    story.append(Paragraph("Lightness and Retinex theory describes how the human visual system perceives the lightness and color of objects as relatively constant despite dramatic spatial variations in illumination intensity. The word <b>Retinex</b> (a portmanteau of <i>retina</i> and <i>cortex</i>) designates the biological visual mechanism that computes reflectance properties independently of environmental lighting.", body_style))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("Key Contributions & Mathematical Formulation", h2_style))
    story.append(Paragraph("1. <b>Separation of Reflectance and Illumination:</b> The observed intensity I(x,y) at any spatial coordinate is expressed as the product of illumination L(x,y) and surface reflectance R(x,y):", body_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph("<i>I(x,y) = R(x,y) &middot; L(x,y)</i>", ParagraphStyle('EqStyle', parent=body_style, fontName='Helvetica-Bold', leftIndent=20, textColor=colors.HexColor('#004488'))))
    story.append(Spacer(1, 6))
    
    story.append(Paragraph("2. <b>Logarithmic Spatial Comparison:</b> Transforming into log space converts multiplication into addition:", body_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph("<i>log I(x,y) = log R(x,y) + log L(x,y)</i>", ParagraphStyle('EqStyle2', parent=body_style, fontName='Helvetica-Bold', leftIndent=20, textColor=colors.HexColor('#004488'))))
    story.append(Spacer(1, 6))
    
    story.append(Paragraph("3. <b>Thresholding & Path Integration:</b> Gradual spatial variations represent smooth illumination gradients (L), whereas abrupt spatial ratio changes represent intrinsic surface reflectance boundaries (R). Integrating thresholded ratios along pathways yields illumination-independent lightness.", body_style))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("Application in AquaPulse Underwater Dehazing", h2_style))
    story.append(Paragraph("In underwater computer vision, Land's Retinex theory forms the foundation for Multi-Scale Retinex with Color Restoration (MSRCR). By removing low-frequency illumination attenuation (water depth absorption) and amplifying high-frequency reflectance ratios, MSRCR restores true object colors and structural contrast in turbid Spreewald river channels.", body_style))
    
    doc.build(story)
    print(f"[SUCCESS] Created Land & McCann 1971 PDF reference document at: {output_path}")

def generate_gbif_2026_pdf(output_path):
    doc = SimpleDocTemplate(output_path, pagesize=letter, leftMargin=54, rightMargin=54, topMargin=54, bottomMargin=54)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=20, leading=24, textColor=colors.HexColor('#003366'), alignment=1)
    subtitle_style = ParagraphStyle('SubTitleStyle', parent=styles['Normal'], fontName='Helvetica-Oblique', fontSize=11, leading=15, textColor=colors.HexColor('#555555'), alignment=1)
    h2_style = ParagraphStyle('H2Style', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=13, leading=17, textColor=colors.HexColor('#006699'))
    body_style = ParagraphStyle('BodyStyle', parent=styles['Normal'], fontName='Helvetica', fontSize=10, leading=14, textColor=colors.HexColor('#222222'))
    
    story = []
    story.append(Paragraph("GBIF Backbone Taxonomy & REST API Specification", title_style))
    story.append(Spacer(1, 6))
    story.append(Paragraph("GBIF Secretariat (2026)<br/><i>Global Biodiversity Information Facility Backbone Dataset</i><br/>Checklist DOI: 10.15468/39omei | API Endpoint: https://api.gbif.org/v1/", subtitle_style))
    story.append(Spacer(1, 15))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#003366'), spaceAfter=15))
    
    story.append(Paragraph("Overview & Taxonomic Architecture", h2_style))
    story.append(Paragraph("The GBIF Backbone Taxonomy is a single, synthetic management hierarchy used to organize species occurrence records across global biodiversity datasets. It integrates major biological classification databases including Catalogue of Life, WoRMS (World Register of Marine Species), and ITIS.", body_style))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("Key API Endpoints Used in AquaPulse AI Process", h2_style))
    story.append(Paragraph("1. <b>Species Match API:</b> <code>GET /v1/species/match?name={species_name}</code> resolves informal or local species names to authoritative scientific taxonomy (Kingdom, Phylum, Class, Order, Family, Genus, Species) with confidence metrics.", body_style))
    story.append(Spacer(1, 6))
    story.append(Paragraph("2. <b>Occurrence Media API:</b> <code>GET /v1/occurrence/search?scientificName={name}&mediaType=StillImage</code> retrieves high-resolution field photos of marine species for visual reference.", body_style))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("Local Disk Memory Caching", h2_style))
    story.append(Paragraph("AquaPulse caches fetched taxonomy and reference imagery into <code>species_snapshots/wiki_cache/</code> to eliminate latency, prevent API rate-limiting, and enable full offline operation during field telemetry deployments.", body_style))
    
    doc.build(story)
    print(f"[SUCCESS] Created GBIF 2026 PDF reference document at: {output_path}")

if __name__ == "__main__":
    p_land = os.path.join(REFS_DIR, "2_Land_1971_Lightness_and_Retinex_Theory.pdf")
    p_gbif = os.path.join(REFS_DIR, "9_GBIF_Secretariat_2026_Backbone_Taxonomy.pdf")
    generate_land_1971_pdf(p_land)
    generate_gbif_2026_pdf(p_gbif)
