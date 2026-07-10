from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from docxtpl import DocxTemplate
import os
import io
import re

app = FastAPI()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")

# 确保模板目录存在
os.makedirs(TEMPLATE_DIR, exist_ok=True)

class ReportRequest(BaseModel):
    template_name: str
    data: dict

def is_safe_filename(filename: str) -> bool:
    # 仅允许字母、数字、下划线、连字符和点（扩展名），不允许路径分隔符
    return bool(re.match(r'^[\w\-\.]+$', filename))

@app.get("/")
def home():
    return {"status": "running", "service": "word generator"}

@app.post("/generate_docx")
async def generate(request: ReportRequest):
    # 校验模板名称安全性
    if not is_safe_filename(request.template_name):
        raise HTTPException(status_code=400, detail="Invalid template name")

    template_path = os.path.join(TEMPLATE_DIR, request.template_name)
    if not os.path.exists(template_path):
        raise HTTPException(status_code=404, detail="Template not found")

    try:
        doc = DocxTemplate(template_path)
        doc.render(request.data)

        # 保存到内存字节流
        byte_stream = io.BytesIO()
        doc.save(byte_stream)
        byte_stream.seek(0)

        # 直接返回文件流
        filename = f"report_{uuid.uuid4().hex}.docx"  # 用 hex 缩短文件名
        return FileResponse(
            content=byte_stream,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            filename=filename
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Rendering failed: {str(e)}")