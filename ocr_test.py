import easyocr
import os
import ssl

# 보안 인증서 무사통과 주문
ssl._create_default_https_context = ssl._create_unverified_context

# 🎯 파일 경로 설정 (jpg에서 png로 완벽 수정!)
current_folder = os.path.dirname(__file__)
image_path = os.path.join(current_folder, "test.png") 

# ⭐ [핵심 방어막] 파일이 진짜 있는지 먼저 검사합니다!
if not os.path.exists(image_path):
    print("\n🚨 [삐빅! 에러 발생]")
    print(f"'{image_path}' 경로에 사진 파일이 없습니다!")
    print("1. 파일이 mywebsite 폴더 안에 제대로 있는지 확인해 주세요.")
    print("2. 파일 이름이 test.png.png 로 되어있지 않은지 꼭 확인해 주세요!\n")
else:
    print("🤖 한국어 OCR 모델 세팅 중...")
    reader = easyocr.Reader(['ko', 'en'])
    
    print("👀 이미지의 글씨를 읽고 있습니다...")
    
    # 만약 나중에 폴더 이름이 다시 한글로 바뀌어도 에러가 나지 않게 바이트로 읽어줍니다!
    with open(image_path, 'rb') as f:
        img_bytes = f.read()

    # 이미지 경로 대신 바이트 데이터를 통째로 넣습니다.
    result = reader.readtext(img_bytes, detail=0)

    print("\n🎉 [읽기 성공! 결과 확인]")
    print("=" * 40)
    print(" ".join(result))
    print("=" * 40)