import re
from typing import List, Optional

from PicImageSearch import Network, SauceNAO

from .ascii2d import ascii2d_search
from .config import config
from .ehentai import ehentai_title_search
from .utils import get_source, handle_img, shorten_url
from .whatanime import whatanime_search


async def saucenao_search(
    url: str, mode: str, proxy: Optional[str], hide_img: bool
) -> List[str]:
    saucenao_db = {
        "all": 999,
        "pixiv": 5,
        "danbooru": 9,
        "anime": 21,
        "doujin": [18, 38],
    }
    async with Network(proxies=proxy) as client:
        if isinstance(db := saucenao_db[mode], list):
            saucenao = SauceNAO(client=client, api_key=config.saucenao_api_key, dbs=db)
        else:
            saucenao = SauceNAO(client=client, api_key=config.saucenao_api_key, db=db)
        res = await saucenao.search(url)
        final_res = []
        max_res = None
        if res and res.raw:
            for i in range(0, config.saucenao_result_num):
                selected_res = res.raw[i]
                try:
                    if selected_res.similarity > max_res.similarity:
                        max_res = selected_res
                except AttributeError:
                    max_res = selected_res
                ext_urls = selected_res.origin["data"].get("ext_urls")
                # 如果结果为 pixiv ，尝试找到原始投稿，避免返回盗图者的投稿
                if selected_res.index_id == saucenao_db["pixiv"]:
                    pixiv_res_list = list(
                        filter(
                            lambda x: x.index_id == saucenao_db["pixiv"]
                            and x.url
                            and abs(x.similarity - selected_res.similarity) < 5,
                            res.raw,
                        )
                    )
                    if len(pixiv_res_list) > 1:
                        selected_res = min(
                            pixiv_res_list,
                            key=lambda x: int(re.search(r"\d+", x.url).group()),  # type: ignore
                        )
                # 如果地址有多个，优先取 danbooru
                elif ext_urls and len(ext_urls) > 1:
                    for i in ext_urls:
                        if "danbooru" in i:
                            selected_res.url = i
                thumbnail = await handle_img(selected_res.thumbnail, proxy, hide_img)
                if selected_res.origin["data"].get("source"):
                    source = shorten_url(selected_res.origin["data"]["source"])
                else:
                    source = shorten_url(await get_source(selected_res.url, proxy))
                # 如果结果为 doujin ，尝试返回日文标题而不是英文标题
                if selected_res.index_id in saucenao_db["doujin"]:  # type: ignore
                    if title := (
                        selected_res.origin["data"].get("jp_name")
                        or selected_res.origin["data"].get("eng_name")
                    ):
                        selected_res.title = title
                _url = shorten_url(selected_res.url)
                res_list = [
                    f"SauceNAO（{selected_res.similarity}%）",
                    f"{thumbnail}",
                    f"{selected_res.title}",
                    f"Author：{selected_res.author}" if selected_res.author else "",
                    _url,
                    f"Source：{source}\n{selected_res.index_name}"
                    if source
                    else f"Source：{selected_res.index_name}",
                ]
                final_res.append("\n".join([i for i in res_list if i != ""]))
            if (
                max_res.similarity < config.saucenao_low_acc
                and mode == "anime"
                or max_res.similarity >= config.saucenao_low_acc
                and "anidb.net" in _url
            ):
                final_res.extend(await whatanime_search(url, proxy, hide_img))
            elif max_res.similarity >= config.saucenao_low_acc and mode == "doujin":
                final_res.extend(
                    await ehentai_title_search(max_res.title, proxy, hide_img)
                )
            elif (
                max_res.similarity < config.saucenao_low_acc
                and config.use_ascii2d_when_low_acc
            ):
                final_res.append(f"相似度 {max_res.similarity}% 过低，自动使用 Ascii2D 进行搜索")
                final_res.extend(await ascii2d_search(url, proxy, hide_img))
        else:
            final_res.append("SauceNAO 暂时无法使用，自动使用 Ascii2D 进行搜索")
            final_res.extend(await ascii2d_search(url, proxy, hide_img))
        return final_res
