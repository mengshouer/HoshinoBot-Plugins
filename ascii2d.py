from typing import List

from aiohttp import ClientSession
from PicImageSearch import Ascii2D
from PicImageSearch.model import Ascii2DResponse

from .config import config
from .utils import handle_img, shorten_url


async def ascii2d_search(url: str, client: ClientSession, hide_img: bool) -> List[str]:
    ascii2d_color = Ascii2D(client=client)
    ascii2d_bovw = Ascii2D(bovw=True, client=client)
    color_res = await ascii2d_color.search(url)
    if not color_res or not color_res.raw:
        return ["Ascii2D 暂时无法使用"]
    # 针对 QQ 图片链接反盗链做处理
    if color_res.raw[0].hash == "5bb9bec07e71ef10a1a47521d396811d":
        url = f"https://images.weserv.nl/?url={url}"
        color_res = await ascii2d_color.search(url)
        bovw_res = await ascii2d_bovw.search(url)
    else:
        bovw_res = await ascii2d_bovw.search(url)

    async def get_final_res(res: Ascii2DResponse) -> str:
        ascii2d_result_num = config.ascii2d_result_num
        n = 0
        if not res.raw[0].url:
            ascii2d_result_num += 1
            n += 1
        res_list = []
        for i in range(n, ascii2d_result_num):
            thumbnail = await handle_img(res.raw[i].thumbnail, hide_img)
            _url = await shorten_url(res.raw[i].url) if res.raw[i] else ""
            res_list += [
                thumbnail,
                res.raw[i].title or "",
                f"作者：{res.raw[i].author}" if res.raw[i].author else "",
                f"来源：{_url}" if _url else "",
                f"搜索页面：{res.url}\n",
            ]
        return [i for i in res_list if i != ""]

    color_final_res = await get_final_res(color_res)
    bovw_final_res = await get_final_res(bovw_res)
    if color_final_res[:-1] == bovw_final_res[:-1]:
        return ["Ascii2D 色合検索与特徴検索結果完全一致\n" + "\n".join(color_final_res)]

    return [
        f"Ascii2D 色合検索結果\n" + "\n".join(color_final_res),
        f"Ascii2D 特徴検索結果\n" + "\n".join(bovw_final_res),
    ]
