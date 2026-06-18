import os
import requests
import google.generativeai as genai
from datetime import datetime

# 1. 환경 변수에서 API 키 안전하게 불러오기
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# [보완] 필수 암호 키가 누락되었는지 사전 검증
if not GEMINI_API_KEY:
    raise ValueError("에러: GEMINI_API_KEY를 찾을 수 없습니다. GitHub Secrets 설정을 확인하세요.")
if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
    raise ValueError("에러: 텔레그램 토큰 또는 Chat ID가 누락되었습니다.")

# 2. Gemini AI 설정 (최신 모델 반영)
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')  # 최신 고속 무료 모델로 교체

# 3. 오늘 날짜 및 투자 보고서 프롬프트 구성
today_str = datetime.today().strftime('%Y-%m-%d')
prompt = f"""
당신은 글로벌 매크로 헤지펀드의 최고투자책임자(CIO)입니다. 
오늘은 {today_str}입니다. 최근의 글로벌 거시경제 동향(미국 증시, 인플레이션, 금리 동향, 원자재 시장 등)을 분석하여 
향후 자산 배분 전략을 제안하는 'Daily CIO 매크로 리포트'를 한글로 작성해 주세요.
보고서는 마크다운(Markdown) 형식으로 작성해야 하며, 마지막에는 바쁜 트레이더들을 위한 3줄 요약(Summary)을 반드시 포함해야 합니다.
"""

try:
    print("AI 분석을 시작합니다 (Gemini-1.5-flash)...")
    response = model.generate_content(prompt)
    report_content = response.text
except Exception as e:
    print(f"Gemini API 호출 중 에러가 발생했습니다: {e}")
    raise e

# 4. 텔레그램으로 보낼 요약본 추출
summary_text = f"📊 *Daily CIO Report Summary ({today_str})*\n\n"
if "요약" in report_content:
    summary_text += report_content.split("요약")[-1].strip()
else:
    summary_text += report_content[:300] + "..."

# 5. 텔레그램 메시지 전송
print("텔레그램 브리핑 전송 중...")
telegram_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
payload = {
    "chat_id": TELEGRAM_CHAT_ID,
    "text": summary_text,
    "parse_mode": "Markdown"
}
try:
    res = requests.post(telegram_url, json=payload)
    if res.status_code == 200:
        print("텔레그램 전송 완료!")
    else:
        print(f"텔레그램 전송 실패 (코드 {res.status_code}): {res.text}")
except Exception as e:
    print(f"텔레그램 전송 중 오류: {e}")

# 6. 옵시디언 동기화를 위해 폴더 및 마크다운 파일 생성
os.makedirs("Daily Reports", exist_ok=True)
file_path = f"Daily Reports/{today_str}.md"
with open(file_path, "w", encoding="utf-8") as f:
    f.write(report_content)

print(f"리포트 파일 생성 성공: {file_path}")
