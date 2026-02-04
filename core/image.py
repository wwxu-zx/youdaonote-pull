import hashlib
import imghdr
import logging
import mimetypes
import os
import re
from typing import Tuple
from urllib import parse
from urllib.parse import urlparse

import requests

REGEX_IMAGE_URL = re.compile(r"!\[.*?\]\((.*?note\.youdao\.com.*?)\)")
REGEX_ATTACH = re.compile(r"\[(.*?)\]\(((http|https)://note\.youdao\.com.*?)\)")
# 资源统一目录
ASSETS = "assets_ori"


def sanitize_filename(filename: str) -> str:
    """
    清理文件名，将中文字符替换为英文
    :param filename: 原始文件名
    :return: 清理后的文件名
    """
    # 智能替换"截图"为screenshot
    # 如果截图前后有字符，保留下划线分隔
    def replace_screenshot(match):
        before = match.group(1)
        after = match.group(2)
        # 如果前面有字符且不是下划线/横杠/点，添加下划线
        prefix = '_' if before and before not in ('_', '-', '.', '') else ''
        # 如果后面有字符且不是下划线/横杠/点，添加下划线  
        suffix = '_' if after and after not in ('_', '-', '.', '') else ''
        return before + prefix + 'screenshot' + suffix + after
    
    # 匹配"截图"，捕获前后字符
    filename = re.sub(r'([^/]*?)截图([^/]*)', replace_screenshot, filename)
    
    return filename


