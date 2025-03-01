import asyncio
from concurrent.futures import ThreadPoolExecutor
import yt_dlp
import os

class AsyncYTDLPWrapper:
    def __init__(self, download_path: str = "downloads", max_concurrent_downloads: int = 3, use_ffmpeg: bool = True):
        """
        Инициализация асинхронной обертки yt-dlp
        :param download_path: Папка для сохранения файлов
        :param max_concurrent_downloads: Максимальное количество параллельных загрузок
        :param use_ffmpeg: Использовать ли FFmpeg для обработки аудио
        """
        self.download_path = download_path
        os.makedirs(self.download_path, exist_ok=True)
        self.executor = ThreadPoolExecutor()
        self.semaphore = asyncio.Semaphore(max_concurrent_downloads)
        self.use_ffmpeg = use_ffmpeg

    @staticmethod
    async def filter_formats(formats):
        """
        Асинхронно фильтрует форматы, удаляя те, у которых неизвестен размер.
        :param formats: Список словарей с форматами видео
        :return: Отфильтрованный список
        """
        return [
            fmt for fmt in formats
            if isinstance(fmt.get("filesize"), (int, float))
        ]

    async def get_format(self, url: str):
        """
        Асинхронно получает список доступных форматов для видео.
        :param url: URL видео
        :return: Список доступных форматов
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, self._get_formats_sync, url)

    @staticmethod
    def _get_formats_sync(url: str):
        """
        Синхронно получает список доступных форматов для видео.
        :param url: URL видео
        :return: Список доступных форматов
        """
        ydl_opts = {"quiet": True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = [
                {
                    "format_id": f["format_id"],
                    "ext": f["ext"],
                    "resolution": f.get("resolution", "unknown"),
                    "fps": f.get("fps", "unknown"),
                    "filesize": f.get("filesize", "unknown"),
                }
                for f in info["formats"]
            ]
            return formats

    async def download(self, url: str, best: bool = True, audio_only: bool = False, format_id: str = None):
        """
        Асинхронно скачивает видео или аудио с ограничением по параллельным загрузкам.
        :param url: URL видео
        :param best: Скачивание в лучшем качестве (по умолчанию True)
        :param audio_only: Скачивание только аудио (по умолчанию False)
        :param format_id: Указанный ID формата (если не None, будет скачан этот формат)
        """
        async with self.semaphore:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                self.executor, self._download_sync, url, best, audio_only, format_id
            )

    def _download_sync(self, url: str, best: bool, audio_only: bool, format_id: str):
        """
        Синхронно скачивает видео или аудио.
        :param url: URL видео
        :param best: Скачивание в лучшем качестве
        :param audio_only: Скачивание только аудио
        :param format_id: Указанный ID формата
        """
        ydl_opts = {
            "outtmpl": os.path.join(self.download_path, "%(title)s.%(ext)s"),
            "quiet": False,
        }

        if audio_only:
            ydl_opts["format"] = "bestaudio/best"
            if self.use_ffmpeg:
                ydl_opts["postprocessors"] = [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }]
        elif best:
            ydl_opts["format"] = "bestvideo+bestaudio/best"
        elif format_id:
            ydl_opts["format"] = format_id

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])