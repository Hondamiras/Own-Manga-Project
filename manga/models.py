from datetime import date
from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.utils.text import slugify
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile
import os

User = get_user_model()

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    created_by = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.CASCADE,
    editable=False,
    related_name="tags_created",
    null=True,
    blank=True,
    )

    class Meta:
        ordering = ("name",)
        verbose_name = "Teg "
        verbose_name_plural = "Teglar "

    def __str__(self):
        return self.name

class Manga(models.Model): 
    title = models.CharField(max_length=255, verbose_name="Nomi")
    author = models.CharField(max_length=255, verbose_name="Muallifi")
    description = models.TextField(verbose_name="Ta'rifi")
    cover_image = models.ImageField(upload_to="covers/", verbose_name="Poster rasmi")
    genres = models.ManyToManyField("Genre", related_name="mangas", blank=True, verbose_name="Janrlar")
    tags = models.ManyToManyField("Tag", related_name="mangas", blank=True, verbose_name="Teglar")
    publication_date = models.DateField(null=True, blank=True, verbose_name="Chiqarilgan sana yani Manga qachon chiqgan?")
    status = models.CharField(
        max_length=50,
        choices=[
            ("Ongoing", "Davom etmoqda"),
            ("Completed", "To'liq chiqarilgan"),
            ("Stopped", "Bekor qilingan"),
            ("Paused", "To'xtatilgan"),
            ("Announced", "E'lon qilingan"),
        ],
        default="Ongoing",
        verbose_name="Manga holati"
    )
    type = models.CharField(
        max_length=50,
        choices=[("Manga", "Manga"), ("Manhwa", "Manhwa"), ("Manhua", "Manhua"), ("Komiks", "Komiks")],
        default="Manga",
    )
    age_rating = models.CharField(
        max_length=50,
        choices=[("Belgilanmagan", "Belgilanmagan"), ("6+", "6+"), ("12+", "12+"), ("16+", "16+"), ("18+", "18+")],
        default="Belgilanmagan",
        verbose_name="Yosh chegarasi"
    )
    translation_status = models.CharField(
        max_length=50,
        choices=[
            ("Not Translated", "Tarjima qilinmagan"),
            ("In Progress", "Tarjima qilinmoqda"),
            ("Completed", "Tarjima qilingan"),
            ("Dropped", "Tashlab qo'yilgan"),
        ],
        default="Not Translated",
        verbose_name="Tarjima holati"
    )
    slug = models.SlugField(max_length=255, unique=True, blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        editable=False,
        related_name="mangas_created",
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ("title",)
        verbose_name = "Taytl "
        verbose_name_plural = "Taytlar "
        indexes = [models.Index(fields=("title",))]

    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs):
        # Slug avto-generatsiyasi, agar bo'sh bo'lsa
        if not self.slug:
            self.slug = slugify(self.title)

        # Convert image only if it's a new upload
        if self.cover_image and isinstance(self.cover_image.file, InMemoryUploadedFile):
            img = Image.open(self.cover_image)
            img = img.convert("RGBA")

            buffer = BytesIO()
            img.save(buffer, format="WEBP", quality=80, method=6)
            buffer.seek(0)

            base, _ = self.cover_image.name.rsplit('.', 1)
            webp_name = f"{slugify(base)}.webp"
            self.cover_image.save(webp_name, ContentFile(buffer.read()), save=False)

        super().save(*args, **kwargs)

class Genre(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Janr nomi")
    
    created_by = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.CASCADE,
    editable=False,
    related_name="genres_created",
    null=True,
    blank=True,
    )

    class Meta:
        ordering = ("name",)
        verbose_name = "Janr "
        verbose_name_plural = "Janrlar "

    def __str__(self) -> str:
        return self.name
    
class Chapter(models.Model):
    manga = models.ForeignKey(
        Manga,
        on_delete=models.CASCADE,
        related_name="chapters",
        verbose_name="Manga",
    )
    volume = models.PositiveIntegerField(default=1, verbose_name="Jild")
    chapter_number = models.PositiveIntegerField(verbose_name="Bob")
    release_date = models.DateField(default=date.today, verbose_name="Chiqarilgan sana (Tegilmasin!)")

    thanks = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="thanked_chapters",
        blank=True,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        editable=False,
        related_name="chapters_created",
        null=True,
        blank=True,
    )

    class Meta:
        unique_together = ("manga", "chapter_number", "volume")
        indexes = [models.Index(fields=("manga", "chapter_number"))]
        verbose_name = "Bob "
        verbose_name_plural = "Boblar "

    def __str__(self) -> str:
        return f"{self.manga.title} - Jild: {self.volume}. Bob: {self.chapter_number}"

    @property
    def thanks_count(self):
        return self.thanks.count()


class Page(models.Model):
    """
    Страница главы в формате изображения (JPEG/PNG).
    Каждая страница привязана к конкретной главе.
    """
    chapter = models.ForeignKey(
        Chapter,
        on_delete=models.CASCADE,
        related_name='pages', verbose_name="Qaysi bobga tegishli?"
    )
    page_number = models.PositiveIntegerField(verbose_name="nechanchi sahifa?")
    image = models.ImageField(
        upload_to='chapters/pages/',
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp'])],
        verbose_name="Rasm (JPEG/PNG)"
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        editable=False,
        related_name="pages_created",
        null=True,
        blank=True,
    )

    class Meta:
        unique_together = ('chapter', 'page_number')
        ordering = ['page_number']
        verbose_name = "Sahifa "
        verbose_name_plural = "Sahifalar "

    def __str__(self):
        return f"{self.chapter} — Page {self.page_number}"


class ReadingProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reading_progress")
    manga = models.ForeignKey(Manga, on_delete=models.CASCADE)
    last_read_chapter = models.ForeignKey(
        Chapter, null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
    last_read_page = models.PositiveIntegerField(default=1)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "manga")
        verbose_name = "O'qish jarayoni "
        verbose_name_plural = "O'qish jarayonlari "

    @property
    def last_read_chapter_pk(self):
        """Возвращает id последней прочитанной главы, или None."""
        return self.last_read_chapter.id if self.last_read_chapter else None

    def __str__(self) -> str:
        ch_num = self.last_read_chapter.chapter_number if self.last_read_chapter else "—"
        return f"{self.user.username} — {self.manga.title} (ch.{ch_num}, p.{self.last_read_page})"