class ImagePull:
    def __init__(
        self,
        youdaonote_api,
        smms_secret_token: str,
        is_relative_path: bool,
    ):
        self.youdaonote_api = youdaonote_api
        self.smms_secret_token = smms_secret_token
        self.is_relative_path = is_relative_path

    @classmethod
    def _url_encode(cls, file_path: str):
        """对一些特殊字符url编码
        :param file_path:
        """
        file_path = file_path.replace(" ", "%20")
        return file_path

    def migration_ydnote_url(self, file_path, local_dir=None):
        """
        迁移有道云笔记文件 URL
        :param file_path: markdown文件路径
        :param local_dir: 本地目录，用于计算assets路径
        :return:
        """

        # 文件内容为空，也下载到本地
        with open(file_path, "rb") as f:
            content = f.read().decode("utf-8")

        # 图片
        image_urls = REGEX_IMAGE_URL.findall(content)
        if len(image_urls) > 0:
            logging.info("正在转换有道云笔记「{}」中的有道云图片链接...".format(file_path))
        for image_url in image_urls:
            try:
                image_path = self._get_new_image_path(file_path, image_url, local_dir)
            except Exception as error:
                logging.info(
                    "下载图片「{}」可能失败！请检查图片！错误提示：{}".format(image_url, format(error))
                )
            if image_url == image_path:
                continue
            # 将绝对路径替换为相对路径
            # markdown 文件在 posts/ 目录，图片在 assets/ 目录，需要 ../assets/...
            if self.is_relative_path and not self.smms_secret_token:
                assets_index = image_path.find(ASSETS)
                if assets_index != -1:
                    # 从 assets 开始的相对路径
                    relative_path = image_path[assets_index:]
                    # 由于 md 文件在 posts/ 目录，需要 ../ 前缀
                    # 使用 <> 包裹路径以支持包含空格和括号的路径
                    image_path = "<../" + relative_path + ">"
                else:
                    # 如果找不到 assets，保持原样
                    image_path = image_path

            content = content.replace(image_url, image_path)

        # 附件
        attach_name_and_url_list = REGEX_ATTACH.findall(content)
        if len(attach_name_and_url_list) > 0:
            logging.info("正在转换有道云笔记「{}」中的有道云附件链接...".format(file_path))
        for attach_name_and_url in attach_name_and_url_list:
            attach_url = attach_name_and_url[1]
            attach_path = self._download_ydnote_url(
                file_path, attach_url, attach_name_and_url[0], local_dir
            )
            if not attach_path:
                continue
            # 将绝对路径替换为相对路径
            # markdown 文件在 posts/ 目录，附件在 assets/ 目录，需要 ../assets/...
            if self.is_relative_path:
                assets_index = attach_path.find(ASSETS)
                if assets_index != -1:
                    # 从 assets 开始的相对路径
                    relative_path = attach_path[assets_index:]
                    # 由于 md 文件在 posts/ 目录，需要 ../ 前缀
                    # 使用 <> 包裹路径以支持包含空格和括号的路径
                    attach_path = "<../" + relative_path + ">"
                else:
                    # 如果找不到 assets，保持原样
                    attach_path = attach_path
            content = content.replace(attach_url, attach_path)

        with open(file_path, "wb") as f:
            f.write(content.encode())
        return

    def _get_new_image_path(self, file_path, image_url, local_dir=None) -> str:
        """
        将图片链接转换为新的链接
        :param file_path:
        :param image_url:
        :param local_dir: 本地目录
        :return: new_image_path
        """
        # 当 smms_secret_token 为空（不上传到 SM.MS），下载到图片到本地
        if not self.smms_secret_token:
            image_path = self._download_ydnote_url(file_path, image_url, None, local_dir)
            return image_path or image_url

        # smms_secret_token 不为空，上传到 SM.MS
        new_file_url, error_msg = ImageUpload.upload_to_smms(
            youdaonote_api=self.youdaonote_api,
            image_url=image_url,
            smms_secret_token=self.smms_secret_token,
        )
        # 如果上传失败，仍下载到本地
        if not error_msg:
            return new_file_url
        logging.info(error_msg)
        image_path = self._download_ydnote_url(file_path, image_url, None, local_dir)
        return image_path or image_url

    def _download_ydnote_url(self, file_path, url, attach_name=None, local_dir=None) -> str:
        """
        下载文件到本地，返回本地路径
        :param file_path: markdown文件路径
        :param url:
        :param attach_name:
        :param local_dir: 本地目录，用于计算assets路径
        :return:  path
        """
        try:
            response = self.youdaonote_api.http_get(url)
        except requests.exceptions.ProxyError as err:
            error_msg = "网络错误，「{}」下载失败。错误提示：{}".format(url, format(err))
            logging.info(error_msg)
            return ""

        content_type = response.headers.get("Content-Type")
        file_type = "附件" if attach_name else "图片"
        if response.status_code != 200 or not content_type:
            error_msg = "下载「{}」失败！{}可能已失效，可浏览器登录有道云笔记后，查看{}是否能正常加载".format(
                url, file_type, file_type
            )
            logging.info(error_msg)
            return ""

        normalized_content_type = content_type.split(";")[0].strip().lower() if content_type else ""
        if (
            not attach_name
            and normalized_content_type
            and not normalized_content_type.startswith("image/")
            and normalized_content_type != "application/octet-stream"
        ):
            error_msg = "下载「{}」失败！返回内容非图片（{}）".format(url, normalized_content_type)
            logging.info(error_msg)
            return ""

        if attach_name:
            # 附件使用原文件名
            file_suffix = attach_name
        else:
            # 图片根据 URL 或 content-type 获取扩展名
            file_suffix = self._guess_image_extension(url, normalized_content_type, response.content)

        # 获取文件所在目录
        if file_path.find(".") == -1:
            # 如果 file_path 没有扩展名，说明是目录，直接在该目录下创建 assets 文件夹
            file_dir = file_path
            md_file_name = None
        else:
            # 获取markdown文件名（不含扩展名）
            md_file_name = os.path.splitext(os.path.basename(file_path))[0]
            # 如果提供了local_dir，说明markdown文件在posts文件夹，需要在local_dir下创建 assets
            if local_dir:
                file_dir = local_dir
            else:
                # 否则使用markdown文件所在目录
                file_dir = file_path[: file_path.rfind("/")]
        
        # 构建本地文件目录
        # 图片和附件都保存在 assets/{markdown文件名}/ 下
        if md_file_name:
            local_file_dir = os.path.join(file_dir, ASSETS, md_file_name).replace("\\", "/")
        else:
            # 如果没有文件名，直接保存在assets文件夹下
            local_file_dir = os.path.join(file_dir, ASSETS).replace("\\", "/")

        if not os.path.exists(local_file_dir):
            os.makedirs(local_file_dir, exist_ok=True)
        file_basename = os.path.basename(urlparse(url).path)

        if attach_name:
            # 请求后的真实的 URL 中才有东西
            realUrl = parse.parse_qs(urlparse(response.url).query)

            if realUrl:
                filename = (
                    realUrl.get("filename")[0]
                    if realUrl.get("filename")
                    else realUrl.get("download")[0]
                    if realUrl.get("download")
                    else ""
                )
                file_name = file_basename + filename
            else:
                file_name = "".join([file_basename, file_suffix])
            # 清理文件名
            file_name = sanitize_filename(file_name)
        else:
            # 图片使用唯一编码命名（基于内容 MD5，相同内容复用文件）
            unique_hash = hashlib.md5(response.content).hexdigest()
            file_name = f"{unique_hash}{file_suffix}"
        
        local_file_path = os.path.join(local_file_dir, file_name).replace("\\", "/")

        try:
            with open(local_file_path, "wb") as f:
                f.write(response.content)  # response.content 本身就为字节类型
            logging.info("已将{}「{}」转换为「{}」".format(file_type, url, local_file_path))
        except:
            error_msg = "{} {}有误！".format(url, file_type)
            logging.info(error_msg)
            return ""

        return local_file_path

    @staticmethod
    def _guess_image_extension(url: str, content_type: str, data: bytes) -> str:
        ext = os.path.splitext(urlparse(url).path)[1].lower()
        if ext and ext != ".bin":
            return ext
        detected = imghdr.what(None, data)
        if detected:
            if detected == "jpeg":
                return ".jpg"
            return f".{detected}"
        if content_type:
            guessed = mimetypes.guess_extension(content_type)
            if guessed and guessed != ".bin":
                return guessed
            if content_type.startswith("image/"):
                return "." + content_type.split("/", 1)[1]
        return ".jpg"

    def _set_relative_file_path(self, file_path, file_name, local_file_dir) -> str:
        """
        图片/附件设置为相对地址
        :param file_path:
        :param file_name:
        :param local_file_dir:
        :return:
        """
        note_file_dir = os.path.dirname(file_path)
        rel_file_dir = os.path.relpath(local_file_dir, note_file_dir)
        rel_file_path = os.path.join(rel_file_dir, file_name)
        new_file_path = rel_file_path.replace("\\", "/")
        return new_file_path


