# from paddleocr import PaddleOCR, draw_ocr


# def perform_ocr(image_path):
#     ocr = PaddleOCR(lang="en")

#     # Run OCR on the image
#     result = ocr.ocr(image_path, cls=True)

#     # Process the OCR result as neede
  
#     for res in result:
#         return res[0][1][0]

# from paddleocr import PaddleOCR


# def perform_ocr(image_path):
#     ocr = PaddleOCR(lang="en")

#     # Run OCR on the image
#     result = ocr.ocr(image_path, cls=True)

#     # Extract and return only the text
#     text_result = []
#     for line in result:
#         line_text = " ".join([word_info[-1] for word_info in line])
#         text_result.append(line_text)

#     return text_result
