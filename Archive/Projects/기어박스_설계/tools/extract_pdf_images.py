"""
PDF 이미지 추출 스크립트
- PyMuPDF(fitz)를 사용하여 PDF에서 이미지를 추출
- 각 이미지를 PNG로 저장하고 위치 정보를 JSON으로 출력
"""

import sys
import json
import os
from pathlib import Path

import fitz  # PyMuPDF
from PIL import Image
import io


def extract_images(pdf_path: str, output_dir: str) -> list[dict]:
    """PDF에서 이미지를 추출하여 output_dir에 저장하고 메타데이터를 반환한다."""
    pdf_path = Path(pdf_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    doc = fitz.open(str(pdf_path))
    images_info = []
    img_counter = 0

    for page_num in range(len(doc)):
        page = doc[page_num]
        image_list = page.get_images(full=True)

        for img_index, img_info in enumerate(image_list):
            xref = img_info[0]

            try:
                base_image = doc.extract_image(xref)
            except Exception:
                continue

            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            width = base_image["width"]
            height = base_image["height"]

            # 너무 작은 이미지는 아이콘/장식이므로 건너뜀
            if width < 50 or height < 50:
                continue

            img_counter += 1
            filename = f"fig{img_counter}.png"
            save_path = output_dir / filename

            # PNG로 변환하여 저장
            try:
                pil_image = Image.open(io.BytesIO(image_bytes))
                # 300dpi 메타데이터 설정
                pil_image.save(str(save_path), "PNG", dpi=(300, 300))
            except Exception:
                # PIL 변환 실패 시 원본 바이트 직접 저장
                with open(save_path, "wb") as f:
                    f.write(image_bytes)

            # 페이지 내 이미지 위치(bbox) 찾기
            bbox = None
            for img_rect in page.get_image_rects(xref):
                bbox = {
                    "x0": round(img_rect.x0, 1),
                    "y0": round(img_rect.y0, 1),
                    "x1": round(img_rect.x1, 1),
                    "y1": round(img_rect.y1, 1),
                }
                break

            images_info.append({
                "index": img_counter,
                "filename": filename,
                "page": page_num + 1,
                "width": width,
                "height": height,
                "original_ext": image_ext,
                "bbox": bbox,
            })

    doc.close()
    return images_info


def main():
    if len(sys.argv) < 3:
        print("사용법: python extract_pdf_images.py <PDF경로> <출력디렉토리>", file=sys.stderr)
        sys.exit(1)

    pdf_path = sys.argv[1]
    output_dir = sys.argv[2]

    if not os.path.isfile(pdf_path):
        print(f"오류: PDF 파일을 찾을 수 없습니다: {pdf_path}", file=sys.stderr)
        sys.exit(1)

    images_info = extract_images(pdf_path, output_dir)

    # JSON으로 결과 출력 (에이전트가 파싱할 수 있도록)
    result = {
        "pdf_path": pdf_path,
        "output_dir": output_dir,
        "total_images": len(images_info),
        "images": images_info,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
