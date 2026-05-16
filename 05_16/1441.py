import random


def play_guessing_game():
    print("=== 猜數字遊戲 ===")
    print("我會選一個 1 到 100 之間的數字，請你一直猜到正確為止。")

    target = random.randint(1, 100)
    attempts = 0

    while True:
        guess_text = input("請輸入你的猜測：")
        if not guess_text.strip():
            print("請輸入一個數字。")
            continue

        if not guess_text.strip().isdigit():
            print("輸入錯誤，請輸入正整數。")
            continue

        guess = int(guess_text)
        attempts += 1

        if guess < target:
            print("太小了！再試一次。")
        elif guess > target:
            print("太大了！再試一次。")
        else:
            print(f"恭喜你猜對了！答案是 {target}。共猜了 {attempts} 次。")
            break


if __name__ == "__main__":
    play_guessing_game()
