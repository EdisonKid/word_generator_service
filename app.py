from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from docxtpl import DocxTemplate

import os
import uuid


app = FastAPI()


BASE_DIR=os.path.dirname(
    os.path.abspath(__file__)
)


TEMPLATE_DIR=os.path.join(
    BASE_DIR,
    "templates"
)


OUTPUT_DIR=os.path.join(
    BASE_DIR,
    "output"
)


os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)



app.mount(
    "/files",
    StaticFiles(directory=OUTPUT_DIR),
    name="files"
)



class ReportRequest(BaseModel):

    template_name:str

    data:dict



@app.get("/")
def home():

    return {
        "status":"running",
        "service":
        "word generator"
    }



@app.post("/generate_docx")
def generate(
        request:ReportRequest
):

    template_path=os.path.join(
        TEMPLATE_DIR,
        request.template_name
    )


    if not os.path.exists(template_path):

        return {
            "error":
            "template not found"
        }


    filename=(
        "report_"
        +str(uuid.uuid4())
        +".docx"
    )


    output_path=os.path.join(
        OUTPUT_DIR,
        filename
    )


    doc=DocxTemplate(
        template_path
    )


    doc.render(
        request.data
    )


    doc.save(
        output_path
    )


    return {

        "status":"success",

        "file":
        filename,

        "url":
        "/files/"+filename

    }