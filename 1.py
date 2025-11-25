from app.core.bot.utils.code.code import generate_code

mas: list[int] = []
for i in range(1, 100001):
    value: int | None = generate_code(i, 4)
    if value == 0:
        print(i)
    if value in mas:
        print(i, value)
        break
    elif value:
        mas.append(value)
