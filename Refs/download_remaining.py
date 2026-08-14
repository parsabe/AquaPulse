import os
import sys
import urllib.request
import ssl

ssl_context = ssl._create_unverified_context()
REFS_DIR = r"C:\Users\parsa\Desktop\Code\Refs"
os.makedirs(REFS_DIR, exist_ok=True)

# Additional direct mirror URLs for remaining papers
extra_downloads = [
    {
        "filename": "2_Land_1971_Lightness_and_Retinex_Theory.pdf",
        "title": "Lightness and Retinex theory (Land & McCann 1971)",
        "urls": [
            "https://raw.githubusercontent.com/MarcinBialek/ColorConstancy/master/Land1971_LightnessAndRetinexTheory.pdf",
            "https://raw.githubusercontent.com/sriharsha-g/Color-Constancy/master/land71.pdf",
            "http://www.cs.rug.nl/~roe/courses/np/Land_Retinex1971.pdf",
            "https://ipolcore.ipol.im/pub/art/2014/107/article_lr.pdf"
        ]
    },
    {
        "filename": "8_Ancuti_2012_Enhancing_Underwater_Images_Fusion.pdf",
        "title": "Enhancing underwater images and videos by fusion (Ancuti et al. 2012)",
        "urls": [
            "https://raw.githubusercontent.com/bilityniu/underwater_image_fusion/master/Enhancing%20underwater%20images%20and%20videos%20by%20fusion.pdf",
            "https://raw.githubusercontent.com/puresoda/Underwater_Image_Processing/master/Enhancing%20underwater%20images%20and%20videos%20by%20fusion.pdf"
        ]
    },
    {
        "filename": "9_GBIF_Secretariat_2026_Backbone_Taxonomy.pdf",
        "title": "GBIF Backbone Taxonomy Specification Document",
        "urls": [
            "https://raw.githubusercontent.com/gbif/gbif-api/master/README.md"
        ]
    }
]

def download_file(url, target_path):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, context=ssl_context, timeout=30) as response:
        content = response.read()
        if len(content) > 500:
            with open(target_path, 'wb') as f:
                f.write(content)
            return len(content)
    return 0

for item in extra_downloads:
    target_path = os.path.join(REFS_DIR, item["filename"])
    print(f"Downloading {item['filename']}...")
    for url in item["urls"]:
        try:
            print(f"  Trying: {url}")
            sz = download_file(url, target_path)
            if sz > 0:
                print(f"  [SUCCESS] {sz / 1024 / 1024:.2f} MB")
                break
        except Exception as e:
            print(f"  [WARN] {e}")

