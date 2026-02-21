import os
from openai import OpenAI
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

# 클라이언트 세팅 (OpenAI 단일화)
openai_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

def generate_baby_recipe(ingredients):
    print(f"\n[{ingredients}] 분석 중... (GPT-4o-mini 동작 중 ✨)")
    
    # 1. 텍스트 레시피 생성 (OpenAI gpt-4o-mini)
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "당신은 15개월 아기를 위한 영양사입니다. 무염식을 엄격히 지키되 버터/치즈 등으로 고칼로리를 내는 레시피를 3~4단계로 간결히 작성하세요."},
            {"role": "user", "content": f"냉장고 재료: '{ingredients}'. 요리 이름을 맨 첫 줄에 '[요리명]' 형식으로 적어줘."}
        ],
        temperature=0.7 # 약간의 창의성을 위한 온도 조절
    )
    
    recipe_text = response.choices[0].message.content
    print("\n=== 📝 레시피 완성 ===")
    print(recipe_text)
    
    # 요리명 추출
    dish_name = recipe_text.split('\n')[0].replace('[', '').replace(']', '').strip()

    # 2. 이미지 생성 (DALL-E 3)
    print(f"\n[{dish_name}] 요리 사진 촬영 중... (DALL-E 3 동작 중 🎨)")
    image_response = openai_client.images.generate(
        model="dall-e-3",
        prompt=f"A highly realistic food photography of {dish_name}. Healthy, high-calorie, salt-free baby food. Bright lighting, professional food styling, cute baby bowl.",
        size="1024x1024",
        n=1,
    )
    
    print("\n=== 🖼️ 생성된 이미지 URL ===")
    print(image_response.data[0].url)
    print("==============================\n")

if __name__ == "__main__":
    my_ingredients = "소고기 안심, 브로콜리, 무염 버터, 아기 치즈"
    generate_baby_recipe(my_ingredients)