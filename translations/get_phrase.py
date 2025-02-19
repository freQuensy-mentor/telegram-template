import yaml
import re
import glob
import loguru

translations = {}
for file in glob.glob("translations/strings/*.yaml"):
    language_code = re.search(r"strings\.([a-z]{2})\.yaml", file).group(1)
    with open(file, "r") as f:
        translations[language_code] = yaml.load(f, Loader=yaml.FullLoader)
assert len(translations.keys()) > 0
DEFAULT_LANGUAGE = "en"


def get_phrase(phrase_tag, language="en"):
    try:
        return translations[language][phrase_tag]
    except KeyError:
        loguru.logger.warning(
            f"Phrase tag {phrase_tag} not found in language {language}"
        )
        return translations[DEFAULT_LANGUAGE][phrase_tag]
