import os
import json
import re
import time
import subprocess
from google import genai
from google.genai import types
from PIL import Image

# ⭐ 1. 본인의 API 키를 여기에 쏙 넣어주세요!
GOOGLE_API_KEY = "AIzaSyDl1jSJX73S0KzOeObNbbwZb5TY_0iWP50"
client = genai.Client(api_key=GOOGLE_API_KEY)

# 📂 2. 폴더 경로 설정 (자신의 컴퓨터 환경에 맞게 되어있는지 확인)
current_folder = os.path.dirname(os.path.abspath(__file__))
anime_folder = os.path.abspath(os.path.join(current_folder, "アニメ"))
db_file = os.path.join(current_folder, "db.js")

print("==================================================")
print("   🚀 일일 20장 자동 자막 추출 머신 가동 시작!   ")
print("==================================================\n")

# 📥 3. 시작 전 최신 상태 당겨오기 (Pull)
print("📥 [1단계] 깃허브에서 최신 장부(db.js)를 당겨옵니다...")
try:
    subprocess.run(["git", "pull", "origin", "main"], check=True, cwd=current_folder)
    print("✅ 동기화 완료!\n")
except Exception as e:
    print("💡 가져올 새 업데이트가 없거나 동기화에 실패했습니다. (그냥 진행합니다)\n")

# 📖 4. 기존 db.js 파일 읽어오기
db_data = {}
if os.path.exists(db_file):
    with open(db_file, "r", encoding="utf-8") as f:
        content = f.read()
        match = re.search(r'const imageTextDB = (\{.*?\});', content, re.DOTALL)
        if match:
            db_data = json.loads(match.group(1))

# 🔍 5. 새 사진 찾기 및 '딱 20장'만 자르기 (하루 할당량 방어!)
all_images = [f for f in os.listdir(anime_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
new_images = [img for img in all_images if img not in db_data][:20] 

if not new_images:
    print("🎉 와우! 폴더 안의 모든 사진이 이미 장부에 등록되어 있습니다! 오늘 할 일 끝!")
    exit()

print(f"🔍 [2단계] 총 {len(new_images)}장의 새로운 사진 분석을 시작합니다. (하루 20장 제한)\n")

# 🛡️ 6. 안전 필터 해제
safety_settings = [
    types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="BLOCK_NONE"),
    types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="BLOCK_NONE"),
    types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="BLOCK_NONE"),
    types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="BLOCK_NONE"),
]

# 🧠 7. 본격적인 AI 자막 분석 (무한 버티기 모드 장착!)
for index, img_name in enumerate(new_images, 1):
    img_path = os.path.join(anime_folder, img_name)
    success = False
    
    while not success:
        try:
            print(f"[{index}/{len(new_images)}] 👀 읽는 중: {img_name} ... ", end="", flush=True)
            img = Image.open(img_path)
            prompt = "이 애니메이션 화면에 있는 자막 텍스트만 추출해 줘. 자막이 없으면 '자막 없음'이라고 해줘. 부가 설명은 하지 마."
            
            response = client.models.generate_content(
                model='gemini-2.5-flash-lite', 
                contents=[prompt, img],
                config=types.GenerateContentConfig(safety_settings=safety_settings)
            )
            
            db_data[img_name] = response.text.strip()
            print("성공! ⭕")
            success = True 
            
            time.sleep(4.5) # 정상 성공 시 구글이 놀라지 않게 4초 휴식
            
        except Exception as e:
            # 429 에러(속도 제한) 발생 시 15초 푹 쉬고 다시 시도!
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                print(f"\n⏳ [속도 제한] 구글이 너무 빠르다며 화를 냅니다. 15초 푹 쉬고 이 사진부터 다시 들이밉니다...")
                time.sleep(15) 
            else:
                db_data[img_name] = ""
                print(f"\n❌ 알 수 없는 에러: {e} (일단 빈칸으로 두고 넘어갑니다)")
                success = True 

# 💾 8. 내 컴퓨터 db.js 파일 덮어쓰기
print("\n💾 [3단계] 분석 완료! 내 컴퓨터의 db.js를 새롭게 업데이트합니다...")
with open(db_file, "w", encoding="utf-8") as f:
    updated_json = json.dumps(db_data, ensure_ascii=False, indent=4)
    f.write(f"const imageTextDB = {updated_json};\n")

# 🚀 9. 깃허브로 쏘아 올리기 (Netlify 자동 배포)
print("\n🚀 [4단계] 파이썬이 깃허브 자동 업로드를 시작합니다...")
try:
    subprocess.run(["git", "add", "."], check=True, cwd=current_folder)
    subprocess.run(["git", "commit", "-m", "자동 업데이트: 오늘의 애니 사진 20장 자막 추가"], check=True, cwd=current_folder)
    subprocess.run(["git", "push"], check=True, cwd=current_folder)
    print("\n✅ 모든 작업이 완벽하게 끝났습니다! 1~2분 뒤 Netlify 웹사이트를 새로고침 해보세요!")
except subprocess.CalledProcessError:
    print("\n💡 깃허브에 새로 올릴 변경 사항이 없습니다.")
except Exception as e:
    print(f"\n❌ 깃허브 업로드 실패 (나중에 터미널에서 직접 올려주세요). 이유: {e}")