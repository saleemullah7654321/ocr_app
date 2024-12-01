from fastapi import FastAPI, Request, UploadFile, File
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import cv2
import numpy as np
from .camera import ImageProcessor
from .ocr_processor import OCRProcessor

app = FastAPI()

# Mount static files and templates
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="templates")

# Initialize processors
image_processor = ImageProcessor()
ocr_processor = OCRProcessor()

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/process")
async def process_image(file: UploadFile = File(...)):
    contents = await file.read()
    nparr = np.fromstring(contents, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    # Get image dimensions
    height, width = image.shape[:2]
    
    # Process the image
    processed_frame = image_processor.process_image(image)
    if processed_frame is None:
        return JSONResponse({
            "error": "No card detected",
            "debug_info": {
                "image_size": f"{width}x{height}",
                "min_area": int(image_processor.min_card_area),
                "max_area": int(image_processor.max_card_area)
            }
        })
    
    # Process OCR
    text_results = ocr_processor.process_image(processed_frame)
    return JSONResponse({
        "success": True,
        "text_results": text_results
    }) 