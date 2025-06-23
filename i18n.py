import os
import yaml
import logging

logger = logging.getLogger(__name__)


class I18n:
    """
    A very lightweight Internationalization (i18n) manager for Python.
    Loads messages from YAML files and supports dynamic value substitution.
    Designed for minimal dependencies and fast execution, suitable for AWS Lambda.
    """

    def __init__(self, translations_dir="locales", default_locale="en"):
        """
        Initializes the I18nManager.

        Args:
            translations_dir (str): The directory where translation YAML files are stored.
                                    E.g., if set to 'locales', it expects files like
                                    'locales/en.yml', 'locales/fr.yml'.
            default_locale (str): The locale to use as a fallback if a message
                                  is not found in the current locale.
        """
        self.translations_dir = translations_dir
        self.default_locale = default_locale
        self._translations_cache = {}
        self._current_locale = default_locale
        self._load_translations_for_locale(default_locale)

    def _load_translations_for_locale(self, locale):
        """
        Loads translations for a specific locale from its YAML file.
        Caches the loaded translations in memory.
        """
        if locale not in self._translations_cache:
            file_path = os.path.join(self.translations_dir, f"{locale}.yml")

            with open(file_path, "r", encoding="utf-8") as f:
                self._translations_cache[locale] = yaml.safe_load(f)

        return self._translations_cache[locale]

    def set_locale(self, locale):
        """
        Sets the current locale for message retrieval.
        Also attempts to load the translations for the new locale if not already cached.

        Args:
            locale (str): The new locale (e.g., 'en', 'fr').
        """
        self._current_locale = locale
        self._load_translations_for_locale(locale)

    def _get_nested_value(self, data, key_path):
        """
        Helper to get a value from a nested dictionary using a dot-separated key path.
        """
        keys = key_path.split(".")
        current_data = data
        for key in keys:
            if isinstance(current_data, dict) and key in current_data:
                current_data = current_data[key]
            else:
                return None
        return current_data

    def t(self, key, **kwargs):
        """
        Translates a message for the current locale.

        Args:
            key (str): The message key (can be dot-separated for nested keys, e.g., 'errors.validation.length').
            **kwargs: Dynamic values to be inserted into the message (e.g., name='Bob').

        Returns:
            str: The translated message with dynamic values populated,
                 or the key itself if no translation is found.
        """
        current_locale_translations = self._translations_cache.get(
            self._current_locale, {}
        )
        message = self._get_nested_value(current_locale_translations, key)

        if message is None and self._current_locale != self.default_locale:
            default_locale_translations = self._translations_cache.get(
                self.default_locale, {}
            )
            message = self._get_nested_value(default_locale_translations, key)

        if message is None:
            return key

        try:
            formatted_message = message
            for k, v in kwargs.items():
                formatted_message = formatted_message.replace(f"{{{k}}}", str(v))
                formatted_message = formatted_message.replace(f"'{{{k}}}'", str(v))
                formatted_message = formatted_message.replace(f'"{{{k}}}"', str(v))
            return formatted_message
        except Exception as e:
            return message
