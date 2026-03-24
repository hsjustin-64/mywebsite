import os
import json
import re
import time # 👈 [추가됨] 시간을 제어하는 부품
from google import genai
from google.genai import types
from PIL import Image

# ⭐ 구글 API 키 입력
GOOGLE_API_KEY = "AIzaSyDl1jSJX73S0KzOeObNbbwZb5TY_0iWP50"
client = genai.Client(api_key=GOOGLE_API_KEY)

# ⭐ 경로 설정 (두 칸 위로 올라가서 アニメ 폴더 찾기)
current_folder = os.path.dirname(os.path.abspath(__file__))
anime_folder = os.path.join(current_folder, "アニメ")
db_file = os.path.join(current_folder, "db.js") # db.js 위치도 필요에 따라 맞춰주세요!

print("🔍 기존 db.js 파일을 분석하고 있습니다...")

# ⭐ 기존 데이터 읽어오기
db_data = {}
if os.path.exists(db_file):
    with open(db_file, "r", encoding="utf-8") as f:
        content = f.read()
        start = content.find('{')
        end = content.rfind('}') + 1
        if start != -1 and end != 0:
            json_str = content[start:end]
            json_str = re.sub(r',\s*}', '}', json_str) 
            db_data = json.loads(json_str)

# ⭐ 새로운 사진 찾아내기
valid_extensions = ('.png', '.jpg', '.jpeg')
all_images = [f for f in os.listdir(anime_folder) if f.lower().endswith(valid_extensions)]
new_images = [img for img in all_images if img not in db_data]

if not new_images:
    print("\n✅ 새로 추가된 사진이 없습니다! (모두 최신 상태입니다.)")
else:
    print(f"\n🎉 총 {len(new_images)}장의 새로운 사진을 분석합니다. (1분당 15장 제한으로 인해 시간이 조금 걸립니다.)\n")
    
    safety_settings = [
        types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_HARASSMENT, threshold=types.HarmBlockThreshold.BLOCK_NONE),
        types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH, threshold=types.HarmBlockThreshold.BLOCK_NONE),
        types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT, threshold=types.HarmBlockThreshold.BLOCK_NONE),
        types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT, threshold=types.HarmBlockThreshold.BLOCK_NONE),
    ]

    # ⭐ 분석 시작!
    for index, img_name in enumerate(new_images, 1):
        img_path = os.path.join(anime_folder, img_name)
        
        try:
            print(f"[{index}/{len(new_images)}] 👀 읽는 중: {img_name} ... ", end="", flush=True)
            img = Image.open(img_path)
            prompt = "이 애니메이션 화면에 있는 자막 텍스트만 추출해 줘. 자막이 없으면 '자막 없음'이라고 해줘. 부가 설명은 하지 마."
            
            # 모델은 현재 가장 빠르고 안정적인 최신 2.0 버전을 사용합니다.
            response = client.models.generate_content(
                model='gemini-1.5-flash-8b', 
                contents=[prompt, img],
                config=types.GenerateContentConfig(safety_settings=safety_settings)
            )
            
            extracted_text = response.text.strip()
            db_data[img_name] = extracted_text
            print("성공! ⭕")
            
        except Exception as e:
            # 실패하더라도 빈칸으로 두고 멈추지 않습니다!
            db_data[img_name] = ""
            print(f"실패! ❌ (이유: {e})")
            
        # ⭐ [핵심 방어막] 성공하든 실패하든 구글 서버가 화내지 않게 무조건 4초(또는 4.5초)를 쉽니다!
        time.sleep(4.5) 

    # ⭐ 업데이트된 데이터 저장
    print("\n💾 분석 완료! db.js 파일을 새롭게 업데이트합니다...")
    with open(db_file, "w", encoding="utf-8") as f:
        updated_json = json.dumps(db_data, ensure_ascii=False, indent=4)
        f.write(f"const imageTextDB = {updated_json};\n")
        
    print("✨ 완벽하게 업데이트가 끝났습니다!")