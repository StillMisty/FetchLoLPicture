import asyncio
import os

import httpx


os.chdir(os.path.dirname(__file__))


async def get_hero_list():
    url = "https://game.gtimg.cn/images/lol/act/img/js/heroList/hero_list.js"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        res = resp.json()
        return res["hero"]


async def fetch_hero(hero_id: int):
    url = f"https://game.gtimg.cn/images/lol/act/img/js/hero/{hero_id}.js"

    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        res = resp.json()
        hero_name = res["hero"]["title"]
        hero_file_path = f"hero/{hero_name}"
        if not os.path.exists(hero_file_path):
            os.mkdir(hero_file_path)

        img_url_list: list[dict] = res["skins"]
        for img in img_url_list:
            img_url = img.get("mainImg", "")
            if img_url == "":
                continue

            full_hero_name: str = img["name"].replace("/", "")
            img_file_path = f"hero/{hero_name}/{full_hero_name}.png"
            if not os.path.exists(img_file_path):
                with open(img_file_path, "wb") as f:
                    img = await client.get(img_url)
                    f.write(img.content)


def progress_bar(
    iteration, total, prefix="", suffix="", decimals=1, length=50, fill="█"
):
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + "-" * (length - filled_length)
    print(f"\r{prefix} |{bar}| {percent}% {suffix}", end="\r")
    if iteration == total:
        print()


async def main():
    hero_list = await get_hero_list()

    if not os.path.exists("hero"):
        os.mkdir("hero")

    tasks = []
    count = 0
    total = len(hero_list)
    now = 0
    for hero in hero_list:
        tasks.append(fetch_hero(hero["heroId"]))
        count += 1
        now += 1

        # 控制并发数
        if count == 10:
            progress_bar(now, total, prefix="Progress:", suffix="Complete", length=50)
            await asyncio.gather(*tasks)
            tasks = []
            count = 0

    if tasks:
        progress_bar(now, total, prefix="Progress:", suffix="Complete", length=50)
        await asyncio.gather(*tasks)


asyncio.run(main())
