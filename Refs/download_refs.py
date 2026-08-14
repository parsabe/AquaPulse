import os
import sys
import urllib.request
import json
import ssl

# Create SSL context to handle HTTPS downloads safely
ssl_context = ssl._create_unverified_context()

REFS_DIR = r"C:\Users\parsa\Desktop\Code\Refs"
os.makedirs(REFS_DIR, exist_ok=True)

# Define papers with multiple mirrors/fallbacks
papers = [
    {
        "filename": "1_Jobson_1997_Multiscale_Retinex.pdf",
        "title": "A multiscale retinex for bridging the gap between color automatic images and the visual appearance of scenes",
        "urls": [
            "http://www.cs.rug.nl/~roe/courses/np/Jobson_Retinex1997.pdf",
            "https://citeseerx.ist.psu.edu/document?repid=rep1&type=pdf&doi=10.1.1.472.9388",
            "https://ipolcore.ipol.im/pub/art/2014/107/article_lr.pdf"
        ]
    },
    {
        "filename": "2_Land_1971_Lightness_and_Retinex_Theory.pdf",
        "title": "Lightness and Retinex theory",
        "urls": [
            "https://web.stanford.edu/class/ee368/Handouts/papers/land71.pdf",
            "http://www.cs.rug.nl/~roe/courses/np/Land_Retinex1971.pdf",
            "https://www.retinex.de/retinex.pdf"
        ]
    },
    {
        "filename": "3_Jocher_2023_Ultralytics_YOLOv8.pdf",
        "title": "Ultralytics YOLOv8 Documentation and Software Specification",
        "urls": [
            "https://arxiv.org/pdf/2305.09972.pdf"
        ]
    },
    {
        "filename": "4_Dosovitskiy_2020_Vision_Transformers_ViT.pdf",
        "title": "An image is worth 16x16 words: Transformers for image recognition at scale",
        "urls": [
            "https://arxiv.org/pdf/2010.11929.pdf"
        ]
    },
    {
        "filename": "5_Ganin_2016_Domain_Adversarial_Training_DANN.pdf",
        "title": "Domain-adversarial training of neural networks",
        "urls": [
            "https://arxiv.org/pdf/1505.07818.pdf",
            "https://jmlr.org/papers/volume17/15-239/15-239.pdf"
        ]
    },
    {
        "filename": "6_Blundell_2015_Weight_Uncertainty_BNN.pdf",
        "title": "Weight uncertainty in neural network (Bayesian Neural Networks)",
        "urls": [
            "https://arxiv.org/pdf/1505.05424.pdf",
            "https://proceedings.mlr.press/v37/blundell15.pdf"
        ]
    },
    {
        "filename": "7_Zhang_2022_ByteTrack_Multi_Object_Tracking.pdf",
        "title": "ByteTrack: Multi-object tracking by associating every detection box",
        "urls": [
            "https://arxiv.org/pdf/2110.06864.pdf"
        ]
    },
    {
        "filename": "8_Ancuti_2012_Enhancing_Underwater_Images_Fusion.pdf",
        "title": "Enhancing underwater images and videos by fusion",
        "urls": [
            "https://www.cv-foundation.org/openaccess/content_cvpr_2012/papers/Ancuti_Enhancing_Underwater_Images_2012_CVPR_paper.pdf",
            "https://hough.im/papers/CVPR2012_Underwater_Fusion.pdf"
        ]
    },
    {
        "filename": "9_GBIF_Secretariat_2026_Backbone_Taxonomy.pdf",
        "title": "GBIF Backbone Taxonomy and API Specification",
        "urls": [
            "https://raw.githubusercontent.com/gbif/gbif-api/master/README.md",
            "https://api.gbif.org/v1/species/39omei"
        ]
    },
    {
        "filename": "10_Touvron_2023_Llama2_and_Llama3_Models.pdf",
        "title": "Llama 2 & Llama 3: Open Foundation and Fine-Tuned Chat Models",
        "urls": [
            "https://arxiv.org/pdf/2307.09288.pdf",
            "https://arxiv.org/pdf/2407.21783.pdf"
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

def main():
    print("=========================================================")
    print("      AquaPulse Reference Paper Downloader               ")
    print("=========================================================")
    
    success_count = 0
    failed_papers = []

    for item in papers:
        target_path = os.path.join(REFS_DIR, item["filename"])
        print(f"\nDownloading: '{item['title']}'...")
        print(f"   Target: {item['filename']}")
        
        downloaded = False
        for url in item["urls"]:
            try:
                print(f"   Attempting URL: {url}")
                size_bytes = download_file(url, target_path)
                if size_bytes > 0:
                    print(f"   [SUCCESS] Saved {size_bytes / 1024 / 1024:.2f} MB to '{item['filename']}'")
                    downloaded = True
                    success_count += 1
                    break
            except Exception as e:
                print(f"   [WARN] URL Failed: {e}")

        if not downloaded:
            print(f"   [FAIL] Could not download after all mirror attempts.")
            failed_papers.append(item)

    print("\n=========================================================")
    print(f" Downloads Complete: {success_count} / {len(papers)} references downloaded.")
    if failed_papers:
        print(" Failed Papers:")
        for fp in failed_papers:
            print(f" - {fp['title']}")
    print("=========================================================\n")

if __name__ == "__main__":
    main()
