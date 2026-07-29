import os
import sys
from google import genai
from google.genai import types

# =====================================================================
# 1. ИНИЦИАЛИЗАЦИЯ КЛИЕНТА GEMINI
# =====================================================================
# Скрипт автоматически попытается взять ключ из переменной окружения GEMINI_API_KEY.
# Если вы хотите вставить ключ вручную в код, замените строчку ниже на:
# client = genai.Client(api_key="AIzaSyDlrW_C8zdm3UmKb0NkCOoNE5Wj9SakiE4")
try:
    client = genai.Client()
except Exception as e:
    print("❌ Ошибка инициализации Gemini API!")
    print("Убедитесь, что вы установили библиотеку: pip install google-genai")
    print("И задали переменную окружения GEMINI_API_KEY.")
    sys.exit(1)

# Словарь для хранения сессий чата (память для каждого отдельного пользователя)
chat_sessions = {}

# =====================================================================
# 2. ФУНКЦИЯ ОБЩЕНИЯ С ИИ
# =====================================================================
def ask_shopmaster_gemini(user_id, user_message):
    try:
        # Проверяем наличие файла настроек поведения
        if not os.path.exists("SystemPrompt.txt"):
            return "Ошибка: Файл SystemPrompt.txt не найден в папке со скриптом!"
            
        # Проверяем наличие файла базы знаний
        if not os.path.exists("knowledge.txt"):
            return "Ошибка: Файл knowledge.txt не найден в папке со скриптом!"

        # Читаем инструкции и базу знаний из файлов
        with open("SystemPrompt.txt", "r", encoding="utf-8") as f:
            system_prompt = f.read()
            
        with open("knowledge.txt", "r", encoding="utf-8") as f:
            knowledge = f.read()

        # Объединяем правила поведения и технические знания в один системный промпт
        full_instruction = f"{system_prompt}\n\nTECHNICAL KNOWLEDGE BASE:\n{knowledge}"

        # Если пользователь пишет впервые — создаем для него изолированную сессию чата
        if user_id not in chat_sessions:
            chat_sessions[user_id] = client.chats.create(
                model="gemini-1.5-flash", # Самая быстрая, экономичная и точная модель для чата
                config=types.GenerateContentConfig(
                    system_instruction=full_instruction,
                    temperature=0.1, # Минимальная температура, чтобы ИИ строго следовал правилам и не галлюцинировал
                )
            )
        
        # Отправляем сообщение в существующую сессию (Gemini сам хранит историю внутри этого объекта)
        chat = chat_sessions[user_id]
        response = chat.send_message(user_message)
        
        return response.text

    except Exception as error:
        return f"Произошла техническая ошибка при запросе к Gemini: {error}"

# =====================================================================
# 3. ТЕСТОВЫЙ ИНТЕРАКТИВНЫЙ ЗАПУСК В КОНСОЛИ
# =====================================================================
if __name__ == "__main__":
    print("\n" + "="*60)
    print("🤖 ИИ-ассистент ShopMaster успешно запущен через Gemini API!")
    print("="*60)
    print("Напишите ваш вопрос (или введите 'exit', 'quit', 'выход' для завершения):")
    
    # Используем фиксированный ID для консольного теста. 
    # В реальном боте сюда будет передаваться реальный Telegram Chat ID.
    test_user_id = "console_test_user"
    
    while True:
        try:
            # Получаем ввод от пользователя
            user_input = input("\nВы: ")
            
            # Проверяем команду выхода
            if user_input.lower() in ['exit', 'quit', 'выход']:
                print("Выход из режима тестирования. До встречи!")
                break
                
            # Игнорируем пустой ввод
            if not user_input.strip():
                continue
                
            print("Gemini думает...")
            
            # Запрашиваем ответ у ИИ
            answer = ask_shopmaster_gemini(test_user_id, user_input)
            
            # Выводим результат
            print(f"\nОтвет ShopMaster AI:\n{answer}")
            
        except KeyboardInterrupt:
            print("\nПрограмма принудительно остановлена.")
            break
        except Exception as e:
            print(f"❌ Ошибка в цикле чата: {e}")