class ImageUpload(object):
    """
    图片上传到指定图床
    """

    @staticmethod
    def upload_to_smms(youdaonote_api, image_url, smms_secret_token) -> Tuple[str, str]:
        """
        上传图片到 sm.ms
        :param image_url:
        :param smms_secret_token:
        :return: url, error_msg
        """
        try:
            smfile = youdaonote_api.http_get(image_url).content
        except:
            error_msg = "下载「{}」失败！图片可能已失效，可浏览器登录有道云笔记后，查看图片是否能正常加载".format(image_url)
            return "", error_msg
        files = {"smfile": smfile}
        upload_api_url = "https://sm.ms/api/v2/upload"
        headers = {"Authorization": smms_secret_token}

        error_msg = (
            "SM.MS 免费版每分钟限额 20 张图片，每小时限额 100 张图片，大小限制 5 M，上传失败！「{}」未转换，"
            "将下载图片到本地".format(image_url)
        )
        try:
            res_json = requests.post(
                upload_api_url, headers=headers, files=files, timeout=5
            ).json()
        except requests.exceptions.ProxyError as err:
            error_msg = "网络错误，上传「{}」到 SM.MS 失败！将下载图片到本地。错误提示：{}".format(
                image_url, format(err)
            )
            return "", error_msg
        except Exception:
            return "", error_msg

        if res_json.get("success"):
            url = res_json["data"]["url"]
            logging.info("已将图片「{}」转换为「{}」".format(image_url, url))
            return url, ""
        if res_json.get("code") == "image_repeated":
            url = res_json["images"]
            logging.info("已将图片「{}」转换为「{}」".format(image_url, url))
            return url, ""
        if res_json.get("code") == "flood":
            return "", error_msg

        error_msg = (
            "上传「{}」到 SM.MS 失败，请检查图片 url 或 smms_secret_token（{}）是否正确！将下载图片到本地".format(
                image_url, smms_secret_token
            )
        )
        return "", error_msg
