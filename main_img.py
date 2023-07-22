import os
import fitz
import time
from dotenv import load_dotenv
 # Constants
FOLDER_PATH = os.getenv("DEFAULT_FILE_FOLDER")
DIMENSION_LIMIT = 0
RELATIVE_SIZE = 0
ABSOLUTE_SIZE = 0
IMG_DIR = "output"
def recover_pix(doc, item):
    xref = item[0]  # xref of PDF image
    smask = item[1]  # xref of its /SMask
    # special case: /SMask or /Mask exists
    if smask > 0:
        pix0 = fitz.Pixmap(doc.extract_image(xref)["image"])
        if pix0.alpha:  # catch irregular situation
            pix0 = fitz.Pixmap(pix0, 0)  # remove alpha channel
        mask = fitz.Pixmap(doc.extract_image(smask)["image"])
        try:
            pix = fitz.Pixmap(pix0, mask)
        except:  # fallback to original base image in case of problems
            pix = fitz.Pixmap(doc.extract_image(xref)["image"])
        if pix0.n > 3:
            ext = "pam"
        else:
            ext = "png"
        return {  # create dictionary expected by caller
            "ext": ext,
            "colorspace": pix.colorspace.n,
            "image": pix.tobytes(ext),
        }
    # special case: /ColorSpace definition exists
    # to be sure, we convert these cases to RGB PNG images
    if "/ColorSpace" in doc.xref_object(xref, compressed=True):
        pix = fitz.Pixmap(doc, xref)
        pix = fitz.Pixmap(fitz.csRGB, pix)
        return {  # create dictionary expected by caller
            "ext": "png",
            "colorspace": 3,
            "image": pix.tobytes("png"),
        }
    return doc.extract_image(xref)

def extract_images_from_pdf(pdf_file_path, pdf_folder_path):
    """Extract images from the given PDF file."""
    doc = fitz.open(pdf_file_path)
    page_count = doc.page_count
    xreflist = []
    imglist = []
    for pno in range(page_count):
        il = doc.get_page_images(pno)
        imglist.extend([x[0] for x in il])
        for img in il:
            xref = img[0]
            if xref in xreflist:
                continue
            width, height = img[2], img[3]
            if min(width, height) <= DIMENSION_LIMIT:
                continue
            image = recover_pix(doc, img)
            n = image["colorspace"]
            imgdata = image["image"]
            if len(imgdata) <= ABSOLUTE_SIZE:
                continue
            if len(imgdata) / (width * height * n) <= RELATIVE_SIZE:
                continue
            imgfile = os.path.join(pdf_folder_path, f"img{xref:05}.{image['ext']}")
            with open(imgfile, "wb") as fout:
                fout.write(imgdata)
            xreflist.append(xref)
    return imglist, xreflist

def main():
    """Main function to extract images from all PDF files in the folder."""
    pdf_files = [file for file in os.listdir(FOLDER_PATH) if file.endswith(".pdf")]
    for pdf_file in pdf_files:
        pdf_file_path = os.path.join(FOLDER_PATH, pdf_file)
        folder_name = os.path.splitext(pdf_file)[0]
        pdf_folder_path = os.path.join(FOLDER_PATH, folder_name)
        os.makedirs(pdf_folder_path, exist_ok=True)
        print(f"Created folder '{folder_name}'.")
        t0 = time.time()
        imglist, xreflist = extract_images_from_pdf(pdf_file_path, pdf_folder_path)
        t1 = time.time()
        print(f"{len(set(imglist))} images in total")
        print(f"{len(xreflist)} images extracted")
        print(f"total time {t1 - t0} sec")

if __name__ == "__main__":
    load_dotenv()
    main()