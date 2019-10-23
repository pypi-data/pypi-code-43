from pdf2image import convert_from_path

def intervalIntersection(leftA, rightA, leftB, rightB):
    if(leftA>rightA or leftB>rightB):
        return 0
    if(leftA>rightB or leftB>rightA):
        return 0
    return min(rightA, rightB) - max(leftA, leftB)

def boxSize(x1, x2, y1, y2):
    return (x2-x1)*(y2-y1)

def boxIntersection(A_x1, A_x2, A_y1, A_y2, B_x1, B_x2, B_y1, B_y2):
    return intervalIntersection(A_x1, A_x2, B_x1, B_x2) * intervalIntersection(A_y1, A_y2, B_y1, B_y2)

def boxUnion(A_x1, A_x2, A_y1, A_y2, B_x1, B_x2, B_y1, B_y2):
    return boxSize(A_x1, A_x2, A_y1, A_y2) + boxSize(B_x1, B_x2, B_y1, B_y2) - boxIntersection(A_x1, A_x2, A_y1, A_y2, B_x1, B_x2, B_y1, B_y2)

def intersectionOverUnion(A_x1, A_x2, A_y1, A_y2, B_x1, B_x2, B_y1, B_y2):
    return boxIntersection(A_x1, A_x2, A_y1, A_y2, B_x1, B_x2, B_y1, B_y2) / boxUnion(A_x1, A_x2, A_y1, A_y2, B_x1, B_x2, B_y1, B_y2)
    
    
def extractBoundingBox(inputPath, pageNumber, outputPath):
    pages = convert_from_path(inputPath, dpi=300, fmt='jpeg', first_page=pageNumber, last_page=pageNumber)
    pageImg = pages[0]
    width = pageImg.width
    height = pageImg.height
    box = pageImg.crop([x1*width, y1*height, x2*width, y2*height])
    box.save(outputPath))